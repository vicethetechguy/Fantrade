-- Fantrade P2P funding. Apply after 16_activity_share_ratio_and_demo.sql.
-- Fiat moves between counterparties. Only existing FTR is escrowed; nothing is minted.
begin;
create table if not exists public.p2p_settings (id boolean primary key default true check(id), live_enabled boolean not null default false);
insert into public.p2p_settings(id) values(true) on conflict do nothing;
create table if not exists public.p2p_offers (
 id uuid primary key default gen_random_uuid(), request_key uuid not null, owner_id uuid not null references auth.users(id),
 side text not null check(side in ('BUY','SELL')), currency text not null check(currency in ('USD','EUR','GBP','NGN','KES','GHS','ZAR','INR','BRL','PHP','AED','CAD','AUD')),
 price numeric(20,6) not null check(price>0), available numeric(20,2) not null check(available>=0),
 min_fiat numeric(20,2) not null check(min_fiat>0), max_fiat numeric(20,2) not null check(max_fiat>=min_fiat),
 method text not null check(method in ('Bank transfer','Wise','Revolut','Mobile money','Instant payment')),
 payment_details jsonb not null default '{}', status text not null default 'ACTIVE' check(status in ('ACTIVE','CLOSED')),
 created_at timestamptz not null default now(), unique(owner_id,request_key)
);
create table if not exists public.p2p_orders (
 id uuid primary key default gen_random_uuid(), request_key uuid not null, creator_id uuid not null references auth.users(id),
 offer_id uuid not null references public.p2p_offers(id), buyer_id uuid not null references auth.users(id), seller_id uuid not null references auth.users(id),
 tokens numeric(20,2) not null check(tokens>0), fiat numeric(20,2) not null check(fiat>0), price numeric(20,6) not null, currency text not null, method text not null,
 payment_details jsonb not null, status text not null default 'AWAITING_PAYMENT' check(status in ('AWAITING_PAYMENT','PAID','DISPUTED','COMPLETED','CANCELLED','EXPIRED')),
 expires_at timestamptz not null default now()+interval '20 minutes', paid_at timestamptz, completed_at timestamptz,
 created_at timestamptz not null default now(), unique(creator_id,request_key), check(buyer_id<>seller_id)
);
create table if not exists public.p2p_messages (
 id bigint generated always as identity primary key, order_id uuid not null references public.p2p_orders(id),
 author_id uuid references auth.users(id), kind text not null default 'MESSAGE', body text not null check(length(body) between 1 and 1500), created_at timestamptz not null default now()
);
create index if not exists p2p_market_idx on public.p2p_offers(currency,side,status);
create index if not exists p2p_buyer_idx on public.p2p_orders(buyer_id,created_at desc);
create index if not exists p2p_seller_idx on public.p2p_orders(seller_id,created_at desc);
create index if not exists p2p_expiry_idx on public.p2p_orders(expires_at) where status='AWAITING_PAYMENT';
alter table public.p2p_settings enable row level security;
alter table public.p2p_offers enable row level security;
alter table public.p2p_orders enable row level security;
alter table public.p2p_messages enable row level security;
revoke all on public.p2p_settings,public.p2p_offers,public.p2p_orders,public.p2p_messages from anon,authenticated;
-- All private payment instructions and writes are served through participant-checked RPCs.
alter table public.transactions drop constraint if exists transactions_type_check;
alter table public.transactions add constraint transactions_type_check check(type in
 ('GRANT','BUY','SELL','SWAP','CONVERT','SEND','RECEIVE','WITHDRAW','STAKE','PAYOUT','SETTLE','ADJUST','LIST','BURN','FEE_SHARE','P2P_LOCK','P2P_UNLOCK','P2P_BUY','P2P_SELL'));

create or replace function public.ft_p2p_enabled() returns void language plpgsql security definer set search_path=public as $$
begin
 if auth.uid() is null then raise exception 'Sign in to use P2P'; end if;
 if not exists(select 1 from p2p_settings where id and live_enabled) then raise exception 'Live P2P is not enabled yet. No funds were moved.'; end if;
end;$$;
create or replace function public.ft_p2p_details(d jsonb) returns jsonb language plpgsql immutable as $$
begin
 if coalesce(length(trim(d->>'name')),0) not between 2 and 100 or coalesce(length(trim(d->>'provider')),0) not between 2 and 100 or coalesce(length(trim(d->>'account')),0) not between 3 and 150 then raise exception 'Enter the account holder, payment provider and account details'; end if;
 if length(coalesce(d->>'instructions',''))>500 then raise exception 'Payment instructions are too long'; end if;
 return jsonb_build_object('name',trim(d->>'name'),'provider',trim(d->>'provider'),'account',trim(d->>'account'),'instructions',coalesce(d->>'instructions',''));
end;$$;
-- Caller has already locked and authorized the order. Paid/disputed orders cannot expire.
create or replace function public.ft_p2p_return(o public.p2p_orders) returns void language plpgsql security definer set search_path=public as $$
declare a p2p_offers%rowtype;
begin
 select * into a from p2p_offers where id=o.offer_id for update;
 if a.side='SELL' and a.status='ACTIVE' then
  update p2p_offers set available=available+o.tokens where id=a.id;
 else
  update wallets set locked=locked-o.tokens,balance=balance+o.tokens,updated_at=now() where user_id=o.seller_id and locked>=o.tokens;
  if not found then raise exception 'Escrow balance mismatch'; end if;
  if a.status='ACTIVE' then update p2p_offers set available=available+o.tokens where id=a.id; end if;
  insert into transactions(user_id,type,label,total,balance_after) select o.seller_id,'P2P_UNLOCK','P2P escrow returned',o.tokens,balance from wallets where user_id=o.seller_id;
 end if;
end;$$;
create or replace function public.ft_p2p_expire() returns void language plpgsql security definer set search_path=public as $$
declare o p2p_orders%rowtype;
begin
 for o in select * from p2p_orders where status='AWAITING_PAYMENT' and expires_at<=now() and (buyer_id=auth.uid() or seller_id=auth.uid()) for update skip locked loop
  perform ft_p2p_return(o);
  update p2p_orders set status='EXPIRED' where id=o.id;
  insert into p2p_messages(order_id,kind,body) values(o.id,'SYSTEM','Payment window expired. Escrow returned.');
 end loop;
end;$$;
create or replace function public.ft_p2p_market(p_currency text,p_side text) returns jsonb language sql security definer set search_path=public as $$
 select jsonb_build_object('enabled',coalesce((select live_enabled from p2p_settings where id),false),'offers',coalesce((select jsonb_agg(x) from (
 select a.id,a.owner_id,a.side,a.currency,a.price,a.available,a.min_fiat,a.max_fiat,a.method,
 coalesce(p.display_name,'Trader') as name,p.handle,
 (select count(*) from p2p_orders o where (o.buyer_id=a.owner_id or o.seller_id=a.owner_id) and o.status='COMPLETED') as completed
 from p2p_offers a left join profiles p on p.id=a.owner_id
 where a.status='ACTIVE' and a.available>0 and a.currency=p_currency and a.side=p_side and a.owner_id is distinct from auth.uid()
 order by case when p_side='SELL' then a.price else -a.price end,a.created_at limit 50)x),'[]'::jsonb));$$;
create or replace function public.ft_p2p_mine() returns jsonb language plpgsql security definer set search_path=public as $$
begin
 if auth.uid() is null then raise exception 'Sign in to view orders'; end if;
 perform ft_p2p_expire();
 return jsonb_build_object('orders',coalesce((select jsonb_agg(x) from (select o.*,o.buyer_id=auth.uid() as is_buyer,
 coalesce(p.display_name,'Trader') as counterparty,
 coalesce((select jsonb_agg(m order by m.created_at) from (select author_id,kind,body,created_at from p2p_messages where order_id=o.id order by created_at desc limit 100)m),'[]'::jsonb) as messages
 from p2p_orders o left join profiles p on p.id=case when o.buyer_id=auth.uid() then o.seller_id else o.buyer_id end
 where o.buyer_id=auth.uid() or o.seller_id=auth.uid() order by o.created_at desc limit 100)x),'[]'::jsonb),
 'offers',coalesce((select jsonb_agg(a order by created_at desc) from p2p_offers a where owner_id=auth.uid()),'[]'::jsonb));
end;$$;
create or replace function public.ft_p2p_offer(p_input jsonb) returns jsonb language plpgsql security definer set search_path=public as $$
declare a p2p_offers%rowtype; qty numeric:=round((p_input->>'tokens')::numeric,2); px numeric:=(p_input->>'price')::numeric; lo numeric:=(p_input->>'min')::numeric; hi numeric:=(p_input->>'max')::numeric; d jsonb:='{}';
begin
 perform ft_p2p_enabled();
 perform pg_advisory_xact_lock(hashtextextended(auth.uid()::text||(p_input->>'key'),0));
 select * into a from p2p_offers where owner_id=auth.uid() and request_key=(p_input->>'key')::uuid;
 if found then return to_jsonb(a); end if;
 if qty is null or px is null or lo is null or hi is null or qty<=0 or px<=0 or lo<=0 or hi<lo or hi>round(qty*px,2) or qty>1000000 or px>1000000000 then raise exception 'Check the quantity, price and payment limits'; end if;
 if p_input->>'side'='SELL' then d:=ft_p2p_details(p_input->'details'); end if;
 if p_input->>'side'='SELL' then
  update wallets set balance=balance-qty,locked=locked+qty,updated_at=now() where user_id=auth.uid() and balance>=qty;
  if not found then raise exception 'Not enough available FTR to escrow this offer'; end if;
  insert into transactions(user_id,type,label,total,balance_after) select auth.uid(),'P2P_LOCK','P2P sell offer escrow',qty,balance from wallets where user_id=auth.uid();
 end if;
 insert into p2p_offers(request_key,owner_id,side,currency,price,available,min_fiat,max_fiat,method,payment_details)
 values((p_input->>'key')::uuid,auth.uid(),p_input->>'side',p_input->>'currency',px,qty,lo,hi,p_input->>'method',d) returning * into a;
 return to_jsonb(a);
end;$$;
create or replace function public.ft_p2p_close_offer(p_offer uuid) returns void language plpgsql security definer set search_path=public as $$
declare a p2p_offers%rowtype;
begin
 select * into a from p2p_offers where id=p_offer and owner_id=auth.uid() for update;
 if not found then raise exception 'Offer not found'; end if;
 if a.status='CLOSED' then return; end if;
 if a.side='SELL' and a.available>0 then
  update wallets set balance=balance+a.available,locked=locked-a.available,updated_at=now() where user_id=a.owner_id and locked>=a.available;
  if not found then raise exception 'Escrow balance mismatch'; end if;
  insert into transactions(user_id,type,label,total,balance_after) select auth.uid(),'P2P_UNLOCK','Closed P2P offer',a.available,balance from wallets where user_id=auth.uid();
 end if;
 update p2p_offers set available=0,status='CLOSED' where id=a.id;
end;$$;
create or replace function public.ft_p2p_open(p_offer uuid,p_fiat numeric,p_key uuid,p_details jsonb default '{}') returns jsonb language plpgsql security definer set search_path=public as $$
declare a p2p_offers%rowtype; o p2p_orders%rowtype; buyer uuid; seller uuid; qty numeric; payment numeric; d jsonb;
begin
 perform ft_p2p_enabled(); perform ft_p2p_expire();
 -- Serialize same-account retry keys before creating an order, including across offers.
 perform pg_advisory_xact_lock(hashtextextended(auth.uid()::text||p_key::text,0));
 select * into o from p2p_orders where creator_id=auth.uid() and request_key=p_key;
 if found then return to_jsonb(o)||jsonb_build_object('is_buyer',o.buyer_id=auth.uid()); end if;
 select * into a from p2p_offers where id=p_offer for update;
 if not found or a.status<>'ACTIVE' or a.owner_id=auth.uid() then raise exception 'This offer is unavailable'; end if;
 if p_fiat is null or p_fiat<a.min_fiat or p_fiat>a.max_fiat or p_fiat>100000000000 then raise exception 'Amount is outside the offer limits'; end if;
 qty:=trunc(p_fiat/a.price,2); payment:=round(qty*a.price,2);
 if qty<=0 or qty>a.available or payment<a.min_fiat then raise exception 'Not enough FTR available for this amount'; end if;
 buyer:=case when a.side='SELL' then auth.uid() else a.owner_id end;
 seller:=case when a.side='SELL' then a.owner_id else auth.uid() end;
 d:=case when a.side='SELL' then a.payment_details else ft_p2p_details(p_details) end;
 perform 1 from wallets where user_id in(buyer,seller) order by user_id for update;
 if not exists(select 1 from wallets where user_id=buyer) then raise exception 'Buyer wallet is unavailable'; end if;
 if a.side='BUY' then
  update wallets set balance=balance-qty,locked=locked+qty,updated_at=now() where user_id=seller and balance>=qty;
  if not found then raise exception 'Not enough available FTR'; end if;
  insert into transactions(user_id,type,label,total,balance_after) select seller,'P2P_LOCK','P2P order escrow',qty,balance from wallets where user_id=seller;
 end if;
 update p2p_offers set available=available-qty where id=a.id;
 insert into p2p_orders(request_key,creator_id,offer_id,buyer_id,seller_id,tokens,fiat,price,currency,method,payment_details)
 values(p_key,auth.uid(),a.id,buyer,seller,qty,payment,a.price,a.currency,a.method,d) returning * into o;
 insert into p2p_messages(order_id,kind,body) values(o.id,'SYSTEM','FTR secured in escrow. Buyer has 20 minutes to pay.');
 return to_jsonb(o)||jsonb_build_object('is_buyer',buyer=auth.uid());
end;$$;
create or replace function public.ft_p2p_action(p_order uuid,p_action text,p_text text default '') returns jsonb language plpgsql security definer set search_path=public as $$
declare o p2p_orders%rowtype;
begin
 if auth.uid() is null then raise exception 'Sign in first'; end if;
 perform ft_p2p_expire();
 select * into o from p2p_orders where id=p_order and auth.uid() in(buyer_id,seller_id) for update;
 if not found then raise exception 'Order not found'; end if;
 if p_action='PAID' then
  if auth.uid()<>o.buyer_id then raise exception 'Only the buyer can confirm payment'; end if;
  if o.status='PAID' then return to_jsonb(o); end if;
  if o.status<>'AWAITING_PAYMENT' then raise exception 'This order cannot be marked paid'; end if;
  update p2p_orders set status='PAID',paid_at=now() where id=o.id;
 elsif p_action='RELEASE' then
  if auth.uid()<>o.seller_id then raise exception 'Only the seller can confirm receipt'; end if;
  if o.status='COMPLETED' then return to_jsonb(o); end if;
  if o.status<>'PAID' then raise exception 'Payment must be confirmed first; disputed escrow stays locked'; end if;
  perform 1 from wallets where user_id in(o.buyer_id,o.seller_id) order by user_id for update;
  update wallets set locked=locked-o.tokens,updated_at=now() where user_id=o.seller_id and locked>=o.tokens;
  if not found then raise exception 'Escrow balance mismatch'; end if;
  update wallets set balance=balance+o.tokens,updated_at=now() where user_id=o.buyer_id;
  if not found then raise exception 'Buyer wallet is unavailable'; end if;
  insert into transactions(user_id,type,label,total,balance_after) select o.buyer_id,'P2P_BUY','P2P FTR received',o.tokens,balance from wallets where user_id=o.buyer_id;
  insert into transactions(user_id,type,label,total,balance_after) select o.seller_id,'P2P_SELL','P2P FTR sold',o.tokens,balance from wallets where user_id=o.seller_id;
  update p2p_orders set status='COMPLETED',completed_at=now() where id=o.id;
 elsif p_action='CANCEL' then
  if auth.uid()<>o.buyer_id or o.status<>'AWAITING_PAYMENT' then raise exception 'Only the buyer can cancel before payment'; end if;
  perform ft_p2p_return(o); update p2p_orders set status='CANCELLED' where id=o.id;
 elsif p_action='DISPUTE' then
  if o.status not in('PAID','DISPUTED') then raise exception 'Disputes are available after payment is marked sent'; end if;
  if length(trim(p_text))<10 then raise exception 'Describe the issue in at least 10 characters'; end if;
  update p2p_orders set status='DISPUTED' where id=o.id;
 elsif p_action='MESSAGE' then
  if o.status not in('AWAITING_PAYMENT','PAID','DISPUTED') then raise exception 'This conversation is closed'; end if;
 else raise exception 'Unknown action'; end if;
 insert into p2p_messages(order_id,author_id,kind,body) values(o.id,auth.uid(),p_action,
 case when p_action='MESSAGE' or p_action='DISPUTE' then trim(p_text) else p_action||case when length(p_text)>0 then ': '||p_text else '' end end);
 select * into o from p2p_orders where id=o.id; return to_jsonb(o);
end;$$;
-- Disputes require a service-side operator; never grant this function to the browser.
create or replace function public.ft_p2p_resolve(p_order uuid,p_award text,p_reason text) returns void language plpgsql security definer set search_path=public as $$
declare o p2p_orders%rowtype;
begin
 if coalesce(auth.role(),'')<>'service_role' then raise exception 'Support operator required'; end if;
 if length(trim(p_reason))<10 then raise exception 'Record the evidence and decision'; end if;
 select * into o from p2p_orders where id=p_order for update;
 if not found or o.status<>'DISPUTED' then raise exception 'No open dispute'; end if;
 perform 1 from wallets where user_id in(o.buyer_id,o.seller_id) order by user_id for update;
 if p_award='BUYER' then
  update wallets set locked=locked-o.tokens,updated_at=now() where user_id=o.seller_id and locked>=o.tokens;
  if not found then raise exception 'Escrow balance mismatch'; end if;
  update wallets set balance=balance+o.tokens,updated_at=now() where user_id=o.buyer_id;
  if not found then raise exception 'Buyer wallet missing'; end if;
  insert into transactions(user_id,type,label,total,balance_after) select o.buyer_id,'P2P_BUY','P2P dispute resolved: received FTR',o.tokens,balance from wallets where user_id=o.buyer_id;
  insert into transactions(user_id,type,label,total,balance_after) select o.seller_id,'P2P_SELL','P2P dispute resolved: FTR released',o.tokens,balance from wallets where user_id=o.seller_id;
  update p2p_orders set status='COMPLETED',completed_at=now() where id=o.id;
 elsif p_award='SELLER' then
  -- Return disputed funds directly to the seller rather than putting them back in an ad.
  update wallets set locked=locked-o.tokens,balance=balance+o.tokens,updated_at=now() where user_id=o.seller_id and locked>=o.tokens;
  if not found then raise exception 'Escrow balance mismatch'; end if;
  insert into transactions(user_id,type,label,total,balance_after) select o.seller_id,'P2P_UNLOCK','P2P dispute refund',o.tokens,balance from wallets where user_id=o.seller_id;
  update p2p_orders set status='CANCELLED' where id=o.id;
 else raise exception 'Choose BUYER or SELLER'; end if;
 insert into p2p_messages(order_id,kind,body) values(o.id,'RESOLUTION',p_reason);
end;$$;
-- Call once a minute from a trusted worker (including when neither party is online).
create or replace function public.ft_p2p_sweep() returns integer language plpgsql security definer set search_path=public as $$
declare o p2p_orders%rowtype; total integer:=0;
begin
 for o in select * from p2p_orders where status='AWAITING_PAYMENT' and expires_at<=now() for update skip locked loop
  perform ft_p2p_return(o);update p2p_orders set status='EXPIRED' where id=o.id;
  insert into p2p_messages(order_id,kind,body) values(o.id,'SYSTEM','Payment window expired. Escrow returned.');total:=total+1;
 end loop;return total;
end;$$;
revoke all on function public.ft_p2p_sweep() from public,anon,authenticated;
grant execute on function public.ft_p2p_sweep() to service_role;
create or replace function public.ft_p2p_disputes() returns jsonb language sql security definer set search_path=public as $$
 select coalesce(jsonb_agg(x),'[]'::jsonb) from (
 select o.*,coalesce((select jsonb_agg(m order by m.created_at) from p2p_messages m where m.order_id=o.id),'[]'::jsonb) as messages
 from p2p_orders o where o.status='DISPUTED' order by o.created_at limit 100)x;
$$;
revoke all on function public.ft_p2p_disputes() from public,anon,authenticated;
grant execute on function public.ft_p2p_disputes() to service_role;
-- Automatically schedule expiry if this Supabase project already has pg_cron enabled.
do $cron$
begin
 if exists(select 1 from pg_extension where extname='pg_cron') then
  perform cron.unschedule(jobid) from cron.job where jobname='fantrade-p2p-expiry';
  perform cron.schedule('fantrade-p2p-expiry','* * * * *','select public.ft_p2p_sweep()');
 end if;
end;$cron$;
revoke all on function public.ft_p2p_enabled(),public.ft_p2p_details(jsonb),public.ft_p2p_return(public.p2p_orders),public.ft_p2p_expire(),public.ft_p2p_resolve(uuid,text,text) from public,anon,authenticated;
revoke all on function public.ft_p2p_market(text,text),public.ft_p2p_mine(),public.ft_p2p_offer(jsonb),public.ft_p2p_close_offer(uuid),public.ft_p2p_open(uuid,numeric,uuid,jsonb),public.ft_p2p_action(uuid,text,text) from public,anon;
grant execute on function public.ft_p2p_market(text,text) to anon,authenticated;
grant execute on function public.ft_p2p_mine(),public.ft_p2p_offer(jsonb),public.ft_p2p_close_offer(uuid),public.ft_p2p_open(uuid,numeric,uuid,jsonb),public.ft_p2p_action(uuid,text,text) to authenticated;
grant execute on function public.ft_p2p_resolve(uuid,text,text) to service_role;
commit;

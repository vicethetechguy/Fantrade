-- Fantrade support workspace. Run AFTER 17_p2p_escrow.sql (and existing admin migrations).
-- This grants dispute support only, not listing/market/account administration.
begin;
create table if not exists public.p2p_support_operators (
 email text primary key check(email=lower(email)),
 user_id uuid unique references auth.users(id) on delete set null,
 enabled boolean not null default true,
 created_at timestamptz not null default now()
);
create table if not exists public.p2p_support_decisions (
 id bigint generated always as identity primary key,
 order_id uuid not null unique references public.p2p_orders(id),
 operator_id uuid references auth.users(id) on delete set null,
 award text not null check(award in ('BUYER','SELLER')),
 reason text not null check(length(reason) between 20 and 1500),
 created_at timestamptz not null default now()
);
alter table public.p2p_support_operators enable row level security;
alter table public.p2p_support_decisions enable row level security;
revoke all on public.p2p_support_operators,public.p2p_support_decisions from public,anon,authenticated;
insert into public.p2p_support_operators(email,user_id)
values('vectorceenation@gmail.com', (select id from auth.users where lower(email)='vectorceenation@gmail.com' and email_confirmed_at is not null))
on conflict(email) do nothing;
-- Bind the allowlisted, verified email to its actual account ID on first use.
-- Browser/local-storage email strings and editable user_metadata are never trusted.
create or replace function public.ft_require_p2p_support() returns uuid
language plpgsql security definer set search_path=public,pg_temp as $$
declare uid uuid:=auth.uid(); em text; operator public.p2p_support_operators%rowtype;
begin
 if uid is null or coalesce(auth.role(),'')<>'authenticated' then raise exception 'Support access required' using errcode='42501'; end if;
 select lower(email) into em from auth.users where id=uid and email_confirmed_at is not null;
 select * into operator from public.p2p_support_operators where email=em for update;
 if not found or not operator.enabled or (operator.user_id is not null and operator.user_id<>uid)
 then raise exception 'Support access required' using errcode='42501'; end if;
 if exists(select 1 from public.profiles where id=uid and suspended) then raise exception 'Support access suspended' using errcode='42501'; end if;
 if operator.user_id is null then update public.p2p_support_operators set user_id=uid where email=em; end if;
 return uid;
end;$$;
create or replace function public.ft_admin_p2p_whoami() returns jsonb
language plpgsql security definer set search_path=public,pg_temp as $$
declare uid uuid;
begin
 uid:=public.ft_require_p2p_support();
 return jsonb_build_object('allowed',true,'email',(select email from auth.users where id=uid));
exception when insufficient_privilege then return jsonb_build_object('allowed',false);
end;$$;
create or replace function public.ft_admin_p2p_queue(p_history boolean default false) returns jsonb
language plpgsql security definer set search_path=public,pg_temp as $$
begin
 perform public.ft_require_p2p_support();
 return jsonb_build_object(
 'live_enabled',(select live_enabled from p2p_settings where id),
 'open_count',(select count(*) from p2p_orders where status='DISPUTED'),
 'escrow_tokens',(select coalesce(sum(tokens),0) from p2p_orders where status='DISPUTED'),
 'resolved_count',(select count(distinct order_id) from p2p_messages where kind='RESOLUTION'),
 'orders',coalesce((select jsonb_agg(x order by x.created_at) from (
 select o.id,o.tokens,o.fiat,o.currency,o.method,o.status,o.created_at,
 coalesce(b.display_name,'Buyer') as buyer_name,coalesce(s.display_name,'Seller') as seller_name,
 (select min(m.created_at) from p2p_messages m where m.order_id=o.id and m.kind='DISPUTE') as disputed_at
 from p2p_orders o left join profiles b on b.id=o.buyer_id left join profiles s on s.id=o.seller_id
 where (not p_history and o.status='DISPUTED') or (p_history and exists(select 1 from p2p_messages m where m.order_id=o.id and m.kind='RESOLUTION'))
 order by o.created_at limit 100) x),'[]'::jsonb));
end;$$;
create or replace function public.ft_admin_p2p_case(p_order uuid) returns jsonb
language plpgsql security definer set search_path=public,pg_temp as $$
declare result jsonb; uid uuid;
begin
 uid:=public.ft_require_p2p_support();
 select to_jsonb(o)||jsonb_build_object(
 'buyer',jsonb_build_object('name',b.display_name,'email',bu.email),
 'seller',jsonb_build_object('name',s.display_name,'email',su.email),
 'can_resolve',o.status='DISPUTED' and uid not in(o.buyer_id,o.seller_id),
 'messages',coalesce((select jsonb_agg(to_jsonb(m)||jsonb_build_object('author_name',
 case when m.author_id=o.buyer_id then coalesce(b.display_name,'Buyer') when m.author_id=o.seller_id then coalesce(s.display_name,'Seller') when m.author_id is null then 'System' else 'Support' end) order by m.created_at,m.id) from p2p_messages m where m.order_id=o.id),'[]'::jsonb),
 'decision',(select to_jsonb(d) from p2p_support_decisions d where d.order_id=o.id)) into result
 from p2p_orders o left join profiles b on b.id=o.buyer_id left join profiles s on s.id=o.seller_id
 left join auth.users bu on bu.id=o.buyer_id left join auth.users su on su.id=o.seller_id
 where o.id=p_order and (o.status='DISPUTED' or exists(select 1 from p2p_messages m where m.order_id=o.id and m.kind='RESOLUTION'));
 if result is null then raise exception 'Dispute not found'; end if;
 return result;
end;$$;
create or replace function public.ft_p2p_resolve(p_order uuid,p_award text,p_reason text) returns void language plpgsql security definer set search_path=public as $$
declare o p2p_orders%rowtype;
begin
 if coalesce(auth.role(),'')<>'service_role' then perform public.ft_require_p2p_support(); end if;
 if coalesce(length(trim(p_reason)),0) not between 10 and 1500 then raise exception 'Record the evidence and decision'; end if;
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
 insert into p2p_messages(order_id,author_id,kind,body) values(o.id,auth.uid(),'RESOLUTION',trim(p_reason));
end;$$;

-- The private settlement helper remains unavailable directly to authenticated users.
create or replace function public.ft_admin_p2p_resolve(p_order uuid,p_award text,p_reason text) returns jsonb
language plpgsql security definer set search_path=public,pg_temp as $$
declare uid uuid; o public.p2p_orders%rowtype; previous public.p2p_support_decisions%rowtype;
begin
 uid:=public.ft_require_p2p_support();
 if p_award is null or p_award not in('BUYER','SELLER') or coalesce(length(trim(p_reason)),0) not between 20 and 1500
 then raise exception 'Choose a recipient and explain the evidence in 20 to 1500 characters'; end if;
 select * into o from p2p_orders where id=p_order for update;
 if not found then raise exception 'Dispute not found'; end if;
 if uid in(o.buyer_id,o.seller_id) then raise exception 'You cannot decide your own order'; end if;
 select * into previous from p2p_support_decisions where order_id=p_order;
 if found then
  if previous.operator_id=uid and previous.award=p_award and previous.reason=trim(p_reason)
  then return public.ft_admin_p2p_case(p_order); end if;
  raise exception 'This dispute has already been resolved';
 end if;
 perform public.ft_p2p_resolve(p_order,p_award,trim(p_reason));
 insert into p2p_support_decisions(order_id,operator_id,award,reason) values(p_order,uid,p_award,trim(p_reason));
 perform public.ft_admin_note('p2p.resolve',p_order::text,jsonb_build_object('award',p_award,'tokens',o.tokens,'reason',trim(p_reason)));
 return public.ft_admin_p2p_case(p_order);
end;$$;
revoke all on function public.ft_require_p2p_support(),public.ft_p2p_resolve(uuid,text,text) from public,anon,authenticated;
grant execute on function public.ft_p2p_resolve(uuid,text,text) to service_role;
revoke all on function public.ft_admin_p2p_whoami(),public.ft_admin_p2p_queue(boolean),public.ft_admin_p2p_case(uuid),public.ft_admin_p2p_resolve(uuid,text,text) from public,anon;
grant execute on function public.ft_admin_p2p_whoami(),public.ft_admin_p2p_queue(boolean),public.ft_admin_p2p_case(uuid),public.ft_admin_p2p_resolve(uuid,text,text) to authenticated;
commit;

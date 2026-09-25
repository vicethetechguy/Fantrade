-- Fantrade · dollars everywhere. Run after 11_ftr_economy.sql. Safe to run again.
--
-- Money in and out of Fantrade is in US dollars: top-ups are bought in
-- dollars at the live $FTR price, withdrawals default to a dollar account,
-- and nothing is quoted in pounds any more.
--   $FTR received for a top-up = dollars ÷ $FTR price, less 0.5%

-- The wallet's rate is now "$FTR per $1".
do $$
begin
  if exists (select 1 from information_schema.columns
              where table_schema = 'public' and table_name = 'wallets' and column_name = 'gbp_rate') then
    alter table public.wallets rename column gbp_rate to usd_rate;
  end if;
end $$;
alter table public.wallets alter column usd_rate type numeric(18,6);
alter table public.wallets alter column usd_rate set default 0.5;
alter table public.payout_accounts alter column currency set default 'USD';

-- Pounds leave the market and the functions that used them.
drop function if exists public.ft_convert_gbp(numeric);
drop function if exists public.ft_admin_set_market(numeric, numeric, numeric);

create or replace function public.ft_reprice()
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare fx numeric := public.ft_ftr_usd();
begin
  update public.assets
     set price = round(coalesce(price_usd, valuation_usd / total_shares) / fx, 6),
         reference_value = round(coalesce(valuation_usd / total_shares, price_usd) / fx, 6),
         updated_at = now()
   where coalesce(price_usd, valuation_usd) is not null;
  update public.listings l
     set fee_level1 = round(500000 * a.valuation_usd / a.total_shares / fx, 2),
         fee_level2 = round(1000000 * a.valuation_usd / a.total_shares / fx, 2)
    from public.assets a
   where a.id = l.asset_id and a.valuation_usd is not null and l.claimed_by is null;
  update public.wallets set usd_rate = round(1 / fx, 6);
end;
$$;

create or replace function public.ft_market()
returns json language sql stable security definer set search_path = public, pg_temp as $$
  select json_build_object(
    'ftr_usd', m.price_usd, 'ftr_per_usd', round(1 / m.price_usd, 6), 'max_supply', m.max_supply, 'burned', m.burned,
    'circulating', coalesce((select sum(balance + locked) from public.wallets), 0),
    'treasury', public.ft_treasury(), 'welcome_grant', m.welcome_grant, 'updated_at', m.updated_at)
  from public.ftr_market m where m.id;
$$;

-- ── Top up with dollars ─────────────────────────────────────────────────
create or replace function public.ft_convert_usd(p_usd numeric)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  fx numeric := public.ft_ftr_usd(); usd numeric(20,2); gross numeric(20,2); fee numeric(20,2); net numeric(20,2); bal numeric(20,2);
begin
  usd := round(p_usd, 2);
  if usd is null or usd <= 0 then raise exception 'Enter an amount greater than zero'; end if;
  if usd > 100000 then raise exception 'Top-ups are capped at $100,000 at a time'; end if;

  gross := round(usd / fx, 2);
  fee   := round(gross * public.ft_fee_rate('CONVERT'), 2);
  net   := gross - fee;
  if net <= 0 then raise exception 'That is too small to buy any $FTR'; end if;
  perform public.ft_draw_treasury(net);

  update public.wallets set balance = balance + net, usd_rate = round(1 / fx, 6), updated_at = now()
   where user_id = uid returning balance into bal;
  if bal is null then raise exception 'No wallet for this account'; end if;

  insert into public.transactions (user_id, type, label, price, total, fee, balance_after)
  values (uid, 'CONVERT', 'Added funds ($' || trim(to_char(usd, 'FM999999990.00')) || ' at $' || trim(to_char(fx, 'FM9990.00')) || ' a $FTR)',
          fx, net, fee, bal);

  return json_build_object('received', net, 'fee', fee, 'balance', bal, 'usd', usd,
                           'ftr_usd', fx, 'ftr_per_usd', round(1 / fx, 6));
end;
$$;

-- ── Withdraw: to a dollar account unless another is chosen ──────────────
create or replace function public.ft_withdraw_to_bank(
  p_amount numeric, p_currency text, p_holder text, p_bank text, p_account text, p_save boolean default true)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  amount numeric(20,2); fee numeric(20,2); total numeric(20,2);
  bal numeric(20,2); digits text; last4 text; fx numeric := public.ft_ftr_usd();
begin
  amount := round(p_amount, 2);
  if amount is null or amount <= 0 then raise exception 'Enter an amount greater than zero'; end if;
  if coalesce(trim(p_holder), '') = '' then raise exception 'Enter the account holder name'; end if;
  if coalesce(trim(p_bank), '') = '' then raise exception 'Enter your bank name'; end if;

  digits := regexp_replace(coalesce(p_account, ''), '[^A-Za-z0-9]', '', 'g');
  if length(digits) < 6 then raise exception 'Enter a valid account number'; end if;
  last4 := right(digits, 4);

  -- 0.5%, at least $5 worth of $FTR.
  fee   := greatest(round(5 / fx, 2), round(amount * public.ft_fee_rate('WITHDRAW'), 2));
  total := amount + fee;

  update public.wallets set balance = balance - total, updated_at = now()
   where user_id = uid and balance >= total returning balance into bal;
  if bal is null then raise exception 'Your balance cannot cover this amount plus the % $FTR fee', fee; end if;

  if p_save then
    insert into public.payout_accounts (user_id, currency, holder, bank, account_last4)
    values (uid, coalesce(p_currency, 'USD'), trim(p_holder), trim(p_bank), last4)
    on conflict (user_id) do update set currency = excluded.currency, holder = excluded.holder,
      bank = excluded.bank, account_last4 = excluded.account_last4, updated_at = now();
  end if;

  insert into public.transactions (user_id, type, label, price, total, fee, balance_after)
  values (uid, 'WITHDRAW', trim(p_bank) || ' ••' || last4 || ' (' || coalesce(p_currency, 'USD') || ')', fx, total, fee, bal);

  return json_build_object('amount', amount, 'usd', round(amount * fx, 2), 'fee', fee, 'total', total, 'balance', bal,
                           'destination', trim(p_bank) || ' ••' || last4);
end;
$$;

-- ── Admin: set the $FTR price and the welcome grant ─────────────────────
create or replace function public.ft_admin_set_market(p_ftr_usd numeric, p_welcome numeric default null)
returns json language plpgsql security definer set search_path = public, pg_temp as $$
declare before numeric;
begin
  perform public.ft_require_admin(true);
  if p_ftr_usd is null or p_ftr_usd <= 0 or p_ftr_usd > 1000000 then raise exception 'Set a $FTR price above $0'; end if;
  if p_welcome is not null and (p_welcome < 0 or p_welcome > 100000) then raise exception 'The welcome grant must be between 0 and 100,000 $FTR'; end if;
  select price_usd into before from public.ftr_market where id for update;
  update public.ftr_market set price_usd = p_ftr_usd, welcome_grant = coalesce(p_welcome, welcome_grant), updated_at = now() where id;
  perform public.ft_reprice();
  perform public.ft_admin_note('market.set', '$FTR', jsonb_build_object('from', before, 'to', p_ftr_usd, 'welcome_grant', p_welcome));
  return public.ft_market();
end;
$$;

-- New sign-ups: the welcome grant, with the wallet's dollar rate.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  base    text;
  candidate text;
  n       int := 0;
  grant_amt numeric(20,2);
begin
  base := lower(regexp_replace(coalesce(new.raw_user_meta_data->>'handle',
                                        new.raw_user_meta_data->>'display_name',
                                        split_part(new.email, '@', 1)), '[^a-zA-Z0-9]+', '_', 'g'));
  base := regexp_replace(base, '^_+|_+$', '', 'g');
  if length(base) < 3 then base := 'manager_' || substr(new.id::text, 1, 6); end if;
  base := left(base, 16);
  candidate := base;
  while exists (select 1 from public.profiles p where p.handle = candidate) loop
    n := n + 1;
    candidate := left(base, 16) || n::text;
  end loop;

  insert into public.profiles (id, handle, display_name, region, home_league)
  values (new.id, candidate,
          coalesce(new.raw_user_meta_data->>'display_name', 'Manager'),
          coalesce(new.raw_user_meta_data->>'region', 'United Kingdom'),
          coalesce(new.raw_user_meta_data->>'home_league', 'Premier League'));

  perform 1 from public.ftr_market where id for update;
  select least(m.welcome_grant, greatest(0, public.ft_treasury())) into grant_amt from public.ftr_market m where m.id;
  insert into public.wallets (user_id, balance, usd_rate)
  values (new.id, grant_amt, (select round(1 / price_usd, 6) from public.ftr_market where id));

  if grant_amt > 0 then
    insert into public.transactions (user_id, type, label, total, balance_after)
    values (new.id, 'GRANT', 'Welcome balance', grant_amt, grant_amt);
  end if;
  return new;
end;
$$;


-- What the app loads: the wallet with its dollar rate, and the market.
create or replace function public.ft_snapshot()
returns json
language plpgsql security definer set search_path = public, pg_temp stable
as $$
declare uid uuid := public.ft_require_user();
begin
  return json_build_object(
    'profile', (select row_to_json(p) from (
        select id, handle, display_name, region, home_league, onboarded, avatar_url, created_at
        from public.profiles where id = uid) p),
    'wallet', (select row_to_json(w) from (
        select balance, locked, season_earned, usd_rate from public.wallets where user_id = uid) w),
    'market', public.ft_market(),
    'holdings', coalesce((select json_agg(h) from (
        select h.asset_id, h.shares, h.locked, h.avg_cost, h.slot, a.name, a.kind, a.club, a.price, a.price_usd, a.valuation_usd
        from public.holdings h join public.assets a on a.id = h.asset_id
        where h.user_id = uid and h.shares > 0 order by h.shares * a.price desc) h), '[]'::json),
    'transactions', coalesce((select json_agg(t) from (
        select type, asset_id, label, shares, price, total, fee, created_at
        from public.transactions where user_id = uid
        order by created_at desc, id desc limit 60) t), '[]'::json),
    'payout', (select row_to_json(b) from (
        select currency, holder, bank, account_last4 from public.payout_accounts where user_id = uid) b),
    'clubs', coalesce((select json_agg(c) from (
        select id, name, stadium, colors, color_name, formation, coach,
               division, season_fp, boost, is_active, created_at
        from public.clubs where user_id = uid order by created_at) c), '[]'::json),
    'entries', coalesce((select json_agg(e) from (
        select id, club_id, mode, target, tier, multiplier, stake, asset_id,
               staked_shares, match, market, selections,
               projected_fp, matchday, status, scored_fp, payout, created_at
        from public.fanplay_entries where user_id = uid and status = 'ACTIVE'
        order by created_at desc) e), '[]'::json)
  );
end;
$$;

-- The admin overview reads ft_market(), which no longer carries pounds.
create or replace function public.ft_admin_overview()
returns json language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public.ft_require_admin();
  return json_build_object(
    'ftr',             public.ft_market(),
    'managers',        (select count(*) from public.profiles),
    'managers_7d',     (select count(*) from public.profiles where created_at > now() - interval '7 days'),
    'suspended',       (select count(*) from public.profiles where suspended),
    'wallet_ftr',      (select coalesce(sum(balance), 0) from public.wallets),
    'locked_ftr',      (select coalesce(sum(locked), 0) from public.wallets),
    'open_to_claim',   (select count(*) from public.listings where is_active and claimed_by is null),
    'paused',          (select count(*) from public.listings l join public.assets a on a.id = l.asset_id
                         where not l.is_active and l.claimed_by is null and not a.is_active),
    'trading',         (select count(*) from public.assets where is_active),
    'claims',          (select count(*) from public.claims),
    'claims_paid',     (select coalesce(sum(fee_paid), 0) from public.claims),
    'claims_burned',   (select coalesce(sum(fee_burned), 0) from public.claims),
    'fanplay_active',  (select count(*) from public.fanplay_entries where status in ('ACTIVE','LIVE')),
    'fanplay_pending', (select count(*) from public.fanplay_entries where status = 'PENDING_SETTLEMENT'),
    'claims_by_day',   (select coalesce(json_agg(json_build_object('day', d::date, 'claims', coalesce(c.n, 0), 'paid', coalesce(c.paid, 0)) order by d), '[]'::json)
                          from generate_series(current_date - 13, current_date, interval '1 day') d
                          left join (select claimed_at::date as day, count(*) n, sum(fee_paid) paid
                                       from public.claims group by 1) c on c.day = d::date),
    'recent',          (select coalesce(json_agg(r order by r.at desc), '[]'::json) from (
                          select * from (
                            select 'claim' as kind, c.claimed_at as at, p.handle as who,
                                   'claimed ' || c.shares / 100000 || '% of ' || a.name as what, c.fee_paid as amount
                              from public.claims c
                              join public.listings l on l.id = c.listing_id
                              join public.assets a on a.id = l.asset_id
                              left join public.profiles p on p.id = c.user_id
                            union all
                            select 'admin', g.created_at, p.handle, g.action || coalesce(' · ' || g.target, ''), null
                              from public.admin_log g left join public.profiles p on p.id = g.admin_id
                            union all
                            select 'signup', p.created_at, p.handle, 'joined Fantrade', null from public.profiles p
                          ) x order by at desc limit 12) r)
  );
end;
$$;



-- Nothing reads the pound rate any more.
alter table public.ftr_market drop column if exists gbp_usd;
select public.ft_reprice();

revoke execute on function public.ft_convert_usd(numeric), public.ft_admin_set_market(numeric, numeric) from public, anon;
grant execute on function public.ft_convert_usd(numeric), public.ft_admin_set_market(numeric, numeric),
  public.ft_withdraw_to_bank(numeric, text, text, text, text, boolean), public.ft_snapshot(), public.ft_admin_overview() to authenticated;
grant execute on function public.ft_market() to anon, authenticated;

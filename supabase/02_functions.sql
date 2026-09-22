-- Fantrade · the only way money and shares move.
--
-- Every function here runs as the table owner (security definer), so it can
-- write tables the browser cannot. Each one starts from auth.uid(), re-reads the
-- price from the catalogue and re-checks the balance or the share count, so a
-- tampered request can only ever fail — never overpay, oversell, or mint shares.

-- Fees, in one place.
create or replace function public.ft_fee_rate(p_kind text)
returns numeric language sql immutable as $$
  select case p_kind
    when 'TRADE'    then 0.004   -- 0.4% on a buy or a sell
    when 'SWAP'     then 0.004
    when 'CONVERT'  then 0.005   -- 0.5% converting pounds to $FTR
    when 'WITHDRAW' then 0.005   -- 0.5%, with a 50 $FTR minimum
    else 0 end;
$$;

create or replace function public.ft_require_user()
returns uuid language plpgsql stable as $$
declare uid uuid := auth.uid();
begin
  if uid is null then raise exception 'Sign in to continue' using errcode = '28000'; end if;
  return uid;
end;
$$;

-- ── Everything the app needs on load, in one round trip ───────────────
create or replace function public.ft_snapshot()
returns json
language plpgsql security definer set search_path = public, pg_temp stable
as $$
declare uid uuid := public.ft_require_user();
begin
  return json_build_object(
    'profile', (select row_to_json(p) from (
        select id, handle, display_name, region, home_league, onboarded, created_at
        from public.profiles where id = uid) p),
    'wallet', (select row_to_json(w) from (
        select balance, locked, season_earned, gbp_rate from public.wallets where user_id = uid) w),
    'holdings', coalesce((select json_agg(h) from (
        select h.asset_id, h.shares, h.locked, h.avg_cost, h.slot, a.name, a.kind, a.club, a.price
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

-- ── Buy ───────────────────────────────────────────────────────────────
create or replace function public.ft_buy_shares(p_asset text, p_shares bigint)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  a   public.assets%rowtype;
  gross numeric(20,2); fee numeric(20,2); total numeric(20,2);
  -- Named apart from the holdings columns: a plpgsql variable sharing a column
  -- name makes `returning shares, avg_cost` ambiguous, and Postgres refuses it.
  bal numeric(20,2); new_held bigint; new_avg numeric(12,4);
begin
  if p_shares is null or p_shares <= 0 then raise exception 'Enter a whole number of shares, one or more'; end if;
  select * into a from public.assets where id = p_asset and is_active for update;
  if not found then raise exception 'That asset is not trading'; end if;

  gross := round(a.price * p_shares, 2);
  fee   := round(gross * public.ft_fee_rate('TRADE'), 2);
  total := gross + fee;

  update public.wallets set balance = balance - total, updated_at = now()
   where user_id = uid and balance >= total
   returning balance into bal;
  if bal is null then raise exception 'Not enough $FTR. This costs % $FTR including the fee.', total; end if;

  insert into public.holdings (user_id, asset_id, shares, avg_cost)
  values (uid, p_asset, p_shares, a.price)
  on conflict (user_id, asset_id) do update
    set avg_cost = round(((public.holdings.shares * public.holdings.avg_cost) + (p_shares * a.price))
                         / (public.holdings.shares + p_shares), 4),
        shares = public.holdings.shares + p_shares,
        updated_at = now()
  returning public.holdings.shares, public.holdings.avg_cost into new_held, new_avg;

  update public.assets set circulating = least(total_shares, circulating + p_shares), updated_at = now() where id = p_asset;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'BUY', p_asset, 'Bought shares', p_shares, a.price, total, fee, bal);

  return json_build_object('asset', p_asset, 'shares', p_shares, 'price', a.price,
                           'fee', fee, 'total', total, 'balance', bal, 'held', new_held, 'avg_cost', new_avg);
end;
$$;

-- ── Sell ──────────────────────────────────────────────────────────────
create or replace function public.ft_sell_shares(p_asset text, p_shares bigint)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  a public.assets%rowtype;
  h public.holdings%rowtype;
  gross numeric(20,2); fee numeric(20,2); net numeric(20,2); bal numeric(20,2);
begin
  if p_shares is null or p_shares <= 0 then raise exception 'Enter a whole number of shares, one or more'; end if;
  select * into a from public.assets where id = p_asset for update;
  if not found then raise exception 'That asset is not listed'; end if;

  select * into h from public.holdings where user_id = uid and asset_id = p_asset for update;
  if not found or (h.shares - h.locked) < p_shares then
    raise exception 'You have % shares available to sell', coalesce(h.shares - h.locked, 0);
  end if;

  gross := round(a.price * p_shares, 2);
  fee   := round(gross * public.ft_fee_rate('TRADE'), 2);
  net   := gross - fee;

  update public.holdings set shares = shares - p_shares, updated_at = now()
   where user_id = uid and asset_id = p_asset;
  update public.assets set circulating = greatest(0, circulating - p_shares), updated_at = now() where id = p_asset;
  update public.wallets set balance = balance + net, updated_at = now() where user_id = uid returning balance into bal;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'SELL', p_asset, 'Sold shares', p_shares, a.price, net, fee, bal);

  return json_build_object('asset', p_asset, 'shares', p_shares, 'price', a.price,
                           'fee', fee, 'total', net, 'balance', bal);
end;
$$;

-- ── Swap one player's shares straight into another's ──────────────────
create or replace function public.ft_swap_shares(p_from text, p_to text, p_shares bigint)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  af public.assets%rowtype; at2 public.assets%rowtype;
  h public.holdings%rowtype;
  gross numeric(20,2); fee numeric(20,2); net numeric(20,2);
  got bigint; spend numeric(20,2); change numeric(20,2); bal numeric(20,2);
begin
  if p_from = p_to then raise exception 'Choose two different assets to swap between'; end if;
  if p_shares is null or p_shares <= 0 then raise exception 'Enter a whole number of shares, one or more'; end if;

  select * into af from public.assets where id = p_from for update;
  if not found then raise exception 'That asset is not listed'; end if;
  select * into at2 from public.assets where id = p_to and is_active for update;
  if not found then raise exception 'That asset is not trading'; end if;

  select * into h from public.holdings where user_id = uid and asset_id = p_from for update;
  if not found or (h.shares - h.locked) < p_shares then
    raise exception 'You have % shares available to swap', coalesce(h.shares - h.locked, 0);
  end if;

  gross := round(af.price * p_shares, 2);
  fee   := round(gross * public.ft_fee_rate('SWAP'), 2);
  net   := gross - fee;
  got   := floor(net / at2.price);
  if got < 1 then raise exception 'That is not enough to buy a whole share of %', p_to; end if;
  spend  := round(got * at2.price, 2);
  change := net - spend;

  update public.holdings set shares = shares - p_shares, updated_at = now()
   where user_id = uid and asset_id = p_from;

  insert into public.holdings (user_id, asset_id, shares, avg_cost)
  values (uid, p_to, got, at2.price)
  on conflict (user_id, asset_id) do update
    set avg_cost = round(((public.holdings.shares * public.holdings.avg_cost) + (got * at2.price))
                         / (public.holdings.shares + got), 4),
        shares = public.holdings.shares + got,
        updated_at = now();

  update public.wallets set balance = balance + change, updated_at = now() where user_id = uid returning balance into bal;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'SWAP', p_to, p_from || ' → ' || p_to, got, at2.price, spend, fee, bal);

  return json_build_object('from', p_from, 'to', p_to, 'spent', p_shares, 'received', got,
                           'fee', fee, 'change', change, 'balance', bal);
end;
$$;

-- ── Add funds (demo conversion from pounds) ───────────────────────────
create or replace function public.ft_convert_gbp(p_gbp numeric)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  rate numeric; gross numeric(20,2); fee numeric(20,2); net numeric(20,2); bal numeric(20,2);
begin
  if p_gbp is null or p_gbp <= 0 then raise exception 'Enter an amount greater than zero'; end if;
  if p_gbp > 100000 then raise exception 'Demo conversions are capped at £100,000'; end if;

  select gbp_rate into rate from public.wallets where user_id = uid for update;
  if rate is null then raise exception 'No wallet for this account'; end if;

  gross := round(p_gbp * rate, 2);
  fee   := round(gross * public.ft_fee_rate('CONVERT'), 2);
  net   := gross - fee;

  update public.wallets set balance = balance + net, updated_at = now() where user_id = uid returning balance into bal;

  insert into public.transactions (user_id, type, label, total, fee, balance_after)
  values (uid, 'CONVERT', 'Added funds (£' || trim(to_char(p_gbp, 'FM999999990.00')) || ')', net, fee, bal);

  return json_build_object('received', net, 'fee', fee, 'balance', bal, 'rate', rate);
end;
$$;

-- ── Send $FTR to another manager by handle ────────────────────────────
create or replace function public.ft_transfer_ftr(p_handle text, p_amount numeric)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  target uuid; target_handle text; amount numeric(20,2); bal numeric(20,2);
begin
  amount := round(p_amount, 2);
  if amount is null or amount <= 0 then raise exception 'Enter an amount greater than zero'; end if;

  select id, handle into target, target_handle
    from public.profiles where handle = lower(ltrim(p_handle, '@'));
  if target is null then raise exception 'No manager with that handle'; end if;
  if target = uid then raise exception 'You cannot send $FTR to yourself'; end if;

  update public.wallets set balance = balance - amount, updated_at = now()
   where user_id = uid and balance >= amount returning balance into bal;
  if bal is null then raise exception 'Not enough $FTR for this transfer'; end if;

  update public.wallets set balance = balance + amount, updated_at = now() where user_id = target;

  insert into public.transactions (user_id, type, label, total, balance_after)
  values (uid, 'SEND', 'Transfer to @' || target_handle, amount, bal);
  insert into public.transactions (user_id, type, label, total)
  values (target, 'RECEIVE', 'Transfer received', amount);

  return json_build_object('sent', amount, 'to', '@' || target_handle, 'balance', bal);
end;
$$;

-- ── Withdraw to a bank account ────────────────────────────────────────
create or replace function public.ft_withdraw_to_bank(
  p_amount numeric, p_currency text, p_holder text, p_bank text, p_account text, p_save boolean default true)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  amount numeric(20,2); fee numeric(20,2); total numeric(20,2);
  bal numeric(20,2); digits text; last4 text;
begin
  amount := round(p_amount, 2);
  if amount is null or amount <= 0 then raise exception 'Enter an amount greater than zero'; end if;
  if coalesce(trim(p_holder), '') = '' then raise exception 'Enter the account holder name'; end if;
  if coalesce(trim(p_bank), '') = '' then raise exception 'Enter your bank name'; end if;

  digits := regexp_replace(coalesce(p_account, ''), '[^A-Za-z0-9]', '', 'g');
  if length(digits) < 6 then raise exception 'Enter a valid account number'; end if;
  last4 := right(digits, 4);

  fee   := greatest(50, round(amount * public.ft_fee_rate('WITHDRAW'), 2));
  total := amount + fee;

  update public.wallets set balance = balance - total, updated_at = now()
   where user_id = uid and balance >= total returning balance into bal;
  if bal is null then raise exception 'Your balance cannot cover this amount plus the % $FTR fee', fee; end if;

  if p_save then
    insert into public.payout_accounts (user_id, currency, holder, bank, account_last4)
    values (uid, coalesce(p_currency, 'GBP'), trim(p_holder), trim(p_bank), last4)
    on conflict (user_id) do update set currency = excluded.currency, holder = excluded.holder,
      bank = excluded.bank, account_last4 = excluded.account_last4, updated_at = now();
  end if;

  insert into public.transactions (user_id, type, label, total, fee, balance_after)
  values (uid, 'WITHDRAW', trim(p_bank) || ' ••' || last4 || ' (' || coalesce(p_currency, 'GBP') || ')', total, fee, bal);

  return json_build_object('amount', amount, 'fee', fee, 'total', total, 'balance', bal,
                           'destination', trim(p_bank) || ' ••' || last4);
end;
$$;

-- ── Profile edits ─────────────────────────────────────────────────────
create or replace function public.ft_update_profile(
  p_display_name text default null, p_handle text default null,
  p_region text default null, p_home_league text default null, p_onboarded boolean default null)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare uid uuid := public.ft_require_user(); wanted text;
begin
  if p_handle is not null then
    wanted := lower(regexp_replace(ltrim(p_handle, '@'), '[^a-zA-Z0-9_]+', '_', 'g'));
    if wanted !~ '^[a-z0-9_]{3,20}$' then raise exception 'Handles are 3–20 letters, numbers or underscores'; end if;
    if exists (select 1 from public.profiles where handle = wanted and id <> uid) then
      raise exception 'That handle is already taken';
    end if;
  end if;

  update public.profiles set
    display_name = coalesce(nullif(trim(p_display_name), ''), display_name),
    handle       = coalesce(wanted, handle),
    region       = coalesce(nullif(trim(p_region), ''), region),
    home_league  = coalesce(nullif(trim(p_home_league), ''), home_league),
    onboarded    = coalesce(p_onboarded, onboarded),
    updated_at   = now()
  where id = uid;

  return (select row_to_json(p) from (
    select handle, display_name, region, home_league, onboarded from public.profiles where id = uid) p);
end;
$$;

-- ── Who may call what ─────────────────────────────────────────────────
revoke execute on all functions in schema public from public, anon;
grant execute on function
  public.ft_snapshot(), public.ft_buy_shares(text, bigint), public.ft_sell_shares(text, bigint),
  public.ft_swap_shares(text, text, bigint), public.ft_convert_gbp(numeric),
  public.ft_transfer_ftr(text, numeric),
  public.ft_withdraw_to_bank(numeric, text, text, text, text, boolean),
  public.ft_update_profile(text, text, text, text, boolean)
to authenticated;

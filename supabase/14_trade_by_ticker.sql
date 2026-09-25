-- Fantrade · Trade by F-ticker. Run after 13_coaches_to_claim.sql.
-- Safe to run more than once.
--
-- The app names shares by their F-ticker (FSAKA, FHLND …) while the database
-- keys them by id ($Saka, $Haaland …). Buying, selling, swapping, setting a
-- Dream Club slot and staking shares in FanPlay all looked the share up by id
-- only, so every trade from the app was refused with "That asset is not
-- trading" and the balance was rolled back. Each of those now accepts either
-- the id or the ticker, and the account snapshot carries the ticker too.

-- The id of a share, given its id or its F-ticker (case-insensitive). Anything
-- it cannot match comes back unchanged, so the usual message still explains.
create or replace function public.ft_asset_id(p text)
returns text language sql stable security definer set search_path = public, pg_temp as $$
  select coalesce(
    (select id from public.assets where id = p limit 1),
    (select id from public.assets where upper(ticker) = upper(trim(p)) limit 1),
    p);
$$;

-- ft_buy_shares: accepts the id or the F-ticker
CREATE OR REPLACE FUNCTION public.ft_buy_shares(p_asset text, p_shares bigint)
 RETURNS json
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
declare
  uid uuid := public.ft_require_user();
  a   public.assets%rowtype;
  px numeric(18,6); gross numeric(20,2); fee numeric(20,2); total numeric(20,2);
  bal numeric(20,2); new_held bigint; new_avg numeric(18,6);
begin
  p_asset := public.ft_asset_id(p_asset);
  if p_shares is null or p_shares <= 0 then raise exception 'Enter a whole number of shares, one or more'; end if;
  select * into a from public.assets where id = p_asset and is_active for update;
  if not found then raise exception 'That asset is not trading'; end if;
  if a.circulating + p_shares > a.total_shares then raise exception 'Only % shares of % are left to buy', a.total_shares - a.circulating, a.name; end if;

  px    := public.ft_share_ftr(p_asset);
  gross := greatest(0.01, round(px * p_shares, 2));
  fee   := round(gross * public.ft_fee_rate('TRADE'), 2);
  total := gross + fee;

  update public.wallets set balance = balance - total, updated_at = now()
   where user_id = uid and balance >= total
   returning balance into bal;
  if bal is null then raise exception 'Not enough $FTR. This costs % $FTR including the fee.', total; end if;

  insert into public.holdings (user_id, asset_id, shares, avg_cost)
  values (uid, p_asset, p_shares, px)
  on conflict (user_id, asset_id) do update
    set avg_cost = round(((public.holdings.shares * public.holdings.avg_cost) + (p_shares * px))
                         / (public.holdings.shares + p_shares), 6),
        shares = public.holdings.shares + p_shares,
        updated_at = now()
  returning public.holdings.shares, public.holdings.avg_cost into new_held, new_avg;

  update public.assets set circulating = circulating + p_shares, price = px, updated_at = now() where id = p_asset;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'BUY', p_asset, 'Bought shares', p_shares, px, total, fee, bal);

  return json_build_object('asset', p_asset, 'shares', p_shares, 'price', px, 'price_usd', a.price_usd,
                           'ftr_usd', public.ft_ftr_usd(), 'fee', fee, 'total', total,
                           'total_usd', round(total * public.ft_ftr_usd(), 2), 'balance', bal, 'held', new_held, 'avg_cost', new_avg);
end;
$function$;

-- ft_sell_shares: accepts the id or the F-ticker
CREATE OR REPLACE FUNCTION public.ft_sell_shares(p_asset text, p_shares bigint)
 RETURNS json
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
declare
  uid uuid := public.ft_require_user();
  a public.assets%rowtype;
  h public.holdings%rowtype;
  px numeric(18,6); gross numeric(20,2); fee numeric(20,2); net numeric(20,2); bal numeric(20,2);
begin
  p_asset := public.ft_asset_id(p_asset);
  if p_shares is null or p_shares <= 0 then raise exception 'Enter a whole number of shares, one or more'; end if;
  select * into a from public.assets where id = p_asset for update;
  if not found then raise exception 'That asset is not listed'; end if;

  select * into h from public.holdings where user_id = uid and asset_id = p_asset for update;
  if not found or (h.shares - h.locked) < p_shares then
    raise exception 'You have % shares available to sell', coalesce(h.shares - h.locked, 0);
  end if;

  px    := public.ft_share_ftr(p_asset);
  gross := round(px * p_shares, 2);
  fee   := round(gross * public.ft_fee_rate('TRADE'), 2);
  net   := gross - fee;
  perform public.ft_draw_treasury(net);

  update public.holdings set shares = shares - p_shares, updated_at = now()
   where user_id = uid and asset_id = p_asset;
  update public.assets set circulating = greatest(0, circulating - p_shares), updated_at = now() where id = p_asset;
  update public.wallets set balance = balance + net, updated_at = now() where user_id = uid returning balance into bal;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'SELL', p_asset, 'Sold shares', p_shares, px, net, fee, bal);

  return json_build_object('asset', p_asset, 'shares', p_shares, 'price', px, 'fee', fee, 'total', net,
                           'total_usd', round(net * public.ft_ftr_usd(), 2), 'balance', bal);
end;
$function$;

-- ft_swap_shares: accepts the id or the F-ticker
CREATE OR REPLACE FUNCTION public.ft_swap_shares(p_from text, p_to text, p_shares bigint)
 RETURNS json
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
declare
  uid uuid := public.ft_require_user();
  af public.assets%rowtype; at2 public.assets%rowtype;
  h public.holdings%rowtype;
  pf numeric(18,6); pt numeric(18,6);
  gross numeric(20,2); fee numeric(20,2); net numeric(20,2);
  got bigint; spend numeric(20,2); change numeric(20,2); bal numeric(20,2);
begin
  p_from := public.ft_asset_id(p_from);
  p_to := public.ft_asset_id(p_to);
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

  pf := public.ft_share_ftr(p_from); pt := public.ft_share_ftr(p_to);
  gross := round(pf * p_shares, 2);
  fee   := round(gross * public.ft_fee_rate('SWAP'), 2);
  net   := gross - fee;
  got   := floor(net / pt);
  if got < 1 then raise exception 'That is not enough to buy a whole share of %', at2.name; end if;
  if at2.circulating + got > at2.total_shares then raise exception 'Only % shares of % are left', at2.total_shares - at2.circulating, at2.name; end if;
  spend  := round(got * pt, 2);
  change := greatest(0, net - spend);
  perform public.ft_draw_treasury(change);

  update public.holdings set shares = shares - p_shares, updated_at = now()
   where user_id = uid and asset_id = p_from;
  update public.assets set circulating = greatest(0, circulating - p_shares), updated_at = now() where id = p_from;

  insert into public.holdings (user_id, asset_id, shares, avg_cost)
  values (uid, p_to, got, pt)
  on conflict (user_id, asset_id) do update
    set avg_cost = round(((public.holdings.shares * public.holdings.avg_cost) + (got * pt))
                         / (public.holdings.shares + got), 6),
        shares = public.holdings.shares + got,
        updated_at = now();
  update public.assets set circulating = circulating + got, updated_at = now() where id = p_to;

  update public.wallets set balance = balance + change, updated_at = now() where user_id = uid returning balance into bal;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'SWAP', p_to, af.ticker || ' → ' || at2.ticker, got, pt, spend, fee, bal);

  return json_build_object('from', p_from, 'to', p_to, 'spent', p_shares, 'received', got,
                           'fee', fee, 'change', change, 'balance', bal);
end;
$function$;

-- ft_set_slot: accepts the id or the F-ticker
CREATE OR REPLACE FUNCTION public.ft_set_slot(p_asset text, p_slot text DEFAULT NULL::text)
 RETURNS json
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
declare uid uuid := public.ft_require_user(); held bigint;
begin
  p_asset := public.ft_asset_id(p_asset);
  select shares into held from public.holdings where user_id = uid and asset_id = p_asset;
  if held is null or held = 0 then
    raise exception 'You do not hold any %', p_asset;
  end if;
  update public.holdings set slot = nullif(trim(coalesce(p_slot, '')), ''), updated_at = now()
   where user_id = uid and asset_id = p_asset;
  return json_build_object('asset', p_asset, 'slot', p_slot);
end;
$function$;

-- ft_enter_fanplay_shares: accepts the id or the F-ticker
CREATE OR REPLACE FUNCTION public.ft_enter_fanplay_shares(p_asset text, p_shares bigint, p_match jsonb DEFAULT NULL::jsonb, p_market jsonb DEFAULT NULL::jsonb, p_selections jsonb DEFAULT NULL::jsonb, p_action_key text DEFAULT NULL::text, p_matchday integer DEFAULT 7)
 RETURNS json
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
declare
  uid uuid := public.ft_require_user();
  a public.assets%rowtype; h public.holdings%rowtype;
  entry public.fanplay_entries; existing public.fanplay_entries;
begin
  p_asset := public.ft_asset_id(p_asset);
  -- A resubmitted entry finds itself rather than locking a second set.
  if p_action_key is not null then
    select * into existing from public.fanplay_entries
      where user_id = uid and action_key = p_action_key;
    if found then return json_build_object('entry', row_to_json(existing), 'replayed', true); end if;
  end if;

  if p_shares is null or p_shares <= 0 then raise exception 'Choose how many shares to stake'; end if;
  select * into a from public.assets where id = p_asset;
  if not found then raise exception 'That asset is not listed'; end if;

  select * into h from public.holdings where user_id = uid and asset_id = p_asset for update;
  if not found or (h.shares - h.locked) < p_shares then
    raise exception 'You have % shares of % free to stake', coalesce(h.shares - h.locked, 0), p_asset;
  end if;

  update public.holdings set locked = locked + p_shares, updated_at = now()
   where user_id = uid and asset_id = p_asset;

  insert into public.fanplay_entries
    (user_id, mode, target, asset_id, staked_shares, match, market, selections,
     matchday, action_key)
  values (uid, 'Individual', p_asset, p_asset, p_shares, p_match, p_market, p_selections,
          p_matchday, p_action_key)
  returning * into entry;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total)
  values (uid, 'STAKE', p_asset, 'FanPlay shares locked', p_shares, a.price, 0);

  return json_build_object('entry', row_to_json(entry), 'replayed', false);
end;
$function$;

-- ft_snapshot: holdings and transactions carry the F-ticker
CREATE OR REPLACE FUNCTION public.ft_snapshot()
 RETURNS json
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
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
        select h.asset_id, a.ticker, h.shares, h.locked, h.avg_cost, h.slot, a.name, a.kind, a.club, a.price, a.price_usd, a.valuation_usd
        from public.holdings h join public.assets a on a.id = h.asset_id
        where h.user_id = uid and h.shares > 0 order by h.shares * a.price desc) h), '[]'::json),
    'transactions', coalesce((select json_agg(t) from (
        select x.type, x.asset_id, a.ticker, x.label, x.shares, x.price, x.total, x.fee, x.created_at
        from public.transactions x left join public.assets a on a.id = x.asset_id
        where x.user_id = uid
        order by x.created_at desc, x.id desc limit 60) t), '[]'::json),
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
$function$;

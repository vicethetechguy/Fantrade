-- Run after 15_optional_photo_credit.sql. Player valuation is compressed 1,000:1.
-- Historical trades, paid claims, share counts and wallet balances are retained.
begin;
alter table public.assets alter column price type numeric(22,10);
alter table public.assets alter column reference_value type numeric(22,10);
alter table public.holdings alter column avg_cost type numeric(22,10);
alter table public.transactions alter column price type numeric(22,10);
create or replace function public.ft_activity_share_usd(p_valuation numeric,p_kind text,p_supply bigint default 10000000)
returns numeric language sql immutable set search_path=public,pg_temp as $$
 select p_valuation / case when p_kind='PLAYER' then 1000 else 1 end / nullif(p_supply,0);
$$;

create or replace function public.ft_admin_upsert_players(p_rows jsonb)
returns json language plpgsql security definer set search_path = public, pg_temp as $$
declare
  r jsonb; v_ticker text; v_name text; v_kind text; v_pos text; v_val numeric; v_gender text; v_foot text;
  v_dob date; v_num int; v_ht int; v_photo text; v_credit text; v_about text;
  v_id text; a public.assets%rowtype; l public.listings%rowtype; launched boolean; bad text; v_src text;
  fx numeric := public.ft_ftr_usd();
  added int := 0; updated int := 0; skipped jsonb := '[]'::jsonb; notes jsonb := '[]'::jsonb;
begin
  perform public.ft_require_admin(true);
  if jsonb_typeof(p_rows) <> 'array' then raise exception 'Send a list of players'; end if;
  if jsonb_array_length(p_rows) > 500 then raise exception 'Upload at most 500 players at a time'; end if;

  for r in select * from jsonb_array_elements(p_rows) loop
    v_ticker := upper(trim(coalesce(r->>'ticker', '')));
    v_name   := trim(coalesce(r->>'name', ''));
    v_kind   := upper(coalesce(nullif(trim(r->>'kind'), ''), 'PLAYER'));
    v_pos    := upper(nullif(trim(r->>'position'), ''));
    v_val    := coalesce(public.ft_try_numeric(r->>'valuation_usd'),
                         public.ft_try_numeric(r->>'reference_value') * fx * 10000000 * case when coalesce(r->>'kind','PLAYER')='PLAYER' then 1000 else 1 end);
    v_src    := nullif(trim(r->>'valuation_source'), '');
    v_gender := upper(nullif(trim(r->>'gender'), ''));
    v_foot   := initcap(nullif(trim(r->>'preferred_foot'), ''));
    v_dob    := public.ft_try_date(r->>'date_of_birth');
    v_num    := public.ft_try_int(r->>'shirt_number');
    v_ht     := public.ft_try_int(r->>'height_cm');
    v_photo  := nullif(trim(r->>'photo_url'), '');
    v_credit := coalesce(nullif(trim(r->>'photo_credit'), ''), 'Official');
    v_about  := nullif(trim(r->>'about'), '');
    bad := null;

    if v_ticker !~ '^F[A-Z0-9]{2,6}$' then bad := 'Ticker must be F plus 2-6 letters or digits';
    elsif length(v_name) < 2 then bad := 'Name is missing';
    elsif v_kind not in ('PLAYER','COACH') then bad := 'Kind must be PLAYER or COACH';
    elsif v_pos is not null and v_pos not in ('GK','DEF','MID','FWD','MGR') then bad := 'Position must be GK, DEF, MID, FWD or MGR';
    elsif v_gender is not null and v_gender not in ('M','W') then bad := 'Game must be M (men''s) or W (women''s)';
    elsif v_foot is not null and v_foot not in ('Left','Right','Both') then bad := 'Foot must be Left, Right or Both';
    elsif nullif(trim(r->>'date_of_birth'), '') is not null and (v_dob is null or v_dob < date '1930-01-01' or v_dob > current_date - interval '14 years') then bad := 'Date of birth must be a real date, YYYY-MM-DD';
    elsif nullif(trim(r->>'shirt_number'), '') is not null and (v_num is null or v_num not between 1 and 99) then bad := 'Shirt number must be 1 to 99';
    elsif nullif(trim(r->>'height_cm'), '') is not null and (v_ht is null or v_ht not between 140 and 220) then bad := 'Height must be in centimetres, 140 to 220';
    elsif length(coalesce(v_about, '')) > 800 then bad := 'About is longer than 800 characters';
    elsif v_photo is not null and v_photo !~ '^https://' then bad := 'Photo link must start with https://';
    end if;
    if bad is not null then
      skipped := skipped || jsonb_build_object('ticker', v_ticker, 'name', v_name, 'reason', bad); continue;
    end if;

    select * into a from public.assets where ticker = v_ticker limit 1;
    if found then
      select * into l from public.listings where asset_id = a.id
       order by (claimed_by is not null) desc, created_at desc limit 1;
      launched := a.is_active or (l.id is not null and l.claimed_by is not null);
      if (r ? 'valuation_usd' or r ? 'reference_value') and (v_val is null or v_val <= 0) then
        skipped := skipped || jsonb_build_object('ticker', v_ticker, 'name', v_name, 'reason', 'Valuation must be above $0'); continue;
      end if;
      update public.assets set
        name           = v_name,
        known_as       = case when r ? 'known_as' then nullif(trim(r->>'known_as'), '') else known_as end,
        gender         = coalesce(v_gender, gender),
        country        = case when r ? 'country' then nullif(trim(r->>'country'), '') else country end,
        club           = case when r ? 'club' then nullif(trim(r->>'club'), '') else club end,
        league         = case when r ? 'league' then nullif(trim(r->>'league'), '') else league end,
        date_of_birth  = case when r ? 'date_of_birth' then v_dob else date_of_birth end,
        shirt_number   = case when r ? 'shirt_number' then v_num else shirt_number end,
        height_cm      = case when r ? 'height_cm' then v_ht else height_cm end,
        preferred_foot = case when r ? 'preferred_foot' then v_foot else preferred_foot end,
        about          = case when r ? 'about' then v_about else about end,
        photo_url      = case when r ? 'photo_url' then v_photo else photo_url end,
        photo_credit   = case when r ? 'photo_url' then v_credit else photo_credit end,
        photo_source   = case when r ? 'photo_url' then nullif(trim(r->>'photo_source'), '') else photo_source end,
        kind           = case when launched then kind else v_kind end,
        position       = case when launched then coalesce(v_pos, position) else coalesce(v_pos, position, case when v_kind = 'COACH' then 'MGR' else 'FWD' end) end,
        valuation_usd  = coalesce(v_val, valuation_usd),
        valuation_source = case when v_val is not null then coalesce(v_src, 'Set in the admin') else valuation_source end,
        valuation_at   = case when v_val is not null then current_date else valuation_at end,
        price_usd      = case when v_val is not null then round(public.ft_activity_share_usd(v_val,kind,total_shares), 8) else price_usd end,
        price          = case when v_val is not null then round(public.ft_activity_share_usd(v_val,kind,total_shares) / fx, 10) else price end,
        reference_value = case when v_val is not null then round(public.ft_activity_share_usd(v_val,kind,total_shares) / fx, 10) else reference_value end,
        reference_at   = case when v_val is not null then now() else reference_at end,
        profile_updated_at = now(), updated_at = now()
       where id = a.id;
      if launched and v_val is not null then
        notes := notes || jsonb_build_object('ticker', v_ticker, 'name', v_name,
                 'note', 'Trading now: the new valuation moves its share price to $' || round(public.ft_activity_share_usd(v_val,a.kind,10000000), 4) || '.');
      end if;
      if not launched and v_val is not null then
        if l.id is null then
          insert into public.listings (id, asset_id, title, is_active, fee_level1, fee_level2)
          values ('lst-' || v_ticker, a.id, 'Open to claim', true, round(500000 * public.ft_activity_share_usd(v_val,a.kind,10000000) / fx, 2), round(1000000 * public.ft_activity_share_usd(v_val,a.kind,10000000) / fx, 2))
          on conflict (id) do nothing;
        else
          update public.listings set fee_level1 = round(500000 * public.ft_activity_share_usd(v_val,a.kind,10000000) / fx, 2), fee_level2 = round(1000000 * public.ft_activity_share_usd(v_val,a.kind,10000000) / fx, 2) where id = l.id;
        end if;
      end if;
      updated := updated + 1;
    else
      if v_val is null or v_val <= 0 then
        skipped := skipped || jsonb_build_object('ticker', v_ticker, 'name', v_name, 'reason', 'Add a valuation in dollars, above $0'); continue;
      end if;
      v_id := '$' || v_ticker;
      insert into public.assets (id, ticker, name, known_as, kind, gender, club, league, position, country, date_of_birth,
                                 shirt_number, height_cm, preferred_foot, about, photo_url, photo_credit, photo_source,
                                 valuation_usd, valuation_source, valuation_at, price_usd,
                                 price, reference_value, reference_at, is_active, profile_updated_at)
      values (v_id, v_ticker, v_name, nullif(trim(r->>'known_as'), ''), v_kind, coalesce(v_gender, 'M'),
              nullif(trim(r->>'club'), ''), nullif(trim(r->>'league'), ''),
              coalesce(v_pos, case when v_kind = 'COACH' then 'MGR' else 'FWD' end), nullif(trim(r->>'country'), ''),
              v_dob, v_num, v_ht, v_foot, v_about, v_photo, v_credit, nullif(trim(r->>'photo_source'), ''),
              v_val, coalesce(v_src, 'Set in the admin'), current_date, round(public.ft_activity_share_usd(v_val,v_kind,10000000), 8),
              round(public.ft_activity_share_usd(v_val,v_kind,10000000) / fx, 10), round(public.ft_activity_share_usd(v_val,v_kind,10000000) / fx, 10), now(), false, now());
      insert into public.listings (id, asset_id, title, is_active, fee_level1, fee_level2)
      values ('lst-' || v_ticker, v_id, 'Open to claim', true, round(500000 * public.ft_activity_share_usd(v_val,v_kind,10000000) / fx, 2), round(1000000 * public.ft_activity_share_usd(v_val,v_kind,10000000) / fx, 2))
      on conflict (id) do nothing;
      added := added + 1;
    end if;
  end loop;

  perform public.ft_admin_note('players.upsert', null,
    jsonb_build_object('added', added, 'updated', updated, 'skipped', jsonb_array_length(skipped)));
  return json_build_object('added', added, 'updated', updated, 'skipped', skipped, 'notes', notes);
end;
$$;
create or replace function public.ft_claim_listing(
  p_listing text,
  p_level int default 1,
  p_vesting_years int default 1
)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  l   public.listings%rowtype;
  a   public.assets%rowtype;
  w   public.wallets%rowtype;
  fx numeric := public.ft_ftr_usd();
  v_share_usd numeric; v_price numeric(22,10); v_shares bigint;
  v_cost numeric(20,2); v_burn numeric(20,2); v_daily bigint; v_until timestamptz;
begin
  if p_listing is null or p_listing = '' then raise exception 'Pick a player to claim'; end if;
  if p_level not in (1, 2) then p_level := 1; end if;
  if p_vesting_years not in (1, 2, 3) then p_vesting_years := 1; end if;

  select * into l from public.listings where id = p_listing for update;
  if not found then raise exception 'That player is not open to claim'; end if;
  if l.claimed_by is not null then
    raise exception 'Someone has already claimed this player. You can buy their shares on the exchange';
  end if;
  if not l.is_active then raise exception 'That player is not open to claim'; end if;

  select * into a from public.assets where id = l.asset_id for update;
  if not found then raise exception 'That player is not in the catalogue'; end if;
  if a.is_active then raise exception 'This player is already trading. You can buy their shares on the exchange'; end if;
  if a.valuation_usd is null then raise exception 'This player has no valuation yet, so they cannot be claimed'; end if;

  v_share_usd := public.ft_activity_share_usd(a.valuation_usd,a.kind,a.total_shares);
  v_price  := round(v_share_usd / fx, 10);
  v_shares := case when p_level = 2 then 1000000 else 500000 end;
  v_cost   := round(v_shares * v_share_usd / fx, 2);
  v_burn   := round(v_cost * 0.02, 2);
  v_daily  := v_shares / 100;
  v_until  := now() + make_interval(years => p_vesting_years);

  select * into w from public.wallets where user_id = uid for update;
  if not found or w.balance < v_cost then
    raise exception 'You need % more $FTR to claim % percent of % (% $FTR at $% a $FTR)',
      v_cost - coalesce(w.balance, 0), v_shares / 100000, a.name, v_cost, fx;
  end if;

  update public.wallets set balance = balance - v_cost, updated_at = now() where user_id = uid;
  -- 2% leaves the supply for good; the rest is now the treasury's.
  update public.ftr_market set burned = burned + v_burn, updated_at = now() where id;

  update public.listings set claimed_by = uid, claimed_at = now(), is_active = false where id = l.id;

  insert into public.claims (listing_id, user_id, claim_level, shares, vesting_years, fee_paid, fee_burned, daily_limit, vesting_until)
  values (l.id, uid, p_level, v_shares, p_vesting_years, v_cost, v_burn, v_daily, v_until);

  insert into public.holdings (user_id, asset_id, shares, avg_cost)
  values (uid, a.id, v_shares, v_price)
  on conflict (user_id, asset_id) do update
    set shares = public.holdings.shares + excluded.shares, avg_cost = excluded.avg_cost, updated_at = now();

  -- Live from here: the claim and Fantrade's 1,000,000 are out of the float.
  update public.assets
     set is_active = true, circulating = least(total_shares, v_shares + 1000000),
         price_usd = round(v_share_usd, 8), price = v_price, updated_at = now()
   where id = a.id;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'LIST', a.id,
          'Claimed ' || (v_shares / 100000) || '% of ' || a.name || ' (' || p_vesting_years || 'y vesting)',
          v_shares, v_price, v_cost, v_burn, w.balance - v_cost);

  return json_build_object(
    'listing', l.id, 'asset', a.id, 'name', a.name, 'ticker', a.ticker,
    'shares', v_shares, 'level', p_level, 'vesting_years', p_vesting_years,
    'price', v_price, 'share_usd', round(v_share_usd, 6), 'ftr_usd', fx,
    'cost', v_cost, 'cost_usd', round(v_cost * fx, 2), 'burned', v_burn, 'daily_limit', v_daily);
end;
$$;
create or replace function public.ft_reprice()
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare fx numeric := public.ft_ftr_usd();
begin
  update public.assets
     set price = round(coalesce(price_usd, public.ft_activity_share_usd(valuation_usd,kind,total_shares)) / fx, 10),
         reference_value = round(coalesce(public.ft_activity_share_usd(valuation_usd,kind,total_shares), price_usd) / fx, 10),
         updated_at = now()
   where coalesce(price_usd, valuation_usd) is not null;
  update public.listings l
     set fee_level1 = round(500000 * public.ft_activity_share_usd(a.valuation_usd,a.kind,a.total_shares) / fx, 2),
         fee_level2 = round(1000000 * public.ft_activity_share_usd(a.valuation_usd,a.kind,a.total_shares) / fx, 2)
    from public.assets a
   where a.id = l.asset_id and a.valuation_usd is not null and l.claimed_by is null;
  update public.wallets set usd_rate = round(1 / fx, 10);
end;
$$;

alter table public.fanplay_entries add column if not exists simulated boolean not null default false;
create or replace function public.ft_simulate_fanplay_demo(p_entry uuid)
returns json language plpgsql security definer set search_path=public,pg_temp as $$
declare uid uuid:=public.ft_require_user(); e public.fanplay_entries; p jsonb; picks jsonb:='[]'; total numeric:=0; earned numeric; ok boolean;
begin
 if not exists(select 1 from auth.users where id=uid and (lower(email) in ('demo@fantrade.com','alex.morgan@fantrade.app') or raw_app_meta_data->>'fantrade_demo'='true')) then
  raise exception 'Simulation is available only on designated demo accounts';
 end if;
 select * into e from public.fanplay_entries where id=p_entry and user_id=uid for update;
 if not found then raise exception 'Entry not found'; end if;
 if e.simulated then return json_build_object('entry',row_to_json(e),'replayed',true); end if;
 if e.status<>'ACTIVE' then raise exception 'That entry has already ended'; end if;
 for p in select value from jsonb_array_elements(coalesce(e.selections,'[]')) loop
  ok:=random()<0.6; earned:=coalesce((p->>(case when ok then 'successFP' else 'failureFP' end))::numeric,0)*e.staked_shares;
  total:=total+earned;
  picks:=picks||jsonb_build_array(p||jsonb_build_object('evaluationResult',case when ok then 'SUCCESS' else 'FAILURE' end,'earnedFP',earned,'evaluationReason','Demo simulation'));
 end loop;
 if jsonb_array_length(picks)=0 then total:=round(e.projected_fp*0.6); end if;
 if e.asset_id is not null then update public.holdings set locked=greatest(0,locked-e.staked_shares),updated_at=now() where user_id=uid and asset_id=e.asset_id; end if;
 if e.stake>0 then update public.wallets set locked=greatest(0,locked-e.stake),balance=balance+e.stake,updated_at=now() where user_id=uid; end if;
 update public.fanplay_entries set status='SETTLED',selections=picks,scored_fp=total,payout=0,simulated=true,settled_at=now() where id=e.id returning * into e;
 return json_build_object('entry',row_to_json(e),'replayed',false);
end;
$$;
revoke all on function public.ft_simulate_fanplay_demo(uuid) from public,anon;
grant execute on function public.ft_simulate_fanplay_demo(uuid) to authenticated;

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
               projected_fp, matchday, status, scored_fp, payout, simulated, settled_at, created_at
        from public.fanplay_entries where user_id = uid
        order by created_at desc) e), '[]'::json)
  );
end;
$function$;

create or replace function public.ft_share_ftr(p_asset text)
returns numeric language sql stable security definer set search_path = public, pg_temp as $$
  select round(coalesce(a.price_usd, public.ft_activity_share_usd(a.valuation_usd,a.kind,a.total_shares)) / public.ft_ftr_usd(), 10)
    from public.assets a where a.id = p_asset;
$$;
CREATE OR REPLACE FUNCTION public.ft_buy_shares(p_asset text, p_shares bigint)
 RETURNS json
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pg_temp'
AS $function$
declare
  uid uuid := public.ft_require_user();
  a   public.assets%rowtype;
  px numeric(22,10); gross numeric(20,2); fee numeric(20,2); total numeric(20,2);
  bal numeric(20,2); new_held bigint; new_avg numeric(22,10);
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
                         / (public.holdings.shares + p_shares), 10),
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
  px numeric(22,10); gross numeric(20,2); fee numeric(20,2); net numeric(20,2); bal numeric(20,2);
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
  pf numeric(22,10); pt numeric(22,10);
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
                         / (public.holdings.shares + got), 10),
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
-- Recompute from valuation, so rerunning never applies a second 1,000 reduction.
update public.assets set price_usd=round(public.ft_activity_share_usd(valuation_usd,kind,total_shares),8)
 where kind='PLAYER' and valuation_usd>0;
select public.ft_reprice();
commit;

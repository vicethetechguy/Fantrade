-- Fantrade · Claim a player by value. Run after 06_listings.sql.
-- Safe to run more than once.
--
-- A player Fantrade has cleared sits in public.assets with is_active = false
-- (so nobody can trade it yet) and has one open row in public.listings.
-- The first manager to claim it:
--   · pays for the shares they take at the player's reference value:
--     Level 1 = 5%  = 500,000 shares, Level 2 = 10% = 1,000,000 shares;
--   · has 2% of that payment recorded as burned;
--   · gets the shares, vesting over 1, 2 or 3 years, with the 1%-a-day
--     trading limit of the white paper;
--   · switches the asset on (is_active = true), so every other manager can
--     buy what is left on the exchange. Fantrade's 1,000,000 are set aside.
-- A listing is claimed once, by one manager. After that it is closed.

alter table public.listings add column if not exists claimed_by uuid references auth.users(id);
alter table public.listings add column if not exists claimed_at timestamptz;

-- Players already trading were never open to claim: close their old drops.
update public.listings l set is_active = false
  from public.assets a
 where a.id = l.asset_id and a.is_active and l.claimed_by is null and l.is_active;

-- The players cleared for listing. Reference values are demo figures.
do $$ begin
  if exists (select 1 from pg_trigger where tgname = 'assets_ticker_fixed'
               and tgrelid = 'public.assets'::regclass) then
    execute 'alter table public.assets disable trigger assets_ticker_fixed';
  end if;
end $$;
insert into public.assets (id, ticker, name, kind, club, league, position, price, reference_value, reference_at, is_active) values
  ('$Ronaldo',    'FCR7',  'Cristiano Ronaldo', 'PLAYER', 'Al Nassr',            'Saudi Pro League', 'FWD', 34.60, 34.60, now(), false),
  ('$Messi',      'FLM10', 'Lionel Messi',      'PLAYER', 'Inter Miami',         'MLS',              'FWD', 38.20, 38.20, now(), false),
  ('$Kane',       'FKANE', 'Harry Kane',        'PLAYER', 'Bayern Munich',       'Bundesliga',       'FWD', 62.40, 62.40, now(), false),
  ('$Rice',       'FRICE', 'Declan Rice',       'PLAYER', 'Arsenal',             'Premier League',   'MID', 49.60, 49.60, now(), false),
  ('$VanDijk',    'FVVD',  'Virgil van Dijk',   'PLAYER', 'Liverpool',           'Premier League',   'DEF', 29.80, 29.80, now(), false),
  ('$Osimhen',    'FOSIM', 'Victor Osimhen',    'PLAYER', 'Galatasaray',         'Süper Lig',        'FWD', 41.30, 41.30, now(), false),
  ('$Salah',      'FSALH', 'Mohamed Salah',     'PLAYER', 'Trabzonspor',         'Süper Lig',        'FWD', 27.90, 27.90, now(), false),
  ('$Lookman',    'FLOOK', 'Ademola Lookman',   'PLAYER', 'Atlético Madrid',     'La Liga',          'FWD', 18.40, 18.40, now(), false),
  ('$Chukwueze',  'FCHUK', 'Samuel Chukwueze',  'PLAYER', 'AC Milan',            'Serie A',          'FWD',  1.85,  1.85, now(), false),
  ('$Shaw',       'FSHAW', 'Khadija Shaw',      'PLAYER', 'Manchester City',     'WSL',              'FWD', 32.50, 32.50, now(), false),
  ('$Pajor',      'FPAJR', 'Ewa Pajor',         'PLAYER', 'Barcelona',           'Liga F',           'FWD', 30.10, 30.10, now(), false),
  ('$Rodman',     'FRODM', 'Trinity Rodman',    'PLAYER', 'Washington Spirit',   'NWSL',             'FWD', 26.40, 26.40, now(), false),
  ('$Kelly',      'FKELY', 'Chloe Kelly',       'PLAYER', 'Arsenal',             'WSL',              'FWD', 22.80, 22.80, now(), false),
  ('$Ajibade',    'FAJBD', 'Rasheedat Ajibade', 'PLAYER', 'Paris Saint-Germain', 'Première Ligue',   'FWD',  1.60,  1.60, now(), false),
  ('$Alozie',     'FALOZ', 'Michelle Alozie',   'PLAYER', 'Chicago Stars',       'NWSL',             'DEF',  1.20,  1.20, now(), false)
on conflict (id) do nothing;
do $$ begin
  if exists (select 1 from pg_trigger where tgname = 'assets_ticker_fixed'
               and tgrelid = 'public.assets'::regclass) then
    execute 'alter table public.assets enable trigger assets_ticker_fixed';
  end if;
end $$;

-- One open listing per cleared player, id 'lst-' || ticker. The fee columns
-- show what each level costs at today's reference value.
insert into public.listings (id, asset_id, title, shares_level1, shares_level2, fee_level1, fee_level2, is_active)
select 'lst-' || a.ticker, a.id, 'Open to claim', 500000, 1000000,
       round(500000 * a.reference_value, 2), round(1000000 * a.reference_value, 2), true
  from public.assets a
 where a.id in ('$Ronaldo','$Messi','$Kane','$Rice','$VanDijk','$Osimhen','$Salah','$Lookman','$Chukwueze',
                '$Shaw','$Pajor','$Rodman','$Kelly','$Ajibade','$Alozie')
   and not a.is_active
on conflict (id) do nothing;

-- ── Who is open to claim ─────────────────────────────────────────────────
create or replace function public.ft_listings()
returns json
language plpgsql stable security definer set search_path = public, pg_temp
as $$
declare uid uuid := auth.uid();
begin
  return coalesce((select json_agg(row_to_json(row)) from (
    select l.id, l.asset_id, l.title, a.name, a.ticker, coalesce(a.reference_value, a.price) as price,
           a.kind, a.club, a.league, a.position,
           (l.claimed_by is not null and l.claimed_by = uid) as claimed
      from public.listings l
      join public.assets a on a.id = l.asset_id
     where l.is_active and l.claimed_by is null and not a.is_active
     order by a.name
  ) row), '[]'::json);
end;
$$;

-- ── Claim a cleared player and launch them ───────────────────────────────
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
  v_price  numeric(12,2);
  v_shares bigint;
  v_cost   numeric(20,2);
  v_burn   numeric(20,2);
  v_daily  bigint;
  v_until  timestamptz;
begin
  if p_listing is null or p_listing = '' then raise exception 'Pick a player to claim'; end if;
  if p_level not in (1, 2) then p_level := 1; end if;
  if p_vesting_years not in (1, 2, 3) then p_vesting_years := 1; end if;

  -- The row lock makes two managers claiming at once queue; the second
  -- one finds it taken.
  select * into l from public.listings where id = p_listing for update;
  if not found then raise exception 'That player is not open to claim'; end if;
  if l.claimed_by is not null then
    raise exception 'Someone has already claimed this player. You can buy their shares on the exchange';
  end if;
  if not l.is_active then raise exception 'That player is not open to claim'; end if;

  select * into a from public.assets where id = l.asset_id for update;
  if not found then raise exception 'That player is not in the catalogue'; end if;
  if a.is_active then
    raise exception 'This player is already trading. You can buy their shares on the exchange';
  end if;

  v_price  := coalesce(a.reference_value, a.price);
  v_shares := case when p_level = 2 then 1000000 else 500000 end;
  v_cost   := round(v_shares * v_price, 2);
  v_burn   := round(v_cost * 0.02, 2);
  v_daily  := v_shares / 100;
  v_until  := now() + make_interval(years => p_vesting_years);

  select * into w from public.wallets where user_id = uid for update;
  if not found or w.balance < v_cost then
    raise exception 'You need % more $FTR to claim % percent of %',
      v_cost - coalesce(w.balance, 0), v_shares / 100000, a.name;
  end if;

  update public.wallets set balance = balance - v_cost, updated_at = now() where user_id = uid;

  update public.listings
     set claimed_by = uid, claimed_at = now(), is_active = false
   where id = l.id;

  insert into public.claims (listing_id, user_id, claim_level, shares, vesting_years,
                             fee_paid, fee_burned, daily_limit, vesting_until)
  values (l.id, uid, p_level, v_shares, p_vesting_years, v_cost, v_burn, v_daily, v_until);

  insert into public.holdings (user_id, asset_id, shares, avg_cost)
  values (uid, a.id, v_shares, v_price)
  on conflict (user_id, asset_id) do update
    set shares = public.holdings.shares + excluded.shares,
        avg_cost = excluded.avg_cost,
        updated_at = now();

  -- Live from here: the claim and Fantrade's 1,000,000 are out of the float.
  update public.assets
     set is_active = true, circulating = least(total_shares, v_shares + 1000000), updated_at = now()
   where id = a.id;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'GRANT', a.id,
          'Claimed ' || (v_shares / 100000) || '% of ' || a.name || ' (' || p_vesting_years || 'y vesting)',
          v_shares, v_price, v_cost, v_burn, w.balance - v_cost);

  return json_build_object(
    'listing', l.id, 'asset', a.id, 'name', a.name, 'ticker', a.ticker,
    'shares', v_shares, 'level', p_level, 'vesting_years', p_vesting_years,
    'price', v_price, 'cost', v_cost, 'burned', v_burn, 'daily_limit', v_daily
  );
end;
$$;

revoke execute on function public.ft_listings() from public, anon;
revoke execute on function public.ft_claim_listing(text, int, int) from public, anon;
grant execute on function public.ft_listings() to authenticated;
grant execute on function public.ft_claim_listing(text, int, int) to authenticated;

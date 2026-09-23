-- Fantrade · Admin-listed Activity Asset Drops & Lister Claiming Infrastructure
-- Per White Paper Draft v2.0 Section 7 & 8:
--   - 10M total conceptual supply per Activity Asset
--   - Level 1: 5% = 500,000 shares (50,000 $FTR fee)
--   - Level 2: 10% = 1,000,000 shares (100,000 $FTR fee)
--   - 2% permanent burn of listing fee
--   - Vesting duration: 1, 2, or 3 years (earns 30% trading fee participation)
--   - 1% daily trading limit on lister allocation (5k/day Level 1; 10k/day Level 2)

create table if not exists public.listings (
  id             text primary key,                       -- 'lst-saka-drop'
  asset_id       text not null references public.assets(id),
  title          text not null default '',
  shares_level1  bigint not null default 500000,
  shares_level2  bigint not null default 1000000,
  fee_level1     numeric(20,2) not null default 50000.00,
  fee_level2     numeric(20,2) not null default 100000.00,
  is_active      boolean not null default true,
  created_at     timestamptz not null default now()
);

-- Backward compatibility for column names
alter table public.listings add column if not exists shares_level1 bigint not null default 500000;
alter table public.listings add column if not exists shares_level2 bigint not null default 1000000;
alter table public.listings add column if not exists fee_level1 numeric(20,2) not null default 50000.00;
alter table public.listings add column if not exists fee_level2 numeric(20,2) not null default 100000.00;

create table if not exists public.claims (
  listing_id     text not null references public.listings(id) on delete cascade,
  user_id        uuid not null references auth.users(id) on delete cascade,
  claim_level    int not null default 1 check (claim_level in (1, 2)),
  shares         bigint not null default 500000,
  vesting_years  int not null default 1 check (vesting_years in (1, 2, 3)),
  fee_paid       numeric(20,2) not null default 50000.00,
  fee_burned     numeric(20,2) not null default 1000.00,
  daily_limit    bigint not null default 5000,
  vesting_until  timestamptz not null default (now() + interval '1 year'),
  claimed_at     timestamptz not null default now(),
  primary key (listing_id, user_id)
);

alter table public.claims add column if not exists claim_level int not null default 1;
alter table public.claims add column if not exists shares bigint not null default 500000;
alter table public.claims add column if not exists vesting_years int not null default 1;
alter table public.claims add column if not exists fee_paid numeric(20,2) not null default 50000.00;
alter table public.claims add column if not exists fee_burned numeric(20,2) not null default 1000.00;
alter table public.claims add column if not exists daily_limit bigint not null default 5000;
alter table public.claims add column if not exists vesting_until timestamptz not null default (now() + interval '1 year');

alter table public.listings enable row level security;
alter table public.claims enable row level security;

drop policy if exists listings_readable on public.listings;
create policy listings_readable on public.listings for select using (true);

drop policy if exists claims_select_own on public.claims;
create policy claims_select_own on public.claims for select using (auth.uid() = user_id);

-- ── What is claimable right now, and what this manager already took ──────
create or replace function public.ft_listings()
returns json
language plpgsql stable security definer set search_path = public, pg_temp
as $$
declare uid uuid := auth.uid();
begin
  return coalesce((select json_agg(row_to_json(row)) from (
    select l.id, l.asset_id, l.title, l.shares_level1, l.shares_level2, l.fee_level1, l.fee_level2,
           a.name, a.ticker, a.price, a.kind, a.club,
           exists (select 1 from public.claims c
                    where c.listing_id = l.id and c.user_id = uid) as claimed
      from public.listings l
      join public.assets a on a.id = l.asset_id
     where l.is_active
     order by l.created_at desc
  ) row), '[]'::json);
end;
$$;

-- ── Claim one listing: Section 7 & 8 Lister Launch Flow ──
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
  v_shares bigint;
  v_fee numeric(20,2);
  v_burn numeric(20,2);
  v_daily bigint;
  v_until timestamptz;
  new_held bigint;
begin
  if p_listing is null or p_listing = '' then raise exception 'Pick a listing to claim'; end if;
  if p_level not in (1, 2) then p_level := 1; end if;
  if p_vesting_years not in (1, 2, 3) then p_vesting_years := 1; end if;

  select * into l from public.listings where id = p_listing and is_active for update;
  if not found then raise exception 'That listing is no longer available'; end if;

  if exists (select 1 from public.claims where listing_id = p_listing and user_id = uid) then
    raise exception 'You have already claimed this listing';
  end if;

  select * into a from public.assets where id = l.asset_id for update;
  if not found then raise exception 'That asset is not listed'; end if;

  -- Economics per Section 7 & 8
  if p_level = 2 then
    v_shares := coalesce(l.shares_level2, 1000000);
    v_fee    := coalesce(l.fee_level2, 100000.00);
    v_daily  := 10000;
  else
    v_shares := coalesce(l.shares_level1, 500000);
    v_fee    := coalesce(l.fee_level1, 50000.00);
    v_daily  := 5000;
  end if;

  v_burn  := round(v_fee * 0.02, 2);
  v_until := now() + (p_vesting_years || ' years')::interval;

  -- Check & deduct wallet balance
  select * into w from public.wallets where user_id = uid for update;
  if w.balance < v_fee then
    raise exception 'Insufficient $FTR balance. Required: % $FTR, available: % $FTR', v_fee, w.balance;
  end if;

  update public.wallets
     set balance = balance - v_fee, updated_at = now()
   where user_id = uid;

  -- Record claim
  insert into public.claims (
    listing_id, user_id, claim_level, shares, vesting_years, fee_paid, fee_burned, daily_limit, vesting_until
  ) values (
    p_listing, uid, p_level, v_shares, p_vesting_years, v_fee, v_burn, v_daily, v_until
  );

  -- Credit shares to user holdings
  insert into public.holdings (user_id, asset_id, shares, avg_cost)
  values (uid, l.asset_id, v_shares, a.price)
  on conflict (user_id, asset_id) do update
    set avg_cost = round(((public.holdings.shares * public.holdings.avg_cost) + (v_shares * a.price))
                         / (public.holdings.shares + v_shares), 4),
        shares = public.holdings.shares + v_shares,
        updated_at = now()
  returning public.holdings.shares into new_held;

  -- Increase circulating supply
  update public.assets
     set circulating = least(total_shares, circulating + v_shares), updated_at = now()
   where id = l.asset_id;

  -- Record transaction
  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'GRANT', l.asset_id,
          'Lister Launch (Level ' || p_level || ' · ' || p_vesting_years || 'y vesting): ' || coalesce(l.title, a.name),
          v_shares, a.price, v_fee, v_burn, w.balance - v_fee);

  return json_build_object(
    'listing', l.id,
    'asset', l.asset_id,
    'name', a.name,
    'ticker', a.ticker,
    'shares', v_shares,
    'level', p_level,
    'vesting_years', p_vesting_years,
    'fee_paid', v_fee,
    'fee_burned', v_burn,
    'daily_limit', v_daily,
    'held', new_held
  );
end;
$$;

-- Overload for single-parameter callers
create or replace function public.ft_claim_listing(p_listing text)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
begin
  return public.ft_claim_listing(p_listing, 1, 1);
end;
$$;

-- Seed listings with proper F-style tickers
insert into public.listings (id, asset_id, title, shares_level1, shares_level2, fee_level1, fee_level2, is_active) values
  ('lst-saka-drop',   'FSAKA', 'Arsenal Star Drop',    500000, 1000000, 50000, 100000, true),
  ('lst-mbappe-drop', 'FKM7',  'Galáctico Drop',       500000, 1000000, 50000, 100000, true),
  ('lst-yamal-drop',  'FYAML', 'Golden Boy Drop',      500000, 1000000, 50000, 100000, true),
  ('lst-haaland-drop','FHLND', 'Goal Machine Drop',    500000, 1000000, 50000, 100000, true)
on conflict (id) do update
  set asset_id = excluded.asset_id,
      title = excluded.title,
      shares_level1 = excluded.shares_level1,
      shares_level2 = excluded.shares_level2,
      fee_level1 = excluded.fee_level1,
      fee_level2 = excluded.fee_level2,
      is_active = excluded.is_active;

-- Permissions
revoke execute on all functions in schema public from public, anon;
grant execute on function public.ft_listings() to authenticated;
grant execute on function public.ft_claim_listing(text, int, int) to authenticated;
grant execute on function public.ft_claim_listing(text) to authenticated;

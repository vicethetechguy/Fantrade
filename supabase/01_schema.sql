-- Fantrade · Supabase schema (step 1: accounts, wallet, holdings, catalogue)
-- Run this whole file once in the Supabase SQL editor.
--
-- Shape of the design:
--   · Every manager is a row in auth.users. profiles/wallets/holdings/transactions
--     hang off that id and are readable only by their owner (row-level security).
--   · Nothing that moves money is writable from the browser. The only write path
--     is the SECURITY DEFINER functions in 02_functions.sql, which re-check the
--     price, the balance and the share count on the server.
--   · assets is the shared catalogue and is readable by everyone, writable by no one.

create extension if not exists citext;

-- ── Managers ──────────────────────────────────────────────────────────
create table if not exists public.profiles (
  id            uuid primary key references auth.users(id) on delete cascade,
  handle        citext unique not null,
  display_name  text not null default 'Manager',
  region        text default 'United Kingdom',
  home_league   text default 'Premier League',
  onboarded     boolean not null default false,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  constraint handle_shape check (handle ~ '^[a-z0-9_]{3,20}$')
);

-- ── Wallet: one $FTR balance per manager ──────────────────────────────
create table if not exists public.wallets (
  user_id       uuid primary key references auth.users(id) on delete cascade,
  balance       numeric(20,2) not null default 0 check (balance >= 0),
  locked        numeric(20,2) not null default 0 check (locked >= 0),
  season_earned numeric(20,2) not null default 0,
  gbp_rate      numeric(10,4) not null default 12.40,
  updated_at    timestamptz not null default now()
);

-- ── Catalogue: players and coaches everyone trades ────────────────────
-- One row per Activity Asset (white paper 4). `kind` holds the two asset types
-- in the app's short form: PLAYER is the paper's PLAYER_ACTIVITY and COACH is
-- its COACH_ACTIVITY. `ticker` is the F-ticker of 5 (FSAKA, FHLND, ...) and is
-- immutable once issued. `price` is the market price a trade executes at, and
-- `reference_value` is the Fantrade Reference Valuation of 6 - the indicative
-- figure an asset is discovered at, which is what the catalogue is seeded
-- with. Conceptually there are always ten million shares of an asset (4.1),
-- so `total_shares` is not a free parameter.
create table if not exists public.assets (
  id            text primary key,                    -- '$Saka'
  ticker        text not null,                       -- 'FSAKA', the F-ticker
  name          text not null,
  kind          text not null default 'PLAYER' check (kind in ('PLAYER','COACH')),
  club          text,
  league        text,
  position      text,
  price         numeric(12,2) not null check (price > 0),
  reference_value numeric(12,2) check (reference_value > 0),
  reference_at  timestamptz,
  -- Left empty on purpose: 15.4 wants day and history figures to come from
  -- recorded executions, and there are none until the exchange engine of 15
  -- is in place. The pages fall back to the reference value meanwhile.
  prev_close    numeric(12,2),
  day_change    numeric(6,2) not null default 0,
  day_high      numeric(12,2),
  day_low       numeric(12,2),
  total_shares  bigint not null default 10000000,
  circulating   bigint not null default 0,
  is_active     boolean not null default true,
  updated_at    timestamptz not null default now()
);
create index if not exists assets_kind_idx on public.assets (kind) where is_active;

-- An install from before the F-ticker arrived adds the columns here, then holds
-- the ticker to the shape of 5. 03_seed_assets.sql fills every listed asset in
-- and makes the column not-null once it has.
alter table public.assets add column if not exists ticker text;
alter table public.assets add column if not exists reference_value numeric(12,2);
alter table public.assets add column if not exists reference_at timestamptz;
create unique index if not exists assets_ticker_idx on public.assets (ticker);
alter table public.assets drop constraint if exists assets_ticker_check;
alter table public.assets drop constraint if exists assets_ticker_shape;
alter table public.assets add constraint assets_ticker_shape
  check (ticker is null or ticker ~ '^F[A-Z0-9]{1,7}$');
alter table public.assets drop constraint if exists assets_total_shares_check;
alter table public.assets drop constraint if exists assets_shares_fixed;
alter table public.assets add constraint assets_shares_fixed check (total_shares = 10000000);

-- 5: a ticker is immutable after issuance. Filling an empty one in is the one
-- change allowed, which is how an earlier install picks its tickers up.
create or replace function public.ft_ticker_is_fixed()
returns trigger
language plpgsql
as $$
begin
  if old.ticker is not null and old.ticker is distinct from new.ticker then
    raise exception 'A ticker cannot be changed once issued (%)', old.ticker
      using errcode = '23514';
  end if;
  return new;
end;
$$;

drop trigger if exists assets_ticker_fixed on public.assets;
create trigger assets_ticker_fixed
  before update on public.assets
  for each row execute function public.ft_ticker_is_fixed();

-- ── What each manager owns ────────────────────────────────────────────
create table if not exists public.holdings (
  user_id     uuid not null references auth.users(id) on delete cascade,
  asset_id    text not null references public.assets(id),
  shares      bigint not null default 0 check (shares >= 0),
  locked      bigint not null default 0 check (locked >= 0),
  avg_cost    numeric(12,4) not null default 0,
  slot        text,                                  -- where it lines up: 'ST', 'CB', 'COACH', 'SUB'
  updated_at  timestamptz not null default now(),
  primary key (user_id, asset_id),
  constraint locked_within_shares check (locked <= shares)
);
create index if not exists holdings_user_idx on public.holdings (user_id);
-- `slot` arrived with the Dream Club step; this keeps an earlier install current.
alter table public.holdings add column if not exists slot text;

-- ── Every movement, in order ──────────────────────────────────────────
create table if not exists public.transactions (
  id          bigint generated always as identity primary key,
  user_id     uuid not null references auth.users(id) on delete cascade,
  type        text not null,                         -- constrained below
  asset_id    text references public.assets(id),
  label       text not null default '',              -- what the row reads as in the app
  shares      bigint not null default 0,
  price       numeric(12,4) not null default 0,
  total       numeric(20,2) not null default 0,      -- $FTR that moved, fee included
  fee         numeric(20,2) not null default 0,
  balance_after numeric(20,2),
  created_at  timestamptz not null default now()
);
create index if not exists transactions_user_idx on public.transactions (user_id, created_at desc);

-- The ledger's allowed types, in one place. The first twelve are what the app
-- books today; the last three are flows the white paper defines and the pages
-- do not have yet, kept here so the ledger can carry them the day they arrive:
--   LIST       a lister's listing/claim payment in $FTR (7)
--   BURN       the 2% of that payment burnt for good (7, 17)
--   FEE_SHARE  a lister's 30% cut of the asset's eligible trading fees (8.3)
alter table public.transactions drop constraint if exists transactions_type_check;
alter table public.transactions add constraint transactions_type_check check (type in
  ('GRANT','BUY','SELL','SWAP','CONVERT','SEND','RECEIVE','WITHDRAW','STAKE','PAYOUT','SETTLE','ADJUST',
   'LIST','BURN','FEE_SHARE'));

-- ── Dream Clubs ───────────────────────────────────────────────────────
-- A manager fields up to six. One is active at a time; the shares that make
-- up the side are the holdings above, each carrying the slot it lines up in.
-- The side is eleven plus a bench chosen from shares actually held, a coach
-- included (19), so a club's FanPlay exposure comes from real holdings and
-- never from fictional ownership. `season_fp` is the Accumulated FP its
-- individual players and coach have scored; `boost` is the team boost applied
-- on top, whose formula 27 still lists as an open parameter.
create table if not exists public.clubs (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  name        text not null check (length(trim(name)) between 2 and 40),
  stadium     text not null default 'Unnamed ground',
  colors      jsonb not null default '["#1800ad","#0f0075"]'::jsonb,
  color_name  text not null default 'Indigo',
  formation   text not null default '4-3-3',
  coach       text references public.assets(id),
  division    text not null default 'Challenger',
  season_fp   numeric(14,2) not null default 0 check (season_fp >= 0),
  boost       numeric(6,2) not null default 0 check (boost >= 0),
  is_active   boolean not null default false,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);
create index if not exists clubs_user_idx on public.clubs (user_id, created_at);
-- Two clubs with the same name would be indistinguishable on the rail.
create unique index if not exists clubs_user_name_idx on public.clubs (user_id, lower(name));
-- Exactly one club is the active one.
create unique index if not exists clubs_one_active_idx on public.clubs (user_id) where is_active;
-- The board ranks on season FP.
create index if not exists clubs_board_idx on public.clubs (season_fp desc, created_at);

-- ── FanPlay ───────────────────────────────────────────────────────────
-- An entry puts something at risk on a matchday, and there are two ways to do
-- it: stake $FTR on a Dream Club, or lock shares in one player against a
-- market. Both live here.
--
--   · a $FTR stake moves out of wallets.balance into wallets.locked
--   · staked shares move into holdings.locked for that asset
--
-- Either way the amount is accounted for the whole time it is in play, and
-- comes back where it came from when the entry settles.
create table if not exists public.fanplay_entries (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  club_id      uuid references public.clubs(id) on delete set null,
  mode         text not null check (mode in ('Dream Club','Individual')),
  target       text not null,                        -- club name, or '$Saka'
  tier         text not null default '',
  multiplier   numeric(6,2) not null default 1 check (multiplier > 0),
  stake        numeric(20,2) not null default 0 check (stake >= 0),      -- $FTR staked
  asset_id     text references public.assets(id),                        -- shares staked, if any
  staked_shares bigint not null default 0 check (staked_shares >= 0),
  match        jsonb,                                 -- fixture the entry rides on
  market       jsonb,                                 -- the market and its tier, 14.4
  selections   jsonb,                                 -- the picks, each with its FP either way, 14.5
  projected_fp numeric(12,2) not null default 0,
  matchday     integer not null default 7,
  status       text not null default 'ACTIVE',       -- the lifecycle, constraint below
  scored_fp    numeric(12,2),
  payout       numeric(20,2),                        -- $FTR out; negative when it loses, 14.3
  settled_at   timestamptz,
  -- The page's idempotency key: a resubmitted entry finds itself rather than
  -- locking a second set of shares.
  action_key   text,
  created_at   timestamptz not null default now(),
  constraint entry_risks_something check (stake > 0 or staked_shares > 0)
);
create index if not exists entries_user_idx on public.fanplay_entries (user_id, created_at desc);
-- One live entry per club per matchday: staking the same side twice would
-- double a single result.
create unique index if not exists entries_one_live_idx
  on public.fanplay_entries (club_id, matchday) where status = 'ACTIVE' and club_id is not null;
create unique index if not exists entries_action_idx
  on public.fanplay_entries (user_id, action_key) where action_key is not null;

-- The lifecycle of 14.6, in one place. The pages only ever open an entry as
-- ACTIVE and can cancel it, which lands as VOID; the live and settlement
-- states belong to the service-role job that settles a matchday, so nothing
-- the browser is allowed to call writes them.
alter table public.fanplay_entries drop constraint if exists fanplay_entries_status_check;
alter table public.fanplay_entries add constraint fanplay_entries_status_check check (status in
  ('DRAFT','ACTIVE','LIVE','PENDING_SETTLEMENT','SETTLED','VOID','CANCELLED','SUSPENDED','DISPUTED'));
-- These arrived with the share-staking entry; this keeps an earlier install current.
alter table public.fanplay_entries add column if not exists asset_id text references public.assets(id);
alter table public.fanplay_entries add column if not exists staked_shares bigint not null default 0;
alter table public.fanplay_entries add column if not exists match jsonb;
alter table public.fanplay_entries add column if not exists market jsonb;
alter table public.fanplay_entries add column if not exists selections jsonb;
alter table public.fanplay_entries add column if not exists action_key text;

-- ── Where withdrawals go. Only the last four digits are ever stored. ──
create table if not exists public.payout_accounts (
  user_id      uuid primary key references auth.users(id) on delete cascade,
  currency     text not null default 'GBP',
  holder       text not null,
  bank         text not null,
  account_last4 text not null,
  updated_at   timestamptz not null default now()
);

-- ── Row-level security ────────────────────────────────────────────────
alter table public.profiles        enable row level security;
alter table public.wallets         enable row level security;
alter table public.assets          enable row level security;
alter table public.holdings        enable row level security;
alter table public.transactions    enable row level security;
alter table public.payout_accounts enable row level security;
alter table public.clubs           enable row level security;
alter table public.fanplay_entries enable row level security;

-- The catalogue is public to read, and to no one to write.
drop policy if exists assets_readable on public.assets;
create policy assets_readable on public.assets for select using (true);

-- Everything personal: readable by its owner, and by nobody else.
drop policy if exists profiles_own on public.profiles;
create policy profiles_own on public.profiles for select using (auth.uid() = id);
drop policy if exists profiles_own_update on public.profiles;
create policy profiles_own_update on public.profiles for update using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists wallets_own on public.wallets;
create policy wallets_own on public.wallets for select using (auth.uid() = user_id);

drop policy if exists holdings_own on public.holdings;
create policy holdings_own on public.holdings for select using (auth.uid() = user_id);

drop policy if exists transactions_own on public.transactions;
create policy transactions_own on public.transactions for select using (auth.uid() = user_id);

drop policy if exists payout_own on public.payout_accounts;
create policy payout_own on public.payout_accounts for select using (auth.uid() = user_id);

drop policy if exists clubs_own on public.clubs;
create policy clubs_own on public.clubs for select using (auth.uid() = user_id);

drop policy if exists entries_own on public.fanplay_entries;
create policy entries_own on public.fanplay_entries for select using (auth.uid() = user_id);

-- No insert/update/delete policies on wallets, holdings, transactions,
-- payout_accounts, clubs or fanplay_entries: the browser cannot write them at
-- all. Everything moves through the functions in 02_functions.sql and
-- 04_fanplay_clubs.sql.
--
-- Note that clubs are readable only by their own manager. The leaderboard
-- needs to see everyone's, so it goes through ft_leaderboard(), which returns
-- the handful of columns a public board shows and nothing else.

-- ── A new sign-up gets a profile, a wallet and a starting balance ─────
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

  insert into public.wallets (user_id, balance) values (new.id, 50000);

  insert into public.transactions (user_id, type, label, total, balance_after)
  values (new.id, 'GRANT', 'Welcome balance', 50000, 50000);

  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

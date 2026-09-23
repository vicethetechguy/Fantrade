-- Fantrade · admin-listed player drops and the claims against them.
--
-- There is no admin app yet: an admin lists a player by inserting a row into
-- public.listings (Supabase Table Editor — the service role bypasses RLS, and
-- the browser has no write policy on either table, so only the dashboard or
-- these SQL files can ever list or unlist). Managers see the active rows on
-- the home page and claim each one once; ft_claim_listing() grants the shares
-- and books a GRANT transaction, starting from the signed-in user like every
-- other money function.
--
-- Safe to re-run: tables use `if not exists`, the functions are
-- `create or replace`, the seed upserts on the listing id.

create table if not exists public.listings (
  id         text primary key,                       -- 'lst-mbappe-drop'
  asset_id   text not null references public.assets(id),
  title      text not null default '',
  shares     bigint not null default 100 check (shares > 0),  -- granted per claim
  is_active  boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.claims (
  listing_id text not null references public.listings(id) on delete cascade,
  user_id    uuid not null references auth.users(id) on delete cascade,
  claimed_at timestamptz not null default now(),
  primary key (listing_id, user_id)
);

alter table public.listings enable row level security;
alter table public.claims enable row level security;

-- Listings are catalogue news, readable by everyone like `assets`. There are
-- deliberately no insert/update/delete policies: the browser cannot list or
-- unlist anything — admins do that from the Table Editor.
drop policy if exists listings_readable on public.listings;
create policy listings_readable on public.listings for select using (true);

-- Each manager reads only their own claims; rows are written by the function.
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
    select l.id, l.asset_id, l.title, l.shares,
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

-- ── Claim one listing: once per manager, shares granted, ledger booked ──
create or replace function public.ft_claim_listing(p_listing text)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  l   public.listings%rowtype;
  a   public.assets%rowtype;
  bal numeric(20,2);
  new_held bigint;
begin
  if p_listing is null or p_listing = '' then raise exception 'Pick a listing to claim'; end if;
  select * into l from public.listings where id = p_listing and is_active for update;
  if not found then raise exception 'That listing is no longer available'; end if;
  if exists (select 1 from public.claims where listing_id = p_listing and user_id = uid) then
    raise exception 'You have already claimed this listing';
  end if;

  select * into a from public.assets where id = l.asset_id for update;
  if not found then raise exception 'That asset is not listed'; end if;

  insert into public.claims (listing_id, user_id) values (p_listing, uid);

  insert into public.holdings (user_id, asset_id, shares, avg_cost)
  values (uid, l.asset_id, l.shares, a.price)
  on conflict (user_id, asset_id) do update
    set avg_cost = round(((public.holdings.shares * public.holdings.avg_cost) + (l.shares * a.price))
                         / (public.holdings.shares + l.shares), 4),
        shares = public.holdings.shares + l.shares,
        updated_at = now()
  returning public.holdings.shares into new_held;

  update public.assets
     set circulating = least(total_shares, circulating + l.shares), updated_at = now()
   where id = l.asset_id;

  select balance into bal from public.wallets where user_id = uid;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'GRANT', l.asset_id,
          'Claimed listing' || case when coalesce(l.title,'') = '' then '' else ': ' || l.title end,
          l.shares, a.price, 0, 0, bal);

  return json_build_object('listing', l.id, 'asset', l.asset_id, 'name', a.name,
                           'ticker', a.ticker, 'shares', l.shares, 'held', new_held);
end;
$$;

-- Two drops to claim on day one; an admin adds more from the Table Editor.
insert into public.listings (id, asset_id, title, shares, is_active) values
  ('lst-mbappe-drop', '$Mbappe', 'Starter drop', 50, true),
  ('lst-yamal-drop',  '$Yamal',  'Rising star drop', 25, true)
on conflict (id) do nothing;

-- Who may call what: signed-in managers only, never anon.
revoke execute on all functions in schema public from public, anon;
grant execute on function public.ft_listings() to authenticated;
grant execute on function public.ft_claim_listing(text) to authenticated;
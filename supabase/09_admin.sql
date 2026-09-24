-- Fantrade · the admin. Run after 08_claim_by_value.sql. Safe to run again.
--
-- Admins are ordinary Fantrade accounts listed in public.admins. The admin
-- pages (/admin) call only the ft_admin_* functions below, and every one of
-- them starts by refusing anyone who is not on that list, so the browser
-- key cannot read other managers' data on its own.
--
-- Make yourself the first admin once, in the SQL editor, with the email you
-- sign in to Fantrade with:
--
--   insert into public.admins (user_id)
--   select id from auth.users where email = 'you@example.com'
--   on conflict do nothing;

create table if not exists public.admins (
  user_id   uuid primary key references auth.users(id) on delete cascade,
  role      text not null default 'admin' check (role in ('admin','viewer')),
  added_at  timestamptz not null default now()
);
alter table public.admins enable row level security;   -- no policies: functions only

-- Every admin action leaves a line here.
create table if not exists public.admin_log (
  id         bigint generated always as identity primary key,
  admin_id   uuid references auth.users(id) on delete set null,
  action     text not null,
  target     text,
  detail     jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
alter table public.admin_log enable row level security;
create index if not exists admin_log_time_idx on public.admin_log (created_at desc);

-- A suspended manager can sign in and look, but cannot move money or shares.
alter table public.profiles add column if not exists suspended boolean not null default false;
alter table public.profiles add column if not exists suspended_reason text;
alter table public.profiles add column if not exists suspended_at timestamptz;

-- Every money function starts with ft_require_user(), so refusing suspended
-- accounts here covers buying, selling, swapping, claiming and FanPlay at once.
create or replace function public.ft_require_user()
returns uuid language plpgsql stable security definer set search_path = public, pg_temp as $$
declare uid uuid := auth.uid();
begin
  if uid is null then raise exception 'Sign in to continue' using errcode = '28000'; end if;
  if exists (select 1 from public.profiles where id = uid and suspended) then
    raise exception 'This account is suspended. Contact Fantrade support.' using errcode = '42501';
  end if;
  return uid;
end;
$$;

create or replace function public.ft_is_admin()
returns boolean language sql stable security definer set search_path = public, pg_temp as $$
  select exists (select 1 from public.admins where user_id = auth.uid());
$$;

-- p_write: true for anything that changes data, which a 'viewer' may not do.
create or replace function public.ft_require_admin(p_write boolean default false)
returns uuid language plpgsql stable security definer set search_path = public, pg_temp as $$
declare uid uuid := auth.uid(); r text;
begin
  if uid is null then raise exception 'Sign in to continue' using errcode = '28000'; end if;
  select role into r from public.admins where user_id = uid;
  if r is null then raise exception 'This account is not a Fantrade admin' using errcode = '42501'; end if;
  if p_write and r <> 'admin' then raise exception 'Your admin role can view but not change data' using errcode = '42501'; end if;
  return uid;
end;
$$;

create or replace function public.ft_admin_note(p_action text, p_target text, p_detail jsonb)
returns void language sql security definer set search_path = public, pg_temp as $$
  insert into public.admin_log (admin_id, action, target, detail) values (auth.uid(), p_action, p_target, coalesce(p_detail, '{}'::jsonb));
$$;

-- ── Who am I ────────────────────────────────────────────────────────────
create or replace function public.ft_admin_whoami()
returns json language plpgsql stable security definer set search_path = public, pg_temp as $$
declare uid uuid := auth.uid();
begin
  return json_build_object(
    'is_admin', exists (select 1 from public.admins where user_id = uid),
    'role', (select role from public.admins where user_id = uid),
    'handle', (select handle from public.profiles where id = uid),
    'name', (select display_name from public.profiles where id = uid),
    'email', (select email from auth.users where id = uid));
end;
$$;

-- ── Overview ────────────────────────────────────────────────────────────
create or replace function public.ft_admin_overview()
returns json language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public.ft_require_admin();
  return json_build_object(
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

-- ── Player eligibility ──────────────────────────────────────────────────
create or replace function public.ft_admin_players()
returns json language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public.ft_require_admin();
  return coalesce((select json_agg(row_to_json(r) order by r.status_rank, r.name) from (
    select l.id as listing_id, a.id as asset_id, a.ticker, a.name, a.kind, a.club, a.league, a.position,
           coalesce(a.reference_value, a.price) as reference_value, a.reference_at,
           case when l.claimed_by is not null or a.is_active then 'claimed'
                when l.is_active then 'open' else 'paused' end as status,
           case when l.claimed_by is not null or a.is_active then 2 when l.is_active then 0 else 1 end as status_rank,
           p.handle as claimed_by, l.claimed_at, l.created_at
      from public.listings l
      join public.assets a on a.id = l.asset_id
      left join public.profiles p on p.id = l.claimed_by
     where l.claimed_by is not null or not a.is_active
  ) r), '[]'::json);
end;
$$;

-- Add or update cleared players from a list (the CSV upload, or one form).
-- Each row: {ticker, name, kind, club, league, position, reference_value}.
-- A player who is already trading or already claimed is skipped, not changed.
create or replace function public.ft_admin_upsert_players(p_rows jsonb)
returns json language plpgsql security definer set search_path = public, pg_temp as $$
declare
  r jsonb; v_ticker text; v_name text; v_kind text; v_pos text; v_val numeric;
  v_id text; a public.assets%rowtype; l public.listings%rowtype;
  added int := 0; updated int := 0; skipped jsonb := '[]'::jsonb;
begin
  perform public.ft_require_admin(true);
  if jsonb_typeof(p_rows) <> 'array' then raise exception 'Send a list of players'; end if;
  if jsonb_array_length(p_rows) > 500 then raise exception 'Upload at most 500 players at a time'; end if;

  for r in select * from jsonb_array_elements(p_rows) loop
    v_ticker := upper(trim(coalesce(r->>'ticker', '')));
    v_name   := trim(coalesce(r->>'name', ''));
    v_kind   := upper(coalesce(nullif(trim(r->>'kind'), ''), 'PLAYER'));
    v_pos    := upper(coalesce(nullif(trim(r->>'position'), ''), case when v_kind = 'COACH' then 'MGR' else 'FWD' end));
    v_val    := nullif(trim(coalesce(r->>'reference_value', '')), '')::numeric;

    if v_ticker !~ '^F[A-Z0-9]{2,6}$' then
      skipped := skipped || jsonb_build_object('ticker', v_ticker, 'name', v_name, 'reason', 'Ticker must be F plus 2-6 letters or digits'); continue; end if;
    if length(v_name) < 2 then
      skipped := skipped || jsonb_build_object('ticker', v_ticker, 'name', v_name, 'reason', 'Name is missing'); continue; end if;
    if v_kind not in ('PLAYER','COACH') then
      skipped := skipped || jsonb_build_object('ticker', v_ticker, 'name', v_name, 'reason', 'Kind must be PLAYER or COACH'); continue; end if;
    if v_val is null or v_val <= 0 then
      skipped := skipped || jsonb_build_object('ticker', v_ticker, 'name', v_name, 'reason', 'Reference price must be above 0'); continue; end if;

    select * into a from public.assets where ticker = v_ticker limit 1;
    if found then
      select * into l from public.listings where asset_id = a.id limit 1;
      if a.is_active or (l.id is not null and l.claimed_by is not null) then
        skipped := skipped || jsonb_build_object('ticker', v_ticker, 'name', v_name, 'reason', 'Already launched, so it can no longer be edited here'); continue; end if;
      update public.assets set name = v_name, kind = v_kind, club = nullif(trim(r->>'club'), ''),
             league = nullif(trim(r->>'league'), ''), position = v_pos,
             price = v_val, reference_value = v_val, reference_at = now(), updated_at = now()
       where id = a.id;
      if l.id is null then
        insert into public.listings (id, asset_id, title, is_active, fee_level1, fee_level2)
        values ('lst-' || v_ticker, a.id, 'Open to claim', true, round(500000 * v_val, 2), round(1000000 * v_val, 2));
      else
        update public.listings set fee_level1 = round(500000 * v_val, 2), fee_level2 = round(1000000 * v_val, 2) where id = l.id;
      end if;
      updated := updated + 1;
    else
      v_id := '$' || v_ticker;
      insert into public.assets (id, ticker, name, kind, club, league, position, price, reference_value, reference_at, is_active)
      values (v_id, v_ticker, v_name, v_kind, nullif(trim(r->>'club'), ''), nullif(trim(r->>'league'), ''), v_pos,
              v_val, v_val, now(), false);
      insert into public.listings (id, asset_id, title, is_active, fee_level1, fee_level2)
      values ('lst-' || v_ticker, v_id, 'Open to claim', true, round(500000 * v_val, 2), round(1000000 * v_val, 2))
      on conflict (id) do nothing;
      added := added + 1;
    end if;
  end loop;

  perform public.ft_admin_note('players.upsert', null,
    jsonb_build_object('added', added, 'updated', updated, 'skipped', jsonb_array_length(skipped)));
  return json_build_object('added', added, 'updated', updated, 'skipped', skipped);
end;
$$;

-- Pause or reopen a player nobody has claimed yet.
create or replace function public.ft_admin_set_open(p_listing text, p_open boolean)
returns json language plpgsql security definer set search_path = public, pg_temp as $$
declare l public.listings%rowtype;
begin
  perform public.ft_require_admin(true);
  select * into l from public.listings where id = p_listing for update;
  if not found then raise exception 'No such listing'; end if;
  if l.claimed_by is not null then raise exception 'This player has been claimed and is trading'; end if;
  update public.listings set is_active = p_open where id = p_listing;
  perform public.ft_admin_note(case when p_open then 'player.reopen' else 'player.pause' end, p_listing, '{}'::jsonb);
  return json_build_object('listing', p_listing, 'open', p_open);
end;
$$;

-- Take a player off the list entirely. Only possible before anyone claims.
create or replace function public.ft_admin_remove_player(p_listing text)
returns json language plpgsql security definer set search_path = public, pg_temp as $$
declare l public.listings%rowtype; a public.assets%rowtype;
begin
  perform public.ft_require_admin(true);
  select * into l from public.listings where id = p_listing for update;
  if not found then raise exception 'No such listing'; end if;
  select * into a from public.assets where id = l.asset_id for update;
  if l.claimed_by is not null or a.is_active then raise exception 'This player has launched and cannot be removed'; end if;
  if exists (select 1 from public.holdings where asset_id = a.id) or exists (select 1 from public.claims where listing_id = l.id) then
    raise exception 'Someone holds shares in this player, so it cannot be removed';
  end if;
  delete from public.listings where id = l.id;
  delete from public.assets where id = a.id
    and not exists (select 1 from public.transactions t where t.asset_id = a.id)
    and not exists (select 1 from public.fanplay_entries f where f.asset_id = a.id)
    and not exists (select 1 from public.clubs c where c.coach = a.id);
  perform public.ft_admin_note('player.remove', a.ticker, jsonb_build_object('name', a.name));
  return json_build_object('removed', p_listing);
end;
$$;

-- ── Claims ──────────────────────────────────────────────────────────────
create or replace function public.ft_admin_claims()
returns json language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public.ft_require_admin();
  return coalesce((select json_agg(row_to_json(r) order by r.claimed_at desc) from (
    select c.listing_id, a.ticker, a.name, a.club, p.handle, p.display_name, c.user_id,
           c.claim_level, c.shares, c.vesting_years, c.fee_paid, c.fee_burned, c.daily_limit,
           c.claimed_at, c.vesting_until, coalesce(a.reference_value, a.price) as reference_value
      from public.claims c
      join public.listings l on l.id = c.listing_id
      join public.assets a on a.id = l.asset_id
      left join public.profiles p on p.id = c.user_id
  ) r), '[]'::json);
end;
$$;

-- ── Managers ────────────────────────────────────────────────────────────
create or replace function public.ft_admin_managers(p_query text default '', p_limit int default 100)
returns json language plpgsql stable security definer set search_path = public, pg_temp as $$
declare q text := lower(trim(coalesce(p_query, '')));
begin
  perform public.ft_require_admin();
  return coalesce((select json_agg(row_to_json(r)) from (
    select p.id, p.handle, p.display_name, u.email, p.region, p.created_at, p.suspended, p.suspended_reason,
           coalesce(w.balance, 0) as balance, coalesce(w.locked, 0) as locked,
           (select coalesce(sum(h.shares * a.price), 0) from public.holdings h join public.assets a on a.id = h.asset_id
             where h.user_id = p.id) as holdings_value,
           (select count(*) from public.holdings h where h.user_id = p.id and h.shares > 0) as positions,
           exists (select 1 from public.admins ad where ad.user_id = p.id) as is_admin
      from public.profiles p
      left join auth.users u on u.id = p.id
      left join public.wallets w on w.user_id = p.id
     where q = '' or lower(p.handle::text) like '%' || q || '%' or lower(p.display_name) like '%' || q || '%'
           or lower(coalesce(u.email, '')) like '%' || q || '%'
     order by p.created_at desc
     limit greatest(1, least(coalesce(p_limit, 100), 500))
  ) r), '[]'::json);
end;
$$;

create or replace function public.ft_admin_manager(p_user uuid)
returns json language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public.ft_require_admin();
  if not exists (select 1 from public.profiles where id = p_user) then raise exception 'No such manager'; end if;
  return json_build_object(
    'profile', (select row_to_json(x) from (
                  select p.id, p.handle, p.display_name, u.email, p.region, p.home_league, p.created_at,
                         p.suspended, p.suspended_reason, p.suspended_at,
                         exists (select 1 from public.admins ad where ad.user_id = p.id) as is_admin
                    from public.profiles p left join auth.users u on u.id = p.id where p.id = p_user) x),
    'wallet', (select row_to_json(w) from public.wallets w where w.user_id = p_user),
    'holdings', (select coalesce(json_agg(row_to_json(x) order by x.value desc), '[]'::json) from (
                   select a.ticker, a.name, h.shares, h.locked, h.avg_cost, a.price, h.shares * a.price as value
                     from public.holdings h join public.assets a on a.id = h.asset_id
                    where h.user_id = p_user and h.shares > 0) x),
    'transactions', (select coalesce(json_agg(row_to_json(x)), '[]'::json) from (
                   select t.type, t.label, a.ticker, t.shares, t.total, t.fee, t.balance_after, t.created_at
                     from public.transactions t left join public.assets a on a.id = t.asset_id
                    where t.user_id = p_user order by t.created_at desc limit 25) x),
    'fanplay', (select coalesce(json_agg(row_to_json(x)), '[]'::json) from (
                   select f.mode, f.target, f.matchday, f.status, f.projected_fp, f.staked_shares, f.created_at
                     from public.fanplay_entries f where f.user_id = p_user order by f.created_at desc limit 10) x)
  );
end;
$$;

create or replace function public.ft_admin_suspend(p_user uuid, p_suspend boolean, p_reason text default null)
returns json language plpgsql security definer set search_path = public, pg_temp as $$
declare me uuid := public.ft_require_admin(true); h text;
begin
  if p_user = me then raise exception 'You cannot suspend your own account'; end if;
  if p_suspend and exists (select 1 from public.admins where user_id = p_user) then
    raise exception 'Remove admin rights before suspending an admin';
  end if;
  if p_suspend and length(trim(coalesce(p_reason, ''))) < 3 then raise exception 'Give a reason for the suspension'; end if;
  update public.profiles
     set suspended = p_suspend,
         suspended_reason = case when p_suspend then trim(p_reason) else null end,
         suspended_at = case when p_suspend then now() else null end
   where id = p_user
  returning handle into h;
  if h is null then raise exception 'No such manager'; end if;
  perform public.ft_admin_note(case when p_suspend then 'manager.suspend' else 'manager.reinstate' end, '@' || h,
                               jsonb_build_object('reason', p_reason));
  return json_build_object('handle', h, 'suspended', p_suspend);
end;
$$;

-- ── FanPlay ─────────────────────────────────────────────────────────────
-- Read-only on purpose: entries settle from verified match data on the
-- server (white paper 14.6), never from a click in a browser.
create or replace function public.ft_admin_fanplay()
returns json language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public.ft_require_admin();
  return json_build_object(
    'by_status', (select coalesce(json_object_agg(status, n), '{}'::json)
                    from (select status, count(*) n from public.fanplay_entries group by status) s),
    'matchdays', (select coalesce(json_agg(row_to_json(m) order by m.matchday desc), '[]'::json) from (
                    select matchday, count(*) as entries,
                           count(*) filter (where status in ('ACTIVE','LIVE')) as live,
                           count(*) filter (where status = 'PENDING_SETTLEMENT') as pending,
                           count(*) filter (where status = 'SETTLED') as settled,
                           coalesce(sum(staked_shares), 0) as shares_staked,
                           coalesce(sum(projected_fp), 0) as projected_fp
                      from public.fanplay_entries group by matchday) m),
    'entries', (select coalesce(json_agg(row_to_json(e)), '[]'::json) from (
                  select f.id, p.handle, f.mode, f.target, a.ticker, f.staked_shares, f.matchday, f.status,
                         f.projected_fp, f.scored_fp, f.created_at, f.match
                    from public.fanplay_entries f
                    left join public.profiles p on p.id = f.user_id
                    left join public.assets a on a.id = f.asset_id
                   order by f.created_at desc limit 200) e)
  );
end;
$$;

create or replace function public.ft_admin_log(p_limit int default 50)
returns json language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public.ft_require_admin();
  return coalesce((select json_agg(row_to_json(r)) from (
    select g.id, g.action, g.target, g.detail, g.created_at, p.handle
      from public.admin_log g left join public.profiles p on p.id = g.admin_id
     order by g.created_at desc limit greatest(1, least(coalesce(p_limit, 50), 200))) r), '[]'::json);
end;
$$;

-- ── Who may call what ───────────────────────────────────────────────────
revoke execute on function public.ft_require_admin(boolean), public.ft_admin_note(text, text, jsonb) from public, anon, authenticated;
revoke execute on function public.ft_is_admin(), public.ft_admin_whoami(), public.ft_admin_overview(),
  public.ft_admin_players(), public.ft_admin_upsert_players(jsonb), public.ft_admin_set_open(text, boolean),
  public.ft_admin_remove_player(text), public.ft_admin_claims(), public.ft_admin_managers(text, int),
  public.ft_admin_manager(uuid), public.ft_admin_suspend(uuid, boolean, text), public.ft_admin_fanplay(),
  public.ft_admin_log(int) from public, anon;
grant execute on function public.ft_is_admin(), public.ft_admin_whoami(), public.ft_admin_overview(),
  public.ft_admin_players(), public.ft_admin_upsert_players(jsonb), public.ft_admin_set_open(text, boolean),
  public.ft_admin_remove_player(text), public.ft_admin_claims(), public.ft_admin_managers(text, int),
  public.ft_admin_manager(uuid), public.ft_admin_suspend(uuid, boolean, text), public.ft_admin_fanplay(),
  public.ft_admin_log(int) to authenticated;

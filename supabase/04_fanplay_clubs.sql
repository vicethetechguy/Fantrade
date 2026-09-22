-- Fantrade · Supabase functions (step 2: Dream Clubs, FanPlay, the board)
-- Run this after 01, 02 and 03. Safe to re-run.
--
-- The tables themselves live in 01_schema.sql, with the rest of the schema.
-- What is here is the only way the browser can change them: no club row and no
-- FanPlay entry is writable directly, so the rules below — six clubs, one
-- active, one live entry per side, a stake that is actually covered — are the
-- database's rules rather than the page's.
--
-- Settlement is deliberately absent. Paying out an entry decides who gets
-- money, so it must never be callable by the browser that placed it. When
-- matchdays start settling it belongs in a scheduled job running as the
-- service role, reading the result from outside, and the grants at the foot of
-- this file are what keep that line drawn.

-- ── Helpers ───────────────────────────────────────────────────────────

-- The club a manager is fielding right now, creating the first one if this is
-- their first save. Onboarding and the club builder both land here.
create or replace function public.ft_active_club(p_uid uuid)
returns uuid
language plpgsql security definer set search_path = public, pg_temp
as $$
declare club_id uuid;
begin
  select id into club_id from public.clubs where user_id = p_uid and is_active limit 1;
  if club_id is null then
    select id into club_id from public.clubs where user_id = p_uid order by created_at limit 1;
    if club_id is not null then
      update public.clubs set is_active = true where id = club_id;
    end if;
  end if;
  return club_id;
end;
$$;

-- ── Clubs ─────────────────────────────────────────────────────────────

create or replace function public.ft_create_club(
  p_name text, p_stadium text default null, p_formation text default null,
  p_colors jsonb default null, p_color_name text default null,
  p_coach text default null, p_division text default null)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare uid uuid := public.ft_require_user(); club public.clubs; held int;
begin
  if coalesce(trim(p_name), '') = '' then raise exception 'Give the club a name first'; end if;

  select count(*) into held from public.clubs where user_id = uid;
  if held >= 6 then raise exception 'Six clubs is the limit for one manager'; end if;
  if exists (select 1 from public.clubs where user_id = uid and lower(name) = lower(trim(p_name))) then
    raise exception 'You already have a club called %', trim(p_name);
  end if;

  -- A newly built side takes over as the one being fielded.
  update public.clubs set is_active = false where user_id = uid and is_active;

  insert into public.clubs (user_id, name, stadium, formation, colors, color_name,
                            coach, division, is_active)
  values (uid, trim(p_name),
          coalesce(nullif(trim(p_stadium), ''), 'Unnamed ground'),
          coalesce(nullif(trim(p_formation), ''), '4-3-3'),
          coalesce(p_colors, '["#1800ad","#0f0075"]'::jsonb),
          coalesce(nullif(trim(p_color_name), ''), 'Indigo'),
          nullif(trim(p_coach), ''),
          coalesce(nullif(trim(p_division), ''), 'Challenger'),
          true)
  returning * into club;

  return row_to_json(club);
end;
$$;

-- Edit a club. With no id this saves the active one, and builds the manager's
-- first club if they have none — which is what onboarding does.
create or replace function public.ft_save_club(
  p_club uuid default null, p_name text default null, p_stadium text default null,
  p_formation text default null, p_colors jsonb default null,
  p_color_name text default null, p_coach text default null)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare uid uuid := public.ft_require_user(); target uuid; club public.clubs;
begin
  target := coalesce(p_club, public.ft_active_club(uid));
  if target is null then
    return public.ft_create_club(coalesce(nullif(trim(p_name), ''), 'My Club'),
                                 p_stadium, p_formation, p_colors, p_color_name, p_coach, null);
  end if;

  if not exists (select 1 from public.clubs where id = target and user_id = uid) then
    raise exception 'That club no longer exists';
  end if;
  if p_name is not null and trim(p_name) <> '' and exists (
       select 1 from public.clubs
        where user_id = uid and id <> target and lower(name) = lower(trim(p_name))) then
    raise exception 'You already have a club called %', trim(p_name);
  end if;

  update public.clubs set
    name       = coalesce(nullif(trim(p_name), ''), name),
    stadium    = coalesce(nullif(trim(p_stadium), ''), stadium),
    formation  = coalesce(nullif(trim(p_formation), ''), formation),
    colors     = coalesce(p_colors, colors),
    color_name = coalesce(nullif(trim(p_color_name), ''), color_name),
    coach      = coalesce(nullif(trim(p_coach), ''), coach),
    updated_at = now()
  where id = target returning * into club;

  return row_to_json(club);
end;
$$;

create or replace function public.ft_switch_club(p_club uuid)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare uid uuid := public.ft_require_user();
begin
  if not exists (select 1 from public.clubs where id = p_club and user_id = uid) then
    raise exception 'That club no longer exists';
  end if;
  update public.clubs set is_active = false where user_id = uid and is_active and id <> p_club;
  update public.clubs set is_active = true, updated_at = now() where id = p_club;
  return json_build_object('active', p_club);
end;
$$;

create or replace function public.ft_delete_club(p_club uuid)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare uid uuid := public.ft_require_user(); held int; was_active boolean;
begin
  select count(*) into held from public.clubs where user_id = uid;
  if held < 2 then raise exception 'Your last club cannot be deleted'; end if;
  select is_active into was_active from public.clubs where id = p_club and user_id = uid;
  if was_active is null then raise exception 'That club no longer exists'; end if;

  -- Money is riding on it: the round has to finish first.
  if exists (select 1 from public.fanplay_entries
              where club_id = p_club and status = 'ACTIVE') then
    raise exception 'That club has a live entry. It settles before you can delete it';
  end if;

  delete from public.clubs where id = p_club and user_id = uid;
  if was_active then perform public.ft_active_club(uid); end if;
  return json_build_object('deleted', p_club);
end;
$$;

-- Where a holding lines up. 'SUB' benches it; null clears it entirely.
create or replace function public.ft_set_slot(p_asset text, p_slot text default null)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare uid uuid := public.ft_require_user(); held bigint;
begin
  select shares into held from public.holdings where user_id = uid and asset_id = p_asset;
  if held is null or held = 0 then
    raise exception 'You do not hold any %', p_asset;
  end if;
  update public.holdings set slot = nullif(trim(coalesce(p_slot, '')), ''), updated_at = now()
   where user_id = uid and asset_id = p_asset;
  return json_build_object('asset', p_asset, 'slot', p_slot);
end;
$$;

-- ── FanPlay ───────────────────────────────────────────────────────────

create or replace function public.ft_enter_fanplay(
  p_mode text, p_target text, p_tier text, p_multiplier numeric,
  p_stake numeric, p_projected_fp numeric default 0,
  p_club uuid default null, p_matchday integer default 7)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  stake numeric(20,2) := round(coalesce(p_stake, 0), 2);
  bal numeric(20,2); entry public.fanplay_entries;
begin
  if stake <= 0 then raise exception 'Enter a stake greater than zero'; end if;
  if coalesce(trim(p_target), '') = '' then raise exception 'Choose what to stake on'; end if;
  if p_club is not null and not exists (
       select 1 from public.clubs where id = p_club and user_id = uid) then
    raise exception 'That club no longer exists';
  end if;

  -- The stake leaves the spendable balance and sits in `locked` until the
  -- matchday settles, so it can be neither spent twice nor quietly lost.
  update public.wallets
     set balance = balance - stake, locked = locked + stake, updated_at = now()
   where user_id = uid and balance >= stake
   returning balance into bal;
  if bal is null then
    raise exception 'Insufficient $FTR balance. Need % $FTR', to_char(stake, 'FM999,999,999');
  end if;

  begin
    insert into public.fanplay_entries
      (user_id, club_id, mode, target, tier, multiplier, stake, projected_fp, matchday)
    values (uid, p_club, p_mode, trim(p_target), p_tier, p_multiplier, stake,
            coalesce(p_projected_fp, 0), p_matchday)
    returning * into entry;
  exception when unique_violation then
    raise exception '% already has a live entry this round', trim(p_target);
  end;

  insert into public.transactions (user_id, type, label, shares, price, total, balance_after)
  values (uid, 'STAKE', 'FanPlay MD ' || lpad(p_matchday::text, 2, '0') || ' (' || p_tier || ')',
          1, stake, stake, bal);

  return json_build_object('entry', row_to_json(entry), 'balance', bal);
end;
$$;

-- The other kind of entry: lock shares in one player against a market on one
-- fixture. Nothing is spent — the shares stay owned, they just cannot be sold
-- or staked again while the entry is live.
create or replace function public.ft_enter_fanplay_shares(
  p_asset text, p_shares bigint, p_match jsonb default null,
  p_market jsonb default null, p_selections jsonb default null,
  p_action_key text default null, p_matchday integer default 7)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  a public.assets%rowtype; h public.holdings%rowtype;
  entry public.fanplay_entries; existing public.fanplay_entries;
begin
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
$$;

-- Pulling out before the whistle. The shares come straight back; a $FTR stake
-- returns to the spendable balance.
create or replace function public.ft_cancel_fanplay(p_entry uuid)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare uid uuid := public.ft_require_user(); e public.fanplay_entries;
begin
  select * into e from public.fanplay_entries
    where id = p_entry and user_id = uid for update;
  if not found then raise exception 'That entry no longer exists'; end if;
  if e.status <> 'ACTIVE' then raise exception 'That entry has already settled'; end if;

  if e.staked_shares > 0 and e.asset_id is not null then
    update public.holdings set locked = greatest(0, locked - e.staked_shares), updated_at = now()
     where user_id = uid and asset_id = e.asset_id;
  end if;
  if e.stake > 0 then
    update public.wallets set balance = balance + e.stake,
                              locked = greatest(0, locked - e.stake), updated_at = now()
     where user_id = uid;
  end if;

  update public.fanplay_entries set status = 'VOID', settled_at = now() where id = p_entry;
  return json_build_object('cancelled', p_entry);
end;
$$;

-- ── The board ─────────────────────────────────────────────────────────
-- Clubs are private to their manager, so this is how anyone sees anyone
-- else's: a fixed, public set of columns, ranked, with the caller's own row
-- marked. Nothing here exposes a balance, a holding or an email.
create or replace function public.ft_leaderboard(p_limit integer default 50)
returns json
language plpgsql security definer set search_path = public, pg_temp stable
as $$
declare uid uuid := auth.uid(); capped integer := least(greatest(coalesce(p_limit, 50), 1), 200);
begin
  return (
    with ranked as (
      select c.id, c.name, c.colors, c.color_name, c.formation, c.division,
             c.season_fp, c.boost, c.user_id,
             p.handle, p.display_name,
             rank() over (order by c.season_fp desc, c.created_at) as position
        from public.clubs c
        join public.profiles p on p.id = c.user_id
    ),
    -- What the manager behind each club is holding, which is what the board
    -- shows as club value.
    valued as (
      select r.*, coalesce((
        select sum(h.shares * a.price) from public.holdings h
          join public.assets a on a.id = h.asset_id
         where h.user_id = r.user_id), 0) as value
        from ranked r
    )
    select json_build_object(
      'rows', coalesce((select json_agg(row_to_json(b)) from (
          select position, id, name, handle, display_name, colors, color_name,
                 formation, division, season_fp, boost, value,
                 (user_id = uid) as you
            from valued order by position limit capped) b), '[]'::json),
      'you', (select json_agg(row_to_json(m)) from (
          select position, id, name, season_fp, value from valued
           where user_id = uid order by position) m),
      'total', (select count(*) from ranked)
    )
  );
end;
$$;

-- ── Who may call what ─────────────────────────────────────────────────
-- ft_active_club is an internal helper: nothing outside these functions calls
-- it, so it is granted to nobody.
revoke execute on function public.ft_active_club(uuid) from public, anon, authenticated;

grant execute on function
  public.ft_create_club(text, text, text, jsonb, text, text, text),
  public.ft_save_club(uuid, text, text, text, jsonb, text, text),
  public.ft_switch_club(uuid),
  public.ft_delete_club(uuid),
  public.ft_set_slot(text, text),
  public.ft_enter_fanplay(text, text, text, numeric, numeric, numeric, uuid, integer),
  public.ft_enter_fanplay_shares(text, bigint, jsonb, jsonb, jsonb, text, integer),
  public.ft_cancel_fanplay(uuid),
  public.ft_leaderboard(integer)
to authenticated;

-- The board is the one thing a signed-out visitor can see.
grant execute on function public.ft_leaderboard(integer) to anon;

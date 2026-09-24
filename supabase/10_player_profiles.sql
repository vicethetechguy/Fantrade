-- Fantrade · player profiles and photos. Run after 09_admin.sql. Safe to run again.
--
-- Everything the admin's player form records: the name fans know them by,
-- men's or women's game, country, date of birth, shirt number, height,
-- stronger foot, a short "about", and a photo with its credit. Photos go in
-- the public Storage bucket 'player-photos'; only admins can upload,
-- replace or delete them, and every photo must carry a credit.

alter table public.assets
  add column if not exists known_as        text,
  add column if not exists gender          text not null default 'M' check (gender in ('M','W')),
  add column if not exists country         text,
  add column if not exists date_of_birth   date,
  add column if not exists shirt_number    smallint check (shirt_number between 1 and 99),
  add column if not exists height_cm       smallint check (height_cm between 140 and 220),
  add column if not exists preferred_foot  text check (preferred_foot in ('Left','Right','Both')),
  add column if not exists about           text check (length(about) <= 800),
  add column if not exists photo_url       text check (photo_url ~ '^https://'),
  add column if not exists photo_credit    text,
  add column if not exists photo_source    text,
  add column if not exists profile_updated_at timestamptz;

-- The women already on the catalogue.
update public.assets set gender = 'W'
 where gender = 'M' and ticker in ('FAITN','FPUTL','FRUSS','FLJMS','FKERR','FWILM','FEARP','FWIEG',
                                   'FSHAW','FPAJR','FRODM','FKELY','FAJBD','FALOZ');

-- ── Photo storage (skipped on a database without Supabase Storage) ───────
do $$
begin
  if to_regclass('storage.buckets') is null then
    raise notice 'No Supabase Storage here: skipping the player-photos bucket';
    return;
  end if;
  insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
  values ('player-photos', 'player-photos', true, 2097152, array['image/webp','image/jpeg','image/png'])
  on conflict (id) do update set public = true, file_size_limit = excluded.file_size_limit,
                                 allowed_mime_types = excluded.allowed_mime_types;
  execute 'drop policy if exists player_photos_admin_insert on storage.objects';
  execute 'drop policy if exists player_photos_admin_update on storage.objects';
  execute 'drop policy if exists player_photos_admin_delete on storage.objects';
  execute $p$create policy player_photos_admin_insert on storage.objects for insert to authenticated
            with check (bucket_id = 'player-photos' and public.ft_is_admin())$p$;
  execute $p$create policy player_photos_admin_update on storage.objects for update to authenticated
            using (bucket_id = 'player-photos' and public.ft_is_admin())$p$;
  execute $p$create policy player_photos_admin_delete on storage.objects for delete to authenticated
            using (bucket_id = 'player-photos' and public.ft_is_admin())$p$;
end $$;

-- Lenient readers for uploaded text: a bad cell skips its row, it never
-- aborts the whole upload.
create or replace function public.ft_try_numeric(t text) returns numeric language plpgsql immutable as $$
begin return nullif(trim(t), '')::numeric; exception when others then return null; end $$;
create or replace function public.ft_try_int(t text) returns int language plpgsql immutable as $$
begin return nullif(trim(t), '')::numeric::int; exception when others then return null; end $$;
create or replace function public.ft_try_date(t text) returns date language plpgsql immutable as $$
begin return nullif(trim(t), '')::date; exception when others then return null; end $$;

-- ── Every player, cleared or trading, with the whole profile ────────────
create or replace function public.ft_admin_players()
returns json language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public.ft_require_admin();
  return coalesce((select json_agg(row_to_json(r) order by r.status_rank, r.name) from (
    select l.id as listing_id, a.id as asset_id, a.ticker, a.name, a.known_as, a.kind, a.gender, a.club, a.league,
           a.position, a.country, a.date_of_birth, a.shirt_number, a.height_cm, a.preferred_foot, a.about,
           a.photo_url, a.photo_credit, a.photo_source,
           coalesce(a.reference_value, a.price) as reference_value, a.price, a.reference_at, a.profile_updated_at,
           case when l.claimed_by is not null then 'claimed' when a.is_active then 'trading'
                when l.is_active then 'open' else 'paused' end as status,
           case when l.claimed_by is not null then 2 when a.is_active then 3 when l.is_active then 0 else 1 end as status_rank,
           p.handle as claimed_by, l.claimed_at
      from public.assets a
      left join lateral (select * from public.listings x where x.asset_id = a.id
                          order by (x.claimed_by is not null) desc, x.is_active desc, x.created_at desc limit 1) l on true
      left join public.profiles p on p.id = l.claimed_by
     where a.is_active or l.id is not null
  ) r), '[]'::json);
end;
$$;

-- Add or update players. For a player already trading, the market sets the
-- price, so only the profile changes (club, photo, about and the rest).
-- A field left out of a row is left as it was.
create or replace function public.ft_admin_upsert_players(p_rows jsonb)
returns json language plpgsql security definer set search_path = public, pg_temp as $$
declare
  r jsonb; v_ticker text; v_name text; v_kind text; v_pos text; v_val numeric; v_gender text; v_foot text;
  v_dob date; v_num int; v_ht int; v_photo text; v_credit text; v_about text;
  v_id text; a public.assets%rowtype; l public.listings%rowtype; launched boolean; bad text;
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
    v_val    := public.ft_try_numeric(r->>'reference_value');
    v_gender := upper(nullif(trim(r->>'gender'), ''));
    v_foot   := initcap(nullif(trim(r->>'preferred_foot'), ''));
    v_dob    := public.ft_try_date(r->>'date_of_birth');
    v_num    := public.ft_try_int(r->>'shirt_number');
    v_ht     := public.ft_try_int(r->>'height_cm');
    v_photo  := nullif(trim(r->>'photo_url'), '');
    v_credit := nullif(trim(r->>'photo_credit'), '');
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
    elsif v_photo is not null and v_credit is null then bad := 'A photo needs a credit (who took it, and the licence)';
    end if;
    if bad is not null then
      skipped := skipped || jsonb_build_object('ticker', v_ticker, 'name', v_name, 'reason', bad); continue;
    end if;

    select * into a from public.assets where ticker = v_ticker limit 1;
    if found then
      select * into l from public.listings where asset_id = a.id
       order by (claimed_by is not null) desc, created_at desc limit 1;
      launched := a.is_active or (l.id is not null and l.claimed_by is not null);
      if not launched and r ? 'reference_value' and (v_val is null or v_val <= 0) then
        skipped := skipped || jsonb_build_object('ticker', v_ticker, 'name', v_name, 'reason', 'Reference price must be above 0'); continue;
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
        price          = case when launched or v_val is null then price else v_val end,
        reference_value = case when launched or v_val is null then reference_value else v_val end,
        reference_at   = case when launched or v_val is null then reference_at else now() end,
        profile_updated_at = now(), updated_at = now()
       where id = a.id;
      if launched and v_val is not null and v_val <> coalesce(a.reference_value, a.price) then
        notes := notes || jsonb_build_object('ticker', v_ticker, 'name', v_name,
                 'note', 'Already trading, so the market sets its price. Profile updated, price left as it was.');
      end if;
      if not launched and v_val is not null then
        if l.id is null then
          insert into public.listings (id, asset_id, title, is_active, fee_level1, fee_level2)
          values ('lst-' || v_ticker, a.id, 'Open to claim', true, round(500000 * v_val, 2), round(1000000 * v_val, 2))
          on conflict (id) do nothing;
        else
          update public.listings set fee_level1 = round(500000 * v_val, 2), fee_level2 = round(1000000 * v_val, 2) where id = l.id;
        end if;
      end if;
      updated := updated + 1;
    else
      if v_val is null or v_val <= 0 then
        skipped := skipped || jsonb_build_object('ticker', v_ticker, 'name', v_name, 'reason', 'Reference price must be above 0'); continue;
      end if;
      v_id := '$' || v_ticker;
      insert into public.assets (id, ticker, name, known_as, kind, gender, club, league, position, country, date_of_birth,
                                 shirt_number, height_cm, preferred_foot, about, photo_url, photo_credit, photo_source,
                                 price, reference_value, reference_at, is_active, profile_updated_at)
      values (v_id, v_ticker, v_name, nullif(trim(r->>'known_as'), ''), v_kind, coalesce(v_gender, 'M'),
              nullif(trim(r->>'club'), ''), nullif(trim(r->>'league'), ''),
              coalesce(v_pos, case when v_kind = 'COACH' then 'MGR' else 'FWD' end), nullif(trim(r->>'country'), ''),
              v_dob, v_num, v_ht, v_foot, v_about, v_photo, v_credit, nullif(trim(r->>'photo_source'), ''),
              v_val, v_val, now(), false, now());
      insert into public.listings (id, asset_id, title, is_active, fee_level1, fee_level2)
      values ('lst-' || v_ticker, v_id, 'Open to claim', true, round(500000 * v_val, 2), round(1000000 * v_val, 2))
      on conflict (id) do nothing;
      added := added + 1;
    end if;
  end loop;

  perform public.ft_admin_note('players.upsert', null,
    jsonb_build_object('added', added, 'updated', updated, 'skipped', jsonb_array_length(skipped)));
  return json_build_object('added', added, 'updated', updated, 'skipped', skipped, 'notes', notes);
end;
$$;

-- ── What the app shows: open-to-claim players with their profile ────────
create or replace function public.ft_listings()
returns json
language plpgsql stable security definer set search_path = public, pg_temp
as $$
declare uid uuid := auth.uid();
begin
  return coalesce((select json_agg(row_to_json(row)) from (
    select l.id, l.asset_id, l.title, a.name, a.known_as, a.ticker, coalesce(a.reference_value, a.price) as price,
           a.kind, a.gender, a.club, a.league, a.position, a.country, a.about, a.photo_url, a.photo_credit,
           (l.claimed_by is not null and l.claimed_by = uid) as claimed
      from public.listings l
      join public.assets a on a.id = l.asset_id
     where l.is_active and l.claimed_by is null and not a.is_active
     order by a.name
  ) row), '[]'::json);
end;
$$;

-- Profiles for every player on the market, for anyone (signed in or not):
-- the app uses these for photos, clubs and the "About the player" section.
create or replace function public.ft_player_profiles()
returns json language sql stable security definer set search_path = public, pg_temp as $$
  select coalesce(json_agg(json_build_object(
           't', ticker, 'n', name, 'known_as', known_as, 'club', club, 'lg', league, 'pos', position,
           'gender', gender, 'country', country, 'dob', date_of_birth, 'number', shirt_number,
           'height', height_cm, 'foot', preferred_foot, 'about', about,
           'photo', photo_url, 'credit', photo_credit)), '[]'::json)
    from public.assets
   where is_active or exists (select 1 from public.listings l where l.asset_id = assets.id and l.is_active);
$$;

revoke execute on function public.ft_try_numeric(text), public.ft_try_int(text), public.ft_try_date(text) from public, anon;
grant execute on function public.ft_player_profiles() to anon, authenticated;
grant execute on function public.ft_listings(), public.ft_admin_players(), public.ft_admin_upsert_players(jsonb) to authenticated;
revoke execute on function public.ft_admin_players(), public.ft_admin_upsert_players(jsonb) from public, anon;

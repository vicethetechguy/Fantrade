-- Fantrade · Optional Photo Credits for Admin Player Profiles
-- Makes photo_credit completely optional when saving player/coach photos in the admin.

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
                         public.ft_try_numeric(r->>'reference_value') * fx * 10000000);
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
        price_usd      = case when v_val is not null then round(v_val / total_shares, 8) else price_usd end,
        price          = case when v_val is not null then round(v_val / total_shares / fx, 6) else price end,
        reference_value = case when v_val is not null then round(v_val / total_shares / fx, 6) else reference_value end,
        reference_at   = case when v_val is not null then now() else reference_at end,
        profile_updated_at = now(), updated_at = now()
       where id = a.id;
      if launched and v_val is not null then
        notes := notes || jsonb_build_object('ticker', v_ticker, 'name', v_name,
                 'note', 'Trading now: the new valuation moves its share price to $' || round(v_val / 10000000, 4) || '.');
      end if;
      if not launched and v_val is not null then
        if l.id is null then
          insert into public.listings (id, asset_id, title, is_active, fee_level1, fee_level2)
          values ('lst-' || v_ticker, a.id, 'Open to claim', true, round(500000 * v_val / 10000000 / fx, 2), round(1000000 * v_val / 10000000 / fx, 2))
          on conflict (id) do nothing;
        else
          update public.listings set fee_level1 = round(500000 * v_val / 10000000 / fx, 2), fee_level2 = round(1000000 * v_val / 10000000 / fx, 2) where id = l.id;
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
              v_val, coalesce(v_src, 'Set in the admin'), current_date, round(v_val / 10000000, 8),
              round(v_val / 10000000 / fx, 6), round(v_val / 10000000 / fx, 6), now(), false, now());
      insert into public.listings (id, asset_id, title, is_active, fee_level1, fee_level2)
      values ('lst-' || v_ticker, v_id, 'Open to claim', true, round(500000 * v_val / 10000000 / fx, 2), round(1000000 * v_val / 10000000 / fx, 2))
      on conflict (id) do nothing;
      added := added + 1;
    end if;
  end loop;

  perform public.ft_admin_note('players.upsert', null,
    jsonb_build_object('added', added, 'updated', updated, 'skipped', jsonb_array_length(skipped)));
  return json_build_object('added', added, 'updated', updated, 'skipped', skipped, 'notes', notes);
end;
$$;

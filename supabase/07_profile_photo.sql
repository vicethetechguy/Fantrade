-- Fantrade · profile photo.
--
-- The photo is resized in the browser to a 256px JPEG and stored as a data
-- URL in profiles.avatar_url (well under a text column's comfort zone). The
-- row-level-security policy from 01 already lets a manager update only their
-- own profile, so the browser writes it directly — no new function, and no
-- change to ft_update_profile's signature. ft_snapshot() is redeclared here
-- (identical body plus avatar_url) so the photo travels with the snapshot on
-- the next device; run this file after 02_functions.sql.
--
-- Safe to re-run: the column uses `if not exists` and the function is
-- `create or replace`. Without this file the app still works — photos stay
-- on the device that uploaded them and the bridge only warns.

alter table public.profiles add column if not exists avatar_url text;

create or replace function public.ft_snapshot()
returns json
language plpgsql security definer set search_path = public, pg_temp stable
as $$
declare uid uuid := public.ft_require_user();
begin
  return json_build_object(
    'profile', (select row_to_json(p) from (
        select id, handle, display_name, region, home_league, onboarded, avatar_url, created_at
        from public.profiles where id = uid) p),
    'wallet', (select row_to_json(w) from (
        select balance, locked, season_earned, gbp_rate from public.wallets where user_id = uid) w),
    'holdings', coalesce((select json_agg(h) from (
        select h.asset_id, h.shares, h.locked, h.avg_cost, h.slot, a.name, a.kind, a.club, a.price
        from public.holdings h join public.assets a on a.id = h.asset_id
        where h.user_id = uid and h.shares > 0 order by h.shares * a.price desc) h), '[]'::json),
    'transactions', coalesce((select json_agg(t) from (
        select type, asset_id, label, shares, price, total, fee, created_at
        from public.transactions where user_id = uid
        order by created_at desc, id desc limit 60) t), '[]'::json),
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
$$;

grant execute on function public.ft_snapshot() to authenticated;
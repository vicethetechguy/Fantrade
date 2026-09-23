-- Fantrade · notifications.
--
-- The bell on every page counts these rows. They are application notices —
-- trade fills, wallet movements, club and account events — and deliberately
-- sit outside the whitepaper's seven protocol tables: no money and no
-- protocol rule reads them. Row-level security keeps each manager's list
-- their own, like everything else here.
--
-- `id` is made by the browser that raised the notice, so the row the phone
-- added is recognised — not duplicated — when the next device pulls the list.

create table if not exists public.notifications (
  id         text primary key,
  user_id    uuid not null references auth.users(id) on delete cascade,
  kind       text not null default 'system',
  icon       text not null default 'bell',
  title      text not null,
  msg        text not null default '',
  amt        text not null default '',
  tone       text not null default '',
  read_at    timestamptz,
  created_at timestamptz not null default now(),
  constraint notifications_kind_check check (kind in ('settle','order','club','system'))
);

create index if not exists notifications_user_idx
  on public.notifications (user_id, created_at desc);

alter table public.notifications enable row level security;

drop policy if exists "notifications_select_own" on public.notifications;
create policy "notifications_select_own" on public.notifications
  for select using (auth.uid() = user_id);

drop policy if exists "notifications_insert_own" on public.notifications;
create policy "notifications_insert_own" on public.notifications
  for insert with check (auth.uid() = user_id);

drop policy if exists "notifications_update_own" on public.notifications;
create policy "notifications_update_own" on public.notifications
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "notifications_delete_own" on public.notifications;
create policy "notifications_delete_own" on public.notifications
  for delete using (auth.uid() = user_id);

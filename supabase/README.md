# Fantrade · Supabase

The app talks to Supabase straight from the browser. There is no server of our
own in between, so the database itself has to be the thing that says no:
row-level security keeps every table private, and every action that moves money
or shares goes through a SQL function that starts from the signed-in user and
re-checks the price, the balance and the share count.

Project: `https://ajjwodnjcnmkzguospay.supabase.co`

## Run this once

In the Supabase dashboard, open **SQL Editor** and run these four files in
order, each in its own query:

| # | File | What it does |
|---|------|--------------|
| 1 | `01_schema.sql` | Tables, row-level security, and the trigger that gives every new account a profile, a wallet and 50,000 $FTR |
| 2 | `02_functions.sql` | The money functions (buy, sell, swap, convert, transfer, withdraw, profile) and who is allowed to call them |
| 3 | `03_seed_assets.sql` | The 18 players and coaches the exchange lists |
| 4 | `04_fanplay_clubs.sql` | Dream Clubs, FanPlay entries and the leaderboard |

They are safe to re-run: the tables use `if not exists`, the functions are
`create or replace`, and the seed upserts on the asset id. Re-run them in
order, though, and re-run all four rather than one on its own — file 2 resets
who may call what, and file 4 hands those rights back out.

Check it worked: **Table Editor** should show `profiles`, `wallets`, `assets`,
`holdings`, `transactions`, `payout_accounts`, `clubs` and `fanplay_entries`,
with 18 rows in `assets` and a green **RLS enabled** badge on all eight.

## Then turn on auth

**Authentication → Providers → Email**: enabled.

**Authentication → URL Configuration**:

- *Site URL* — where the app is served from. For a local run that is
  `http://localhost:8000` (whatever port you use); for the deployed build, the
  real domain.
- *Redirect URLs* — add the same address with `/dashboard.html` on the end.

**Confirm email** (same Providers screen) decides what happens right after
someone signs up. Leave it **on** for anything public. While you are testing,
turning it **off** lets a new account go straight into onboarding instead of
waiting on an inbox — the sign-up page handles both, and says which one
happened.

## About the key in the page

`public/fantrade-supabase.js` carries the anon key in plain sight. That is how
it is meant to be: it is the publishable key, it identifies the project and
nothing else, and on its own it can read nothing private. The protection is the
row-level security in `01_schema.sql` — no table has an insert, update or
delete policy at all, so the browser can only ever change data by calling one
of the functions in `02_functions.sql`, each of which begins by asking the
database who is signed in.

The **service role** key is the one that must never appear in this repo or in
any page. Nothing here needs it.

## What lives in the database, and what does not

In the database now: accounts and profiles, the $FTR wallet, holdings and the
slot each one lines up in, the transaction history, saved payout details (only
the last four digits of an account number are ever stored), the asset
catalogue, Dream Clubs and live FanPlay entries.

Still in the browser's own storage: notifications and the preference toggles.

**Settlement is deliberately not in here.** Paying out a FanPlay entry decides
who gets money, so a function the browser can call must never be able to do it.
When matchdays start settling, that belongs in a scheduled job running as the
service role and reading the result from outside. `04_fanplay_clubs.sql` grants
nothing that could stand in for one.

Clubs are readable only by their own manager, so the leaderboard cannot work by
querying the table. It goes through `ft_leaderboard()`, which returns a fixed
public set of columns — club name, manager handle, formation, season FP, club
value — and no balance, holding or email. Until real clubs fill the board, the
leaderboard page shows them above a clearly labelled sample field.

## When the database cannot be reached

The pages never wait on the network. Every action applies to the local state
first and mirrors to Supabase straight afterwards, so an offline browser, a
signed-out visitor, or the site opened as a plain file all still work — the app
runs from this browser alone and says so. When a call is refused, the answer
from the database is taken as the truth: the local state is re-synced from it
and the reason is shown, so what you see is what the database actually holds.

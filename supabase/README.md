# Fantrade · Supabase

The app talks to Supabase straight from the browser. There is no server of our
own in between, so the database itself has to be the thing that says no:
row-level security keeps every table private, and every action that moves money
or shares goes through a SQL function that starts from the signed-in user and
re-checks the price, the balance and the share count.

Project: `https://ajjwodnjcnmkzguospay.supabase.co`

## Run this once

In the Supabase dashboard, open **SQL Editor** and run these seven files in
order, each in its own query:

| # | File | What it does |
|---|------|--------------|
| 1 | `01_schema.sql` | Tables, row-level security, and the trigger that gives every new account a profile, a wallet and a starting balance (file 11 makes this 1,000 $FTR from the treasury) |
| 2 | `02_functions.sql` | The money functions (buy, sell, swap, convert, transfer, withdraw, profile) and who is allowed to call them |
| 3 | `03_seed_assets.sql` | The 18 players and coaches the exchange lists, each with its immutable F-ticker and its reference value |
| 4 | `04_fanplay_clubs.sql` | Dream Clubs, FanPlay entries and the leaderboard |
| 5 | `05_notifications.sql` | The notifications table behind the bell — every fill, wallet move, club and account notice, per manager under row-level security |
| 6 | `06_listings.sql` | Admin-listed player drops and one-claim-per-manager claiming — listings are added from the Table Editor, claims grant shares through `ft_claim_listing()` |
| 7 | `07_profile_photo.sql` | `profiles.avatar_url` and an `ft_snapshot()` that carries it, so a profile photo uploaded on one device shows on the next |
| 8 | `08_claim_by_value.sql` | Cleared players that are not trading yet, and first-come claiming: the claimer pays for 5% or 10% of the shares at the reference value, and the player goes live for everyone else |
| 9 | `09_admin.sql` | The admin at /admin: the admins list, an activity log, account suspension, and the `ft_admin_*` functions it calls, each refusing anyone not on the list. Re-run it after re-running `02_functions.sql` |
| 10 | `10_player_profiles.sql` | Player profiles kept in the admin (known-as name, men's or women's game, country, date of birth, shirt number, height, foot, about, photo and its credit), the public `player-photos` Storage bucket that only admins can write to, and `ft_player_profiles()` that the app reads |
| 11 | `11_ftr_economy.sql` | The $FTR economy: a 10,000,000 cap (wallets + treasury + burned), a market price in dollars (starts at $2, set in the admin), real-world player valuations in dollars (a share = valuation ÷ 10,000,000, paid in $FTR at the live price), and every buy, sell, swap, top-up, withdrawal, claim and welcome grant reworked to that maths. Moves existing balances across once, keeping their dollar value |
| 12 | `12_dollars.sql` | Dollars everywhere: top-ups are bought in dollars at the live $FTR price (`ft_convert_usd`), withdrawals default to a dollar account, the wallet's rate is $FTR per $1, and the pound rate is gone |

They are safe to re-run: the tables use `if not exists`, the functions are
`create or replace`, and the seed upserts on the asset (and listing) id. Re-run them in
order, though, and re-run all seven rather than one on its own — file 2 resets
who may call what, file 4 hands those rights back out, and file 7 restates
`ft_snapshot()` after file 2.

Check it worked: **Table Editor** should show `profiles`, `wallets`, `assets`,
`holdings`, `transactions`, `payout_accounts`, `clubs`, `fanplay_entries`,
`notifications`, `listings` and `claims`, with 18 rows in `assets` (every one
carrying a `ticker`), 2 rows in `listings`, and a green **RLS enabled** badge
on all eleven.

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
the last four digits of an account number are ever stored), the asset catalogue
with each row's immutable F-ticker and reference value, Dream Clubs and live
FanPlay entries.

Still in the browser's own storage: notifications and the preference toggles.

**Settlement is deliberately not in here.** Paying out a FanPlay entry decides
who gets money, so a function the browser can call must never be able to do it.
When matchdays start settling, that belongs in a scheduled job running as the
service role and reading the result from outside. `04_fanplay_clubs.sql` grants
nothing that could stand in for one.

Clubs are readable only by their own manager, so the leaderboard cannot work by
querying the table. It goes through `ft_leaderboard()`, which returns a fixed
public set of columns — club name, manager handle, formation, season FP, club
value — and no balance, holding or email. The board lists only clubs that
really exist; until managers build theirs, the page says the table is empty
rather than padding it with invented managers.

## Where the white paper's model lives in the schema

The four files follow the white paper, so the parts of it that are data rules
are enforced here rather than in the pages:

| White paper | In the database |
|---|---|
| Activity Assets and the two types (4) | `assets.kind` — `PLAYER` / `COACH`, the paper's PLAYER_ACTIVITY and COACH_ACTIVITY in short form |
| The F-ticker, immutable after issuance (5) | `assets.ticker`, shaped `^F[A-Z0-9]{1,7}$` and unique, with `ft_ticker_is_fixed()` refusing to change one once it is set |
| Ten million shares per asset (4.1) | `assets_shares_fixed` on `total_shares` |
| Reference Valuation, which is not the trading price (6) | `assets.reference_value` and `reference_at`, seeded with the opening figure; `assets.price` stays the price a trade executes at |
| Listing fees and lister economics (7, 8) | the ledger types `LIST`, `BURN` and `FEE_SHARE` are reserved in `transactions_type_check` |
| Fan Points converted at 1,000 FP = 1 $FTR (14.3) | `ft_fp_rate()` |
| The FanPlay lifecycle (14.6) | `fanplay_entries_status_check` holds all nine states; the browser only ever writes ACTIVE, and a cancel lands as VOID |
| Dream Clubs built from real holdings, with a team boost (19) | `holdings.slot`, `clubs.season_fp` and `clubs.boost` |

Listing and claiming (7–9, phase 6) exists only in the simplified form the home
page needs: an admin lists a row in `listings` and each manager takes it once
through `ft_claim_listing()`, which grants the shares immediately at the
catalogue price — with no listing fee, no price paid to the lister and no
vesting, because the pages do not charge for those yet. What is still
deliberately not here, because the pages do not have them and the paper puts
them at a later phase: the $FTR allocation, presale and airdrop (11–13, phase
7), and the order book with resting orders, matching and fills (15.1–15.3,
phase 2). Trades today execute at the catalogue price, which
is what `assets.price` holds until that engine arrives.

Nothing here invents a market either. The seed sets a reference value and
leaves `prev_close`, `day_change`, `day_high` and `day_low` empty, because 15.4
wants those to come from recorded executions; the pages fall back to the
reference value until the first real trade exists. The same rule is what keeps
the pages free of generated charts, quoted volumes and sample manager tables.

## When the database cannot be reached

The pages never wait on the network. Every action applies to the local state
first and mirrors to Supabase straight afterwards, so an offline browser, a
signed-out visitor, or the site opened as a plain file all still work — the app
runs from this browser alone and says so. When a call is refused, the answer
from the database is taken as the truth: the local state is re-synced from it
and the reason is shown, so what you see is what the database actually holds.

-- Fantrade · the $FTR economy. Run after 10_player_profiles.sql. Safe to run again.
--
-- The rules this file puts into the database:
--   · $FTR has a fixed maximum supply of 10,000,000. Every $FTR is in a
--     manager's wallet, in Fantrade's treasury, or burned. Nothing mints more:
--     anything paid out to a manager (a welcome grant, a sale, a top-up) comes
--     out of the treasury, and is refused if the treasury cannot cover it.
--   · $FTR has a dollar price set by the market. Until the $FTR exchange is
--     live, admins set it (ft_admin_set_market); it starts at $2.00.
--   · Every player and coach has 10,000,000 fixed Activity Shares.
--   · A player's valuation is in real dollars. One share is worth
--     valuation ÷ 10,000,000 dollars, and costs that many dollars' worth of
--     $FTR at the current $FTR price. So when $FTR rises, every share costs
--     fewer $FTR, and the other way round.
--   · Claiming 5% (500,000 shares) or 10% (1,000,000) costs those shares' dollar
--     value in $FTR. 2% of the payment is burned for good; the rest goes to the
--     treasury.
--
--   share $     = valuation_usd / total_shares
--   share $FTR  = share $ / $FTR price
--   claim $FTR  = shares claimed × share $FTR
--   treasury    = 10,000,000 − burned − (every wallet's balance + locked)

-- ── The $FTR market, one row ────────────────────────────────────────────
create table if not exists public.ftr_market (
  id            boolean primary key default true check (id),
  price_usd     numeric(18,6) not null default 2.00 check (price_usd > 0),
  max_supply    numeric(20,2) not null default 10000000,
  burned        numeric(20,2) not null default 0 check (burned >= 0),
  gbp_usd       numeric(10,4) not null default 1.3372 check (gbp_usd > 0),   -- pounds to dollars, for top-ups
  welcome_grant numeric(20,2) not null default 1000 check (welcome_grant >= 0),
  migrated_v2   boolean not null default false,
  updated_at    timestamptz not null default now()
);
insert into public.ftr_market (id) values (true) on conflict (id) do nothing;
alter table public.ftr_market enable row level security;   -- read through ft_market()

-- Share prices now run to fractions of a cent in $FTR, so they need the room.
alter table public.assets
  alter column price type numeric(18,6),
  alter column reference_value type numeric(18,6),
  alter column prev_close type numeric(18,6),
  alter column day_high type numeric(18,6),
  alter column day_low type numeric(18,6);
alter table public.holdings alter column avg_cost type numeric(18,6);
alter table public.transactions alter column price type numeric(18,6);

alter table public.assets
  add column if not exists valuation_usd    numeric(16,2) check (valuation_usd > 0),
  add column if not exists valuation_source text,
  add column if not exists valuation_at     date,
  add column if not exists price_usd        numeric(18,8) check (price_usd > 0);

-- ── Reading the market ──────────────────────────────────────────────────
create or replace function public.ft_ftr_usd()
returns numeric language sql stable security definer set search_path = public, pg_temp as $$
  select price_usd from public.ftr_market where id;
$$;

-- $FTR the treasury holds: whatever is neither burned nor in a wallet.
create or replace function public.ft_treasury()
returns numeric language sql stable security definer set search_path = public, pg_temp as $$
  select m.max_supply - m.burned - coalesce((select sum(balance + locked) from public.wallets), 0)
    from public.ftr_market m where m.id;
$$;

-- Pay out of the treasury, or refuse. The row lock queues concurrent payouts.
create or replace function public.ft_draw_treasury(p_amount numeric)
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare left_over numeric;
begin
  if coalesce(p_amount, 0) <= 0 then return; end if;
  perform 1 from public.ftr_market where id for update;
  left_over := public.ft_treasury();
  if left_over < p_amount then
    raise exception 'Fantrade''s $FTR treasury cannot cover % $FTR right now (the supply is capped at 10,000,000)', p_amount
      using errcode = 'P0001';
  end if;
end;
$$;

-- The price of one share in $FTR, at today's $FTR price.
create or replace function public.ft_share_ftr(p_asset text)
returns numeric language sql stable security definer set search_path = public, pg_temp as $$
  select round(coalesce(a.price_usd, a.valuation_usd / a.total_shares) / public.ft_ftr_usd(), 6)
    from public.assets a where a.id = p_asset;
$$;

-- Keep the $FTR prices on every asset, and each wallet's pound rate, in step
-- with the dollar prices. Run whenever the $FTR price or a valuation moves.
create or replace function public.ft_reprice()
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare fx numeric := public.ft_ftr_usd(); gbp numeric;
begin
  select gbp_usd into gbp from public.ftr_market where id;
  update public.assets
     set price = round(coalesce(price_usd, valuation_usd / total_shares) / fx, 6),
         reference_value = round(coalesce(valuation_usd / total_shares, price_usd) / fx, 6),
         updated_at = now()
   where coalesce(price_usd, valuation_usd) is not null;
  update public.listings l
     set fee_level1 = round(500000 * a.valuation_usd / a.total_shares / fx, 2),
         fee_level2 = round(1000000 * a.valuation_usd / a.total_shares / fx, 2)
    from public.assets a
   where a.id = l.asset_id and a.valuation_usd is not null and l.claimed_by is null;
  update public.wallets set gbp_rate = round(gbp / fx, 4);
end;
$$;

-- Anyone may read the market: the app shows it on every price.
create or replace function public.ft_market()
returns json language sql stable security definer set search_path = public, pg_temp as $$
  select json_build_object(
    'ftr_usd', m.price_usd, 'gbp_usd', m.gbp_usd, 'max_supply', m.max_supply, 'burned', m.burned,
    'circulating', coalesce((select sum(balance + locked) from public.wallets), 0),
    'treasury', public.ft_treasury(), 'welcome_grant', m.welcome_grant, 'updated_at', m.updated_at)
  from public.ftr_market m where m.id;
$$;

-- ── Real-world valuations (Sept 2026) ───────────────────────────────────
-- Men's values are Transfermarkt's as reported between July and September
-- 2026; women's are Soccerdonna's (Transfermarkt's women's site), several of
-- which have not been updated for a while. Euros were converted at
-- EUR/USD 1.1464 (US Federal Reserve, 18 Sep 2026). Coaches have no market
-- value, so theirs are Fantrade estimates. Admins can change any of them.
-- Only players without a valuation yet are filled, so re-running this file
-- never overwrites a value set in the admin.
drop table if exists ft_seed_vals;
create temporary table ft_seed_vals (ticker text primary key, usd numeric, source text);
insert into ft_seed_vals (ticker, usd, source) values
  ('FSAKA', 126104000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FHLND', 252208000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FKM7', 229280000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FVJR', 160496000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FBEL', 183424000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FPLMR', 114640000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FYAML', 252208000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FMUS', 114640000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FWRTZ', 114640000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FRODR', 57320000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FFODN', 91712000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FPEDR', 171960000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FSALI', 114640000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FBRN', 40124000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FJACK', 45856000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FCR7', 11464000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FLM10', 17196000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FKANE', 68784000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FRICE', 137568000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FVVD', 32099200.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FOSIM', 85980000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FSALH', 25220800.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FLOOK', 45856000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FCHUK', 22928000.00, 'Transfermarkt, as reported Jul–Sep 2026'),
  ('FAITN', 1834240.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FPUTL', 1375680.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FRUSS', 1490320.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FLJMS', 802480.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FKERR', 573200.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FWILM', 859800.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FEARP', 137568.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FSHAW', 831140.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FPAJR', 458560.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FRODM', 401240.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FKELY', 1031760.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FAJBD', 487220.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FALOZ', 91712.00, 'Soccerdonna (Transfermarkt), latest published'),
  ('FARTA', 22050000.00, 'Fantrade estimate: coaches have no transfer-market value'),
  ('FPEP', 29600000.00, 'Fantrade estimate: coaches have no transfer-market value'),
  ('FMARS', 18300000.00, 'Fantrade estimate: coaches have no transfer-market value'),
  ('FWIEG', 26800000.00, 'Fantrade estimate: coaches have no transfer-market value');

-- ── One-time move from the old economy (1 $FTR = $0.10, no cap) ─────────
-- Balances keep their dollar value: at $2 instead of $0.10, each old $FTR
-- becomes 0.05 $FTR. Holdings keep their shares and their profit or loss in
-- percent; only the $FTR cost basis is re-expressed at the new prices.
do $$
declare done boolean;
begin
  select migrated_v2 into done from public.ftr_market where id;
  if done then return; end if;

  update public.holdings h
     set avg_cost = round(h.avg_cost * (v.usd / a.total_shares / public.ft_ftr_usd()) / nullif(a.price, 0), 6)
    from public.assets a join ft_seed_vals v on v.ticker = a.ticker
   where a.id = h.asset_id and a.price > 0;

  update public.wallets set balance = round(balance * 0.05, 2), locked = round(locked * 0.05, 2),
                            season_earned = round(season_earned * 0.05, 2);
  update public.fanplay_entries set stake = round(stake * 0.05, 2) where stake > 0;

  -- Clubs that changed in the 2026 window.
    update public.assets set club = 'Liverpool', league = 'Premier League' where ticker = 'FWRTZ';
    update public.assets set club = 'Barcelona', league = 'La Liga' where ticker = 'FRODR';
    update public.assets set club = 'Aston Villa', league = 'Premier League' where ticker = 'FJACK';
  -- Anything not in the list above (e.g. a player added in the admin) gets the
  -- dollar value its old $FTR price implied, and its cost basis moves with it.
  update public.holdings h set avg_cost = round(h.avg_cost * 0.05, 6)
    from public.assets a
   where a.id = h.asset_id and a.valuation_usd is null
     and not exists (select 1 from ft_seed_vals v where v.ticker = a.ticker);
  update public.assets a
     set valuation_usd = round(a.price * 0.10 * a.total_shares, 2),
         valuation_source = 'Converted from its old $FTR price; set a real valuation in the admin',
         valuation_at = current_date
   where a.valuation_usd is null and not exists (select 1 from ft_seed_vals v where v.ticker = a.ticker);
  update public.ftr_market set migrated_v2 = true, updated_at = now() where id;
end $$;

update public.assets a
   set valuation_usd = v.usd, valuation_source = v.source, valuation_at = date '2026-09-24'
  from ft_seed_vals v
 where v.ticker = a.ticker and a.valuation_usd is null;

-- Until the share order book is live, a share trades at its valuation.
update public.assets set price_usd = round(valuation_usd / total_shares, 8)
 where price_usd is null and valuation_usd is not null;
select public.ft_reprice();

-- New players' welcome grant: out of the treasury, and only while it lasts.
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
  grant_amt numeric(20,2);
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

  perform 1 from public.ftr_market where id for update;
  select least(m.welcome_grant, greatest(0, public.ft_treasury())) into grant_amt from public.ftr_market m where m.id;
  insert into public.wallets (user_id, balance, gbp_rate)
  values (new.id, grant_amt, (select round(gbp_usd / price_usd, 4) from public.ftr_market where id));

  if grant_amt > 0 then
    insert into public.transactions (user_id, type, label, total, balance_after)
    values (new.id, 'GRANT', 'Welcome balance', grant_amt, grant_amt);
  end if;
  return new;
end;
$$;

-- ── Buy: $FTR goes from the manager to the treasury ─────────────────────
create or replace function public.ft_buy_shares(p_asset text, p_shares bigint)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  a   public.assets%rowtype;
  px numeric(18,6); gross numeric(20,2); fee numeric(20,2); total numeric(20,2);
  bal numeric(20,2); new_held bigint; new_avg numeric(18,6);
begin
  if p_shares is null or p_shares <= 0 then raise exception 'Enter a whole number of shares, one or more'; end if;
  select * into a from public.assets where id = p_asset and is_active for update;
  if not found then raise exception 'That asset is not trading'; end if;
  if a.circulating + p_shares > a.total_shares then raise exception 'Only % shares of % are left to buy', a.total_shares - a.circulating, a.name; end if;

  px    := public.ft_share_ftr(p_asset);
  gross := greatest(0.01, round(px * p_shares, 2));
  fee   := round(gross * public.ft_fee_rate('TRADE'), 2);
  total := gross + fee;

  update public.wallets set balance = balance - total, updated_at = now()
   where user_id = uid and balance >= total
   returning balance into bal;
  if bal is null then raise exception 'Not enough $FTR. This costs % $FTR including the fee.', total; end if;

  insert into public.holdings (user_id, asset_id, shares, avg_cost)
  values (uid, p_asset, p_shares, px)
  on conflict (user_id, asset_id) do update
    set avg_cost = round(((public.holdings.shares * public.holdings.avg_cost) + (p_shares * px))
                         / (public.holdings.shares + p_shares), 6),
        shares = public.holdings.shares + p_shares,
        updated_at = now()
  returning public.holdings.shares, public.holdings.avg_cost into new_held, new_avg;

  update public.assets set circulating = circulating + p_shares, price = px, updated_at = now() where id = p_asset;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'BUY', p_asset, 'Bought shares', p_shares, px, total, fee, bal);

  return json_build_object('asset', p_asset, 'shares', p_shares, 'price', px, 'price_usd', a.price_usd,
                           'ftr_usd', public.ft_ftr_usd(), 'fee', fee, 'total', total,
                           'total_usd', round(total * public.ft_ftr_usd(), 2), 'balance', bal, 'held', new_held, 'avg_cost', new_avg);
end;
$$;

-- ── Sell: the treasury buys the shares back, if it can cover them ───────
create or replace function public.ft_sell_shares(p_asset text, p_shares bigint)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  a public.assets%rowtype;
  h public.holdings%rowtype;
  px numeric(18,6); gross numeric(20,2); fee numeric(20,2); net numeric(20,2); bal numeric(20,2);
begin
  if p_shares is null or p_shares <= 0 then raise exception 'Enter a whole number of shares, one or more'; end if;
  select * into a from public.assets where id = p_asset for update;
  if not found then raise exception 'That asset is not listed'; end if;

  select * into h from public.holdings where user_id = uid and asset_id = p_asset for update;
  if not found or (h.shares - h.locked) < p_shares then
    raise exception 'You have % shares available to sell', coalesce(h.shares - h.locked, 0);
  end if;

  px    := public.ft_share_ftr(p_asset);
  gross := round(px * p_shares, 2);
  fee   := round(gross * public.ft_fee_rate('TRADE'), 2);
  net   := gross - fee;
  perform public.ft_draw_treasury(net);

  update public.holdings set shares = shares - p_shares, updated_at = now()
   where user_id = uid and asset_id = p_asset;
  update public.assets set circulating = greatest(0, circulating - p_shares), updated_at = now() where id = p_asset;
  update public.wallets set balance = balance + net, updated_at = now() where user_id = uid returning balance into bal;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'SELL', p_asset, 'Sold shares', p_shares, px, net, fee, bal);

  return json_build_object('asset', p_asset, 'shares', p_shares, 'price', px, 'fee', fee, 'total', net,
                           'total_usd', round(net * public.ft_ftr_usd(), 2), 'balance', bal);
end;
$$;

-- ── Swap one player's shares into another's, at their dollar values ─────
create or replace function public.ft_swap_shares(p_from text, p_to text, p_shares bigint)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  af public.assets%rowtype; at2 public.assets%rowtype;
  h public.holdings%rowtype;
  pf numeric(18,6); pt numeric(18,6);
  gross numeric(20,2); fee numeric(20,2); net numeric(20,2);
  got bigint; spend numeric(20,2); change numeric(20,2); bal numeric(20,2);
begin
  if p_from = p_to then raise exception 'Choose two different assets to swap between'; end if;
  if p_shares is null or p_shares <= 0 then raise exception 'Enter a whole number of shares, one or more'; end if;

  select * into af from public.assets where id = p_from for update;
  if not found then raise exception 'That asset is not listed'; end if;
  select * into at2 from public.assets where id = p_to and is_active for update;
  if not found then raise exception 'That asset is not trading'; end if;

  select * into h from public.holdings where user_id = uid and asset_id = p_from for update;
  if not found or (h.shares - h.locked) < p_shares then
    raise exception 'You have % shares available to swap', coalesce(h.shares - h.locked, 0);
  end if;

  pf := public.ft_share_ftr(p_from); pt := public.ft_share_ftr(p_to);
  gross := round(pf * p_shares, 2);
  fee   := round(gross * public.ft_fee_rate('SWAP'), 2);
  net   := gross - fee;
  got   := floor(net / pt);
  if got < 1 then raise exception 'That is not enough to buy a whole share of %', at2.name; end if;
  if at2.circulating + got > at2.total_shares then raise exception 'Only % shares of % are left', at2.total_shares - at2.circulating, at2.name; end if;
  spend  := round(got * pt, 2);
  change := greatest(0, net - spend);
  perform public.ft_draw_treasury(change);

  update public.holdings set shares = shares - p_shares, updated_at = now()
   where user_id = uid and asset_id = p_from;
  update public.assets set circulating = greatest(0, circulating - p_shares), updated_at = now() where id = p_from;

  insert into public.holdings (user_id, asset_id, shares, avg_cost)
  values (uid, p_to, got, pt)
  on conflict (user_id, asset_id) do update
    set avg_cost = round(((public.holdings.shares * public.holdings.avg_cost) + (got * pt))
                         / (public.holdings.shares + got), 6),
        shares = public.holdings.shares + got,
        updated_at = now();
  update public.assets set circulating = circulating + got, updated_at = now() where id = p_to;

  update public.wallets set balance = balance + change, updated_at = now() where user_id = uid returning balance into bal;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'SWAP', p_to, af.ticker || ' → ' || at2.ticker, got, pt, spend, fee, bal);

  return json_build_object('from', p_from, 'to', p_to, 'spent', p_shares, 'received', got,
                           'fee', fee, 'change', change, 'balance', bal);
end;
$$;

-- ── Top up: buy $FTR from the treasury with pounds, at the dollar price ──
create or replace function public.ft_convert_gbp(p_gbp numeric)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  m public.ftr_market%rowtype; usd numeric(20,2); gross numeric(20,2); fee numeric(20,2); net numeric(20,2); bal numeric(20,2);
begin
  if p_gbp is null or p_gbp <= 0 then raise exception 'Enter an amount greater than zero'; end if;
  if p_gbp > 100000 then raise exception 'Top-ups are capped at £100,000 at a time'; end if;
  select * into m from public.ftr_market where id;

  usd   := round(p_gbp * m.gbp_usd, 2);
  gross := round(usd / m.price_usd, 2);
  fee   := round(gross * public.ft_fee_rate('CONVERT'), 2);
  net   := gross - fee;
  perform public.ft_draw_treasury(net);

  update public.wallets set balance = balance + net, gbp_rate = round(m.gbp_usd / m.price_usd, 4), updated_at = now()
   where user_id = uid returning balance into bal;
  if bal is null then raise exception 'No wallet for this account'; end if;

  insert into public.transactions (user_id, type, label, price, total, fee, balance_after)
  values (uid, 'CONVERT', 'Added funds (£' || trim(to_char(p_gbp, 'FM999999990.00')) || ' at $' || trim(to_char(m.price_usd, 'FM9990.00')) || ')',
          m.price_usd, net, fee, bal);

  return json_build_object('received', net, 'fee', fee, 'balance', bal, 'rate', round(m.gbp_usd / m.price_usd, 4),
                           'ftr_usd', m.price_usd, 'usd', usd);
end;
$$;

-- ── Withdraw: $FTR goes back to the treasury; the payout is its dollar value ─
create or replace function public.ft_withdraw_to_bank(
  p_amount numeric, p_currency text, p_holder text, p_bank text, p_account text, p_save boolean default true)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  amount numeric(20,2); fee numeric(20,2); total numeric(20,2);
  bal numeric(20,2); digits text; last4 text; fx numeric := public.ft_ftr_usd();
begin
  amount := round(p_amount, 2);
  if amount is null or amount <= 0 then raise exception 'Enter an amount greater than zero'; end if;
  if coalesce(trim(p_holder), '') = '' then raise exception 'Enter the account holder name'; end if;
  if coalesce(trim(p_bank), '') = '' then raise exception 'Enter your bank name'; end if;

  digits := regexp_replace(coalesce(p_account, ''), '[^A-Za-z0-9]', '', 'g');
  if length(digits) < 6 then raise exception 'Enter a valid account number'; end if;
  last4 := right(digits, 4);

  -- 0.5%, at least $5 worth of $FTR.
  fee   := greatest(round(5 / fx, 2), round(amount * public.ft_fee_rate('WITHDRAW'), 2));
  total := amount + fee;

  update public.wallets set balance = balance - total, updated_at = now()
   where user_id = uid and balance >= total returning balance into bal;
  if bal is null then raise exception 'Your balance cannot cover this amount plus the % $FTR fee', fee; end if;

  if p_save then
    insert into public.payout_accounts (user_id, currency, holder, bank, account_last4)
    values (uid, coalesce(p_currency, 'GBP'), trim(p_holder), trim(p_bank), last4)
    on conflict (user_id) do update set currency = excluded.currency, holder = excluded.holder,
      bank = excluded.bank, account_last4 = excluded.account_last4, updated_at = now();
  end if;

  insert into public.transactions (user_id, type, label, price, total, fee, balance_after)
  values (uid, 'WITHDRAW', trim(p_bank) || ' ••' || last4 || ' (' || coalesce(p_currency, 'GBP') || ')', fx, total, fee, bal);

  return json_build_object('amount', amount, 'usd', round(amount * fx, 2), 'fee', fee, 'total', total, 'balance', bal,
                           'destination', trim(p_bank) || ' ••' || last4);
end;
$$;

-- ── Claim a cleared player: pay the dollar value of the shares in $FTR ───
create or replace function public.ft_claim_listing(
  p_listing text,
  p_level int default 1,
  p_vesting_years int default 1
)
returns json
language plpgsql security definer set search_path = public, pg_temp
as $$
declare
  uid uuid := public.ft_require_user();
  l   public.listings%rowtype;
  a   public.assets%rowtype;
  w   public.wallets%rowtype;
  fx numeric := public.ft_ftr_usd();
  v_share_usd numeric; v_price numeric(18,6); v_shares bigint;
  v_cost numeric(20,2); v_burn numeric(20,2); v_daily bigint; v_until timestamptz;
begin
  if p_listing is null or p_listing = '' then raise exception 'Pick a player to claim'; end if;
  if p_level not in (1, 2) then p_level := 1; end if;
  if p_vesting_years not in (1, 2, 3) then p_vesting_years := 1; end if;

  select * into l from public.listings where id = p_listing for update;
  if not found then raise exception 'That player is not open to claim'; end if;
  if l.claimed_by is not null then
    raise exception 'Someone has already claimed this player. You can buy their shares on the exchange';
  end if;
  if not l.is_active then raise exception 'That player is not open to claim'; end if;

  select * into a from public.assets where id = l.asset_id for update;
  if not found then raise exception 'That player is not in the catalogue'; end if;
  if a.is_active then raise exception 'This player is already trading. You can buy their shares on the exchange'; end if;
  if a.valuation_usd is null then raise exception 'This player has no valuation yet, so they cannot be claimed'; end if;

  v_share_usd := a.valuation_usd / a.total_shares;
  v_price  := round(v_share_usd / fx, 6);
  v_shares := case when p_level = 2 then 1000000 else 500000 end;
  v_cost   := round(v_shares * v_share_usd / fx, 2);
  v_burn   := round(v_cost * 0.02, 2);
  v_daily  := v_shares / 100;
  v_until  := now() + make_interval(years => p_vesting_years);

  select * into w from public.wallets where user_id = uid for update;
  if not found or w.balance < v_cost then
    raise exception 'You need % more $FTR to claim % percent of % (% $FTR at $% a $FTR)',
      v_cost - coalesce(w.balance, 0), v_shares / 100000, a.name, v_cost, fx;
  end if;

  update public.wallets set balance = balance - v_cost, updated_at = now() where user_id = uid;
  -- 2% leaves the supply for good; the rest is now the treasury's.
  update public.ftr_market set burned = burned + v_burn, updated_at = now() where id;

  update public.listings set claimed_by = uid, claimed_at = now(), is_active = false where id = l.id;

  insert into public.claims (listing_id, user_id, claim_level, shares, vesting_years, fee_paid, fee_burned, daily_limit, vesting_until)
  values (l.id, uid, p_level, v_shares, p_vesting_years, v_cost, v_burn, v_daily, v_until);

  insert into public.holdings (user_id, asset_id, shares, avg_cost)
  values (uid, a.id, v_shares, v_price)
  on conflict (user_id, asset_id) do update
    set shares = public.holdings.shares + excluded.shares, avg_cost = excluded.avg_cost, updated_at = now();

  -- Live from here: the claim and Fantrade's 1,000,000 are out of the float.
  update public.assets
     set is_active = true, circulating = least(total_shares, v_shares + 1000000),
         price_usd = round(v_share_usd, 8), price = v_price, updated_at = now()
   where id = a.id;

  insert into public.transactions (user_id, type, asset_id, label, shares, price, total, fee, balance_after)
  values (uid, 'LIST', a.id,
          'Claimed ' || (v_shares / 100000) || '% of ' || a.name || ' (' || p_vesting_years || 'y vesting)',
          v_shares, v_price, v_cost, v_burn, w.balance - v_cost);

  return json_build_object(
    'listing', l.id, 'asset', a.id, 'name', a.name, 'ticker', a.ticker,
    'shares', v_shares, 'level', p_level, 'vesting_years', p_vesting_years,
    'price', v_price, 'share_usd', round(v_share_usd, 6), 'ftr_usd', fx,
    'cost', v_cost, 'cost_usd', round(v_cost * fx, 2), 'burned', v_burn, 'daily_limit', v_daily);
end;
$$;

-- ── What the app reads ──────────────────────────────────────────────────
create or replace function public.ft_listings()
returns json
language plpgsql stable security definer set search_path = public, pg_temp
as $$
declare uid uuid := auth.uid(); fx numeric := public.ft_ftr_usd();
begin
  return coalesce((select json_agg(row_to_json(row)) from (
    select l.id, l.asset_id, l.title, a.name, a.known_as, a.ticker,
           round(a.valuation_usd / a.total_shares / fx, 6) as price,
           round(a.valuation_usd / a.total_shares, 6) as share_usd, a.valuation_usd, fx as ftr_usd,
           a.kind, a.gender, a.club, a.league, a.position, a.country, a.about, a.photo_url, a.photo_credit,
           (l.claimed_by is not null and l.claimed_by = uid) as claimed
      from public.listings l
      join public.assets a on a.id = l.asset_id
     where l.is_active and l.claimed_by is null and not a.is_active and a.valuation_usd is not null
     order by a.name
  ) row), '[]'::json);
end;
$$;

create or replace function public.ft_player_profiles()
returns json language sql stable security definer set search_path = public, pg_temp as $$
  select coalesce(json_agg(json_build_object(
           't', ticker, 'n', name, 'known_as', known_as, 'club', club, 'lg', league, 'pos', position,
           'gender', gender, 'country', country, 'dob', date_of_birth, 'number', shirt_number,
           'height', height_cm, 'foot', preferred_foot, 'about', about,
           'photo', photo_url, 'credit', photo_credit,
           'v', valuation_usd, 'price_usd', coalesce(price_usd, valuation_usd / total_shares), 'p', price)), '[]'::json)
    from public.assets
   where is_active or exists (select 1 from public.listings l where l.asset_id = assets.id and l.is_active);
$$;

-- ── Admin: the market, players and the overview ─────────────────────────
create or replace function public.ft_admin_set_market(p_ftr_usd numeric, p_gbp_usd numeric default null, p_welcome numeric default null)
returns json language plpgsql security definer set search_path = public, pg_temp as $$
declare before numeric;
begin
  perform public.ft_require_admin(true);
  if p_ftr_usd is null or p_ftr_usd <= 0 or p_ftr_usd > 1000000 then raise exception 'Set a $FTR price above $0'; end if;
  if p_gbp_usd is not null and (p_gbp_usd <= 0 or p_gbp_usd > 10) then raise exception 'That pound to dollar rate looks wrong'; end if;
  if p_welcome is not null and (p_welcome < 0 or p_welcome > 100000) then raise exception 'The welcome grant must be between 0 and 100,000 $FTR'; end if;
  select price_usd into before from public.ftr_market where id for update;
  update public.ftr_market
     set price_usd = p_ftr_usd, gbp_usd = coalesce(p_gbp_usd, gbp_usd),
         welcome_grant = coalesce(p_welcome, welcome_grant), updated_at = now()
   where id;
  perform public.ft_reprice();
  perform public.ft_admin_note('market.set', '$FTR', jsonb_build_object('from', before, 'to', p_ftr_usd,
          'gbp_usd', p_gbp_usd, 'welcome_grant', p_welcome));
  return public.ft_market();
end;
$$;

create or replace function public.ft_admin_players()
returns json language plpgsql stable security definer set search_path = public, pg_temp as $$
declare fx numeric := public.ft_ftr_usd();
begin
  perform public.ft_require_admin();
  return coalesce((select json_agg(row_to_json(r) order by r.status_rank, r.name) from (
    select l.id as listing_id, a.id as asset_id, a.ticker, a.name, a.known_as, a.kind, a.gender, a.club, a.league,
           a.position, a.country, a.date_of_birth, a.shirt_number, a.height_cm, a.preferred_foot, a.about,
           a.photo_url, a.photo_credit, a.photo_source,
           a.valuation_usd, a.valuation_source, a.valuation_at,
           round(coalesce(a.price_usd, a.valuation_usd / a.total_shares), 8) as share_usd,
           round(coalesce(a.price_usd, a.valuation_usd / a.total_shares) / fx, 6) as price, fx as ftr_usd,
           a.profile_updated_at,
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
    -- The valuation is in real dollars. (An old-style reference_value, $FTR
    -- a share, is still accepted and turned into dollars at today's price.)
    v_val    := coalesce(public.ft_try_numeric(r->>'valuation_usd'),
                         public.ft_try_numeric(r->>'reference_value') * fx * 10000000);
    v_src    := nullif(trim(r->>'valuation_source'), '');
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
        -- Until the share order book is live, a share trades at its valuation,
        -- so a new valuation moves the price for trading players too.
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


-- The overview, now with the $FTR market in it.
create or replace function public.ft_admin_overview()
returns json language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public.ft_require_admin();
  return json_build_object(
    'ftr',             public.ft_market(),
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


revoke execute on function public.ft_draw_treasury(numeric), public.ft_reprice() from public, anon, authenticated;
revoke execute on function public.ft_admin_set_market(numeric, numeric, numeric) from public, anon;
grant execute on function public.ft_market(), public.ft_ftr_usd(), public.ft_share_ftr(text), public.ft_player_profiles() to anon, authenticated;
grant execute on function public.ft_admin_set_market(numeric, numeric, numeric), public.ft_listings(),
  public.ft_claim_listing(text, int, int), public.ft_admin_players(), public.ft_admin_upsert_players(jsonb),
  public.ft_admin_overview() to authenticated;
drop table if exists ft_seed_vals;

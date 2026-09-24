-- Fantrade · the shared catalogue of players and coaches.
-- Safe to run more than once: it updates rows that already exist.
--
-- Two things to know before editing a row.
--   · `ticker` is the immutable F-ticker of 5. FSAKA, FHLND, FBRN and FKM7 are
--     the paper's own examples; the rest follow the same convention, which 5
--     calls illustrative rather than a final registry. (FCR7 and FLM10, the
--     paper's other two, belong to players this catalogue does not list.)
--   · `reference_value` is the Fantrade Reference Valuation of 6 - the figure
--     an asset is discovered at. It is not a traded price: 15.4 has market
--     prices coming from recorded executions, so prev_close, day_change,
--     day_high and day_low are left empty here rather than filled with
--     invented movement. The pages show the reference value until the first
--     real trade exists.
-- The immutable-ticker guard is lifted for this run only: three codes are
-- being settled into the short F-form below before any real trading exists,
-- and the seed is the one place a listed ticker may be set.
alter table public.assets disable trigger if exists assets_ticker_fixed;
insert into public.assets (id, ticker, name, kind, club, league, position, price, reference_value, reference_at) values
  ('$Saka', 'FSAKA', 'Bukayo Saka', 'PLAYER', 'Arsenal', 'Premier League', 'FWD', 48.20, 48.20, now()),
  ('$Haaland', 'FHLND', 'Erling Haaland', 'PLAYER', 'Manchester City', 'Premier League', 'FWD', 71.40, 71.40, now()),
  ('$Mbappe', 'FKM7', 'Kylian Mbappé', 'PLAYER', 'Real Madrid', 'La Liga', 'FWD', 78.50, 78.50, now()),
  ('$Vinicius', 'FVJR', 'Vinícius Júnior', 'PLAYER', 'Real Madrid', 'La Liga', 'FWD', 63.10, 63.10, now()),
  ('$Bellingham', 'FBEL', 'Jude Bellingham', 'PLAYER', 'Real Madrid', 'La Liga', 'MID', 58.90, 58.90, now()),
  ('$Palmer', 'FPLMR', 'Cole Palmer', 'PLAYER', 'Chelsea', 'Premier League', 'MID', 52.80, 52.80, now()),
  ('$Yamal', 'FYAML', 'Lamine Yamal', 'PLAYER', 'Barcelona', 'La Liga', 'FWD', 66.20, 66.20, now()),
  ('$Musiala', 'FMUS', 'Jamal Musiala', 'PLAYER', 'Bayern Munich', 'Bundesliga', 'MID', 46.70, 46.70, now()),
  ('$Wirtz', 'FWRTZ', 'Florian Wirtz', 'PLAYER', 'Bayer Leverkusen', 'Bundesliga', 'MID', 44.60, 44.60, now()),
  ('$Rodri', 'FRODR', 'Rodri', 'PLAYER', 'Manchester City', 'Premier League', 'MID', 61.30, 61.30, now()),
  ('$Foden', 'FFODN', 'Phil Foden', 'PLAYER', 'Manchester City', 'Premier League', 'FWD', 54.10, 54.10, now()),
  ('$Pedri', 'FPEDR', 'Pedri González', 'PLAYER', 'Barcelona', 'La Liga', 'MID', 41.15, 41.15, now()),
  ('$Saliba', 'FSALI', 'William Saliba', 'PLAYER', 'Arsenal', 'Premier League', 'DEF', 33.80, 33.80, now()),
  ('$Bruno', 'FBRN', 'Bruno Fernandes', 'PLAYER', 'Manchester United', 'Premier League', 'MID', 39.75, 39.75, now()),
  ('$Jackson', 'FJACK', 'Nicolas Jackson', 'PLAYER', 'Chelsea', 'Premier League', 'FWD', 14.85, 14.85, now()),
  ('$Arteta', 'FARTA', 'Mikel Arteta', 'COACH', 'Arsenal', 'Premier League', 'MGR', 22.05, 22.05, now()),
  ('$Pep', 'FPEP', 'Pep Guardiola', 'COACH', 'Manchester City', 'Premier League', 'MGR', 29.60, 29.60, now()),
  ('$Maresca', 'FMARS', 'Enzo Maresca', 'COACH', 'Chelsea', 'Premier League', 'MGR', 18.30, 18.30, now()),
  -- The women's game. Clubs as of the 2026-27 season.
  ('$Bonmati', 'FAITN', 'Aitana Bonmatí', 'PLAYER', 'Barcelona', 'Liga F', 'MID', 44.80, 44.80, now()),
  ('$Putellas', 'FPUTL', 'Alexia Putellas', 'PLAYER', 'London City Lionesses', 'WSL', 'MID', 36.40, 36.40, now()),
  ('$Russo', 'FRUSS', 'Alessia Russo', 'PLAYER', 'Arsenal', 'WSL', 'FWD', 38.90, 38.90, now()),
  ('$LJames', 'FLJMS', 'Lauren James', 'PLAYER', 'Chelsea', 'WSL', 'FWD', 35.70, 35.70, now()),
  ('$Kerr', 'FKERR', 'Sam Kerr', 'PLAYER', 'Gotham FC', 'NWSL', 'FWD', 31.20, 31.20, now()),
  ('$Williamson', 'FWILM', 'Leah Williamson', 'PLAYER', 'Arsenal', 'WSL', 'DEF', 27.50, 27.50, now()),
  ('$Earps', 'FEARP', 'Mary Earps', 'PLAYER', 'London City Lionesses', 'WSL', 'GK', 24.30, 24.30, now()),
  ('$Wiegman', 'FWIEG', 'Sarina Wiegman', 'COACH', 'England', 'International', 'MGR', 26.80, 26.80, now())
on conflict (id) do update set
  ticker = excluded.ticker, name = excluded.name, kind = excluded.kind,
  club = excluded.club, league = excluded.league, position = excluded.position,
  price = excluded.price, reference_value = excluded.reference_value, reference_at = excluded.reference_at,
  -- An install seeded before this file stopped inventing day statistics still
  -- carries them; running this clears them again, so the catalogue tells the
  -- truth about how much trading has actually happened.
  prev_close = null, day_change = 0, day_high = null, day_low = null,
  updated_at = now();
alter table public.assets enable trigger if exists assets_ticker_fixed;

-- Every row above now carries its ticker, so the column can hold the line for
-- whatever is added next. On an install that predates the F-ticker this is the
-- step that makes it not-null; add a ticker here for any asset you add too.
alter table public.assets alter column ticker set not null;

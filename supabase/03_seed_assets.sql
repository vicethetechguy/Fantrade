-- Fantrade · the shared catalogue of players and coaches.
-- Safe to run more than once: it updates rows that already exist.
insert into public.assets (id, name, kind, club, league, position, price, prev_close, day_change, day_high, day_low) values
  ('$Saka', 'Bukayo Saka', 'PLAYER', 'Arsenal', 'Premier League', 'FWD', 48.20, 45.3, 6.4, 51.2, 46.8),
  ('$Haaland', 'Erling Haaland', 'PLAYER', 'Manchester City', 'Premier League', 'FWD', 71.40, 72.71, -1.8, 74.0, 70.1),
  ('$Mbappe', 'Kylian Mbappé', 'PLAYER', 'Real Madrid', 'La Liga', 'FWD', 78.50, 74.9, 4.8, 81.0, 76.2),
  ('$Vinicius', 'Vinícius Júnior', 'PLAYER', 'Real Madrid', 'La Liga', 'FWD', 63.10, 62.66, 0.7, 65.0, 62.0),
  ('$Bellingham', 'Jude Bellingham', 'PLAYER', 'Real Madrid', 'La Liga', 'MID', 58.90, 57.02, 3.3, 61.0, 57.2),
  ('$Palmer', 'Cole Palmer', 'PLAYER', 'Chelsea', 'Premier League', 'MID', 52.80, 48.8, 8.2, 54.5, 49.1),
  ('$Yamal', 'Lamine Yamal', 'PLAYER', 'Barcelona', 'La Liga', 'FWD', 66.20, 60.51, 9.4, 68.0, 61.5),
  ('$Musiala', 'Jamal Musiala', 'PLAYER', 'Bayern Munich', 'Bundesliga', 'MID', 46.70, 44.43, 5.1, 48.5, 44.2),
  ('$Wirtz', 'Florian Wirtz', 'PLAYER', 'Bayer Leverkusen', 'Bundesliga', 'MID', 44.60, 42.97, 3.8, 46.2, 43.0),
  ('$Rodri', 'Rodri', 'PLAYER', 'Manchester City', 'Premier League', 'MID', 61.30, 60.45, 1.4, 62.5, 60.1),
  ('$Foden', 'Phil Foden', 'PLAYER', 'Manchester City', 'Premier League', 'FWD', 54.10, 54.76, -1.2, 56.0, 53.2),
  ('$Pedri', 'Pedri González', 'PLAYER', 'Barcelona', 'La Liga', 'MID', 41.15, 41.52, -0.9, 42.5, 40.1),
  ('$Saliba', 'William Saliba', 'PLAYER', 'Arsenal', 'Premier League', 'DEF', 33.80, 32.91, 2.7, 35.0, 32.4),
  ('$Bruno', 'Bruno Fernandes', 'PLAYER', 'Manchester United', 'Premier League', 'MID', 39.75, 38.93, 2.1, 41.8, 38.5),
  ('$Jackson', 'Nicolas Jackson', 'PLAYER', 'Chelsea', 'Premier League', 'FWD', 14.85, 13.35, 11.2, 15.5, 13.2),
  ('$Arteta', 'Mikel Arteta', 'COACH', 'Arsenal', 'Premier League', 'MGR', 22.05, 21.02, 4.9, 23.5, 21.0),
  ('$Pep', 'Pep Guardiola', 'COACH', 'Manchester City', 'Premier League', 'MGR', 29.60, 29.72, -0.4, 30.8, 28.9),
  ('$Maresca', 'Enzo Maresca', 'COACH', 'Chelsea', 'Premier League', 'MGR', 18.30, 18.08, 1.2, 19.2, 17.8)
on conflict (id) do update set
  name = excluded.name, kind = excluded.kind, club = excluded.club, league = excluded.league,
  position = excluded.position, price = excluded.price, prev_close = excluded.prev_close,
  day_change = excluded.day_change, day_high = excluded.day_high, day_low = excluded.day_low,
  updated_at = now();

-- Fantrade · Coaches open to claim. Run after 12_dollars.sql.
-- Safe to run more than once.
--
-- Clears five coaches for claiming, the same way 08 cleared players: each
-- sits in public.assets switched off (is_active = false) with one open
-- listing, so the first manager to claim them launches their shares.
-- Coaches have no transfer-market value, so their valuations are Fantrade
-- estimates in line with the coaches already trading. Clubs, photos and
-- profiles can all be changed in the admin (Coaches).

do $$
declare
  fx numeric := public.ft_ftr_usd();
  c record;
begin
  for c in select * from (values
      ('$Enrique',   'FLENR', 'Luis Enrique',     'M', 'Paris Saint-Germain', 'Ligue 1',       'Spain',         26000000.00),
      ('$Simeone',   'FSIME', 'Diego Simeone',    'M', 'Atlético Madrid',     'La Liga',       'Argentina',     20000000.00),
      ('$Flick',     'FFLCK', 'Hansi Flick',      'M', 'Barcelona',           'La Liga',       'Germany',       24000000.00),
      ('$Ancelotti', 'FANCE', 'Carlo Ancelotti',  'M', 'Brazil',              'International', 'Italy',         22000000.00),
      ('$Hayes',     'FHAYS', 'Emma Hayes',       'W', 'United States',       'International', 'England',        9000000.00)
    ) v(id, ticker, name, gender, club, league, country, usd)
  loop
    if not exists (select 1 from public.assets where ticker = c.ticker) then
      insert into public.assets (id, ticker, name, kind, gender, club, league, position, country,
                                 valuation_usd, valuation_source, valuation_at, price_usd,
                                 price, reference_value, reference_at, is_active, profile_updated_at)
      values (c.id, c.ticker, c.name, 'COACH', c.gender, c.club, c.league, 'MGR', c.country,
              c.usd, 'Fantrade estimate: coaches have no transfer-market value', current_date, round(c.usd / 10000000, 8),
              round(c.usd / 10000000 / fx, 6), round(c.usd / 10000000 / fx, 6), now(), false, now());
    end if;
    if not exists (select 1 from public.listings l join public.assets a on a.id = l.asset_id where a.ticker = c.ticker) then
      insert into public.listings (id, asset_id, title, is_active, fee_level1, fee_level2)
      select 'lst-' || c.ticker, a.id, 'Open to claim', true,
             round(500000 * c.usd / 10000000 / fx, 2), round(1000000 * c.usd / 10000000 / fx, 2)
        from public.assets a where a.ticker = c.ticker
      on conflict (id) do nothing;
    end if;
  end loop;
end $$;

# Activity-share pricing and demo FanPlay

Player launch pricing: activity pool USD = real-world valuation USD / 1,000. One share USD = activity pool USD / 10,000,000. Payment FTR = share USD / current FTR USD quote. The FTR exchange rate remains market-driven.

For a $100,000,000 player: pool $100,000; one share $0.01; 5% allocation (500,000 shares) $5,000; 10% allocation $10,000. At $20 per FTR, those claims cost 250 and 500 FTR. Coach activity valuations retain their existing model.

Apply `supabase/16_activity_share_ratio_and_demo.sql` after migration 15. It updates current player reference prices and unclaimed listing fees, preserves share counts and historical paid claims/trades, adds fractional-price precision, and fixes subsequent admin valuation updates and claim calculations. Reapplying derives prices from valuation rather than dividing an already reduced price again. Do not edit the historical migrations.

The migration also adds persistent simulation results and completed entries to the account snapshot. Demo simulation is permitted for `demo@fantrade.com`, `alex.morgan@fantrade.app`, or Supabase users with administrator-controlled `raw_app_meta_data.fantrade_demo = true`. The REST service supports the two named demo accounts. Simulation unlocks staked shares, records per-prediction results in History and does not pay real FTR or change leaderboard FP. Normal accounts still use verified results.

The migration is supplied in the repository; pushing frontend code does not execute Supabase migrations. Deploy migration 16 before expecting signed-in Supabase simulation and revised server claim prices to work.

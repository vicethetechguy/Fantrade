# Transaction audit — October 8, 2026

## Corrected

- Removed the two sample open orders instantiated for every market. Outstanding orders now come from the authenticated exchange account, filtered by asset, active status and positive remaining quantity. Cancellation waits for server confirmation.
- Market is the default order type. Activity-share RPC purchases resolve the visible ticker to the database asset ID, including servers that have not installed the ticker-compatible RPC migration.
- Financial actions await confirmation before showing success or mutating account balances. Supabase and REST transactions are no longer both submitted for the same action.
- Rejected trades, swaps, transfers, withdrawals and FanPlay entries cannot silently become successful local simulations. Disconnected accounts carrying live wallet/session data cannot transact against preview funds.
- FanPlay submits once to the selected service, keeps its action key for retries, removes rejected/unconfirmed phantom entries on snapshots, and protects locked shares. Account entries cannot be settled using the preview simulation button.
- REST wallet and portfolio refreshes use the actual API response fields. Market-order confirmation uses actual fill quantities and totals, including partial fills. IOC orders with no remaining quantity do not appear as open orders.
- REST write retries retain their request keys after uncertain network/server failures. Cached receipts cannot be replayed across users or endpoints.
- Matching failures reject their orders and release reserved funds/shares instead of returning an unprocessed order as successful.
- Deposits cannot mint a live-account balance from the preview conversion or top-up controls. Simulated market ticks cannot overwrite live account prices.

## Validation

- `node tools/check-transactions.cjs`: successful and pending trades, database ID resolution, refused transactions, confirmed/refused FanPlay, phantom-entry cleanup, REST wallet/portfolio contracts, real open-order filtering, cancellation failure/success, partial fills and lost-response retry keys. Services are mocked; no live trades were sent.
- `npx vitest run tests/transaction-confirmation.test.ts --fileParallelism=false`: four isolated server checks for failed-match compensation and retry ownership.
- `node tools/check-app-ui.cjs`: 29 app pages at 320, 390, 768 and 1280 pixels, plus wallet links and UI journeys.
- `node tools/check-onboarding.cjs`: purchases, validation and saved setup at four screen sizes.
- `node tools/check-feed.cjs`: feed interactions, responsive filters and fractional preview purchases.
- `npm run build` and Git whitespace checks passed.

## Integration limits

Live end-to-end money movement was not tested. The production account service must be reachable and contain the required existing functions/tables. Supabase activity-share accounts support immediate purchase/sale RPCs; resting limit orders require the REST exchange service and its authenticated account. A lack of counterparties can result in an unfilled or partial exchange order. Deposits require a payment-provider integration, and bank withdrawal processing requires its payout integration. A confirmed write whose follow-up account read fails is reported as confirmed with a refresh notice, never silently resubmitted. The seed-driven database integration suite was not run because it resets its configured database.

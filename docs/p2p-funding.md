# Fantrade P2P funding

Buy (`buy.html`) and sell (`withdraw.html`, or `buy.html?side=sell`) now use peer-to-peer offers, rather than a demo conversion or a direct-bank withdrawal. The screens share the existing dark, Montserrat and brand-blue design.

## What is held in escrow

Fantrade reserves the seller's **existing $FTR**, not the buyer's fiat money. The buyer pays the seller directly through the agreed external bank/payment provider. Fantrade has no bank-account access and cannot independently verify a fiat payment. Marking payment sent never credits a wallet. The seller must check their account and explicitly confirm receipt before release.

Sell advertisements reserve their entire token inventory upfront. Buy advertisements reserve the accepting seller's tokens when an order opens. Tokens remain part of the seller's wallet total but cannot be spent. Completing an order transfers reserved tokens to the buyer; P2P never mints tokens or sets the market value of $FTR. The advertiser chooses a local-currency price, fixed for each order. Quantities use two token decimals to match the wallet ledger; prices use six decimals. There is currently no Fantrade P2P fee.

## Included

- Buy/Sell marketplace, 13 currency filters and five payment-method filters, custom popup pickers.
- Public rates, limits, available quantities, and actual completed-order counts. Private receiving-account details appear only to the order's parties.
- Escrow checkout with an exact payment and token quote, 20-minute window, duplicate-request keys, and server-side affordability checks.
- Participant-only messages, optional payment reference, buyer payment confirmation, seller receipt confirmation, order history, and a saved conversation.
- Buyer cancellation before payment, automatic unpaid expiry, offer closure that preserves open-order escrow, and disputes that freeze tokens.
- Trusted support tools to inspect disputes and award escrow to the buyer or refund the seller, with a recorded reason.
- Demo Buy/Sell simulations clearly marked as practice; demo counterparties and account instructions are fictional. Authenticated service errors never switch into the demo or credit invented funds.

## Database setup (not applied by the frontend build)

1. Apply `supabase/17_p2p_escrow.sql` after migration 16 using a database administrator. This creates tables, indexes, restricted RPCs and transaction types. It starts with live trading **disabled**.
2. Configure a support operator and expiry runner before activation. If `pg_cron` is already enabled, the migration schedules unpaid expiry every minute. Otherwise run `npm run p2p:sweep` every minute on a trusted server. The page also checks expiry when either participant opens their orders. Paid and disputed orders are never automatically refunded.
3. Enable live trading after operational readiness is confirmed:

```sql
update public.p2p_settings set live_enabled = true where id = true;
```

4. Real users can create offers once enabled. An empty market stays empty; the live UI does not insert demo merchants, fictional verification badges or fake completion rates.

The P2P database integration uses the app's Supabase account service. The separate legacy Express account service does not implement these RPCs; those sessions see a connection notice and cannot initiate P2P. To use live P2P, the deployed app must use its Supabase accounts. The migration has been tested in an isolated local PostgreSQL cluster, not applied to a live project by these checks.

## Support operations

Configure `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` only on a trusted operator host. Never put the service-role key into browser configuration or commit it. Dispute listings contain private payment and conversation information; restrict operator output and access.

```text
npm run p2p:sweep
npm run p2p:support -- disputes
npm run p2p:support -- resolve ORDER_UUID BUYER "Verified payment receipt and reviewed both parties' evidence."
npm run p2p:support -- resolve ORDER_UUID SELLER "Reviewed the evidence; buyer did not complete the agreed payment."
```

The browser cannot resolve disputes. The support decision atomically settles/refunds escrow and records an audit message. A disputed refund goes directly back to the seller rather than reopening inventory in the original offer.

## Launch dependencies and limits

This implementation does not provide bank connectivity, automatic fiat verification, identity verification or an external payment-provider licence. Merchant eligibility checks, identity/payment-account verification, abuse screening, a staffed dispute response, jurisdiction-specific operating requirements and payment-provider agreements need to be established before exposing live financial trading. The supplied backend does not assert that any merchant is verified. Currency prices are supplied by advertisers; there is no automatic FX conversion. Evidence currently uses saved order messages/payment references, not uploaded bank statements. Do not treat text claims or screenshots as automatic proof of receipt.

## Verification

`node tools/check-p2p-escrow.cjs` creates and stops a fresh PostgreSQL cluster under ignored `artifacts/`; it never reads `DATABASE_URL` or touches existing wallets. It checks permission boundaries, privacy, duplicate requests, buyer/seller authorization, release, cancellation, expiry, paid holds, support resolution, concurrent orders and supply conservation.

`node tools/check-p2p-ui.cjs` covers Buy/Sell, escrow balances, confirmations, messaging, offer creation/closure, currency selection, mobile/desktop layout, and no demo fallback for authenticated failures.

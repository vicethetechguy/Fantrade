# Fantrade Admin: P2P support

Open https://fantrade.vercel.app/admin#/p2p (or /admin.html#/p2p locally).

## One-time setup

1. Apply `supabase/18_p2p_support_admin.sql` in Supabase SQL Editor after migration 17. It does not enable live P2P, move balances or grant general market administration.
2. The operator must have a normal Fantrade account using **vectorceenation@gmail.com**. If it does not exist, create it through Fantrade sign-up and verify the email through Supabase's confirmation link. The migration does not create a password or send an invitation.
3. Sign in at `/admin` with that account's existing password. The admin uses a separate login session from the consumer application.
4. Open **P2P disputes**. The first successful server check binds the verified, approved email to the actual account ID. Other accounts, unverified emails and editable browser metadata cannot obtain support access.

No service-role key is needed in the browser. No secret keys should be pasted into the admin page. Existing platform administrators retain their existing management screens; this operator receives only dispute review and settlement unless separately granted general admin access.

## Review an order

- **Needs review** lists disputed orders and protected FTR. Select an order to see buyer/seller identities, private receiving details, dates and the saved conversation.
- Check actual payment evidence; messages and screenshots are not automatic proof of payment. The current system has no bank connection or evidence-file uploader.
- Choose **Release to buyer** when payment is confirmed, or **Return to seller** when payment was not received. Record the evidence and reason, review the amount and confirm the decision.
- Settlement is atomic, records the operator and reason, updates the participant wallets and writes to the existing admin activity log. Identical request retries do not transfer tokens twice. A conflicting second decision is refused.
- **Decision history** includes resolutions made through the dashboard and the existing service-side support tool. Refresh reloads the current queue. Up to 100 cases are shown per list.
- An operator cannot resolve an order involving their own account. Use an independent authorized support operator for such a case.
- Sample mode is explicitly labelled and never settles real funds. Account/database errors do not switch to sample mode automatically.

## Revoke access

In the Supabase SQL Editor:

```sql
update public.p2p_support_operators
set enabled = false
where email = 'vectorceenation@gmail.com';
```

The server immediately refuses subsequent private reads and settlement requests. Changing the account's email or suspending its profile also blocks access. Sign-out clears the private dashboard content. Support approval does not grant privileges to edit offers, token prices, listings or other users' balances directly.

Apply migrations in order. If migration 17 is reapplied later, reapply 18 afterward so the support settlement authorization remains in place. Keep the automatic unpaid-expiry job from migration 17 running separately.

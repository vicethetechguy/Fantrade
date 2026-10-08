# Coach activity publishing and settlement

Player and coach options are validated separately before shares are reserved. Publish coach options against the coach asset ID, the eligible fixture and the selected market configuration; the live UI does not substitute preview options when the published catalogue is empty or unavailable.

Supported coach metrics:

- `team_won` (also `team_result`, `teamresult`, `win`): `eq` with a boolean, using the coach club's final fixture score.
- `clean_sheet`: `eq` with a boolean, using the opposing team's final score.
- `substitutions`: number of the coach team's substitution events.
- `substitutions_before_60`: substitutions recorded strictly before minute 60.
- `player_used` / `player_started`: `eq` with a boolean and `playerId` containing the platform player asset ID.

Events must identify the club by a canonical name in `teamId` or `metadata.teamName`. Provider IDs alone must be mapped before ingestion. `MINUTES_PLAYED` records for player selection must include `metadata.participationConfirmed: true`; `player_started` also requires a boolean `metadata.started`, and `value` contains minutes played.

To certify a complete substitution stream, a team-scoped authoritative event must carry `metadata.completeEventTypes: ["SUBSTITUTION"]`. An observed positive threshold can succeed before this marker exists, but an absent event cannot prove failure or avoidance without complete coverage. Final match scores are authoritative only after the fixture is `FULL_TIME`.

Incomplete data leaves settlement pending before any ledger transfer or share release. No artificial player statistics are substituted for a coach. Existing provider ingestion must supply these confirmations; this change does not connect a new external football data API or publish options to the production database.

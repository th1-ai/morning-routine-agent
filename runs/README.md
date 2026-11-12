# runs/

The morning routine keeps its memory here. Everything in this folder except this file and `.gitkeep` is ignored by git, because it describes your hotel's day.

| Path | Written by | What it is |
|---|---|---|
| `LOG.md` | the routine, 1 entry per run | The run log. The routine reads the newest entries before it acts, so that it does not do the same work twice. |
| `handoff/morning-routine-agent.md` | the routine, Level 2 and up | Items the sibling agents must pick up, one section per sibling. The file is replaced on each run. |
| `latest-briefing.md`, `cron.log` | your scheduler (see the README) | The printed briefing and the errors of the last scheduled run. |

## Entry format in `LOG.md`

Newest entry at the bottom: the last entry is the latest run summary. Ids only: reservation ids, message ids, sheet row numbers. No guest names, addresses or message text.

```
## 2030-01-15T07:02 | scheduled | Level 1 | ok
- Checked: email, finance, calendar, pms, upgrades, pre-arrival, leads, concierge, tasks
- Not checked: pricing (not configured)
- Siblings: room-upgrade ran at Level 1 (ok); dynamic-pricing already ran 06:30; crm-pipeline not run (paused)
- Actions taken: none
- Proposed: handoff to finance-filing-agent (2 invoices)
- Errors: none
- Needs you: 2 (reservation 12345 has no room; Inbox row 14 draft pending)
```

Header fields: timestamp in local time, `scheduled` or `manual`, the level the run worked at, and the result: `ok`, `shadow`, `stopped` (with the reason: `PAUSED`, Level 0, already ran, or a failed write) or `error`. A stopped entry is one header line and one `- Reason:` line.

## Handoff file format

Every agent in the stack writes its handoffs to `runs/handoff/<its-own-repo>.md` in its own folder. The routine writes `runs/handoff/morning-routine-agent.md` and reads `runs/handoff/<sibling-repo>.md` in each installed sibling's folder.

```
# Handoff from morning-routine-agent — 2030-01-15T07:02

## To finance-filing-agent
- invoice | message id 18c2f0a1 | inbox INBOX_PRIMARY | attachment 1 of 1
- invoice | message id 18c2f0b7 | inbox INBOX_BOOKINGS | attachment 2 of 2

## To room-upgrade-agent
- accepted upgrade | reservation 12345 | message id 18c2f0c3
```

One line per item: what it is, the id that finds it again, and where it is. The sibling reads the source itself.

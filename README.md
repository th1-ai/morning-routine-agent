# Morning Routine Agent

A Claude Code skill for hotel operators. It runs your daily operational sweep in one shot — reads every inbox, scans for invoices, checks the calendar, audits the next seven days of reservations in your PMS, surfaces upgrade opportunities and pre-arrival outreach candidates, and finishes with a "today's focus" recommendation.

Built on the **WAT framework** (Workflows, Agents, Tools): probabilistic AI handles reasoning, deterministic scripts handle execution.

---

## What it does

- **Triage all configured inboxes** — reads the body of every unread guest email (subject lines aren't enough; OTA relay names often differ from the reservation name)
- **Flag invoices and receipts** for the finance-filing flow before they get buried
- **Pull your calendar** and surface check-ins, check-outs, deliveries, and contractor visits
- **Audit the next seven days in your PMS** — unassigned rooms, unconfirmed reservations, tight turnarounds, large parties
- **Spot upgrade opportunities** and upgrade acceptances waiting on a room change
- **Find pre-arrival outreach candidates** (premium rooms, 7-21 days out, not yet contacted)
- **Run the CRM-pipeline checks** — stale leads, follow-ups due, recent conversions, conversion rate
- **Show concierge follow-ups** — pending restaurant bookings, transfers, requests
- **Run dynamic pricing in dry-run mode** and surface the proposed diff
- **Review tasks** grouped by status
- **End with a "today's focus"** — three concrete recommended actions

---

## What you need

- [Claude Code](https://claude.ai/code) installed
- One or more email accounts you can read programmatically (Gmail via the Google Workspace CLI is the reference setup)
- A PMS with API access — the routine calls a `lookup_guest`-style tool. The reference setup is Cloudbeds, but any PMS with reservation lookup endpoints works.
- Google Sheets (or any sheet store accessed via the same CLI) for the email-inbox tracker, the task list, and the concierge tracker
- Optional sub-tools the routine orchestrates: pre-arrival scanner, CRM pipeline tool, dynamic-pricing tool. Drop the steps that don't apply to you.

---

## Quick start

1. **Clone the repo** into a Claude Code project:

   ```bash
   git clone https://github.com/th1-ai/morning-routine-agent.git
   cd morning-routine-agent
   ```

2. **Copy the env template** and fill it in:

   ```bash
   cp .env.example .env
   ```

3. **Edit [`.claude/skills/morning-routine/SKILL.md`](.claude/skills/morning-routine/SKILL.md)** — replace the placeholders described in [Customising](#customising) with the wrappers and IDs your setup uses.

4. **Open in Claude Code** from the project root:

   ```bash
   claude
   ```

5. **Invoke the skill**:

   > "Good morning — let's do the morning routine."

   Claude Code will pick up the `morning-routine` skill automatically because of its trigger phrases.

---

## File structure

```
morning-routine-agent/
├── README.md                                     # This file
├── .env.example                                  # Inboxes, PMS auth, Sheet IDs, etc.
├── .gitignore
├── LICENSE
└── .claude/
    └── skills/
        └── morning-routine/
            └── SKILL.md                          # The skill definition
```

---

## Customising

The skill file uses placeholders so it can be adapted to any email + PMS + sheet stack. Replace the following before first run:

| Placeholder | What to put | Example |
|---|---|---|
| `{{INBOX_PRIMARY}}` | Main business inbox address (or alias) | `info@yourhotel.com` |
| `{{INBOX_BOOKINGS}}` | Inquiries / OTA inbox | `bookings@yourhotel.com` |
| `{{INBOX_RENTALS}}` | Whole-property / villa inbox (optional) | `rentals@yourhotel.com` |
| `{{EMAIL_CLI}}` | Command-line wrapper to your email + sheets provider | `gws` |
| `{{PMS_LOOKUP_TOOL}}` | Script that looks up reservations by name / email / confirmation # | `tools/lookup_guest.py` |
| `{{PMS_NOTES_TOOL}}` | Script that appends a note to a reservation | `tools/cloudbeds_notes.py` |
| `{{PMS_PROPERTY_ID}}` | Property ID in your PMS | (provider-specific) |
| `{{SHEET_ID_INBOX}}` | Sheet that tracks processed emails | (Google Sheet ID) |
| `{{SHEET_ID_TASKS}}` | Sheet that tracks tasks | (Google Sheet ID) |
| `{{SHEET_ID_CONCIERGE}}` | Sheet that tracks concierge follow-ups | (Google Sheet ID) |
| `{{PRE_ARRIVAL_TOOL}}` | Pre-arrival scanner | `tools/pre_arrival_scan.py` |
| `{{CRM_TOOL}}` | CRM pipeline tool | `tools/crm_pipeline.py` |
| `{{PRICING_TOOL}}` | Dynamic-pricing tool | `tools/dynamic_pricing.py` |
| `{{GCP_PROJECT_ID}}` | Google Cloud project for the Workspace CLI | (project ID) |

The reference setup uses scripts named `tools/lookup_guest.py`, `tools/cloudbeds_notes.py`, `tools/pre_arrival_scan.py`, `tools/crm_pipeline.py`, and `tools/dynamic_pricing.py`. Yours can live anywhere and use any names — the placeholders are the only thing the skill cares about.

You can do replacements with any text editor or with one `sed` pass:

```bash
sed -i '' \
  -e 's|{{INBOX_PRIMARY}}|info@yourhotel.com|g' \
  -e 's|{{INBOX_BOOKINGS}}|bookings@yourhotel.com|g' \
  -e 's|{{EMAIL_CLI}}|gws|g' \
  -e 's|{{PMS_LOOKUP_TOOL}}|tools/lookup_guest.py|g' \
  .claude/skills/morning-routine/SKILL.md
```

---

## How memory works

This skill leans on Claude Code's per-project memory. After each morning routine, useful patterns to record include:

- **Senders confirmed as recurring noise** so triage skips them faster next time
- **Reservation gotchas** — e.g. "OTA modifications need to be actioned in the OTA extranet, not the PMS API"
- **Operator preferences** — which sections to lead with, which to mute on quiet days

Keep memory concise — one line per pattern.

---

## Related agents

This skill orchestrates several other agents. It works well alongside:

- [`email-triage-agent`](https://github.com/th1-ai/email-triage-agent) — the underlying inbox triage logic
- [`email-processor-agent`](https://github.com/th1-ai/email-processor-agent) — runs triage on a 15-minute schedule and logs every classification to a sheet
- [`booking-inquiry-agent`](https://github.com/th1-ai/booking-inquiry-agent) — drafts the warm, personal reply once an inquiry is flagged
- [`pre-arrival-outreach-agent`](https://github.com/th1-ai/pre-arrival-outreach-agent) — finds high-value upcoming guests and drafts welcome messages
- [`dynamic-pricing-agent`](https://github.com/th1-ai/dynamic-pricing-agent) — proposes rate and MLOS changes for the next 30 days
- [`finance-filing-agent`](https://github.com/th1-ai/finance-filing-agent) — processes flagged invoices end to end

---

## License

MIT — see [LICENSE](LICENSE).

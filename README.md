# Morning Routine Agent

A Claude Code skill for hotel operators. It runs your daily operational sweep in one go: it reads every inbox, scans for invoices, checks the calendar, audits the next seven days of reservations in your PMS, surfaces upgrade opportunities and pre-arrival outreach candidates, and finishes with a "today's focus" recommendation.

Built on the **WAT framework** (Workflows, Agents, Tools): the AI handles reasoning, your own scripts handle execution.

This repo is a template. It contains the skill (a markdown file) and nothing else. It does not ship an email CLI, a PMS connector or any scripts: you bring those, and you tell the skill what they are called.

---

## What it does

- **Triages all configured inboxes**: reads the body of every unread guest email (subject lines aren't enough; OTA relay names often differ from the reservation name)
- **Flags invoices and receipts** for filing before they get buried
- **Pulls your calendar** and surfaces check-ins, check-outs, deliveries and contractor visits
- **Audits the next seven days in your PMS**: unassigned rooms, unconfirmed reservations, same-day turnarounds, large parties
- **Spots upgrade opportunities** and upgrade acceptances waiting on a room change
- **Finds pre-arrival outreach candidates** (premium rooms, 7 to 21 days out, not yet contacted)
- **Runs the lead-pipeline checks**: stale leads, follow-ups due, recent conversions, conversion rate
- **Shows concierge follow-ups**: pending restaurant bookings, transfers, requests
- **Runs dynamic pricing as a dry run** and surfaces the proposed changes
- **Reviews tasks** grouped by status
- **Ends with "today's focus"**: up to three concrete recommended actions

The routine is read-only by default. It never sends an email, changes a reservation or pushes a rate on its own. It shows you drafts and proposals and waits for your approval of each one.

---

## What you need

- [Claude Code](https://code.claude.com/docs/en/quickstart) installed
- A command-line tool that can read your email accounts, your calendar and your spreadsheets. The reference setup is a Google Workspace CLI wrapper called as `<cli> <account> <command>`.
- A script that looks up reservations in your PMS (upcoming reservations, one reservation by ID, today's check-outs). Any PMS with reservation lookup endpoints works.
- Three spreadsheets: an email tracking sheet, a task list and (optional) a concierge tracker
- Optional tools: a pre-arrival scanner, a lead-pipeline tool, a dynamic-pricing tool. The routine skips the checks you have no tool for.

The skill file shows the exact commands it expects. If your tools use other subcommands or flags, edit the commands in the skill file to match.

---

## Quick start

1. **Clone the repo** and open Claude Code in it:

   ```bash
   git clone https://github.com/th1-ai/morning-routine-agent.git
   cd morning-routine-agent
   claude
   ```

2. **Let Claude Code set it up with you.** Paste this prompt:

   > Read the README and set this agent up with me. Ask me for each placeholder in the Customising table, one at a time, and tell me which ones are optional. Then replace the placeholders in `.claude/skills/morning-routine/SKILL.md`, remove the steps I do not use, and show me the commands the routine will run so I can check them against my tools.

   If you prefer to do it by hand, see [Customising](#customising).

3. **Run it.** Type `/morning-routine`, or say:

   > Good morning, let's do the morning routine.

   Claude Code picks the skill up from its description, so either way works.

### Use it in your own project

To add the routine to a project you already have, copy the skill folder into it:

```bash
cp -r .claude/skills/morning-routine /path/to/your-project/.claude/skills/
```

Claude Code discovers project skills at `.claude/skills/<skill-name>/SKILL.md`.

---

## Verify it works

1. In Claude Code, type `/` and check that `morning-routine` is in the list.
2. Run this from the repo root. It prints nothing when every placeholder is filled:

   ```bash
   grep -n '{{' .claude/skills/morning-routine/SKILL.md
   ```

3. Run the routine once and read the "Not checked" section of the briefing. It lists each check that was skipped or failed, with the reason.

## Troubleshooting

- **`/morning-routine` is not in the list.** Start `claude` from the folder that contains `.claude/`, and check that the file is at `.claude/skills/morning-routine/SKILL.md` and still starts with the `---` block.
- **A check says "not configured".** A `{{...}}` placeholder is still in the skill file for that step. Fill it in, or delete the step if you do not use it.
- **A command fails.** The skill shows the reference command shape. Run the same command in your terminal, fix it for your tool, and edit the command in the skill file.
- **Claude Code asks permission for every command.** That is the default. Approve as you go, or allow your read-only commands in the project's permission settings.
- **The briefing shows the wrong mailbox or calendar.** Check that every command names the account. The skill always passes the account as an argument for this reason.

---

## File structure

```
morning-routine-agent/
├── README.md                                     # This file
├── .env.example                                  # Worksheet for your setup values (no secrets)
├── .gitignore
├── LICENSE
└── .claude/
    └── skills/
        └── morning-routine/
            └── SKILL.md                          # The skill definition
```

---

## Customising

The skill file uses placeholders so it can be adapted to any email, PMS and sheet stack. Replace them before the first run:

| Placeholder | What to put | Example |
|---|---|---|
| `{{EMAIL_CLI}}` | Command-line wrapper for your email, calendar and sheets | `gws` |
| `{{INBOX_PRIMARY}}` | Main business inbox, as your CLI names the account. Also used for calendar and sheets. | `info@yourhotel.com` |
| `{{INBOX_BOOKINGS}}` | Inquiries / OTA inbox | `bookings@yourhotel.com` |
| `{{INBOX_RENTALS}}` | Third inbox, for example whole-property rentals (optional) | `rentals@yourhotel.com` |
| `{{PMS_LOOKUP_TOOL}}` | Read-only script that looks up reservations | `tools/lookup_guest.py` |
| `{{SHEET_ID_INBOX}}` | Sheet that tracks processed emails (tab `Inbox`) | (spreadsheet ID) |
| `{{SHEET_ID_TASKS}}` | Sheet that tracks tasks (tab `Tasks`) | (spreadsheet ID) |
| `{{SHEET_ID_CONCIERGE}}` | Sheet that tracks concierge follow-ups (tab `Guests`, optional) | (spreadsheet ID) |
| `{{PRE_ARRIVAL_TOOL}}` | Pre-arrival scanner (optional) | `tools/pre_arrival_scan.py` |
| `{{CRM_TOOL}}` | Lead-pipeline tool (optional) | `tools/crm_pipeline.py` |
| `{{PRICING_TOOL}}` | Dynamic-pricing tool, dry-run invocation (optional) | `tools/dynamic_pricing.py` |

The example script names are only examples. Your tools can live anywhere and have any names.

For an optional item you do not use, delete its step from the skill file (and its line in the Process overview and the Output format). If you leave the placeholder in, the routine skips that check and reports it as "not configured".

[`.env.example`](.env.example) lists the same names. You can copy it to `.env` and use it as a worksheet while you collect the values; the setup prompt can read it. Claude Code does not load it when the routine runs, and it must not hold passwords or API keys. Your tools keep their own credentials.

To replace by hand, use any text editor, or one `sed` pass (macOS syntax shown; on Linux use `sed -i` without the `''`):

```bash
sed -i '' \
  -e 's|{{EMAIL_CLI}}|gws|g' \
  -e 's|{{INBOX_PRIMARY}}|info@yourhotel.com|g' \
  -e 's|{{INBOX_BOOKINGS}}|bookings@yourhotel.com|g' \
  -e 's|{{PMS_LOOKUP_TOOL}}|tools/lookup_guest.py|g' \
  .claude/skills/morning-routine/SKILL.md
```

---

## How memory works

Claude Code keeps notes per project (auto memory, on by default; run `/memory` to read or edit them). You can tell it to remember what it learns from a routine, for example:

- **Senders confirmed as recurring noise**, so triage skips them faster next time
- **Reservation gotchas**, such as "OTA modifications are actioned in the OTA extranet, not through the PMS API"
- **Your preferences**: which sections to lead with, which to mute on quiet days

Keep it to one line per pattern, and keep guest details out of memory.

---

## Related agents

The routine calls on other agents for three of its checks. Each one is optional: install it into the same project (copy its `.claude/` contents next to this skill) and the routine uses it; leave it out and the routine does the read-only part itself or skips the check.

- [`room-upgrade-agent`](https://github.com/th1-ai/room-upgrade-agent): the upgrade scan in check 5, and the room change after a guest accepts
- [`dynamic-pricing-agent`](https://github.com/th1-ai/dynamic-pricing-agent): the pricing dry run in check 9, and the push after you approve
- [`finance-filing-agent`](https://github.com/th1-ai/finance-filing-agent): processes the invoices that check 2 flags

It also works well alongside:

- [`email-triage-agent`](https://github.com/th1-ai/email-triage-agent): the underlying inbox triage logic
- [`email-processor-agent`](https://github.com/th1-ai/email-processor-agent): processes new email on a schedule and logs each one to the tracking sheet that check 1 reads
- [`booking-inquiry-agent`](https://github.com/th1-ai/booking-inquiry-agent): drafts the reply once an inquiry is flagged
- [`pre-arrival-outreach-agent`](https://github.com/th1-ai/pre-arrival-outreach-agent): drafts the welcome messages for the guests check 6 finds
- [`crm-pipeline-agent`](https://github.com/th1-ai/crm-pipeline-agent): the lead pipeline behind check 7
- [`concierge-agent`](https://github.com/th1-ai/concierge-agent): the concierge tracker behind check 8

All 21 agents: [th1.ai/agent-stack](https://th1.ai/agent-stack)

---

## License

MIT — see [LICENSE](LICENSE).

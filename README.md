# Morning Routine Agent

A Claude Code skill for hotel operators. It runs your daily operational sweep in one go: it reads every inbox, scans for invoices, checks the calendar, audits the next seven days of reservations in your PMS, surfaces upgrade opportunities and pre-arrival outreach candidates, and finishes with a "today's focus" recommendation.

Built on the **WAT framework** (Workflows, Agents, Tools): the AI handles reasoning, your own scripts handle execution.

This repo is a template. It contains the skill (a markdown file), an autonomy settings file and one small guard script for scheduled runs. It does not ship an email CLI, a PMS connector or a scheduler: you bring those, and you tell the skill what they are called.

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

The routine is read-only by default. It never sends a message to a guest, changes a reservation or pushes a rate on its own. It shows you drafts and proposals and waits for your approval of each one.

It can also run on a schedule and act as the orchestrator for the other agents in the stack: it reads each installed agent's latest run report, runs the ones that are due, and puts only the exceptions in front of you. How far it may go is set in [`AUTONOMY.md`](AUTONOMY.md), one level at a time. See [Run it on its own](#run-it-on-its-own).

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

   > Read the README and set this agent up with me. Ask me for each placeholder in the Customising table, one at a time, and tell me which ones are optional. Then replace the placeholders in `.claude/skills/morning-routine/SKILL.md` and `AUTONOMY.md`, remove the steps I do not use, and show me the commands the routine will run so I can check them against my tools. Leave the level in `AUTONOMY.md` as it is.

   If you prefer to do it by hand, see [Customising](#customising).

3. **Run it.** Type `/morning-routine`, or say:

   > Good morning, let's do the morning routine.

   Claude Code picks the skill up from its description, so either way works.

### Use it in your own project

To add the routine to a project you already have, copy the skill folder into it:

```bash
cp -r .claude/skills/morning-routine /path/to/your-project/.claude/skills/
```

For scheduled runs, also copy `AUTONOMY.md`, the `runs/` folder, `.claude/hooks/` and `.claude/settings.example.json`.

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
- **A scheduled run prints "Paused by AUTONOMY.md" or "Already ran today".** The first means the `Level:` line is `0` or `PAUSED`, or is missing, repeated or has another value. The second means `runs/LOG.md` already has a scheduled entry for today.
- **A scheduled run reports most checks as "Not checked".** `dontAsk` denied the commands. Compare the commands in the skill file with the allow rules in `.claude/settings.scheduled.json`; they must match word for word up to the `*`.
- **The guard hook blocks a read command.** The command contains one of the hook's words (for example a search for the word "reply"). Change the word list at the top of `.claude/hooks/autonomy-guard.py`.
- **The briefing shows the wrong mailbox or calendar.** Check that every command names the account. The skill always passes the account as an argument for this reason.

---

## File structure

```
morning-routine-agent/
├── README.md                                     # This file
├── AUTONOMY.md                                   # Your autonomy level, limits and sibling list
├── .env.example                                  # Worksheet for your setup values (no secrets)
├── .gitignore
├── LICENSE
├── runs/
│   ├── README.md                                 # Run log and handoff file formats
│   └── .gitkeep                                  # LOG.md and handoff/ appear here, ignored by git
└── .claude/
    ├── settings.example.json                     # Example permissions and hook for scheduled runs
    ├── hooks/
    │   └── autonomy-guard.py                     # Blocks send-type commands below Level 3
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
| `{{OPERATOR_EMAIL}}` | Your own address: the only one a scheduled run may write to (optional, used from Level 2) | `you@yourhotel.com` |
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
  -e 's|{{OPERATOR_EMAIL}}|you@yourhotel.com|g' \
  .claude/skills/morning-routine/SKILL.md AUTONOMY.md
```

---

## Run it on its own

The routine can run on a schedule with nobody at the keyboard. [`AUTONOMY.md`](AUTONOMY.md) says how far it may go. You edit that file; the routine reads it at the start of every run and cannot edit it.

| Level | What a scheduled run does |
|---|---|
| PAUSED | Nothing. It logs why it stopped. |
| 0 | Nothing. The routine runs only when you ask. |
| 1 (default) | Runs every check, reads the other agents' run reports, prints the briefing. Writes only its run log in `runs/`. |
| 2 | Also runs the due sibling agents so they prepare drafts and proposals, writes a handoff file for them, saves the briefing as a draft to you, adds task rows. |
| 3 | Also sends the briefing to your own address, marks sent drafts as `SENT` in the tracking sheet, and runs each sibling at the sibling's own level. Each action has a limit in `AUTONOMY.md`. |

At no level does a scheduled run send anything to a guest, a partner or a supplier, change the PMS, push a rate, move money or delete anything.

### 1. Make the settings file for scheduled runs

[`.claude/settings.example.json`](.claude/settings.example.json) is an example of least-privilege permissions: it allows file reads, edits inside `runs/` and the read commands of the reference tools, and it denies `rm`, `curl`, `wget`, the email CLI's send commands and edits to `AUTONOMY.md` and `.claude/`. It is not named `settings.json`, so cloning the repo changes nothing. Copy it and fill in the same placeholders as in the skill:

```bash
cp .claude/settings.example.json .claude/settings.scheduled.json
```

Then replace the `{{...}}` values in the copy, delete the lines for tools you do not have, and change the subcommands to the ones your tools use. A permission rule matches the command text as written, so treat these rules as a seat belt. The real limit is what your tools' credentials can do: where your email CLI or PMS offers a read-only token, use it for scheduled runs.

The file also registers one hook, [`.claude/hooks/autonomy-guard.py`](.claude/hooks/autonomy-guard.py) (needs `python3`). Before every shell command it reads `AUTONOMY.md` and blocks a command that contains a send-type word (`send`, `reply`, `forward`, `push`, `apply`, `publish`) unless the file says `Level: 3`. It blocks `refund`, `charge`, `pay`, `payout`, `delete` and `cancel` at every level. It matches whole words, so it also blocks a harmless command that contains one of them. Edit the two word lists at the top of the script to fit your tools.

### 2. The command

Run this by hand first, from the repo folder:

```bash
claude -p "/morning-routine scheduled" \
  --permission-mode dontAsk \
  --settings .claude/settings.scheduled.json \
  --max-turns 80 < /dev/null
```

- `-p` runs Claude Code without a session and prints the result. `/morning-routine` in the prompt loads the skill.
- `--permission-mode dontAsk` denies every tool call that would otherwise ask you. Only your allow rules and Claude Code's built-in read-only commands run.
- `--settings` adds the permissions and the hook for this run only. Your interactive sessions are not changed.
- `--max-turns` stops a run that loops. Raise it if a full briefing is cut off.
- Do not add `--bare`: it skips skills and hooks, and the routine needs both.

Read the briefing. "Not checked" lists every check that a permission rule denied, so you can see which rule to adjust.

### 3. Schedule it

An example for cron on macOS or Linux (`crontab -e`), every day at 06:30. Cron has a short `PATH`, so use the full paths that `which claude` and `pwd` print:

```
30 6 * * * cd /path/to/morning-routine-agent && /path/to/claude -p "/morning-routine scheduled" --permission-mode dontAsk --settings .claude/settings.scheduled.json --max-turns 80 < /dev/null > runs/latest-briefing.md 2>> runs/cron.log
```

This line is an example. It was not tested on your machine: check after the first morning that `runs/latest-briefing.md` and a new entry in `runs/LOG.md` exist. The computer must be on and awake, and Claude Code must be logged in for the user that owns the crontab. The Claude Code desktop app also has scheduled tasks that run on your computer and catch up on a missed run; see the [Claude Code docs](https://code.claude.com/docs/en/desktop-scheduled-tasks). Cloud scheduled tasks start from a fresh clone and cannot reach tools on your computer, so they do not fit this template as it is.

Headless use of a personal Pro or Max plan is subject to Anthropic's usage policy; for a heavy or business-critical schedule, use an API key or a team plan.

### 4. Let it run the other agents

The routine is the orchestrator. Install each sibling agent in a `siblings/` folder inside this repo, so that it keeps its own `AUTONOMY.md` and its own `runs/` folder:

```bash
mkdir -p siblings
git clone https://github.com/th1-ai/room-upgrade-agent.git siblings/room-upgrade-agent
```

Then keep its row in the "Sibling agents" table of `AUTONOMY.md` and delete the rows of the agents you did not install. On each run the routine:

1. reads three paths in each sibling's folder: `AUTONOMY.md` (its level), the last entry of `runs/LOG.md` (its latest run summary) and `runs/handoff/<sibling-repo>.md` (what it hands off), and puts that agent's errors and open items in your briefing;
2. decides which siblings are due (daily, on a weekday, or when the routine found work for them);
3. runs each due sibling, at the lowest of three levels: the routine's level, the sibling's own level, and the "Max level" column in the table. The routine cannot raise a sibling above the level you set in the sibling's own file.

Claude Code loads a skill in a nested `siblings/<repo>/.claude/skills/` folder when it first reads a file in that folder, which the routine does in step 1. Sub-agent definitions are not found in nested folders: for a sibling that ships `.claude/agents/*.md`, copy those files into this repo's `.claude/agents/`. A sibling also needs its own read commands in `.claude/settings.scheduled.json`; copy the allow rules from the sibling's own `settings.example.json`.

A sibling that has its own schedule (for example `email-processor-agent`, which runs many times a day) stays `read only` in the table: the routine reads its report and does not start it. If you schedule a sibling yourself, set its time before the routine's, so that the briefing has its result.

### 5. Move up one level at a time

1. Run for 5 days at the current level.
2. Read `runs/LOG.md`. Each entry lists what the run did, what it proposed, its errors and what it needed from you. Check that "Proposed" holds only things you would have approved.
3. Change the one line in `AUTONOMY.md`, for example `Level: 1` to `Level: 2`.
4. The first 5 runs at the new level are shadow runs: the routine still works one level down and logs what the new level would have done. After that the new level is active.

To stop everything, write `Level: PAUSED` in `AUTONOMY.md`. The next scheduled run stops at its start and logs why. `AUTONOMY.md` has exactly one `Level:` line, with the value `0`, `1`, `2`, `3` or `PAUSED`; a missing file, a missing line or any other value counts as `PAUSED`.

---

## How memory works

Claude Code keeps notes per project (auto memory, on by default; run `/memory` to read or edit them). You can tell it to remember what it learns from a routine, for example:

- **Senders confirmed as recurring noise**, so triage skips them faster next time
- **Reservation gotchas**, such as "OTA modifications are actioned in the OTA extranet, not through the PMS API"
- **Your preferences**: which sections to lead with, which to mute on quiet days

Keep it to one line per pattern, and keep guest details out of memory.

Separately from this, the routine keeps a run log in `runs/LOG.md` (format in [`runs/README.md`](runs/README.md)). It reads the latest entries at the start of a run so that it does not flag, hand off or send the same thing twice.

---

## Related agents

The routine calls on other agents for its checks and hands work to them. Each one is optional: install it into the same project (clone it into `siblings/`, see [Let it run the other agents](#4-let-it-run-the-other-agents), or copy its `.claude/` contents next to this skill) and the routine uses it; leave it out and the routine does the read-only part itself or skips the check.

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

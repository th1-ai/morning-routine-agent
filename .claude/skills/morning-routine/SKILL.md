# Skill: Morning Routine

Daily morning check-in — the comprehensive operational sweep. Runs all relevant skills, surfaces everything that needs attention, and presents it as an actionable briefing.

> **Template note:** Replace `{{INBOX_*}}`, `{{EMAIL_CLI}}`, `{{PMS_*}}`, `{{SHEET_ID_*}}`, `{{GCP_PROJECT_ID}}` and tool placeholders with the wrappers and IDs your setup uses. See `README.md` for guidance.

## Trigger

User says "morning", "good morning", "let's do the morning routine", "daily check", "what's on today", or similar.

## Process Overview

Run these checks **in parallel where possible**, then present a unified briefing:

1. Email triage (all configured inboxes)
2. Finance scan (invoices/receipts in emails)
3. Calendar
4. PMS health check
5. Room upgrade opportunities
6. Pre-arrival outreach scan
7. Concierge follow-ups
8. Dynamic pricing & MLOS
9. Task review
10. Recommendations

---

### 1. Email Triage — Read EVERY Unread Email

**CRITICAL:** Do not just list unread emails by subject — **read the body of every unread guest message**. OTA relay names (e.g. Booking.com aliases) often differ from the reservation name. The only way to catch these is to read the content.

**Step 1a: Check the Email Inbox sheet** for recently processed emails:

```bash
{{EMAIL_CLI}} primary sheets-get --spreadsheet-id "{{SHEET_ID_INBOX}}" --range "Inbox!A:L"
```

Filter to rows from the last 48 hours. Note any with Draft Status = `PENDING REVIEW`.

**Step 1b: Scan all configured inboxes for unread emails** not yet in the sheet:

```bash
{{EMAIL_CLI}} {{INBOX_PRIMARY}} triage --query "after:YYYY/MM/DD is:unread" --max 20
{{EMAIL_CLI}} {{INBOX_BOOKINGS}} triage --query "after:YYYY/MM/DD is:unread" --max 20
{{EMAIL_CLI}} {{INBOX_RENTALS}} triage --query "after:YYYY/MM/DD is:unread" --max 20
```

Use yesterday's date for `after:`. Compare against the sheet — any unread email NOT in the sheet must be read and triaged.

**Step 1c: Read the body of every unread email** that is:
- From a guest or guest relay (Booking.com, Expedia, etc.)
- Classified as `guest-message`, `needs-attention`, or `booking-inquiry`
- From a supplier with an attachment (could be an invoice)
- From anyone not obviously marketing/spam

Do NOT skip emails just because they look routine from the subject line.

**Step 1d: Present grouped by urgency:**
- **NEEDS ACTION** — guest messages needing replies, upgrade acceptances, modification requests, invoices to file
- **REVIEW** — drafts pending approval, OTA notifications worth noting
- **LOW** — count only ("X newsletters/marketing emails ignored")

**Draft review:** For any drafts with status `PENDING REVIEW`:
1. Fetch and show the draft content
2. Ask the operator to approve, edit, or reject
3. On approval, send via the email CLI's `drafts send` command for the relevant account
4. Update the sheet row's Draft Status to `SENT` or `REJECTED`

---

### 2. Finance Scan — Invoices & Receipts in Emails

While reading emails, flag any that contain:
- PDF attachments that are invoices/receipts (e.g. supplier deliveries, retail receipts)
- PMS payment notifications (these are income, not expenses)
- Stripe / payment-processor invoice notifications

For each invoice/receipt found:
- **Flag it** in the briefing: "Supplier invoice `<invoice_filename>.pdf` — needs filing"
- **Offer to run the finance-filing skill** to download, extract, rename, upload to Drive, and log to the Finances spreadsheet

Remember:
- PMS-generated invoices = INCOME (guest receipts), not expenses
- Supplier invoices = EXPENSES

---

### 3. Calendar

```bash
{{EMAIL_CLI}} {{INBOX_PRIMARY}} calendar agenda
```

**IMPORTANT:** Always use a per-account wrapper. Never set the active account via a global env var that can silently fall back to the wrong account.

Surface:
- Guest check-ins / check-outs
- Meetings or calls
- Deliveries or contractor visits
- Reminders or deadlines
- Concierge bookings (restaurant reservations, tours, transfers)

If nothing is on the calendar, say "Calendar is clear today."

---

### 4. PMS Health Check

```bash
{{PMS_LOOKUP_TOOL}} --upcoming --days 7 --status "confirmed,not_confirmed"
```

Check upcoming reservations (next 7 days) for issues.

**IMPORTANT: Get room assignments** — list endpoints often do NOT return room details. For each reservation, call the single-reservation lookup to get the assigned room:

```bash
{{PMS_LOOKUP_TOOL}} --reservation-id <RES_ID>
```

Read room info from the response (e.g. assigned room name / room type / assignment flag).

Also check today's checkouts:

```bash
{{PMS_LOOKUP_TOOL}} --checkout-on today --status "checked_in"
```

**Flag:**
- **Unassigned rooms** — reservations with no room assigned (URGENT if check-in is today or tomorrow)
- **Not confirmed** status — needs attention
- **Same-day check-in with checkout** — tight turnarounds, alert housekeeping
- **Large parties** (4+ guests) — may need extra prep
- **Overlapping room assignments**

---

### 5. Room Upgrade Opportunities

Run the room-upgrade skill logic: scan reservations in the next 14-21 days for guests in standard rooms who could be offered an upgrade.

For each candidate:
1. Check if the upgrade room type is available for their dates
2. Calculate upgrade pricing (use rate plans API)
3. Check if an offer has already been sent (search email for "upgrade" + guest name/booking ref)
4. If not yet offered, flag as "Upgrade opportunity"

**Also check for upgrade acceptances** — search emails for replies to previous upgrade offers. If a guest has accepted:
- Flag it as "Upgrade ACCEPTED — needs room change"
- Show current room, target room, and price difference
- Note if it's an OTA reservation (room change may need to be done in the PMS admin UI, not the API)

Present as:
```
### Upgrade Opportunities
- <Guest> ({dates}, {current room}) → upgrade available, +€X/night — offer not yet sent
- <Guest> ({dates}) — ACCEPTED upgrade, needs room change in PMS
```

Or "No upgrade opportunities" if none found.

---

### 6. Pre-Arrival Outreach

Scan for high-value upcoming guests (7-21 days out) in premium rooms who haven't been contacted yet:

```bash
{{PRE_ARRIVAL_TOOL}} --format json
```

For qualifying guests:
- Check if a pre-arrival email has already been sent
- If not, flag: "Pre-arrival outreach needed for <Guest>, checking in {date}"
- Note booking value and room type

Also check if any previously contacted guests have replied and need follow-up.

---

### 6b. Lead Pipeline

Run the CRM pipeline checks and present a summary:

```bash
{{CRM_TOOL}} check-stale --format json
{{CRM_TOOL}} check-bookings --format json
{{CRM_TOOL}} check-lifecycle --format json
{{CRM_TOOL}} summary --format json
```

Present:
- **Active leads** count and total pipeline value
- **Follow-ups due** — list each lead needing follow-up with name, dates, and how long since last contact
- **Recent conversions** (last 7 days) — leads that booked
- **Recent losses** (last 7 days) — leads gone stale or lost
- **Conversion rate** for current month

If there are leads in `FOLLOW_UP_DUE` status, recommend: "X leads need follow-up. Want me to draft follow-up emails?"

---

### 7. Concierge Follow-ups

Check the concierge tracker for active guests with pending items:

```bash
{{EMAIL_CLI}} primary sheets-get --spreadsheet-id "{{SHEET_ID_CONCIERGE}}" --range "Guests!A:L"
```

Flag:
- Guests with upcoming check-ins who have pending concierge requests
- Restaurant reservations that need confirming
- Transfer bookings that need confirming
- Any concierge items marked as "waiting" or "pending"

---

### 8. Dynamic Pricing & MLOS

Run the dynamic-pricing skill via a sub-agent. The sub-agent dry-runs the tool, presents a diff, and pushes only after the operator approves.

```bash
{{PRICING_TOOL}} --format json
```

Spawn the `dynamic-pricing` sub-agent with the JSON output and let it render the diff. In the briefing, surface:

- "Dynamic pricing — N changes proposed across {rooms}. Awaiting approval." (if changes exist)
- "Dynamic pricing — no changes today." (if `changes` array is empty)

Do NOT push without explicit approval. After approval, the sub-agent runs the pricing tool's `--push` flag and refreshes any downstream mirror.

---

### 9. Task Review

```bash
{{EMAIL_CLI}} primary sheets-get --spreadsheet-id "{{SHEET_ID_TASKS}}" --range "Tasks!A1:H50"
```

Present tasks grouped by status:
- **In Progress** — what's actively being worked on
- **Urgent/High priority open items** — what should be tackled today
- **Waiting** — items that may need a nudge (flag if waiting >7 days)
- **Recently completed** — quick wins from yesterday

---

### 10. Recommendations

Based on ALL the above, recommend what the operator should focus on today. Be specific and actionable:
- "<Guest> accepted the upgrade — change room in the PMS and I'll draft the confirmation"
- "Supplier invoice needs filing — want me to process it?"
- "<Guest> checks in tomorrow — room not assigned yet"
- "Contractor hasn't called back in 11 days — follow up?"

---

## Output Format

Keep it scannable. Use this structure:

```
## Morning Briefing — {date}

### Emails — Needs Action
- {actionable email summaries with what to do}

### Emails — For Review
- {drafts pending, OTA notifications}

### Finances
- {invoices to file, payments received}

### Calendar
{today's events or "Calendar is clear today"}

### PMS
- Check-ins today: {list}
- Check-outs today: {list}
- Flags: {unassigned rooms, issues}

### Upgrades
- {opportunities and acceptances}

### Pre-Arrival
- {guests to contact}

### Concierge
- {pending items}

### Pricing & MLOS
- {N changes proposed — awaiting approval | no changes today}

### Tasks
- {key items by status}

### Today's Focus
1. {recommended action}
2. {recommended action}
3. {recommended action}

### Anything to add or update?
```

## Guardrails

- Never send emails — only create drafts, show to the operator for approval
- Never modify reservations without approval — flag, ask, change, draft, ask to send
- Never modify task statuses without confirming with the operator
- Use cost-efficient models for research subtasks
- Only check the configured hotel inboxes, never an unrelated personal account
- Read the BODY of every unread guest email, don't just scan subjects
- When OTA relay names don't match reservation names, cross-reference by booking number or check-in dates

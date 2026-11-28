# NeatSprint — UI/UX Design System & Screen Specification

> **Status**: Approved v1.0 · **Version**: 1.0 · **Last updated**: 2026-11-21
> **Owner/Designer**: OpenCade (AI, chief UI/UX) · **Reviewer**: Laksiri Fernando
> **Scope**: Web app (MVP), Desktop agent (MVP), Mobile (Phase 2)
> **Related**: `SCOPE.md` FR-WEB/FR-DSK, `ARCHITECTURE.md`, `TEST_PLAN.md` TS-07

---

## 1. Design Principles

| # | Principle | In practice |
| :--- | :--- | :--- |
| 1 | **Calm over dense** | Generous whitespace, one primary action per screen, progressive disclosure |
| 2 | **The work is the hero** | Boards and lists dominate; chrome recedes; no decorative dashboards |
| 3 | **Honest by design** | Recording state always visible; destructive actions state exactly what will happen |
| 4 | **Fast feels trustworthy** | Optimistic UI with clear rollback; skeletons instead of spinners |
| 5 | **Keyboard-first, mouse-friendly** | Every core action has a shortcut; drag-and-drop is never the only path |
| 6 | **Accessible by default** | AA contrast, visible focus, semantic markup, reduced motion respected |
| 7 | **Consistent rhythm** | One spacing scale, one radius scale, one set of components |

### 1.1 Personality

NeatSprint should feel like a **well-organised workshop**: precise, quiet, confident. Not a
surveillance console, not a toy. Copy is direct and human. Visuals are flat with soft elevation;
no gradients on data surfaces, no glassmorphism, no emoji in navigation.

### 1.2 Anti-patterns (explicitly rejected)

- Red "recording" treatments that feel punitive. Recording is amber, not red.
- Gamified streaks or leaderboards for time worked (encourages overwork).
- Hiding the privacy controls behind a settings maze.
- Infinite-scroll-only tables for audit data (needs pagination + filters).
- Colour-only status encoding.

---

## 2. Brand & Visual Identity

### 2.1 Logo & mark

- Wordmark: **NeatSprint** in Inter SemiBold, tightened tracking (-1%).
- Mark (final, 2026-11-28): a neon neural-brain on a deep-blue gradient plate, with a cyan orbit
  ring and circuit traces. App icon: 505×505, 22% corner radius, no text
  (`reference/neatsprint-brain-app-icon.png`).
- Banner lockup: mark + wordmark + "AI POWERED ENTERPRISE AGILE" on a 1536×495 plate
  (`reference/neatsprint-website-logo-brain.png`). Used on the sign-in brand panel.
- Usage: app shell and favicon use the square mark; never place the banner on a light surface
  without the plate, and never stretch or recolour either asset.

### 2.2 Colour tokens

Light theme:

| Token | Hex | Use |
| :--- | :--- | :--- |
| `--bg-canvas` | `#F8FAFC` | App background |
| `--bg-surface` | `#FFFFFF` | Cards, panels, tables |
| `--bg-subtle` | `#F1F5F9` | Hover rows, inset areas |
| `--bg-inverse` | `#0F172A` | Tooltips, toasts |
| `--border-default` | `#E2E8F0` | Dividers, card borders |
| `--border-strong` | `#CBD5E1` | Inputs, focusable outlines (non-focus) |
| `--text-primary` | `#0F172A` | Headings, body |
| `--text-secondary` | `#475569` | Labels, metadata |
| `--text-tertiary` | `#94A3B8` | Placeholders, disabled |
| `--text-inverse` | `#F8FAFC` | On dark surfaces |
| `--primary-600` | `#4F46E5` | Primary buttons, links, active nav |
| `--primary-700` | `#4338CA` | Hover |
| `--primary-100` | `#E0E7FF` | Selected row, chips |
| `--accent-500` | `#06B6D4` | Focus rings, data accents |
| `--success-600` | `#059669` | Done, success toast |
| `--warning-500` | `#F59E0B` | Recording state, pending, warnings |
| `--danger-600` | `#DC2626` | Destructive, errors |
| `--info-500` | `#0EA5E9` | Informational callouts |

Dark theme:

| Token | Hex |
| :--- | :--- |
| `--bg-canvas` | `#0B1120` |
| `--bg-surface` | `#111827` |
| `--bg-subtle` | `#1F2937` |
| `--border-default` | `#1F2937` |
| `--border-strong` | `#334155` |
| `--text-primary` | `#F1F5F9` |
| `--text-secondary` | `#94A3B8` |
| `--primary-600` | `#6366F1` |
| `--primary-700` | `#818CF8` |

**Status colours** (always paired with an icon and a label):

| Status | Light | Dark | Icon |
| :--- | :--- | :--- | :--- |
| To do | `#64748B` | `#94A3B8` | circle |
| In progress | `#2563EB` | `#60A5FA` | half-circle |
| In review | `#7C3AED` | `#A78BFA` | eye |
| Blocked | `#DC2626` | `#F87171` | octagon |
| Done | `#059669` | `#34D399` | check |

Priority: Low `#64748B`, Medium `#0EA5E9`, High `#F59E0B`, Urgent `#DC2626`.

Contrast: every text token pair must pass 4.5:1 (normal) / 3:1 (large). Accent is decorative only
and never the sole carrier of meaning.

### 2.3 Typography

| Role | Font | Size / line | Weight |
| :--- | :--- | :--- | :--- |
| Display | Inter | 36 / 44 | 600 |
| H1 (page title) | Inter | 24 / 32 | 600 |
| H2 (section) | Inter | 20 / 28 | 600 |
| H3 (card title) | Inter | 16 / 24 | 600 |
| Body | Inter | 14 / 22 | 400 |
| Body large | Inter | 16 / 26 | 400 |
| Label | Inter | 13 / 18 | 500 |
| Caption / meta | Inter | 12 / 16 | 400 |
| Mono (IDs, keys, time) | JetBrains Mono | 13 / 20 | 400 |

Rules: max line length 72ch for prose; numerals tabular in tables; no all-caps except 11px
overline labels with 2% tracking; never below 12px.

### 2.4 Spacing, radius, elevation, motion

- **Spacing**: 4px base — `4, 8, 12, 16, 24, 32, 40, 48, 64`.
- **Radius**: `sm 6`, `md 8`, `lg 12`, `xl 16`, `full 9999`. Buttons `md`, cards `lg`, drawer `xl`,
  avatars/chips `full`.
- **Elevation**:
  - `e1`: `0 1px 2px rgba(15,23,42,.06)`
  - `e2`: `0 4px 12px rgba(15,23,42,.08)`
  - `e3`: `0 12px 32px rgba(15,23,42,.14)` (drawer, popover)
- **Motion**: 120 ms micro, 200 ms panel, 280 ms page. Easing `cubic-bezier(.2,.8,.2,1)`.
  Respect `prefers-reduced-motion` (fade only, no transforms).
- **Focus ring**: 2px `--accent-500` with 2px offset; never removed.

### 2.5 Iconography

Lucide icons, 1.5 px stroke, 16/20/24 sizes. Icons always pair with a label in navigation; icon-only
buttons require `aria-label` and a tooltip.

---

## 3. Information Architecture

```text
NeatSprint (web)
├── Dashboard                 /
├── Work
│   ├── Projects              /projects
│   ├── Project → Backlog     /projects/:id/backlog
│   ├── Project → Board       /projects/:id/board
│   ├── Project → Sprints     /projects/:id/sprints
│   └── Item drawer           (overlay, deep-linkable)
├── My work
│   ├── Timesheet             /me/timesheet
│   ├── My screenshots        /me/screenshots
│   └── Transparency log      /me/transparency
├── Team
│   ├── Teams                 /teams
│   └── Members               /teams/:id
├── Insights
│   ├── Reports               /reports
│   └── Monitoring            /reports/monitoring
└── Admin
    ├── Users                 /admin/users
    ├── Roles                 /admin/roles
    ├── Tenant settings       /admin/settings
    ├── Modules               /admin/modules
    └── Audit log             /admin/audit
```

Navigation rules:

- Sidebar collapses to icons under 1280 px, hides under 768 px behind a menu button.
- Active section has a 3 px primary bar and `--primary-100` background.
- Nav items are hidden when the user lacks the corresponding view permission (never shown then
  disabled, except "My work" which is always present).
- Mobile web uses a bottom bar for Dashboard / Projects / My work / More.

---

## 4. Layout Shell

```text
┌──────────────────────────────────────────────────────────────┐
│ Topbar: [tenant + module]      [search]   [timer] [bell] [av]│
├──────────┬───────────────────────────────────────────────────┤
│ Sidebar  │ Page header: title · breadcrumb · actions         │
│          ├───────────────────────────────────────────────────┤
│ nav      │ Content (max 1440 px, 24 px gutters)              │
│          │                                                   │
│ [privacy]│                                                   │
└──────────┴───────────────────────────────────────────────────┘
```

- **Topbar** (56 px): tenant name + enabled apps switcher, global search (`Ctrl/⌘ K`), live timer
  pill, notification bell, and — flush right — a **Neat AI** placeholder pill (dashed outline,
  disabled, "Neat AI is coming soon") immediately left of the **avatar menu**. The avatar shows the
  user's initials; clicking it opens a menu with the full name, email and **Sign out**. The name and
  sign-out control live only in this menu, not inline in the topbar.
- **Timer pill**: shows `● 01:24:36 · AUTH-142` when running; click opens the timer popover
  (switch task, stop, open desktop). Amber dot = recording; grey = idle.
- **Sidebar** (240 px): navigation, and at the bottom a **Privacy card** — "Screenshots are on /
  paused. Review your captures." This is a permanent, visible affordance.
- **Content**: max width 1440 px; tables may use full width; forms cap at 720 px.

---

## 5. Component Library

Built on shadcn/ui primitives with NeatSprint tokens. Stored in `components/ui` and demonstrated
on `/design` (internal page).

| Component | Variants | Notes |
| :--- | :--- | :--- |
| `Button` | primary, secondary, ghost, danger; sm/md | Loading state replaces label with spinner + keeps width |
| `IconButton` | ghost, subtle | Requires `aria-label` + tooltip |
| `Input`, `Textarea`, `Select` | default, error, disabled | Label above, helper text below, error replaces helper |
| `Combobox` | single/multi, async | Used for assignee, labels, teams |
| `Badge` | status, priority, neutral | Icon + text, never colour-only |
| `Avatar` | xs/sm/md, stack | Initials fallback; presence dot optional |
| `Card` | surface, interactive | `e1`, 12 px radius |
| `DataTable` | dense, comfortable | Sticky header, column chooser, pagination, selection |
| `KanbanColumn` | default, collapsed, WIP-limit | Drag handle, count, add button |
| `Drawer` | right, 480/640 | Item detail, filters; ESC closes; focus trap |
| `Modal` | sm/md/lg | Destructive confirmations, invitations |
| `Toast` | success, error, info | Bottom-right, 5 s, dismissible, `aria-live` |
| `Tabs` | underline | Project views |
| `Timeline` | compact | Item history, transparency log |
| `EmptyState` | illustration + title + body + action | Required for every list |
| `Skeleton` | text, card, table-row | Matches final layout |
| `PrivacyPill` | recording, paused, off | Icon + label + tooltip |
| `TimerPill` | running, paused, idle | Tabular numerals |
| `TimeCell` | duration, overtime | `hh:mm` with tooltip of exact seconds |
| `ConfirmDialog` | default, destructive | Requires explicit verb ("Delete screenshot") |

### 5.1 Interaction rules

- Destructive actions require a confirmation dialog naming the object and consequence.
- Optimistic updates: board moves and status changes apply instantly; on failure, revert with a
  toast explaining why.
- Autosave on blur for inline edits; explicit Save only for forms with multiple fields.
- Never block the whole screen for a single save; use inline progress.
- Dialogs close on ESC and restore focus to the trigger.
- All async actions expose pending/success/error states.

---

## 6. Screen Inventory — Web MVP

Each screen lists its purpose, primary action, key components, permissions and states.

### S-01 Login

- **Purpose**: authenticate.
- **Layout**: split — left brand panel with a one-line value statement, right form card (max 400 px).
- **Elements**: email, password, show/hide, "Sign in", "Continue with Google", "Forgot password?",
  invite-only note.
- **States**: idle, submitting, invalid credentials, locked, rate limited, SSO error.
- **Copy**: heading "Welcome back"; sub "Sign in to your workspace."
- **A11y**: labels, autocomplete attributes, error summary announced.

### S-02 Accept invitation

- **Shows**: tenant name and logo, invited email (read-only), full name, password + confirm,
  optional Google button.
- **States**: valid, expired (with "Ask your admin to resend"), already accepted (link to login).

### S-03 Forgot / reset password

- Single email field; neutral confirmation "If that email exists, we sent a reset link." Reset form
  has password + confirm and a success state that redirects to login.

### S-04 Dashboard

- **Purpose**: answer "what should I do now?"
- **Widgets** (role-aware):
  - My day: running timer, today's logged time, and every item assigned to you in an **active
    sprint** (items outside an active sprint are excluded; Done is included), ordered
    In progress → To do → In review → Blocked → Done. The list shows up to five items, each with
    its status badge, and a **More… (n)** control expands the rest; **Show less** collapses it
    again. When nothing qualifies it shows the hint "No active-sprint items."
  - Sprint pulse: active sprint name, days left, progress bar, blocked count.
  - Team activity (managers): active members now, items moved yesterday.
  - Privacy summary (self): captures today, deletions, link to transparency log.
- **Primary action**: "Start timer" (or "Continue AUTH-142").
- **Empty state**: onboarding checklist (invite team, create project, install agent).
- **States**: no projects, no active sprint, agent not installed (callout with download link).

### S-05 Projects list

- **Layout**: header with count + "New project"; toolbar (search, status filter, sort); table or
  card grid toggle.
- **Columns**: key, name, teams, open items, sprint state, updated.
- **States**: empty ("Create your first project"), filtered-empty, archived toggle.

### S-06 Project settings

- Tabs: General (name, key read-only after creation, description, dates, status), Teams, Danger
  zone (archive).
- **Guard**: archive confirmation explains read-only behaviour.

### S-07 Backlog

- **Layout**: toolbar (search, type filter, priority, assignee, group by), table with inline edit.
- **Rows**: drag handle, type icon, key, title, status badge, priority, assignee avatar, estimate,
  sprint chip, updated.
- **Bulk bar** appears on selection: assign, move to sprint, set priority, delete.
- **Keyboard**: `↑/↓` row focus, `Enter` open drawer, `Space` select, `E` edit title.
- **States**: empty backlog, no results, permission-limited (no create button).

### S-08 Board

- **Layout**: sprint header (name, dates, progress, complete button) + columns.
- **Columns**: To do, In progress, In review, Blocked, Done (configurable WIP limits).
- **Card**: key, title, priority dot, assignee, estimate, comment count, blocked icon.
- **Interactions**: drag between columns (keyboard: `Ctrl/⌘ + ←/→` moves focused card), quick-add
  at column footer.
- **Edge cases**: WIP limit reached (column header warning, drop still allowed with confirm),
  item hidden by filter (toast "1 item moved out of view").
- **Performance**: virtualised columns over 200 cards.

### S-09 Sprint planning

- **Layout**: two-pane. Left: backlog with filters and estimate sum. Right: sprint basket with
  capacity bar (committed vs team capacity).
- **Actions**: add/remove, "Start sprint" (disabled until at least one item), save draft.
- **States**: no planned sprint, sprint already active.

### S-10 Sprint detail / completion

- Header metrics: committed points, completed, carried over, velocity delta.
- Completion dialog: lists unfinished items with per-item choice (back to backlog / next sprint),
  and a note that history is preserved.
- Empty state: sprint not started.

### S-11 Item detail drawer

- **Header**: key + type, title (inline edit), status select, priority, close.
- **Body**: description (rich text), activity tabs (Comments / History / Attachments / Time).
- **Sidebar**: assignee, reporter, sprint, estimate, due date, labels, created/updated.
- **Actions**: assign, transition, delete (confirm).
- **Mobile**: full-screen sheet.
- **States**: read-only for viewer; archived project banner.

### S-12 My timesheet

- **Layout**: week switcher, grid (rows = items, columns = Mon–Sun), totals row/column, "Add entry".
- **Cells**: duration, click to edit; entries coloured by source (timer vs manual).
- **Header**: total hours, billable indicator (P3), export CSV.
- **Empty state**: "No time logged this week" + start timer.

### S-13 My screenshots

- **Purpose**: fulfil the privacy promise in the UI.
- **Layout**: intro banner explaining the window ("You can delete any screenshot for 23 h 12 m
  after capture. After that, it stays in your team's activity record."), tabs Pending / Visible.
- **Card**: thumbnail (blurred until hover/click for shoulder-surfing), captured time, task,
  countdown, "Delete" button.
- **Delete dialog**: "Delete this screenshot permanently? Your manager will see that it was deleted,
  but not the image. This cannot be undone." Buttons: Cancel / Delete permanently.
- **After deletion**: card becomes a muted tombstone "Deleted by you · 10:42".
- **States**: no captures, agent not running, window closed (delete disabled with reason).

### S-14 Manager monitoring

- **Layout**: filters (team, member, date range), summary strip (sessions, active time, captures,
  deletions), timeline + thumbnail grid grouped by session.
- **Tombstone card**: hatched background, trash icon, "Deleted by user at 10:42", no image, no
  retry.
- **Pending**: never shown; if a date range includes pending captures the count says "in review".
- **Audit notice**: "Viewing a screenshot is recorded in the audit log." persistent, small.
- **Permission**: `monitor:data:view_team` / `view_all`.

### S-15 Transparency log

- **Layout**: filterable timeline (date, project, status) with export.
- **Rows**: time, project/item, device, capture status, deletion time.
- **Copy**: "This is everything NeatSprint recorded about your work."

### S-16 Reports hub

- Cards: Time, Completion, Velocity, Burndown, Monitoring, Transparency, plus Export centre.
- Each card states the question it answers and the required permission; unavailable cards are
  hidden, not disabled.

### S-17 Time report

- Filters: date range presets (this week, last week, this sprint, custom), group by project/user/
  team, team/project filters.
- Visual: horizontal stacked bars + table. Toggle "Show table" for accessibility.
- Export CSV / PDF in the header.

### S-18 Velocity & burndown

- Velocity: bar chart last 5–8 sprints + average line; table of committed/completed/carried over.
- Burndown: line chart with ideal dotted line; tooltip shows remaining points/items; blocked
  markers.
- Both include a "How this is calculated" disclosure.

### S-19 Monitoring summary report

- Heatmap (day × hour) of active time; deletion-rate card; table by member.
- Aggregation mode banner when individual rows are hidden, explaining the threshold.

### S-20 Export centre

- Table of jobs: type, filters, status, created, expires, download.
- Failed job shows reason and retry.

### S-21 Teams

- Team list with member counts; detail with members table, lead assignment, project associations.
- Lead gets add/remove controls; others read-only.

### S-22 Users (admin)

- Table: name, email, roles, teams, status, last active.
- Actions: invite (dialog), edit roles, deactivate, resend invite.
- Bulk invite via CSV (P2).

### S-23 Roles (admin)

- System roles matrix (read-only in MVP), custom roles list (P3 for editing).
- Matrix rows = permissions grouped by domain, columns = roles, cells = check.
- Search permissions; "show only differences" toggle.

### S-24 Tenant settings (admin)

- Sections: General (name, timezone, week start), Monitoring policy (interval min/max, privacy
  window, retention, displays), Modules (toggles with plan lock), Danger zone (close tenant).
- **Copy guard**: changing the privacy window shows "This applies to new captures. Existing
  screenshots keep their original window."

### S-25 Modules

- Card per application: name, description, status, plan requirement, enable/disable.
- Disabled module shows what is hidden, not a broken screen.

### S-26 Audit log

- Filters: actor, action, target type, date range. Table with expandable before/after diff.
- Read-only, export CSV (admin).

### S-27 Onboarding checklist

- Three steps: invite your team, create a project, install the desktop agent.
- Dismissible; reappears in the dashboard empty state until complete.

### S-28 Design page (internal)

- Token swatches, typography scale, component gallery, states. Not linked in production nav.

### S-29 Error pages

- 403 (permission), 404, 500, offline. Each has a clear headline, one sentence of cause, and a way
  forward ("Go to my projects", "Retry", "Contact admin").

### S-30 Command palette

- `Ctrl/⌘ K`: navigate, create item, start/stop timer, open my screenshots.
- Fuzzy search, grouped results, keyboard-only operation.

---

## 7. Key Flows

### 7.1 First login → first tracked minute (target ≤ 3 min)

```text
Login → Dashboard (empty) → Onboarding card
  → [Install agent] download → tray login (device registered)
  → [Create project] name + key → project created
  → [Add item] title → item in backlog
  → Board → Start timer on item → Timer pill running
  → Toast: "Tracking AUTH-1. Screenshots are on — review them anytime."
```

Design notes: never show a blank dashboard; the checklist is the empty state. The agent download
includes a 3-step install guide with a "I've installed it" poll.

### 7.2 Delete a screenshot (trust-critical)

```text
My screenshots → Pending tab → card hover → Delete
  → ConfirmDialog (explicit consequence) → Delete permanently
  → Optimistic tombstone + toast "Screenshot deleted. It cannot be recovered."
  → (server) blob + embeddings destroyed, audit written
  → Manager view (later) shows tombstone only
```

Rules: the button is never hidden behind a menu; the countdown is always visible; a failed deletion
restores the card and explains the error; there is no "undo".

### 7.3 Sprint planning

```text
Project → Sprints → New sprint (name, goal, dates)
  → Planning: drag items from backlog to sprint; capacity bar updates
  → Start sprint (confirm: scope snapshot)
  → Board active; timer can attach
  → Complete sprint → carry-over dialog → summary
```

### 7.4 Invite a teammate

```text
Admin → Users → Invite
  → email + roles + teams → Send
  → row appears as "Invited" with resend/revoke
  → invitee accepts → status becomes Active
```

### 7.5 Manager reviews a day

```text
Reports → Monitoring → filters (team, yesterday)
  → summary strip → member timeline → screenshot grid
  → click thumbnail (audited) → drawer with capture time + task
  → tombstones visible as evidence of user deletion
```

---

## 8. Desktop Agent UI

Tray-first. The main window is only opened deliberately; the tray menu covers daily actions.

### 8.1 Tray menu

```text
NeatSprint
──────────────────────────────
● Tracking  AUTH-142  01:24:36
  Switch task…
  Pause
  Stop
──────────────────────────────
Screenshots: on (review 3)
Open NeatSprint
Settings
Quit
```

### 8.2 Main window

| Area | Contents |
| :--- | :--- |
| Header | logo, sync state (`Synced 1m ago` / `Offline — 12 items queued`), settings, minimise |
| Timer card | current task key/title, large elapsed time, Start/Pause/Stop, task switcher |
| Today | total tracked, sessions strip, idle time |
| Review strip | "3 screenshots waiting for review" with thumbnails and countdown |
| Footer | version, device name, privacy link |

### 8.3 Review tray

- Grid of pending captures with countdown badges.
- Click → preview (decrypted in memory), metadata (time, task, display).
- Actions: **Keep** (upload now), **Delete permanently** (confirm), close.
- Copy: "If you do nothing, this is shared with your team when the review window ends in 22 h 14 m."
- Amber banner: "Screenshots are only taken while your timer is running."

### 8.4 Agent states

| State | UI |
| :--- | :--- |
| Signed out | Login window, device registration progress |
| Idle (no timer) | Grey dot, "Not tracking" |
| Tracking | Amber dot, elapsed time, toast at each capture |
| Paused (idle) | Amber outline, "Paused — no activity" + Keep/Discard segment prompt |
| Offline | Cloud-off icon, queue count, "Still tracking locally" |
| Suspended by admin | Locked overlay with reason and contact |
| Revoked | Login screen, "This device was signed out by your admin" |
| Update available | Non-blocking banner with "Restart to update" |
| Error | Red banner with a specific cause and a diagnostics action |

### 8.5 Idle prompt

```text
You've been idle for 8 minutes.
[Keep 8 min]  [Discard]  [Keep and continue]
```
Focus the safest choice (`Keep`), never auto-discard silently.

### 8.6 Notifications

- Capture: `Screenshot taken · 10:42` (2 s, non-interactive, no thumbnail).
- Delete success: `Screenshot deleted permanently.`
- Sync failure: `Can't reach NeatSprint — your work is saved locally.`
- Revoked: persistent dialog.

---

## 9. Mobile App (Phase 2)

Screens: Sign in (biometric unlock), Home (my day), My work (list + detail), Timer remote,
Notifications, Chat, Profile.
Rules: read-first; status update and manual time are the only writes; chat is full-featured; no
screenshot review on mobile in P2 (desktop only) to avoid confusing the privacy story.

---

## 10. Content & Microcopy

### 10.1 Voice

- Plain, calm, specific. Short sentences. No jargon, no exclamation marks, no blame.
- Always say what will happen, not just what the button does.
- Use "screenshot" (not "screen capture"), "review window" (not "grace period"), "your admin"
  (not "the administrator").

### 10.2 Standard strings

| Context | Copy |
| :--- | :--- |
| Empty project list | "No projects yet. Create one to start planning work." |
| Empty backlog | "This backlog is empty. Add your first item to get started." |
| No search results | "No matches for “{query}”. Try a different term or clear filters." |
| Delete screenshot title | "Delete this screenshot?" |
| Delete screenshot body | "Your manager will see that it was deleted, but never the image. This cannot be undone." |
| Delete confirm | "Delete permanently" |
| Delete success | "Screenshot deleted. It cannot be recovered." |
| Window closed | "The review window has closed. Contact your admin if this was a mistake." |
| Recording indicator tooltip | "Screenshots are taken at random intervals only while your timer is running." |
| Agent offline | "You're offline. NeatSprint is still tracking and will sync when you reconnect." |
| Permission denied | "You don't have permission to do that. Ask your admin if you need access." |
| Session expired | "Your session ended. Sign in again to continue." |
| Archive project | "Archive “{name}”? It becomes read-only and disappears from active views." |
| Invite sent | "Invitation sent to {email}." |
| Export ready | "Your export is ready. The link expires in 24 hours." |
| Aggregation mode | "Individual results are hidden because this team is smaller than {n} people." |
| Confirm sprint start | "Start “{name}”? Scope is saved as a snapshot for burndown and velocity." |

### 10.3 Dates, numbers, time

- Dates: `21 Nov 2026`; relative within 7 days (`Yesterday`, `Tue 18 Nov`).
- Time: 24-hour (`14:30`) with the user's timezone shown in settings.
- Durations: `1h 24m`, never `84m` in UI (exact seconds in tooltips).
- Numbers: locale-aware thousands separators; points shown without decimals unless half-points.

---

## 11. States (mandatory for every screen)

| State | Requirement |
| :--- | :--- |
| Loading | Skeleton matching final layout; no full-page spinner |
| Empty | Illustration/icon, one-sentence explanation, primary action |
| Filtered empty | Explains the filters applied + "Clear filters" |
| Error | What failed, whether data is safe, retry action, error id for support |
| Permission denied | What is missing and who to ask, no dead end |
| Offline | Banner with queue status; read-only caches marked "Last updated …" |
| Partial | Shows available data and flags what is missing |
| Success | Toast for actions; inline confirmation for settings |

---

## 12. Accessibility

- WCAG 2.1 AA baseline; AAA contrast for body text where the palette allows.
- Semantic landmarks: `header`, `nav`, `main`, `aside`; one `h1` per page.
- All interactive elements reachable by Tab in visual order; focus visible at all times.
- Drag-and-drop always has a keyboard alternative (documented per screen).
- Live regions announce toasts, save state, and timer changes (throttled to avoid chatter).
- Forms: explicit labels, `aria-describedby` for help/errors, error summary at the top on submit.
- Charts: data table alternative, patterns in addition to colour, accessible summaries.
- Images require alt text; decorative images are `alt=""`; screenshot thumbnails use
  "Screenshot of {task} at {time}" and never expose content in alt text.
- Motion: reduced-motion disables slides/scales; no autoplay animation.
- Target size: minimum 32×32 px (44×44 for mobile); spacing between targets ≥ 8 px.
- Screen-reader test matrix: NVDA + Chrome (Windows), VoiceOver + Safari (macOS/iOS).

---

## 13. Responsive Behaviour

| Breakpoint | Behaviour |
| :--- | :--- |
| ≥ 1440 px | Full shell, 5 board columns visible, right drawer 640 px |
| 1280–1439 | Sidebar icons-only optional, board horizontal scroll |
| 1024–1279 | Sidebar collapsible, tables drop secondary columns |
| 768–1023 | Drawer full-width, reports stack, board scrolls |
| < 768 | Bottom nav, single column, item drawer full-screen, tables become cards |

No horizontal page scroll at any breakpoint. Board columns scroll inside their container.

---

## 14. Design Deliverables & Handoff

| Item | Location |
| :--- | :--- |
| Tokens (source of truth) | `services/neatsprint-web/src/styles/tokens.css` + Tailwind config |
| Component gallery | `/design` route (dev/staging only) |
| Screen specs | this document |
| Copy deck | §10 + `services/neatsprint-web/src/i18n/en.json` |
| Icon set | Lucide via `lucide-react` |
| Assets | `services/neatsprint-web/public/brand/` |

Rules: no hard-coded hex values in components; no custom font sizes outside the scale; any new
component must be added to `/design` and documented here before use in a feature.

---

## 15. UI Acceptance Checklist (per milestone)

- [x] Every screen in this document exists with empty/error states *(route `loading.tsx` removed in v1.0.2; see §16)*
- [ ] All copy matches §10 and is externalised in `en.json`
- [x] Keyboard-only path works for every primary flow
- [x] axe: zero serious/critical violations on all routes
- [x] Light and dark themes reviewed
- [x] 1024 px and 1440 px layouts reviewed
- [x] No colour-only status encoding
- [x] Destructive actions name the object and consequence
- [x] Privacy affordances visible on every relevant screen (dashboard, gallery, agent tray)
- [x] Design page updated with new components

---

## 16. Required Improvements (Post-v1.0.2 Review)

The following UI/UX gaps and alignment items were identified during the post-v1.0.2 review:

- [ ] **IMP-UX-01 (Enable `Reports` in desktop sidebar navigation — S2)**: In
  `services/neatsprint-web/src/components/app-shell.tsx:52`, `Reports` is still marked
  `enabled: false` without `href: "/reports"`, even though `/reports` and all sub-reports shipped in
  M4 and are linked on mobile nav and the dashboard (`IMP-T03`).
- [ ] **IMP-UX-02 (Gate Backlog `New item` on `task:item:create` — S2)**:
  `projects/[id]/backlog/page.tsx:87` passes `canEdit` (`task:item:edit`) to `BacklogClient`, which
  uses it to gate the **New item** button. Because `MEMBER` holds `task:item:create` but not
  `task:item:edit`, members cannot create backlog items in the UI. Pass a separate `canCreate` prop
  (`IMP-T03`).
- [ ] **IMP-UX-03 (Project sub-navigation `Settings` tab — S2)**: The project sub-navigation on
  `Board`, `Backlog` and `Planning` pages only shows `Board | Backlog | Planning`, omitting the
  `Settings` tab (`/projects/:id/settings`) which only appears when already on the Settings page
  (`IMP-T03`).
- [ ] **IMP-UX-04 (Live topbar timer pill — S2)**: The topbar timer indicator in `AppShell`
  (`app-shell.tsx:148`) is hardcoded to `"No timer running"`. Connect it to
  `/api/session/work/current` so it displays the active session (`● hh:mm:ss · KEY`) and allows
  stopping the timer per §4 (`IMP-T03`).
- [ ] **IMP-UX-05 (Reconcile IA route paths in §3)**: Update §3 Information Architecture to reflect
  the canonical implemented routes (`/projects/:id/planning` instead of `/sprints`, `/timesheet`
  instead of `/me/timesheet`, inline team member cards on `/teams`, and modules inside
  `/admin/settings`).
- [ ] **IMP-UX-06 (Client-safe loading states & Next.js 16 streaming)**: Route-level `loading.tsx`
  files were removed in `v1.0.2` because Next.js 16 standalone streaming left pages stuck on
  `"Loading…"`. Provide client-side transition skeletons or resolve the Next.js 16 RSC streaming
  issue so §11 Loading state is met without hanging navigation.
- [ ] **IMP-UX-07 (Externalise UI copy to `src/i18n/en.json` & link legal pages)**: Extract inline
  component strings into `services/neatsprint-web/src/i18n/en.json` (§14) and add footer links to
  Terms, Privacy Policy, DPA and Monitoring Disclosure (`IMP-T10`).

---

**End of UI/UX Design**

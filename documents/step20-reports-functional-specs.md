# NeatSprint – Step 20: Reports Functional Specifications

This document defines the **Functional Requirements** and **Metric Logic** for the reporting module. It is powered by the architectural components defined in **[Step 19: Reports Architecture](step19-reports-architecture.md)**.

---

## 1. Productivity Reports

These reports track resource utilization and time efficiency.

### 1.1. Time Spent by Project
**Visual**: Stacked Bar Chart (X: Date, Y: Hours, Segment: Project)
**Purpose**: High-level view of where effort is going.

| Metric | Calculation Logic |
| :--- | :--- |
| **Total Hours** | $\sum(\text{Session Duration})$ where status = SYNCED |
| **Billable Hours** | Total Hours where Project is tagged "Billable" |
| **Cost Estimate** | Total Hours $\times$ User Hourly Rate (RBAC Protected) |

### 1.2. User Efficiency
**Visual**: Scatter Plot (X: Actual Time, Y: Estimated Time)
**Purpose**: Identify estimation accuracy drifts.

-   **Efficiency Score**: $(\frac{\text{Estimated Time}}{\text{Actual Time}}) \times 100\%$
    -   $> 100\%$: Completed faster than estimated.
    -   $< 100\%$: Took longer than estimated.

---

## 2. Agile Process Reports

These reports track the team's delivery velocity and process health.

### 2.1. Sprint Burndown
**Visual**: Dual Line Chart (Ideal Trend vs. Remaining Effort)
**Purpose**: Daily tracking of sprint completion probability.

-   **Ideal Line**: Linear decay from Total Points to 0 over Sprint duration.
-   **Remaining Effort**: $\sum(\text{Points of Tasks not DONE})$.

### 2.2. Team Velocity
**Visual**: Bar Chart (Last 5 Sprints)
**Purpose**: Predict future capacity based on historical performance.

-   **Velocity**: $\sum(\text{Story Points})$ of items moved to **DONE** within the Sprint window.
    -   *Excludes*: Items removed from sprint.
    -   *Excludes*: Items completed *after* sprint close.

---

## 3. Monitoring & Transparency Reports

These reports provide insight into activity while rigorously enforcing privacy.

### 3.1. Work Monitoring Summary
**Visual**: Heatmap (Activity intensity by hour)
**Audience**: Managers, Admin.

| Metric | Calculation Logic |
| :--- | :--- |
| **Active Time** | Time where `idle_seconds < threshold`. |
| **Idle Time** | Time where `idle_seconds > threshold`. |
| **Screenshot Count** | Total valid screenshots stored. |
| **Privacy Deletions** | Count of `deleted_by_user=true` records. |

**Privacy Rule (Critical)**:
-   If a screenshot is deleted by the user, the *time* associated with that screenshot is **NOT** deducted from "Active Time".
-   *Rationale*: The user worked, but chose to hide the visual proof. The time is valid, the visual is not.

### 3.2. User Transparency Log
**Visual**: Timeline List
**Audience**: The Individual User (Employee).

-   Shows a precise log of everything sent to the server.
-   **Columns**: Time, Project, Window Title, Screenshot Status (Stored/Deleted).
-   **Action**: Allows "Retroactive Delete" within the configuration window (e.g., 24h).

---

## 4. Compliance & Audit

### 4.1. Access Audit Log
**Visual**: Data Grid (Filterable)
**Purpose**: Security compliance (SOC2 / ISO 27001).

-   **Log Events**: Login, Failed Login, Password Change, Role Change, Report Export.
-   **Retention**: Immutable for 1 year (configurable).

---

## 5. AI Insights (Enterprise)

### 5.1. Daily Work Summary
**Format**: Text Paragraph (GenAI)
**Input**:
-   List of tickets touched.
-   Commit messages (GitHub integration).
-   Worklog comments.

**Output Example**:
> *"John focused on the **Auth Module** today. He completed the **Login Flow** (Task-101) and started investigation on **SSO Integration** (Task-102). No blockers reported."*

---

**End of Functional Specs**

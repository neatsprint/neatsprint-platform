# Database Review & Partition Maintenance

Date: 2026-11-24

## Index review

| Service | Table | Indexes | Purpose |
| :--- | :--- | :--- | :--- |
| Task | `backlog_items` | `(tenant_id, project_id, sprint_id, status, rank)`, `(tenant_id, assignee_id)` | Board/backlog ordering and my-work |
| Task | `item_comments` | `(item_id, created_at)` | Drawer timeline |
| Task | `saved_views` | unique `(tenant_id, user_id, project_id, name)` | Personal views |
| Team | `team_members` | PK `(team_id, user_id)`, tenant index | Membership lookups |
| Worklog | `work_sessions` | `(tenant_id, user_id, started_at)`, partial unique open session | Timer lookup |
| Worklog | `time_entries` | `(tenant_id, user_id, started_at)`, `(tenant_id, project_id, started_at)`, `(tenant_id, client_id)` | Timesheet, reports, sync |
| Monitoring | `screenshots` | owner pending, manager gallery, session | Privacy/gallery queries |
| Monitoring | `activity_heartbeats` | `(session_id, recorded_at)` | Session aggregation |
| Reports | facts | tenant/date, project, user, sprint | Report filters |

Slow-query log should be enabled in staging with `log_min_duration_statement = 500ms`; no slow
queries were observed locally at demo scale.

## Partition maintenance

`scripts/maintenance/partitions.py` pre-creates:

- Worklog monthly partitions for the current month + 3 months.
- Monitoring weekly partitions for the current week + 5 weeks.

Run nightly from cron/CI:

```bash
python scripts/maintenance/partitions.py
```

The script is idempotent (`CREATE TABLE IF NOT EXISTS ... PARTITION OF`). The default partition
catches out-of-range rows until the next run.

## Follow-ups

- Add an alert if the default partition receives rows.
- Schedule the script in the staging/production maintenance job.
- Revisit monthly partitioning for `activity_heartbeats` at scale.

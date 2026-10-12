# DECISIONS.md

1. **Indexes:**
   We created a unique index on `employees.emp_code` (enforcing business code uniqueness) and a unique compound index on `attendance_logs.(emp_code, date)` (guaranteeing one record per employee-day and preventing race conditions). We created `attendance_logs.(date: -1, emp_code: 1)` for fast paginated listing and `(emp_code: 1, punch_in: -1)` for rapid punch-out lookups. We considered and rejected indexing `history` or standalone `late_minutes`, as query patterns are strictly bounded by date or employee.

2. **Punch-in race:**
   Both simultaneous requests validate the employee and compute the same attendance date. Both attempt `insert_one`. MongoDB's unique index on `(emp_code, date)` grants an atomic insert to the first request (returning 201). The second request immediately triggers a `DuplicateKeyError`, which our code intercepts and converts to HTTP 409 Conflict.

3. **Ties:**
   We apply Standard Competition Ranking (1, 2, 2, 4). When employees tie on `total_late_minutes`, they receive the identical rank, and subsequent ranks are skipped. Filtering occurs *after* ranking (`rank <= limit`), so our leaderboard returns all tied employees at the cutoff, ordered secondarily by `emp_code`.

4. **Headcount:**
   Our aggregation pipeline initiates from the `employees` collection (filtering `joined_on <= month_end`) and executes a `$lookup` into `attendance_logs`. Employees with zero attendance logs remain preserved in the pipeline, ensuring exact headcount figures.

5. **One thing you would change for 100x data:**
   Shard `attendance_logs` on a compound shard key `(date, emp_code)` and maintain pre-aggregated monthly summary rollups updated via Change Streams to eliminate costly multi-collection lookups at query time.

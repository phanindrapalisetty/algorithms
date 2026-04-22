# Interview Prep: SQL & Python Questions
**Role**: Senior Analytics & Data Engineer  
**Context**: CoderByte assessment, DS interviewer, analytics engineering focus

---

## SQL Questions

Each question includes a dataset you can run locally (SQLite / DuckDB / PostgreSQL compatible).

---

### Q1 — Period-over-Period Revenue Change per SKU

**Difficulty**: Medium  
**Concepts**: Window functions, LAG, PARTITION BY

**Scenario**: You're given a monthly billing metrics table. Compute month-over-month revenue change and percentage change per SKU. Flag SKUs where revenue dropped more than 20% vs the prior month.

**Dataset**:
```sql
CREATE TABLE billing_metrics (
    sku        TEXT,
    month      DATE,
    revenue    NUMERIC
);

INSERT INTO billing_metrics VALUES
('DataPlus',    '2024-01-01', 50000),
('DataPlus',    '2024-02-01', 62000),
('DataPlus',    '2024-03-01', 58000),
('DataPlus',    '2024-04-01', 44000),
('LogsPro',     '2024-01-01', 30000),
('LogsPro',     '2024-02-01', 31500),
('LogsPro',     '2024-03-01', 29000),
('LogsPro',     '2024-04-01', 25000),
('APM',         '2024-01-01', 80000),
('APM',         '2024-02-01', 85000),
('APM',         '2024-03-01', 90000),
('APM',         '2024-04-01', 88000);
```

**Task**: Write a query that returns: `sku`, `month`, `revenue`, `prev_month_revenue`, `mom_change`, `mom_pct_change`, and a boolean/flag column `is_significant_drop` (true if pct change < -20%).

**Expected output shape**:
| sku | month | revenue | prev_month_revenue | mom_change | mom_pct_change | is_significant_drop |
|---|---|---|---|---|---|---|
| DataPlus | 2024-02-01 | 62000 | 50000 | 12000 | 24.0 | false |
| DataPlus | 2024-04-01 | 44000 | 58000 | -14000 | -24.1 | true |

<details>
<summary>Solution</summary>

```sql
WITH monthly_with_lag AS (
    SELECT
        sku,
        month,
        revenue,
        LAG(revenue) OVER (PARTITION BY sku ORDER BY month) AS prev_month_revenue
    FROM billing_metrics
),
computed AS (
    SELECT
        sku,
        month,
        revenue,
        prev_month_revenue,
        revenue - prev_month_revenue AS mom_change,
        ROUND(
            100.0 * (revenue - prev_month_revenue) / prev_month_revenue,
            1
        ) AS mom_pct_change
    FROM monthly_with_lag
    WHERE prev_month_revenue IS NOT NULL
)
SELECT
    *,
    CASE WHEN mom_pct_change < -20 THEN true ELSE false END AS is_significant_drop
FROM computed
ORDER BY sku, month;
```

**Key things the interviewer is looking for**:
- Use of CTE decomposition (not nested subqueries)
- Correct `PARTITION BY` + `ORDER BY` in the window
- NULL handling for the first month per SKU
- Clean expression for percentage change
</details>

---

### Q2 — Cohort Retention Analysis

**Difficulty**: Hard  
**Concepts**: First-touch attribution, cohort bucketing, window functions, self-join or conditional aggregation

**Scenario**: You have a table of customer orders. Find each customer's acquisition month (first order month), then compute what % of customers from each cohort placed an order in months 1, 2, and 3 after acquisition (month 0 = acquisition month).

**Dataset**:
```sql
CREATE TABLE orders (
    order_id     INT,
    customer_id  INT,
    order_date   DATE,
    amount       NUMERIC
);

INSERT INTO orders VALUES
(1,  101, '2024-01-05', 200),
(2,  102, '2024-01-12', 150),
(3,  103, '2024-01-20', 300),
(4,  101, '2024-02-08', 180),
(5,  102, '2024-02-15', 220),
(6,  104, '2024-02-10', 400),
(7,  101, '2024-03-01', 160),
(8,  103, '2024-03-18', 210),
(9,  105, '2024-03-05', 130),
(10, 102, '2024-04-20', 190),
(11, 104, '2024-04-11', 250),
(12, 106, '2024-04-03', 310),
(13, 101, '2024-04-25', 140),
(14, 105, '2024-05-09', 170);
```

**Task**: Return a cohort retention table: `cohort_month`, `month_number` (0, 1, 2, 3), `customers_retained`, `cohort_size`, `retention_pct`.

<details>
<summary>Solution</summary>

```sql
WITH customer_cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
customer_activity AS (
    SELECT
        o.customer_id,
        c.cohort_month,
        DATE_TRUNC('month', o.order_date) AS activity_month,
        -- months since acquisition
        EXTRACT(YEAR FROM AGE(DATE_TRUNC('month', o.order_date), c.cohort_month)) * 12 +
        EXTRACT(MONTH FROM AGE(DATE_TRUNC('month', o.order_date), c.cohort_month)) AS month_number
    FROM orders o
    JOIN customer_cohorts c USING (customer_id)
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
),
retention AS (
    SELECT
        cohort_month,
        month_number,
        COUNT(DISTINCT customer_id) AS customers_retained
    FROM customer_activity
    WHERE month_number <= 3
    GROUP BY cohort_month, month_number
)
SELECT
    r.cohort_month,
    r.month_number,
    r.customers_retained,
    cs.cohort_size,
    ROUND(100.0 * r.customers_retained / cs.cohort_size, 1) AS retention_pct
FROM retention r
JOIN cohort_sizes cs USING (cohort_month)
ORDER BY cohort_month, month_number;
```

**Key things the interviewer is looking for**:
- Correct first-touch cohort assignment (MIN order date)
- Computing month number correctly (not just calendar month diff)
- Separate CTE for cohort size (avoid re-aggregating)
- Denominator is cohort size, not retained count
</details>

---

### Q3 — Customer Lifetime Value with Ranking

**Difficulty**: Medium  
**Concepts**: Aggregation, RANK/DENSE_RANK, CASE, filtering on window results

**Scenario**: From the same `orders` table above, compute total LTV per customer, rank them within their acquisition month cohort, and return only the top 2 customers per cohort by LTV.

**Task**: Return `cohort_month`, `customer_id`, `total_ltv`, `cohort_rank`. Only include rank 1 and 2 per cohort.

<details>
<summary>Solution</summary>

```sql
WITH customer_cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
customer_ltv AS (
    SELECT
        customer_id,
        SUM(amount) AS total_ltv
    FROM orders
    GROUP BY customer_id
),
ranked AS (
    SELECT
        c.cohort_month,
        c.customer_id,
        l.total_ltv,
        DENSE_RANK() OVER (
            PARTITION BY c.cohort_month
            ORDER BY l.total_ltv DESC
        ) AS cohort_rank
    FROM customer_cohorts c
    JOIN customer_ltv l USING (customer_id)
)
SELECT *
FROM ranked
WHERE cohort_rank <= 2
ORDER BY cohort_month, cohort_rank;
```

**Why DENSE_RANK over RANK**: If two customers tie, RANK skips the next position (1,1,3). DENSE_RANK gives (1,1,2) — in a "top 2" scenario, DENSE_RANK is usually the right intent.
</details>

---

### Q4 — Detecting Duplicate/Fanout from a Bad Join

**Difficulty**: Medium  
**Concepts**: Grain awareness, COUNT vs COUNT DISTINCT, diagnosing inflated metrics

**Scenario**: A junior analyst joins `orders` to a `promotions` table and reports total revenue. Their number looks suspiciously high. Diagnose and fix it.

**Dataset**:
```sql
CREATE TABLE promotions (
    promo_id     INT,
    customer_id  INT,
    promo_code   TEXT
);

INSERT INTO promotions VALUES
(1, 101, 'SAVE10'),
(2, 101, 'FREESHIP'),   -- customer 101 has TWO promos
(3, 102, 'SAVE10'),
(4, 104, 'SAVE20');
```

**The broken query** (what the analyst wrote):
```sql
-- This inflates revenue for customers with multiple promos
SELECT SUM(o.amount) AS total_revenue
FROM orders o
JOIN promotions p ON o.customer_id = p.customer_id;
```

**Task**:
1. Explain in a comment why this query is wrong
2. Write a corrected version that computes total revenue only for customers who have at least one promo, without duplication

<details>
<summary>Solution</summary>

```sql
-- PROBLEM: orders joins to promotions on customer_id.
-- Customer 101 has 2 promo rows, so every order from customer 101
-- appears TWICE in the result — revenue is double-counted.
-- This is a classic fan-out / row multiplication from a one-to-many join.

-- CORRECT APPROACH: deduplicate promo customers before joining
WITH promo_customers AS (
    SELECT DISTINCT customer_id
    FROM promotions
),
orders_with_promos AS (
    SELECT o.*
    FROM orders o
    INNER JOIN promo_customers p USING (customer_id)
)
SELECT SUM(amount) AS total_revenue
FROM orders_with_promos;

-- ALTERNATIVE using EXISTS (avoids join entirely):
SELECT SUM(amount) AS total_revenue
FROM orders o
WHERE EXISTS (
    SELECT 1 FROM promotions p WHERE p.customer_id = o.customer_id
);
```

**Why this matters**: Fan-out from joins is one of the most common silent bugs in analytics. The interviewer may ask: "how would you catch this in a dbt test?" — answer: a `not_null` + `unique` test on the join key, or a row count assertion post-join.
</details>

---

### Q5 — Gap and Island: Consecutive Active Days

**Difficulty**: Hard  
**Concepts**: Gap-and-island, row_number trick, sessionization

**Scenario**: Find each customer's longest streak of consecutive days with at least one order.

**Dataset**:
```sql
CREATE TABLE daily_activity (
    customer_id  INT,
    activity_date DATE
);

INSERT INTO daily_activity VALUES
(101, '2024-01-01'),
(101, '2024-01-02'),
(101, '2024-01-03'),
(101, '2024-01-05'),  -- gap here
(101, '2024-01-06'),
(102, '2024-02-10'),
(102, '2024-02-11'),
(102, '2024-02-12'),
(102, '2024-02-13'),
(102, '2024-02-15');
```

**Task**: Return `customer_id`, `streak_start`, `streak_end`, `streak_length` for the longest streak per customer.

<details>
<summary>Solution</summary>

```sql
WITH deduped AS (
    -- in case multiple events on the same day
    SELECT DISTINCT customer_id, activity_date
    FROM daily_activity
),
with_groups AS (
    SELECT
        customer_id,
        activity_date,
        -- subtract row_number to get a constant "group key" for consecutive dates
        activity_date - INTERVAL '1 day' * ROW_NUMBER() OVER (
            PARTITION BY customer_id ORDER BY activity_date
        ) AS streak_group
    FROM deduped
),
streaks AS (
    SELECT
        customer_id,
        MIN(activity_date) AS streak_start,
        MAX(activity_date) AS streak_end,
        COUNT(*) AS streak_length
    FROM with_groups
    GROUP BY customer_id, streak_group
),
ranked AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY customer_id ORDER BY streak_length DESC) AS rnk
    FROM streaks
)
SELECT customer_id, streak_start, streak_end, streak_length
FROM ranked
WHERE rnk = 1
ORDER BY customer_id;
```

**The trick explained**: If you subtract a sequential row_number from consecutive dates, the result is constant within a streak (because both increment by 1). A gap in dates breaks the sequence, producing a different constant — a new group.
</details>

---

## Python Questions

These are data pipeline / manipulation style — no algorithms, no LeetCode.

---

### P1 — Time to Second Event per User

**Difficulty**: Easy–Medium  
**Concepts**: GroupBy, sort, first/second row extraction, timedelta

**Scenario**:
```python
import pandas as pd

data = {
    'user_id':    [1, 1, 1, 2, 2, 3, 3, 3],
    'event_type': ['login','purchase','logout','login','purchase','login','login','purchase'],
    'timestamp':  [
        '2024-01-01 08:00', '2024-01-01 08:30', '2024-01-01 09:00',
        '2024-01-02 10:00', '2024-01-02 10:45',
        '2024-01-03 07:00', '2024-01-03 07:10', '2024-01-03 08:00'
    ]
}
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])
```

**Task**: Write a function `time_to_second_event(df)` that returns a DataFrame with `user_id`, `first_event_time`, `second_event_time`, and `minutes_to_second_event`. Users with only one event should be excluded.

<details>
<summary>Solution</summary>

```python
def time_to_second_event(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each user, compute time between their first and second event.
    Users with fewer than 2 events are excluded.
    """
    sorted_df = df.sort_values(['user_id', 'timestamp'])

    # rank events per user
    sorted_df['event_rank'] = sorted_df.groupby('user_id')['timestamp'].rank(method='first')

    first  = sorted_df[sorted_df['event_rank'] == 1][['user_id', 'timestamp']].rename(columns={'timestamp': 'first_event_time'})
    second = sorted_df[sorted_df['event_rank'] == 2][['user_id', 'timestamp']].rename(columns={'timestamp': 'second_event_time'})

    result = first.merge(second, on='user_id')
    result['minutes_to_second_event'] = (
        result['second_event_time'] - result['first_event_time']
    ).dt.total_seconds() / 60

    return result.reset_index(drop=True)


print(time_to_second_event(df))
```
</details>

---

### P2 — Parse and Flatten a Nested JSON Pipeline Payload

**Difficulty**: Medium  
**Concepts**: JSON parsing, nested dict handling, DataFrame construction, robustness

**Scenario**:
```python
import json

raw_payload = '''
[
  {"user_id": 1, "metadata": {"plan": "pro",   "region": "us-east"}, "events": 42},
  {"user_id": 2, "metadata": {"plan": "free",  "region": "eu-west"}, "events": 7},
  {"user_id": 3, "metadata": {"plan": "pro",   "region": "us-west"}, "events": 130},
  {"user_id": 4, "metadata": null,                                    "events": 15}
]
'''

records = json.loads(raw_payload)
```

**Task**: Write a function `flatten_payload(records)` that returns a flat DataFrame with columns: `user_id`, `plan`, `region`, `events`. For records where `metadata` is null, `plan` and `region` should be `None`.

<details>
<summary>Solution</summary>

```python
def flatten_payload(records: list) -> pd.DataFrame:
    """
    Flattens a list of dicts with a nested 'metadata' key.
    Handles null metadata gracefully.
    """
    rows = []
    for rec in records:
        metadata = rec.get('metadata') or {}
        rows.append({
            'user_id': rec['user_id'],
            'plan':    metadata.get('plan'),
            'region':  metadata.get('region'),
            'events':  rec.get('events')
        })
    return pd.DataFrame(rows)


print(flatten_payload(records))
```

**What they're watching for**: Handling `null` metadata without a KeyError (`or {}` pattern), not assuming dict keys always exist (`.get()`), clean loop structure. An interviewer may follow up: "how would you do this if the payload had 10M records?" — answer: generator expression + chunked processing, avoid materializing all rows at once.
</details>

---

### P3 — Rolling 7-Day Revenue per Customer

**Difficulty**: Medium  
**Concepts**: Resample or rolling, groupby + apply, date handling

**Scenario**:
```python
data = {
    'customer_id': [101,101,101,101,101,102,102,102,102],
    'order_date':  ['2024-01-01','2024-01-03','2024-01-05',
                    '2024-01-08','2024-01-10',
                    '2024-01-02','2024-01-04','2024-01-09','2024-01-11'],
    'amount':      [100, 200, 150, 300, 250, 400, 180, 220, 310]
}
df = pd.DataFrame(data)
df['order_date'] = pd.to_datetime(df['order_date'])
```

**Task**: For each row, compute the total revenue that customer generated in the 7-day window *ending on that row's date* (inclusive). Add it as a new column `rolling_7d_revenue`.

<details>
<summary>Solution</summary>

```python
def rolling_7d_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds rolling 7-day revenue per customer, per row.
    Window: 7 days ending on (and including) the row's order_date.
    """
    df = df.sort_values(['customer_id', 'order_date']).copy()

    def compute_rolling(group):
        group = group.set_index('order_date').sort_index()
        group['rolling_7d_revenue'] = (
            group['amount']
            .rolling('7D', closed='right')
            .sum()
        )
        return group.reset_index()

    result = df.groupby('customer_id', group_keys=False).apply(compute_rolling)
    return result.reset_index(drop=True)


print(rolling_7d_revenue(df))
```

**Follow-up the interviewer might ask**: "What's the difference between `rolling('7D')` and `rolling(7)`?" — `'7D'` is time-based (handles irregular dates), `rolling(7)` is row-count based (assumes uniform daily data). Always use time-based rolling for real-world order data.
</details>

---

### P4 — Idempotent Upsert Function

**Difficulty**: Medium  
**Concepts**: Merge/upsert logic, handling duplicates, pipeline design thinking

**Scenario**: You're building a pipeline that runs daily and loads new customer records. But some records may already exist (same `customer_id`). New records should be inserted; existing ones should be updated only if the incoming `updated_at` is more recent.

```python
existing = pd.DataFrame({
    'customer_id': [1, 2, 3],
    'name':        ['Alice', 'Bob', 'Carol'],
    'plan':        ['pro', 'free', 'pro'],
    'updated_at':  pd.to_datetime(['2024-01-01', '2024-01-05', '2024-01-10'])
})

incoming = pd.DataFrame({
    'customer_id': [2, 3, 4],
    'name':        ['Bob', 'Carol Updated', 'Dave'],
    'plan':        ['pro', 'enterprise', 'free'],
    'updated_at':  pd.to_datetime(['2024-01-03', '2024-01-15', '2024-01-12'])
})
```

**Task**: Write `upsert(existing, incoming)` that returns the merged DataFrame. Customer 2 should NOT be updated (incoming is older). Customer 3 SHOULD be updated. Customer 4 should be inserted.

<details>
<summary>Solution</summary>

```python
def upsert(existing: pd.DataFrame, incoming: pd.DataFrame) -> pd.DataFrame:
    """
    Idempotent upsert: incoming records update existing ones only if
    incoming.updated_at > existing.updated_at. New records are appended.
    """
    merged = existing.merge(
        incoming,
        on='customer_id',
        how='outer',
        suffixes=('_existing', '_incoming')
    )

    def resolve_row(row):
        # brand new record — only incoming data exists
        if pd.isna(row.get('updated_at_existing')):
            return {
                'customer_id': row['customer_id'],
                'name':        row['name_incoming'],
                'plan':        row['plan_incoming'],
                'updated_at':  row['updated_at_incoming']
            }
        # existing only (not in incoming) — keep as-is
        if pd.isna(row.get('updated_at_incoming')):
            return {
                'customer_id': row['customer_id'],
                'name':        row['name_existing'],
                'plan':        row['plan_existing'],
                'updated_at':  row['updated_at_existing']
            }
        # both exist — keep whichever is newer
        if row['updated_at_incoming'] > row['updated_at_existing']:
            return {
                'customer_id': row['customer_id'],
                'name':        row['name_incoming'],
                'plan':        row['plan_incoming'],
                'updated_at':  row['updated_at_incoming']
            }
        else:
            return {
                'customer_id': row['customer_id'],
                'name':        row['name_existing'],
                'plan':        row['plan_existing'],
                'updated_at':  row['updated_at_existing']
            }

    resolved = merged.apply(resolve_row, axis=1, result_type='expand')
    return resolved.sort_values('customer_id').reset_index(drop=True)


print(upsert(existing, incoming))
```

**Why this matters in interviews**: This is exactly what a SCD Type 1 or pipeline reload scenario looks like in Python. The interviewer may ask: "how would you do this at scale with 50M rows?" — answer: push the logic into SQL (MERGE statement / dbt snapshot), not Pandas.
</details>

---

### P5 — Detect Schema Drift in Incoming Data

**Difficulty**: Medium–Hard  
**Concepts**: Schema validation, defensive pipeline design, error reporting

**Scenario**: Your pipeline receives a CSV daily. You have a known expected schema. Write a validation function that detects: missing columns, unexpected extra columns, and columns with wrong dtype.

```python
import pandas as pd

EXPECTED_SCHEMA = {
    'customer_id': 'int64',
    'order_date':  'datetime64[ns]',
    'amount':      'float64',
    'status':      'object'
}

# Simulate an incoming dataframe with drift
incoming = pd.DataFrame({
    'customer_id': [1, 2, 3],
    'order_date':  ['2024-01-01', '2024-01-02', '2024-01-03'],  # not cast yet
    'amount':      [100.0, 200.0, 300.0],
    'region':      ['us', 'eu', 'us']   # unexpected column
    # 'status' is missing
})
```

**Task**: Write `validate_schema(df, expected_schema)` that returns a dict with keys `missing_columns`, `extra_columns`, `type_mismatches` (list of `{column, expected, actual}`). It should not raise — just report.

<details>
<summary>Solution</summary>

```python
def validate_schema(df: pd.DataFrame, expected_schema: dict) -> dict:
    """
    Validates a DataFrame against an expected schema.
    Returns a report dict — does not raise exceptions.
    """
    actual_cols    = set(df.columns)
    expected_cols  = set(expected_schema.keys())

    missing_columns   = list(expected_cols - actual_cols)
    extra_columns     = list(actual_cols - expected_cols)

    type_mismatches = []
    for col in expected_cols & actual_cols:
        expected_dtype = expected_schema[col]
        actual_dtype   = str(df[col].dtype)
        if actual_dtype != expected_dtype:
            type_mismatches.append({
                'column':   col,
                'expected': expected_dtype,
                'actual':   actual_dtype
            })

    return {
        'missing_columns':  missing_columns,
        'extra_columns':    extra_columns,
        'type_mismatches':  type_mismatches,
        'is_valid':         not any([missing_columns, extra_columns, type_mismatches])
    }


report = validate_schema(incoming, EXPECTED_SCHEMA)
for k, v in report.items():
    print(f"{k}: {v}")
```

**Follow-up the interviewer might ask**: "Where would you plug this into a pipeline?" — answer: at ingestion, before any transformation. Fail fast and alert; don't let schema drift silently corrupt downstream models. In dbt, this maps to `source` freshness + schema tests at the staging layer — tie it back to your shift-left testing story.
</details>

---

## Quick Reference: Patterns to Know Cold

### SQL
| Pattern | Function |
|---|---|
| Period-over-period | `LAG(col) OVER (PARTITION BY x ORDER BY date)` |
| Top-N per group | `DENSE_RANK() OVER (...) <= N` in a CTE, filter outside |
| Consecutive streaks | `date - INTERVAL * ROW_NUMBER()` group trick |
| Cohort assignment | `MIN(date)` per user, then `DATE_TRUNC('month', ...)` |
| Dedup before join | `SELECT DISTINCT` or `EXISTS` subquery |

### Python
| Pattern | Use case |
|---|---|
| `groupby + rank(method='first')` | First/Nth event per user |
| `rolling('7D')` | Time-based (not row-based) rolling window |
| `merge(..., suffixes=)` | Upsert / conflict resolution |
| `or {}` on nullable dicts | Safe JSON flattening |
| Schema set diff | `set(df.columns) - set(expected)` |



# Advanced SQL: Analytical Thinking & Window Functions
**Focus**: Problems that require window function composition, not just syntax recall  
**Style**: The kind a DS interviewer asks to test how you *think* about data, not just write SQL

---

## Q1 — Running Revenue Share per SKU (Cumulative Distribution)

**Difficulty**: Medium  
**Concepts**: SUM() OVER, cumulative totals, percentage of total, ordering within partitions

**Scenario**: You're a data engineer at a SaaS company. The finance team wants to understand which SKUs are driving the bulk of revenue — specifically, they want a running cumulative revenue share so they can identify the "80% revenue" SKUs (Pareto analysis).

**Dataset**:
```sql
CREATE TABLE sku_revenue (
    sku         TEXT,
    month       DATE,
    revenue     NUMERIC
);

INSERT INTO sku_revenue VALUES
('APM',         '2024-01-01', 95000),
('DataPlus',    '2024-01-01', 72000),
('LogsPro',     '2024-01-01', 58000),
('Infra',       '2024-01-01', 41000),
('Synthetics',  '2024-01-01', 23000),
('Browser',     '2024-01-01', 18000),
('Mobile',      '2024-01-01', 9000),
('Errors',      '2024-01-01', 4000);
```

**Task**: For the month of `2024-01-01`, return each SKU with:
- `revenue`
- `revenue_rank` (1 = highest revenue)
- `pct_of_total` (this SKU's % share of total revenue)
- `cumulative_pct` (running cumulative % ordered by revenue desc)
- `is_pareto` — flag `'Y'` if the SKU falls within the top 80% cumulative revenue

**Expected shape**:
| sku | revenue | revenue_rank | pct_of_total | cumulative_pct | is_pareto |
|---|---|---|---|---|---|
| APM | 95000 | 1 | 29.4 | 29.4 | Y |
| DataPlus | 72000 | 2 | 22.3 | 51.7 | Y |
| ... | ... | ... | ... | ... | ... |

**Hint**: You'll need a window SUM for total, a window SUM for cumulative, and a CASE for the flag. Think carefully about *when* the cumulative crosses 80% — the row that pushes it over should still be flagged Y.

<details>
<summary>Solution</summary>

```sql
WITH base AS (
    SELECT
        sku,
        revenue,
        RANK() OVER (ORDER BY revenue DESC) AS revenue_rank,
        ROUND(
            100.0 * revenue / SUM(revenue) OVER (),
            1
        ) AS pct_of_total,
        ROUND(
            100.0 * SUM(revenue) OVER (
                ORDER BY revenue DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) / SUM(revenue) OVER (),
            1
        ) AS cumulative_pct
    FROM sku_revenue
    WHERE month = '2024-01-01'
)
SELECT
    sku,
    revenue,
    revenue_rank,
    pct_of_total,
    cumulative_pct,
    -- the row that CROSSES 80% is still included (cumulative_pct >= 80 catches it)
    CASE
        WHEN cumulative_pct - pct_of_total < 80 THEN 'Y'
        ELSE 'N'
    END AS is_pareto
FROM base
ORDER BY revenue_rank;
```

**The subtle part**: `cumulative_pct - pct_of_total < 80` means "the cumulative *before* this row was under 80%", so the crossing row gets flagged Y. If you used `cumulative_pct <= 80` you'd miss the exact crossing row when it lands at exactly 80%.

**What the interviewer is watching for**:
- Correct `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` frame
- `SUM() OVER ()` with no ORDER BY for total (full partition sum)
- Thinking about the boundary condition on the 80% flag — not just `<= 80`
</details>

---

## Q2 — Session Detection (Sessionization)

**Difficulty**: Hard  
**Concepts**: LAG, conditional logic, cumulative SUM as session ID, gap detection

**Scenario**: You have a table of user events with timestamps. A "session" is defined as a group of events from the same user where no two consecutive events are more than 30 minutes apart. Assign a session ID to each event and compute session-level stats.

**Dataset**:
```sql
CREATE TABLE user_events (
    user_id     INT,
    event_type  TEXT,
    event_time  TIMESTAMP
);

INSERT INTO user_events VALUES
(1, 'page_view',  '2024-01-01 09:00:00'),
(1, 'click',      '2024-01-01 09:10:00'),
(1, 'purchase',   '2024-01-01 09:25:00'),
(1, 'page_view',  '2024-01-01 10:30:00'),  -- 65 min gap → new session
(1, 'click',      '2024-01-01 10:45:00'),
(2, 'page_view',  '2024-01-01 08:00:00'),
(2, 'click',      '2024-01-01 08:20:00'),
(2, 'page_view',  '2024-01-01 09:05:00'),  -- 45 min gap → new session
(2, 'purchase',   '2024-01-01 09:15:00'),
(2, 'click',      '2024-01-01 09:20:00');
```

**Task — Part A**: Assign a `session_id` (can be a number per user, e.g. user 1 session 1, user 1 session 2) to each event row.

**Task — Part B**: From the sessionized data, return session-level summary: `user_id`, `session_id`, `session_start`, `session_end`, `duration_minutes`, `event_count`, `converted` (Y if any event_type = 'purchase' in that session).

<details>
<summary>Solution</summary>

```sql
-- PART A: Assign session IDs
WITH lagged AS (
    SELECT
        user_id,
        event_type,
        event_time,
        LAG(event_time) OVER (
            PARTITION BY user_id ORDER BY event_time
        ) AS prev_event_time
    FROM user_events
),
gap_flagged AS (
    SELECT
        *,
        CASE
            WHEN prev_event_time IS NULL THEN 1  -- first event = new session
            WHEN EXTRACT(EPOCH FROM (event_time - prev_event_time)) / 60 > 30 THEN 1
            ELSE 0
        END AS is_new_session
    FROM lagged
),
sessionized AS (
    SELECT
        *,
        -- cumulative sum of new_session flags = session number per user
        SUM(is_new_session) OVER (
            PARTITION BY user_id ORDER BY event_time
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_id
    FROM gap_flagged
)
SELECT user_id, event_type, event_time, session_id
FROM sessionized
ORDER BY user_id, event_time;


-- PART B: Session-level summary
WITH lagged AS (
    SELECT *,
        LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) AS prev_event_time
    FROM user_events
),
gap_flagged AS (
    SELECT *,
        CASE
            WHEN prev_event_time IS NULL THEN 1
            WHEN EXTRACT(EPOCH FROM (event_time - prev_event_time)) / 60 > 30 THEN 1
            ELSE 0
        END AS is_new_session
    FROM lagged
),
sessionized AS (
    SELECT *,
        SUM(is_new_session) OVER (
            PARTITION BY user_id ORDER BY event_time
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_id
    FROM gap_flagged
)
SELECT
    user_id,
    session_id,
    MIN(event_time) AS session_start,
    MAX(event_time) AS session_end,
    ROUND(
        EXTRACT(EPOCH FROM MAX(event_time) - MIN(event_time)) / 60,
        1
    ) AS duration_minutes,
    COUNT(*) AS event_count,
    MAX(CASE WHEN event_type = 'purchase' THEN 'Y' ELSE 'N' END) AS converted
FROM sessionized
GROUP BY user_id, session_id
ORDER BY user_id, session_id;
```

**The core trick**: `is_new_session` is 1 at every gap boundary, 0 otherwise. A cumulative SUM of this column increments exactly when a new session starts — giving you a session counter per user. This is the canonical sessionization pattern.

**Follow-up the interviewer will ask**: "What if the 30-minute threshold is configurable?" → parameterize it. In dbt, this becomes a var: `{{ var('session_gap_minutes', 30) }}`. Shows you think about reusability.
</details>

---

## Q3 — Month-over-Month Churn Detection

**Difficulty**: Medium-Hard  
**Concepts**: LAG, NULL handling, status transitions, CASE-based state machine

**Scenario**: You have monthly subscription snapshots. A customer is considered **churned** in month M if they were active in month M-1 but have no record in month M. A customer is **reactivated** if they have no record in month M-1 but are active in month M (and were active before that).

**Dataset**:
```sql
CREATE TABLE subscriptions (
    customer_id  INT,
    month        DATE,
    plan         TEXT
);

INSERT INTO subscriptions VALUES
(101, '2024-01-01', 'pro'),
(101, '2024-02-01', 'pro'),
(101, '2024-03-01', 'pro'),
-- 101 churns in April
(102, '2024-01-01', 'free'),
(102, '2024-02-01', 'free'),
-- 102 churns in March
(102, '2024-04-01', 'pro'),   -- 102 reactivates in April
(103, '2024-02-01', 'pro'),   -- 103 is a new customer in Feb
(103, '2024-03-01', 'pro'),
(103, '2024-04-01', 'pro');
```

**Task**: Generate a spine of all `customer_id × month` combinations (for all months a customer ever appeared), then classify each row as: `active`, `churned`, `reactivated`, or `new`.

**Hint**: You'll need to generate a complete month spine per customer first — months with no record are the churn signal.

<details>
<summary>Solution</summary>

```sql
-- Step 1: Build a complete spine of customer × every possible month
WITH all_months AS (
    SELECT DISTINCT month FROM subscriptions
),
all_customers AS (
    SELECT DISTINCT customer_id FROM subscriptions
),
spine AS (
    SELECT c.customer_id, m.month
    FROM all_customers c
    CROSS JOIN all_months m
),
-- Step 2: Join actual subscription records onto the spine (NULL = no record that month)
with_activity AS (
    SELECT
        s.customer_id,
        s.month,
        sub.plan,
        CASE WHEN sub.plan IS NOT NULL THEN 1 ELSE 0 END AS is_active
    FROM spine s
    LEFT JOIN subscriptions sub
           ON s.customer_id = sub.customer_id
          AND s.month = sub.month
),
-- Step 3: Bring in prior month's activity using LAG
with_lag AS (
    SELECT
        *,
        LAG(is_active) OVER (
            PARTITION BY customer_id ORDER BY month
        ) AS prev_is_active
    FROM with_activity
),
-- Step 4: Classify each row
classified AS (
    SELECT
        customer_id,
        month,
        plan,
        CASE
            WHEN is_active = 1 AND prev_is_active IS NULL     THEN 'new'
            WHEN is_active = 1 AND prev_is_active = 1         THEN 'active'
            WHEN is_active = 1 AND prev_is_active = 0         THEN 'reactivated'
            WHEN is_active = 0 AND prev_is_active = 1         THEN 'churned'
            ELSE NULL  -- was inactive last month and this month — skip
        END AS status
    FROM with_lag
)
SELECT *
FROM classified
WHERE status IS NOT NULL
ORDER BY customer_id, month;
```

**Why this pattern matters**: This is the foundation of SaaS revenue metrics — MRR movement (new, expansion, contraction, churn, reactivation). A DS interviewer will immediately recognize this as subscription analytics gold. Connects directly to your New Relic billing work.

**What to say**: "In dbt, I'd model this as a snapshot (SCD Type 2) on the subscriptions table rather than computing it at query time — so the spine and lag logic is pre-baked into the snapshot model and this query becomes a simple filter on status."
</details>

---

## Q4 — Detecting Anomalous Days Using Standard Deviation

**Difficulty**: Medium-Hard  
**Concepts**: AVG/STDDEV as window functions, z-score computation, statistical flagging

**Scenario**: A data scientist asks you to flag days where revenue for any SKU was statistically anomalous — more than 2 standard deviations away from that SKU's mean daily revenue. This is a common ask for automated alerting pipelines.

**Dataset**:
```sql
CREATE TABLE daily_revenue (
    sku         TEXT,
    date        DATE,
    revenue     NUMERIC
);

INSERT INTO daily_revenue VALUES
('APM', '2024-01-01', 9000),
('APM', '2024-01-02', 9200),
('APM', '2024-01-03', 9100),
('APM', '2024-01-04', 9300),
('APM', '2024-01-05', 14500),  -- spike
('APM', '2024-01-06', 9000),
('APM', '2024-01-07', 8800),
('LogsPro', '2024-01-01', 3000),
('LogsPro', '2024-01-02', 3100),
('LogsPro', '2024-01-03', 3050),
('LogsPro', '2024-01-04', 3200),
('LogsPro', '2024-01-05', 3100),
('LogsPro', '2024-01-06', 1200),  -- drop
('LogsPro', '2024-01-07', 3000);
```

**Task**: Return all rows flagged as anomalous, with columns: `sku`, `date`, `revenue`, `mean_revenue`, `stddev_revenue`, `z_score`, `anomaly_direction` (`'spike'` or `'drop'`).

<details>
<summary>Solution</summary>

```sql
WITH stats AS (
    SELECT
        sku,
        date,
        revenue,
        AVG(revenue) OVER (PARTITION BY sku)    AS mean_revenue,
        STDDEV(revenue) OVER (PARTITION BY sku) AS stddev_revenue
    FROM daily_revenue
),
z_scored AS (
    SELECT
        *,
        ROUND(
            (revenue - mean_revenue) / NULLIF(stddev_revenue, 0),
            2
        ) AS z_score
    FROM stats
)
SELECT
    sku,
    date,
    revenue,
    ROUND(mean_revenue, 1)   AS mean_revenue,
    ROUND(stddev_revenue, 1) AS stddev_revenue,
    z_score,
    CASE
        WHEN z_score >  2 THEN 'spike'
        WHEN z_score < -2 THEN 'drop'
    END AS anomaly_direction
FROM z_scored
WHERE ABS(z_score) > 2
ORDER BY sku, date;
```

**Key details**:
- `NULLIF(stddev_revenue, 0)` prevents division by zero if all values are identical
- `AVG/STDDEV OVER (PARTITION BY sku)` with no ORDER BY = whole-partition stats (not rolling)
- Threshold of 2 is a parameter — in production you'd make this configurable

**Follow-up the DS interviewer will almost certainly ask**: "Is population or sample standard deviation more appropriate here?" — `STDDEV` in most engines is sample stddev (divides by N-1). For a small window (7 days), sample stddev is more conservative and appropriate. `STDDEV_POP` divides by N. Know the difference.

**Connect to your work**: "This is essentially what the Daily Explainer does — surfaces anomalous day-over-day changes. I'd extend this with a rolling window stddev (`ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`) to make the baseline adaptive rather than static."
</details>

---

## Q5 — Customer Reactivation Lag & Lifecycle Sequencing

**Difficulty**: Hard  
**Concepts**: Multiple window functions composed, lifecycle state transitions, LEAD + LAG together, conditional aggregation

**Scenario**: You want to understand the full lifecycle of churned-and-reactivated customers: how long were they dormant, what plan did they return on, and did they churn again?

**Dataset**:
```sql
CREATE TABLE customer_lifecycle (
    customer_id  INT,
    event_date   DATE,
    event_type   TEXT,   -- 'subscribed', 'churned', 'reactivated'
    plan         TEXT
);

INSERT INTO customer_lifecycle VALUES
(101, '2023-06-01', 'subscribed',   'free'),
(101, '2023-09-15', 'churned',      NULL),
(101, '2024-01-10', 'reactivated',  'pro'),
(101, '2024-05-20', 'churned',      NULL),
(102, '2023-03-01', 'subscribed',   'pro'),
(102, '2023-07-01', 'churned',      NULL),
(102, '2023-10-15', 'reactivated',  'pro'),
(103, '2023-01-01', 'subscribed',   'free'),
(103, '2024-02-01', 'churned',      NULL);
-- 103 has not reactivated
```

**Task**: For each customer who has ever reactivated, return:
- `customer_id`
- `churn_date` (the churn event just before reactivation)
- `reactivation_date`
- `dormant_days` (days between churn and reactivation)
- `reactivation_plan`
- `churned_again` — `'Y'` if they churned again after reactivation, `'N'` otherwise

<details>
<summary>Solution</summary>

```sql
WITH sequenced AS (
    SELECT
        customer_id,
        event_date,
        event_type,
        plan,
        -- look back to find the previous event
        LAG(event_date)  OVER (PARTITION BY customer_id ORDER BY event_date) AS prev_event_date,
        LAG(event_type)  OVER (PARTITION BY customer_id ORDER BY event_date) AS prev_event_type,
        -- look forward to find the next event after reactivation
        LEAD(event_date) OVER (PARTITION BY customer_id ORDER BY event_date) AS next_event_date,
        LEAD(event_type) OVER (PARTITION BY customer_id ORDER BY event_date) AS next_event_type
    FROM customer_lifecycle
),
reactivations AS (
    SELECT
        customer_id,
        prev_event_date                              AS churn_date,
        event_date                                   AS reactivation_date,
        event_date - prev_event_date                 AS dormant_days,
        plan                                         AS reactivation_plan,
        CASE
            WHEN next_event_type = 'churned' THEN 'Y'
            ELSE 'N'
        END                                          AS churned_again
    FROM sequenced
    WHERE event_type = 'reactivated'
      AND prev_event_type = 'churned'  -- safety: ensure the prior event was indeed a churn
)
SELECT *
FROM reactivations
ORDER BY customer_id, reactivation_date;
```

**What makes this hard**: You need LAG and LEAD *simultaneously* on the same row — backward to find the churn date, forward to check if they churn again. Composing both in a single window pass is the elegant solution.

**Edge cases to mention**:
- What if there are two consecutive churns with no reactivation between? The `prev_event_type = 'churned'` guard handles it.
- What if `event_date` has ties? Add a secondary sort key (e.g. `event_type`) or acknowledge the ambiguity.
- Customer 103 correctly drops out — no `reactivated` event, so no row in output.

**Connect to your work**: "This is the kind of lifecycle sequencing I'd model as a dbt snapshot with status columns — so the LAG/LEAD logic is computed once at snapshot time and downstream queries don't need to re-derive it."
</details>

---

## Window Function Cheat Sheet

| Function | What it does | Common use case |
|---|---|---|
| `ROW_NUMBER()` | Unique sequential rank, no ties | Dedup, first/last row per group |
| `RANK()` | Rank with gaps on ties (1,1,3) | Leaderboards where ties skip positions |
| `DENSE_RANK()` | Rank without gaps on ties (1,1,2) | Top-N filtering with ties |
| `LAG(col, n)` | Value from n rows behind | Period-over-period, state transitions |
| `LEAD(col, n)` | Value from n rows ahead | Churn detection, next-event analysis |
| `FIRST_VALUE(col)` | First value in the window frame | First touch attribution |
| `LAST_VALUE(col)` | Last value in the window frame | Needs `ROWS BETWEEN ... UNBOUNDED FOLLOWING` |
| `SUM() OVER (ORDER BY ...)` | Running total | Cumulative revenue, session IDs |
| `AVG/STDDEV OVER (PARTITION BY ...)` | Partition-level stats | Z-score, anomaly detection |
| `NTILE(n)` | Divide rows into n buckets | Quartiles, decile analysis |

## Frame Clause Reference

```sql
-- Default (when ORDER BY present): RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
-- Explicit running total:
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW

-- Full partition (no ORDER BY needed, but explicit is clearer):
ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING

-- Rolling 7-row window:
ROWS BETWEEN 6 PRECEDING AND CURRENT ROW

-- Time-based rolling (use RANGE, not ROWS):
RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW
```

**ROWS vs RANGE**: `ROWS` counts physical rows. `RANGE` works on value ranges — if two rows have the same ORDER BY value, RANGE includes both in "current row". For most analytical work, `ROWS` is more predictable.
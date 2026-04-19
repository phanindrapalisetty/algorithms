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
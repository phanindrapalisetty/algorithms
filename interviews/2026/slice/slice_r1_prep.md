```
Round 1
SQL fluency - Correct use of window functions, joins, aggregations. Handles NULLs and edge cases. 
Writes readable, well-structured SQL without prompting.Incremental & SCD logic - Understands SCD Type 2, late-arriving data, and idempotency. 
Can reason about trade-offs between Type 1 and Type 2 without being led.
Code quality & testing instinct - Python is modular, named well, and testable. 
Proactively thinks about configurability and edge cases. 
Would pass a PR review without major comments.
Scale & performance awareness - Thinks about query performance, partition pruning, and data volume without being prompted. 
Knows when a solution that works at 1M rows breaks at 500M.
Storage engine awareness - Understands how Delta Lake vs Pinot changes model design. 
Makes deliberate partitioning and pre-aggregation decisions for each engine.
```

**The core mental model:**

Storage engine → query pattern → model design

Not the other way around. You don't design a model and then pick a storage engine. The storage engine is chosen first based on latency requirements, and the model follows.

---

**Delta Lake — design principles:**

**Characteristics:**
- ACID transactions
- Schema evolution
- Time travel
- Optimized for large sequential scans
- Query latency: seconds to minutes
- Storage: S3-backed Parquet files

**Model design implications:**
- Normalize — join at query time is fine
- Full fact + dimension tables, star schema
- SCD Type 2 on slowly changing dimensions
- Partition by date — most queries filter by date range
- Compaction via OPTIMIZE to reduce small files
- Z-ordering on high cardinality filter columns

**When to use:**
- Finance reporting — accuracy over speed
- DS historical analysis — 3 years of data
- ML feature engineering — batch features
- Regulatory compliance — audit trails via time travel

---

**Pinot — design principles:**

**Characteristics:**
- Real-time OLAP
- Data ingested from Kafka directly
- Pre-aggregated at ingestion time
- No joins at query time
- Query latency: milliseconds
- Optimized for high QPS dashboards

**Model design implications:**
- Denormalize everything — no joins at query time
- Pre-aggregate commonly used metrics at ingestion
- Wide flat tables — all attributes in one row
- Segment by time — Pinot's native partitioning
- Star-tree index for fast aggregations
- Think about query patterns before designing schema

**When to use:**
- User-facing dashboards — sub-second response
- Real-time metrics — live transaction counts
- High QPS scenarios — thousands of queries per second
- Operational analytics — current state of the system

---

**The key design difference with an example:**

Say Slice needs `repayment_rate` metric.

**Delta Lake model:**
```sql
-- Normalized, joined at query time
SELECT 
    u.user_segment,
    COUNT(CASE WHEN r.status = 'repaid' THEN 1 END) / COUNT(*) as repayment_rate
FROM fct_repayments r
JOIN dim_user u ON r.user_sk = u.user_sk
WHERE r.repayment_date >= '2024-01-01'
GROUP BY u.user_segment
```
Accurate, flexible, seconds of latency. Fine for Finance dashboard.

**Pinot model:**
```sql
-- Pre-aggregated, denormalized, milliseconds
SELECT 
    user_segment,
    repayment_rate  -- pre-computed at ingestion
FROM repayments_realtime
WHERE date = TODAY()
```
Fast, rigid, milliseconds. Fine for real-time product dashboard.

---

**Questions they might ask — and your answers:**

**Q: "How does Delta Lake affect your incremental model design?"**

*"Delta Lake's ACID transactions make incremental models reliable — I can use merge operations knowing they'll be atomic. I partition by date and use Z-ordering on high cardinality columns like user_id. For late arriving data I extend the lookback window on each run and rely on Delta's MERGE to handle deduplication correctly."*

**Q: "How would you model the same metric differently for Delta vs Pinot?"**

*"For Delta I'd keep it normalized — fact table with dimension joins at query time. For Pinot I'd denormalize completely — pre-join all dimension attributes at ingestion, pre-aggregate commonly queried metrics. The same `repayment_rate` metric would be a derived column computed at query time in Delta, but a pre-computed column updated at ingestion in Pinot."*

**Q: "When would you choose Pinot over Delta?"**

*"When the latency requirement is sub-second and the query pattern is predictable. Pinot trades flexibility for speed — you pre-aggregate for known queries, so ad-hoc analysis is hard. If a business user needs to slice a metric 10 different ways interactively, Delta is better. If they need one dashboard to load in under 200ms for thousands of concurrent users, Pinot is better."*

**Q: "What are the trade-offs of denormalizing for Pinot?"**

*"Three trade-offs: storage cost — you duplicate dimension attributes across millions of rows. Update complexity — if a user's segment changes, you need to reprocess all their historical Pinot records, not just update a dimension table. And query flexibility — you can only answer questions you pre-anticipated at design time. Delta handles all three better but at the cost of latency."*

**Q: "How do you handle schema evolution differently in Delta vs Pinot?"**

*"Delta handles schema evolution gracefully — you can add nullable columns without rewriting data, and time travel lets you query old schema versions. Pinot is more rigid — schema changes often require reingestion of historical data. So for frequently changing schemas I'd keep Delta as the source of truth and only push stable, well-defined schemas to Pinot."*

---

**The one-liner to open with if they ask about storage engine awareness:**

*"My mental model is query pattern first, then storage engine, then data model. The business question and latency requirement tell me which engine to use, and the engine tells me how to model the data. The same metric looks completely different in Delta Lake vs Pinot because the query patterns they serve are fundamentally different."*

---

**Fintech-specific angle for Slice:**

Slice likely uses:
- **Delta Lake** → KYC approval history, repayment history, disbursement volumes, cohort retention analysis
- **Pinot** → Real-time transaction counts, live repayment rates, current account balances for product dashboards

Connecting your answer to their domain will land better than generic examples.

---

**Quick reference card:**

```
Delta Lake:
- Batch, ACID, schema evolution, time travel
- Normalize, SCD Type 2, partition by date
- Seconds latency, flexible queries
- Use for: Finance, DS, compliance

Pinot:
- Real-time OLAP, pre-aggregated, high QPS
- Denormalize, pre-aggregate, no joins at query time
- Milliseconds latency, rigid query patterns
- Use for: Product dashboards, real-time metrics

Key principle:
Storage engine → query pattern → model design
Same metric = different physical model per engine
```


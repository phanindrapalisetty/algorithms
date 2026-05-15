**The Data Pipeline System Design Framework**

Every data pipeline design question can be structured around 6 components. Always walk through them in this order:

**1. Clarify Requirements (2-3 mins)**
Before designing anything, ask:
- What's the data source and volume?
- Batch or real-time? What latency is acceptable?
- Who are the consumers — analysts, ML models, dashboards?
- What's the SLA — how fresh does the data need to be?
- Any compliance or data retention requirements?

This shows maturity. Never start designing without clarifying.

---

**2. High Level Architecture (5 mins)**
Draw the data flow end to end:
```
Source → Ingestion → Storage → Processing → Serving → Consumption
```
Name the tool at each stage. For Uber context:
- Source: app events, databases, Kafka topics
- Ingestion: Kafka, Kinesis, batch extract
- Storage: S3, data lake, raw tables
- Processing: Spark, dbt, Airflow DAGs
- Serving: warehouse tables, marts
- Consumption: dashboards, ML models, APIs

---

**3. Deep Dive on Critical Components (10 mins)**
Pick the 2-3 hardest parts and go deep:
- How do you handle late arriving data?
- How do you ensure idempotency?
- How do you partition for query performance?
- How do you handle schema evolution?
- How do you backfill historical data?

---

**4. Batch vs Streaming Trade-off (5 mins)**
Always address this even if not asked:
- **Batch** — simpler, cheaper, higher latency, good for historical analysis
- **Streaming** — complex, expensive, low latency, good for real-time decisions
- **Lambda architecture** — both together, batch for accuracy, streaming for speed
- When to choose which — based on latency requirement from step 1

---

**5. Reliability + Monitoring (5 mins)**
- How do you handle failures? Retries, dead letter queues, alerting
- How do you monitor data quality? Row counts, freshness checks, anomaly detection
- How do you handle pipeline failures mid-run? Checkpointing, idempotent reruns
- SLA monitoring — what happens if data is late?

---

**6. Scale + Optimization (5 mins)**
- Partitioning strategy — by date, by region, by user_id
- File format — Parquet over CSV, columnar for analytical queries
- Caching — frequently accessed aggregations pre-computed
- Cost optimization — avoid full scans, use incremental processing

---

**The golden rule for HLD:**

Always think out loud. Say:
*"I'm going to start by clarifying requirements before jumping into the design"*

Then walk through each component sequentially. Never jump straight to tools — requirements first, architecture second, tools third.

---

**Now let's practice.**

Here's your scenario — answer it using the framework:

**"Design a data pipeline to track driver earnings at Uber. Drivers need to see their earnings in near real-time in the app. Finance needs accurate daily earnings reports. Data science needs historical earnings data for incentive modeling."**

Start with clarifying questions, then walk through the design. Take your time.



Good clarifying questions — you identified the dual requirement (real-time + batch) immediately which shows you understood the problem deeply.

A few additions that would strengthen your clarification:

- **Who are the consumers exactly?** — Driver app (real-time), Finance dashboard (daily batch), DS team (historical bulk access). Each has different latency and format needs.
- **What counts as "earnings"?** — Base fare only, or tips + surge + bonuses too? This affects the data model grain.
- **What's the acceptable latency for "near real-time"?** — 30 seconds? 5 minutes? This determines whether you need Kafka or if micro-batch is fine.
- **Scale** — How many active drivers? Uber has ~5M globally. That's the volume anchor.

---

**Now assume the interviewer answers:**
- Source: trip completion events from Kafka, ~500K trips/hour globally
- Near real-time: within 5 minutes for driver app
- Finance: accurate daily report by 6am next day
- DS: last 3 years of historical data
- Earnings = base fare + tips + surge + bonuses

---

Now go ahead — walk through the high level architecture. Name the tools at each stage, address both the real-time and batch paths.


Good instinct to ask — in a real interview always clarify the schema before designing. That's exactly what an experienced engineer does.

Assume the interviewer gives you this:

```
trip_completion_event
----------------------
trip_id          STRING
driver_id        STRING
rider_id         STRING
city             STRING
start_time       TIMESTAMP
end_time         TIMESTAMP
base_fare        DECIMAL
surge_multiplier DECIMAL
tips             DECIMAL
bonus            DECIMAL
distance_km      DECIMAL
status           STRING  -- 'completed', 'cancelled'
payment_method   STRING
event_timestamp  TIMESTAMP  -- when event was emitted
```

---

One thing to note for your design — `event_timestamp` vs `end_time` is an important distinction:

- `end_time` — when the trip actually ended
- `event_timestamp` — when the Kafka event was emitted

These can differ by seconds or minutes. For real-time earning calculations you use `event_timestamp`. For accurate financial reporting you use `end_time`. This difference matters when handling late arriving data — a trip that ended at 11:58pm but whose event arrived at 12:02am belongs to which day's finance report?

That's the kind of nuance that impresses interviewers at senior level.

---

Now walk through the high level architecture — both real-time and batch paths, tools at each stage.

Good thinking — you're already identifying two valid approaches. Let me probe each before you continue.

**On approach 1 — Kinesis → S3 → Athena:**

Athena queries S3 directly which means latency depends on how frequently Firehose flushes to S3. Firehose default buffer is 60 seconds to 15 minutes. So "near real-time" with Athena means 1-5 minute latency at best.

For driver app showing earnings — is 1-5 minutes acceptable? You said the requirement is within 5 minutes, so this barely works. But Athena has cold start query time on top of that, so it might exceed 5 minutes in practice.

**On approach 2 — Kinesis → S3 → Redis:**

This is actually stronger for the driver app use case. Pre-computed earnings stored in Redis gives sub-second read latency for the app. But now you need a processing layer between S3 and Redis — something that reads new events, calculates earnings, and writes to Redis.

**The question that unlocks your design:**

What sits between S3 and Redis to do the calculation and update? That's the critical component you haven't named yet.

Think about what tool would:
- Trigger when new data lands in S3
- Calculate `base_fare + tips + surge + bonus` per driver
- Aggregate with previously seen earnings for that driver
- Write the updated total to Redis

What would you use?

Exactly right — Lambda is the perfect fit here. Lightweight, event-driven, scales automatically, no infrastructure to manage.

So your real-time path is:

```
Kafka → Kinesis Firehose → S3 → Lambda (S3 trigger) → Redis → Driver App
```

That's a clean, production-grade real-time architecture. ✅

---

**Two follow-up probes on this path:**

**1. Idempotency**
What happens if the same `trip_completion_event` is delivered twice by Kinesis — which can happen due to at-least-once delivery? Your Lambda would double-count earnings for that trip.

How do you handle that?

**2. Late arriving events**
A driver completes a trip at 11:55pm but the Kinesis event arrives at 12:05am due to network delay. Your Lambda updates Redis correctly — but how do you know the driver's "today's earnings" boundary? Do you use `end_time` or `event_timestamp`?

Answer both — these are exactly the follow-up questions an Uber interviewer will probe.

A Kafka is really needed? Can't I send directly to Firehose?

Great question — and yes, you can send directly to Firehose without Kafka. Let me give you the honest trade-off:

**Without Kafka — Direct to Firehose:**
```
Trip Service → Kinesis Firehose → S3 → Lambda → Redis
```
- Simpler architecture
- Less operational overhead
- Firehose handles buffering and delivery to S3
- Fine if the only consumer is this earnings pipeline

**With Kafka in between:**
```
Trip Service → Kafka → Kinesis Firehose → S3 → Lambda → Redis
                    → Other consumers (ML, Analytics, Fraud detection)
```
- Multiple consumers can read the same trip event independently
- Replay capability — if Lambda fails, you can reprocess from Kafka
- Decouples the trip service from downstream consumers
- Standard at Uber scale where the same event feeds 10+ systems

---

**For Uber specifically — Kafka makes sense because:**
- Trip completion events are consumed by earnings, surge pricing, driver ratings, fraud detection, analytics simultaneously
- Uber's entire real-time infrastructure is built on Kafka
- Removing Kafka would mean each downstream system directly tapping the trip service — tight coupling at massive scale

**The right answer in the interview:**

*"Technically you can skip Kafka and go directly to Firehose if earnings is the only consumer. But at Uber's scale, trip completion events feed multiple downstream systems simultaneously — so Kafka acts as the central nervous system, decoupling producers from consumers and enabling replay."*

That shows architectural maturity — you know when a component is necessary vs optional.

Now answer the two probes from before:
1. How do you handle duplicate events in Lambda?
2. How do you handle late arriving data — `end_time` vs `event_timestamp`?

1. I need to manage idempotency via the Lambda function I believe, like if the event_id is already present then do not process it again sort of. 
2. I would be using event_timestamp, with a 10 min buffer to show today's earnings.

Both good answers. Let me sharpen them.

**On idempotency:**
Your approach is correct — but where do you store the seen `trip_id`s to check against? Lambda is stateless, so you need an external store.

Two options:
- **Redis itself** — store processed `trip_id` as a key with a TTL of 24 hours. Before processing, check if `trip_id` exists in Redis. If yes, skip. If no, process and add to Redis.
- **DynamoDB** — dedicated idempotency table with `trip_id` as partition key and TTL

Redis is the better choice here since you're already using it — one less infrastructure component.

So the complete idempotency logic:
```
Event arrives → Check Redis for trip_id → 
  If exists: skip
  If not: calculate earnings, update driver total, store trip_id with TTL
```
✅ Clean and practical.

---

**On late arriving data:**
The 10-minute buffer is a good instinct but think about what "buffer" means technically. If you use `event_timestamp` with a 10-minute buffer:

- Trip ends at 11:55pm → event arrives at 12:03am
- `event_timestamp` = 12:03am → belongs to next day's earnings
- But driver actually earned it on the previous day

So the buffer should work the other way — use `end_time` as the source of truth for which day the earning belongs to, and use `event_timestamp` only for when to process it.

The clean answer:

*"I'd use `end_time` for financial attribution — which day the earning belongs to. And `event_timestamp` for processing trigger — when the Lambda fires. For late arriving events where `event_timestamp` and `end_time` differ by more than a threshold, I'd flag them for reconciliation in the batch pipeline rather than silently attributing to the wrong day."*

That's a senior-level answer — you're not just solving the happy path, you're thinking about correctness under edge cases.

---

**Now let's move to the batch path.**

You have the real-time path done:
```
Trip Service → Kafka → Kinesis Firehose → S3 → Lambda → Redis → Driver App
```

Now design the batch path for:
- Finance — accurate daily earnings report by 6am
- Data Science — 3 years of historical data for incentive modeling

Walk through the architecture.


I would like to ask this question: 

1. What is the frequency at which the batch job should run? Like if it is finance reports by 6am, then I can have one batch job to process all the previous day's trips. I can extend the same model to support the incentive modeling team.

Good clarifying question — always right to confirm before designing.

Assume the interviewer says:

- **Finance** — once daily, processes previous day's completed trips, must be ready by 6am
- **Data Science** — ad-hoc access to 3 years of history, no strict SLA, needs clean partitioned data they can query efficiently

Now one follow-up from me before you design:

**You already have raw trip data landing in S3 from Firehose.** So the batch path doesn't need a separate ingestion layer — the data is already there.

The question is what happens *after* S3:
- How do you process it?
- How do you model it for Finance vs DS?
- How do you ensure the 6am SLA?
- How do you handle late arriving trips from the previous day?

Walk through the batch architecture now. Tools at each stage, how you'd structure the data model, and how you guarantee Finance gets accurate numbers by 6am.

So as the raw events are present in S3. Now I would like to push the events to Redshift using COPY command. Here the timestamp I'm interested to use is `end_time`. But in order to go for batch modelling I would like to know the metrics of interest for both finance and DS teams.

Good instinct to clarify metrics before modeling — that's exactly the "think in metrics before tables" mindset Slice was looking for too.

Assume the interviewer says:

**Finance needs:**
- Total earnings per driver per day (base fare + tips + surge + bonus)
- Total trips completed per driver per day
- City-level revenue aggregations
- Any adjustments or corrections to previous days

**Data Science needs:**
- Trip-level granular data — every attribute per trip
- Driver earnings history — daily rollups over 3 years
- Surge multiplier patterns by city and time of day
- Incentive payout history vs actual earnings

---

**Now one probe before you continue:**

You said COPY command to Redshift from S3 — that's valid. But think about this:

Firehose dumps raw JSON events to S3 continuously throughout the day. Your batch job runs once at night to process previous day's data.

**Two questions:**

1. How do you know which S3 files belong to "yesterday" — do you partition S3 by date? If not, how do you filter?

2. You mentioned using `end_time` for financial attribution — but some trips that ended yesterday might have their Firehose file land in today's S3 partition due to late delivery. How do you handle that in your batch job?

Answer these before designing the Redshift model — they affect how you structure both ingestion and the data model.


Because I would partition the S3 based on yyyy/mm/dd/hh format which is available in Firehose on top of event_timestamp attribute.

Good — S3 partitioning by `yyyy/mm/dd/hh` is the right call and Firehose supports this natively. ✅

But notice the conflict you've just created:

You said:
- **S3 partitioned by** `event_timestamp` — when the event was emitted
- **Financial attribution uses** `end_time` — when the trip actually ended

So a trip that **ended at 11:58pm** but whose **event was emitted at 12:03am** lands in tomorrow's S3 partition — but financially belongs to yesterday.

Your batch job processing `yyyy/mm/dd=yesterday` will **miss this trip entirely.**

This is the late arriving data problem. How do you handle it?

Two common approaches — think about which one you'd use:

**Option A — Reprocessing window**
Every night process not just yesterday's partition but also the last 2-3 hours of the previous day's partition to catch late arrivals. Then deduplicate in Redshift using `trip_id`.

**Option B — Use end_time for partitioning**
Repartition or rewrite S3 files based on `end_time` rather than `event_timestamp` before loading to Redshift. A separate Lambda or Glue job does this repartitioning.

**Option C — Reconciliation job**
Accept that the main batch job might miss some late arrivals. Run a separate reconciliation job at 5am that checks for any trips with `end_time = yesterday` that haven't been processed yet, regardless of which S3 partition they landed in.

Which approach would you use and why?

I would ike t go with Option A

Good choice — Option A is the most practical and commonly used. Simple, no extra infrastructure, handles most late arriving data.

**Flesh it out a bit more though:**

How exactly would you implement the reprocessing window? Specifically:

1. Which partitions do you process — just yesterday's, or yesterday + last N hours of the day before?
2. How do you deduplicate in Redshift when the same `trip_id` gets loaded twice — once in the original run, once in the reprocessing window?
3. How do you ensure the Finance report is still ready by 6am given the reprocessing adds extra time?

Answer these three — they're the natural follow-ups an interviewer will probe.

1. Yesterday + last 2-3 hours of day before
2. I need to load the data to a temp table first, then delete from main table based on `trip_id` and the load the temp_table data to main table and then delete the data in temp table
3. I need to start as early as possible so that SLA can be met. Ideally start the job at 1am, so that the job completes by 6 am.

All three are correct. Let me validate and sharpen each.

**On point 1** ✅
Yesterday's full partition + last 2-3 hours of day before catches the vast majority of late arrivals. In practice 99%+ of events arrive within 2 hours of `end_time`. Clean and practical.

**On point 2** ✅
That's the classic upsert pattern using a staging table:
```sql
-- Load to staging
COPY staging_trips FROM S3 ...

-- Delete existing records that will be refreshed  
DELETE FROM trips 
WHERE trip_id IN (SELECT trip_id FROM staging_trips)

-- Insert from staging
INSERT INTO trips SELECT * FROM staging_trips

-- Clean up
TRUNCATE staging_trips
```
This is idempotent — safe to run multiple times. ✅

**On point 3** ✅
Starting at 1am gives you a 5-hour window for a 6am SLA. Reasonable for previous day's volume. But add one thing — **SLA monitoring:**

*"I'd set up an Airflow DAG with SLA miss callbacks — if the job hasn't completed by 5am, alert the on-call engineer so there's time to investigate before Finance needs the report at 6am."*

That one addition shows production-grade thinking.

---

**Now you have the complete architecture:**

```
Real-time path:
Trip Service → Kafka → Kinesis Firehose → S3 → Lambda → Redis → Driver App

Batch path:
S3 (partitioned by event_timestamp yyyy/mm/dd/hh)
→ Airflow DAG (1am daily)
→ COPY to Redshift staging (yesterday + 2-3hrs day before)
→ Upsert to trips fact table (delete + insert via trip_id)
→ dbt models → Finance mart + DS mart
→ Finance report ready by 6am
→ DS historical data available for ad-hoc queries
```

---

**Now the data model.**

You know Finance and DS needs. Design the Redshift data model — fact and dimension tables, grain, what goes where.

Don't overthink it — walk through it like you would in an interview.

I would like to ask this question: Given the schema of the `trip_completion_event` is there any need to do data modelling? I was thinking to keep it as it is, and add DISTRIBUTE AND SORT KEYS so that data retrieval is easy. For aggregates we can always have fact tables.

Sharp question — and it shows good engineering judgment. You're not modeling for the sake of modeling.

The honest answer is: **partially yes, partially no.**

---

**Where you're right — keeping raw trips as-is:**
The `trip_completion_event` schema is already fairly clean and normalized. A `fact_trips` table that mirrors it closely with good distribution and sort keys is perfectly valid for both Finance and DS access patterns.

Good choices for Redshift:
```sql
DISTKEY(driver_id)  -- most queries filter/group by driver
SORTKEY(end_time)   -- most queries filter by date range
```
✅ Practical, defensible, production-grade.

---

**Where modeling adds value:**

**1. Earnings calculation**
Raw event has `base_fare`, `surge_multiplier`, `tips`, `bonus` separately. Finance and DS always want `total_earnings = base_fare * surge_multiplier + tips + bonus`. Rather than every downstream query recalculating this, derive it once in a `fact_trips` model.

**2. Aggregated marts**
- `fct_driver_daily_earnings` — pre-aggregated per driver per day. Finance queries this, not raw trips. Avoids expensive full scans on billions of trip rows every time Finance runs a report.
- `fct_city_daily_revenue` — city level rollup for Finance reporting

**3. Dimensions**
- `dim_driver` — driver attributes, city, signup date, tier
- `dim_city` — city metadata, region, country

These don't exist in your raw event — they come from other source systems and need joining.

---

**The answer that lands well in an interview:**

*"The raw trip event is clean enough that I wouldn't over-engineer the model. I'd keep a `fact_trips` table close to the source schema with derived `total_earnings`, distributed on `driver_id` and sorted on `end_time`. On top of that I'd build two aggregated marts — `fct_driver_daily_earnings` for Finance and a denormalized trip-level table for DS. Dimensions like `dim_driver` come from separate source systems and join at the mart layer."*

That's dimensional modeling thinking without unnecessary complexity.

---

**Final piece — monitoring and reliability.**

You have the full architecture now. Two quick questions to close the design:

1. How do you monitor data quality in this pipeline — what breaks first if something goes wrong and how do you catch it?
2. How do you handle a full pipeline failure — say the Airflow DAG fails at 3am. What's your recovery plan to still meet the 6am SLA?

1. For data quality I would like to keep some DQ checks like: freshness per hour or every 15 mins, assertion tests like earnings cannot be less than 0 etc. 
2. For this all i can think is to have more compute to process via a adhoc pipeline, so that after the failure the on-call engineer can trigger.

Both solid answers. Let me validate and sharpen.

**On data quality** ✅
Good instincts. Let me make it more concrete:

- **Freshness check** — alert if no new trips landed in S3 in the last 15 mins during peak hours. Catches Kafka or Firehose failures early.
- **Volume check** — compare today's trip count vs 7-day average for same hour. A 30% drop signals upstream issues.
- **Assertion tests** — `total_earnings >= 0`, `end_time > start_time`, `trip_id` uniqueness. These catch data corruption.
- **Reconciliation check** — after batch loads, compare Redshift trip count vs S3 file record count. Catches incomplete COPY operations.

Add one more critical one for Finance specifically:
- **SLA check** — Airflow callback at 5am if `fct_driver_daily_earnings` hasn't refreshed. Gives 1 hour buffer before Finance needs it.

---

**On pipeline failure recovery** ✅
Your answer is correct — more compute + manual trigger. Make it more precise:

*"The Airflow DAG is designed to be idempotent — safe to rerun from any point of failure. If it fails at 3am, the on-call engineer gets alerted via PagerDuty, assesses which task failed, clears that task in Airflow and reruns from that point rather than restarting the entire DAG. The staging + upsert pattern ensures no duplicate data regardless of how many times it reruns."*

Two additions that show production maturity:
- **Checkpointing** — Airflow tasks are granular enough that failure in dbt mart building doesn't require re-running the Redshift COPY
- **Runbook** — on-call engineer follows a documented runbook, not tribal knowledge

---

**You now have a complete end-to-end system design:**

```
Real-time path:
Trip Service → Kafka → Kinesis Firehose → S3 
→ Lambda (idempotent via Redis trip_id check) 
→ Redis → Driver App (< 5 min latency)

Batch path:
S3 (partitioned by event_timestamp yyyy/mm/dd/hh)
→ Airflow DAG (1am, PagerDuty alert if incomplete by 5am)
→ COPY to Redshift staging 
  (yesterday's partition + last 2-3hrs of day before)
→ Upsert to fact_trips 
  (delete + insert via trip_id, idempotent)
→ dbt models:
  - fct_driver_daily_earnings (Finance, ready by 6am)
  - fct_city_daily_revenue (Finance)
  - dim_driver, dim_city (from source systems)
  - Denormalized trip table (DS, 3 years history)

Data Quality:
→ Freshness checks every 15 mins
→ Volume anomaly detection vs 7-day average
→ Assertion tests (earnings >= 0, uniqueness)
→ Reconciliation check post-load
→ SLA monitoring with 5am alert
```

---

**Honest assessment of your HLD performance:**

| Area | Rating | Notes |
|---|---|---|
| Requirements clarification | Strong ✅ | Asked right questions upfront |
| Architecture | Strong ✅ | Real-time + batch paths clean |
| Tool choices | Good ✅ | Kafka, Firehose, S3, Lambda, Redis, Redshift all justified |
| Late arriving data | Good ✅ | Option A with reprocessing window |
| Idempotency | Strong ✅ | Redis dedup + staging upsert |
| Data modeling | Strong ✅ | Questioned over-engineering, right instinct |
| Data quality | Good ✅ | Needs more specificity on metrics |
| Failure recovery | Good ✅ | Needs runbook + checkpointing language |

---

You're ready for the HLD round. The framework is in your head now — requirements → architecture → deep dive → reliability → monitoring.

**One thing to practice before Wednesday:**

Say this design out loud from memory in 15 minutes without referring to notes. That's the real test — structured verbal delivery under time pressure.

**What the Airflow DAG actually orchestrates:**

At Uber scale, the DAG would look like this:

```
1. Check S3 data availability (sensor)
2. Run Glue/EMR Spark job — read S3, clean, deduplicate
3. COPY cleaned data to Redshift staging
4. Run upsert — delete + insert to fact_trips
5. Run dbt models — build marts
6. Run DQ checks — assertions, volume, reconciliation
7. Send success notification to Finance
```

---

**But for your design specifically — do you even need Spark?**

That depends on volume. Let's think about it:

- 500K trips/hour × 24 hours = ~12M trips/day
- Each event is maybe 500 bytes
- Total daily volume = ~6GB/day

**6GB/day is not big data.** Redshift COPY can handle this directly from S3 without Spark in between. Spark adds operational complexity that isn't justified at this volume.

So the honest answer for your design:

*"At 12M trips/day and ~6GB, I wouldn't introduce Spark just for the sake of it. Redshift COPY directly from S3 is sufficient. The Airflow DAG orchestrates the COPY command, the upsert logic via SQL, and then triggers dbt for mart building. If volume grows 10x — say 120M trips/day — then I'd introduce a Spark/EMR step between S3 and Redshift for pre-aggregation and cleaning."*

That's a mature answer — you're making deliberate tool choices based on actual requirements, not just listing technologies.

---

**So the Airflow DAG tasks are:**

```python
# Simplified DAG structure

check_s3_sensor          # wait for yesterday's S3 files
↓
copy_to_staging          # Redshift COPY from S3
↓
upsert_fact_trips        # delete + insert via trip_id
↓
dbt_run_marts            # build Finance + DS marts
↓
dq_checks                # assertions, volume, freshness
↓
sla_notification         # alert Finance team on success
```

Each task is a separate Airflow operator:
- `S3KeySensor` for file availability
- `RedshiftSQLOperator` for COPY and upsert
- `BashOperator` or `DbtCloudRunJobOperator` for dbt
- `PythonOperator` for DQ checks
- `SlackWebhookOperator` for notifications

---

**This is also a great answer for the C2 round** when they ask about your pipeline engineering experience — you can map your NCM Airflow DAG to this same pattern.

**SCD Type 2**

**What is SCD Type 2?**

SCD = Slowly Changing Dimension. It's how you track historical changes to dimension attributes over time.

**The problem it solves:**

Say you have a driver who moves from Bangalore to Mumbai. If you just update the record:

```
driver_id | city
1         | Mumbai  ← overwrites Bangalore
```

You've lost history. Any historical trip analysis now shows the driver was always in Mumbai — which is wrong.

**SCD Type 2 solution — add new row instead of updating:**

```
driver_id | city       | start_date  | end_date    | is_current
1         | Bangalore  | 2022-01-01  | 2024-06-30  | False
1         | Mumbai     | 2024-07-01  | 9999-12-31  | True
```

Now you can answer: *"What city was this driver in when they completed this trip?"* — by joining on `trip_date BETWEEN start_date AND end_date`.

---

**Key columns in SCD Type 2:**

- `surrogate_key` — synthetic primary key, unique per row (not driver_id)
- `natural_key` — the business key (driver_id)
- `start_date` — when this version became active
- `end_date` — when this version expired (9999-12-31 for current)
- `is_current` — boolean flag for easy filtering

---

**SCD Type 1 vs Type 2 trade-off:**

| | Type 1 | Type 2 |
|---|---|---|
| Approach | Overwrite | Add new row |
| History | Lost | Preserved |
| Storage | Less | More |
| Complexity | Simple | Complex |
| Use when | History doesn't matter | History matters |

**When to use Type 1:**
- Fixing data errors — wrong phone number, typo in name
- Attributes where history is irrelevant — email preferences

**When to use Type 2:**
- City, region, driver tier changes
- Price changes
- Any attribute that affects historical analysis accuracy

---

**Implementation in dbt:**

```sql
-- Identify changed records
WITH source AS (
    SELECT * FROM {{ source('raw', 'drivers') }}
),

existing AS (
    SELECT * FROM {{ this }}
    WHERE is_current = True
),

changed AS (
    SELECT s.*
    FROM source s
    LEFT JOIN existing e ON s.driver_id = e.driver_id
    WHERE e.driver_id IS NULL  -- new driver
    OR s.city != e.city        -- city changed
    OR s.tier != e.tier        -- tier changed
)

-- Expire old records
UPDATE {{ this }}
SET end_date = CURRENT_DATE - 1,
    is_current = False
WHERE driver_id IN (SELECT driver_id FROM changed)
AND is_current = True;

-- Insert new versions
INSERT INTO {{ this }}
SELECT
    {{ dbt_utils.generate_surrogate_key(['driver_id', 'start_date']) }},
    driver_id,
    city,
    tier,
    CURRENT_DATE as start_date,
    '9999-12-31' as end_date,
    True as is_current
FROM changed;
```

---

**Late arriving data problem with SCD Type 2:**

What if a record arrives today saying a driver moved to Mumbai on June 1st, but today is June 15th? You need to:

1. Find the currently active record
2. Expire it with `end_date = May 31st` — not today
3. Insert new record with `start_date = June 1st`
4. Potentially split an existing record if the change falls in the middle of an active period

This is the hardest part of SCD Type 2 — **backdated changes.**

---

**Now let's test your understanding.**

**Question 1:**

You have this `dim_driver` table:

```
surrogate_key | driver_id | city       | tier   | start_date  | end_date    | is_current
1             | D001      | Bangalore  | Silver | 2023-01-01  | 9999-12-31  | True
```

Driver D001 gets promoted to Gold tier on May 10th. What does the table look like after the SCD Type 2 update?

**Answer**
surrogate_key | driver_id | city      | tier   | start_date  | end_date    | is_current
1             | D001      | Bangalore | Silver | 2023-01-01  | 2024-05-09  | False
2             | D001      | Bangalore | Gold   | 2024-05-10  | 9999-12-31  | True


**Question 2 — harder**:
Now a record arrives today (May 10th) saying Driver D001 actually moved from Bangalore to Mumbai on April 1st — a backdated change.
Current table state is what you just saw above — Silver until May 9th, Gold from May 10th.
What should the table look like after processing this backdated city change?

**Answer**
surrogate_key | driver_id | city      | tier   | start_date  | end_date    | is_current
1             | D001      | Bangalore | Silver | 2023-01-01  | 2024-03-31  | False
2             | D001      | Mumbai    | Silver | 2024-04-01  | 2024-05-09  | False
3             | D001      | Mumbai    | Gold   | 2024-05-10  | 9999-12-31  | True
**Scenario:**

Uber wants to build a data warehouse to track **driver incentives and payouts**. Here's the business context:

- Uber runs weekly incentive programs for drivers — e.g. *"Complete 50 trips this week and earn ₹2000 bonus"*
- Incentive programs vary by city, vehicle type, and driver tier
- A driver can be eligible for multiple incentive programs simultaneously
- At the end of each week, eligible drivers receive payouts
- Finance needs to report total incentive spend by city, program, and week
- DS needs to analyze which incentive programs drive the most incremental trips

**Source data available:**
- Driver profiles — driver_id, city, tier, vehicle_type, signup_date
- Incentive programs — program_id, program_name, city, tier_eligibility, vehicle_eligibility, target_trips, bonus_amount, start_date, end_date
- Trip completions — trip_id, driver_id, trip_date, status
- Payouts — payout_id, driver_id, program_id, week_start_date, trips_completed, bonus_paid, payout_date

---

**Your task:**

Design the dimensional model. Walk through:

1. What are your fact tables and what's the grain of each?
2. What are your dimensions?
3. How do you handle SCD Type 2 where relevant?
4. How does Finance query total incentive spend by city and week?
5. How does DS access incremental trip analysis?

Take your time — think out loud as you go.


Of course. Let me walk you through how to think about dimensional modeling systematically — this is the framework to apply to any scenario.

---

**Step 1 — Identify the business processes first**

Before thinking about tables, ask: *what are the things that happen in this business?*

For this scenario:
- Drivers **complete trips**
- Drivers **earn incentives** based on trips
- Uber **pays out** bonuses to eligible drivers

Each business process typically becomes a fact table.

---

**Step 2 — Define the grain of each fact table**

Grain = one row represents what exactly?

This is the most important decision in dimensional modeling. Get grain wrong and everything downstream is wrong.

For each business process ask: *what is the most atomic event?*

- Trip completions → one row per trip *(trip_id)*
- Incentive eligibility → one row per driver per program per week *(driver_id + program_id + week)*
- Payouts → one row per payout *(payout_id)*

---

**Step 3 — Identify measures (facts)**

What numbers live in each fact table?

- Trip fact → fare_amount, distance_km, duration
- Incentive fact → trips_completed, trips_target, completion_pct
- Payout fact → bonus_paid

---

**Step 4 — Identify dimensions**

Dimensions answer: *who, what, where, when, which?*

Look at each fact table and ask what context surrounds each event:

- **Who** — driver
- **What** — incentive program
- **Where** — city
- **When** — date/week
- **Which** — vehicle type, tier

These become your dimension tables.

---

**Step 5 — Identify where SCD Type 2 is needed**

Ask: *does this dimension attribute change over time and does that change matter for historical analysis?*

- Driver city changes → does it affect incentive eligibility analysis? Yes → Type 2
- Driver tier changes → does it affect which programs they qualified for? Yes → Type 2
- Program bonus amount changes → does it affect payout analysis? Yes → Type 2
- Driver name changes → does it affect any analysis? No → Type 1

---

**Step 6 — Think about how stakeholders query**

Work backwards from the questions Finance and DS need to answer:

**Finance:** *"Total incentive spend by city and week"*
→ Need payout fact + city dimension + date dimension
→ City must be on the payout fact or joinable via driver dimension

**DS:** *"Which programs drove the most incremental trips?"*
→ Need trip fact + incentive program dimension
→ Need to link trips to programs the driver was enrolled in that week

This tells you whether you need bridge tables, what foreign keys to include, and where pre-aggregation helps.

---

**Step 7 — Draw the star schema**

Center = fact table
Surrounding = dimension tables
Each dimension joins to fact via surrogate key

```
                    dim_date
                       |
dim_driver ——— fct_payouts ——— dim_program
                       |
                    dim_city
```

---

**Now apply this thinking to the scenario:**

Go through each step out loud:

1. What are your fact tables and grain?
2. What are your dimensions?
3. Where do you apply Type 2?
4. How does the star schema look?

**Scenario: Uber Driver Incentives Data Warehouse**

You have these source systems:
- Driver profiles — driver_id, city, tier, vehicle_type, signup_date
- Incentive programs — program_id, program_name, city, tier_eligibility, vehicle_eligibility, target_trips, bonus_amount, start_date, end_date
- Trip completions — trip_id, driver_id, trip_date, status
- Payouts — payout_id, driver_id, program_id, week_start_date, trips_completed, bonus_paid, payout_date

**Business questions to answer:**
- Finance: Total incentive spend by city and week
- DS: Which programs drove the most incremental trips?


How many fact tables do you need for the Uber driver incentives scenario, and what does one row represent in each?

Good — 3 fact tables is right. Now define the grain for each.

**What does one row represent in:**

1. `fct_trips` — one row per ___?
2. `fct_incentive` — one row per ___?
3. `fct_payouts` — one row per ___?

Be specific — grain definition is the most important decision in dimensional modeling. Don't just say "one row per trip" — think about whether you need driver + program + week level or something more granular.

Let me validate the reasoning:

**fct_trips** — one row per trip_id ✅
Most atomic event. Stores base fare, distance, duration. Links to driver, date, city dimensions.

**fct_incentive** — one row per driver + week + program ✅
Correct grain. A driver can be enrolled in multiple programs simultaneously, so you need program in the grain. Week is the incentive cycle. This table tracks progress — trips_completed vs target.

**fct_payouts** — one row per driver + week ✅
Payout happens once per driver per week — aggregated across all programs they qualified for. Or should it be one row per driver + week + program? Think about this — if a driver qualifies for 3 programs in one week, do they get one combined payout or three separate payouts?

What do you think?
> Aggregated across programs per week

That works — but flag it as an assumption in the interview.

In reality payout structure varies by company:
- Some pay per program separately — driver gets 3 payouts for 3 programs
- Some aggregate into one weekly payout — simpler for accounting

**The right interview answer:**

*"I'd clarify with Finance how payouts are structured — per program or aggregated weekly. If aggregated, grain is driver + week. If per program, grain is driver + week + program. I'll assume aggregated for now."*

That shows you think about business rules before locking grain — which is exactly what the C2 evaluator wants to see.

---

**Now Step 2 — Dimensions.**

You have 3 fact tables. What dimension tables do you need?

For each dimension tell me:
- Name
- Key attributes
- Whether it needs SCD Type 2 and why

> I guess these are the dimension tables: driver table, program table, city table, date table for week calculation, vehicle type table, tier table.

Good list — but let me push back on a few:

**`dim_vehicle_type` and `dim_tier` — do these need separate dimension tables?**

Think about it — vehicle type and tier are attributes of a driver, not independent entities. They don't have their own measures or rich attributes. 

Do they deserve their own tables or should they live inside `dim_driver`?

**`dim_city` — same question.**

City is an attribute of both drivers and incentive programs. Does it need its own table or can it be a column in `dim_driver` and `dim_program`?

---

**The rule of thumb:**

A separate dimension table is justified when:
- It has multiple descriptive attributes of its own
- It's shared across multiple fact tables as a conformed dimension
- It changes independently of the entity it describes

A simple attribute stays inside the parent dimension when:
- It only has one or two values
- It doesn't have rich descriptive attributes
- It only relates to one entity

---

Apply this thinking — which of your 6 dimensions deserve their own tables and which should collapse into parent dimensions?

> City can be an individual entity as well, which can be used for other things as well like pincodes etc. So I’m thinking city to be separate. If vehicle type and tier are driver attributes then we need to decide on the scd type 2 implementation on how

Exactly right on both points. Good reasoning.

**On city** ✅
Correct — city as a conformed dimension makes sense when it has rich attributes (pincode, region, country, timezone) and is shared across multiple fact tables. At Uber, city is a first-class entity — it drives surge pricing, incentive programs, regulatory requirements. Separate dimension justified.

**On vehicle_type and tier inside dim_driver** ✅
Correct — they stay as attributes of dim_driver. But now the SCD Type 2 question becomes important as you flagged.

The decision:

- **tier → Type 2** — affects incentive eligibility historically. If a driver was Bronze during week 3 and Silver during week 4, that changes which programs they qualified for. History matters. ✅
- **vehicle_type → Type 2** — same reasoning. A driver on a Bike qualifies for different programs than on a Car. Historical accuracy matters for incentive analysis. ✅
- **city → Type 2 on dim_driver** — if a driver moves cities, which city's incentive programs did they qualify for historically? History matters. ✅

---

**So your confirmed dimension tables are:**

1. `dim_driver` — with Type 2 on tier, vehicle_type, city
2. `dim_program` — incentive program details
3. `dim_city` — conformed dimension, rich city attributes
4. `dim_date` — week, month, quarter, year

---

**Now Step 3 — the star schema.**

How do your fact tables connect to dimensions? Draw it out in text — which foreign keys live in each fact table?

For example:
```
fct_trips → (driver_sk, city_sk, date_sk, ...)
fct_incentive → (...)
fct_payouts → (...)
```

Fill in the foreign keys for each fact table.

Good structure — a few things to tighten:

**fct_trips:**
- `city_sk` appears twice — remove the duplicate
- Add `trip_id` as the natural key — but remember in dimensional modeling the PK is a surrogate key, not the natural key. So it's `trip_sk` as PK, `trip_id` as natural key for traceability
- Add measures — `fare_amount`, `distance_km`, `duration_mins`, `status`

**fct_incentive:**
- Good — but add `program_sk` should link to `dim_program`
- Add measures — `trips_completed`, `trips_target`, `completion_pct`
- Missing: how do you know if the driver **qualified** for the program? Add `is_eligible` flag and `is_paid` flag

**fct_payouts:**
- Missing `program_sk` — wait, you said grain is driver + week aggregated across programs. So program_sk doesn't belong here. ✅
- Add measures — `total_bonus_paid`, `programs_qualified_count`

---

**Corrected schema:**

```
fct_trips
---------
trip_sk (PK)
driver_sk (FK → dim_driver)
city_sk (FK → dim_city)
date_sk (FK → dim_date)
trip_id (natural key)
fare_amount
distance_km
duration_mins
status

fct_incentive
-------------
incentive_sk (PK)
driver_sk (FK → dim_driver)
program_sk (FK → dim_program)
date_sk (FK → dim_date)
trips_completed
trips_target
completion_pct
is_eligible
is_paid

fct_payouts
-----------
payout_sk (PK)
driver_sk (FK → dim_driver)
date_sk (FK → dim_date)
total_bonus_paid
programs_qualified_count
```

---

**Now Step 4 — answer the business questions.**

**Finance query:** Total incentive spend by city and week.

City is on `dim_driver` and `dim_city` — but `fct_payouts` only has `driver_sk` and `date_sk`. How do you get city into the Finance report?

Think about this carefully — it's a common dimensional modeling trap.

> Driver's city will be in the driver's table and it'll taken directly from there based on scd-2 structure depending on dates.

Exactly right — and you instinctively knew to use SCD Type 2 here which is the key insight.

The join logic:

```sql
SELECT 
    c.city_name,
    d.week,
    SUM(p.total_bonus_paid) as total_incentive_spend
FROM fct_payouts p
JOIN dim_driver dr 
    ON p.driver_sk = dr.surrogate_key
    -- SCD Type 2 join on payout date
    AND p.payout_date BETWEEN dr.start_date AND dr.end_date
JOIN dim_city c ON dr.city_sk = c.city_sk
JOIN dim_date d ON p.date_sk = d.date_sk
GROUP BY c.city_name, d.week
```

The critical line is:
```sql
AND p.payout_date BETWEEN dr.start_date AND dr.end_date
```

This ensures you're joining to the driver's city **at the time of payout** — not their current city. That's SCD Type 2 working correctly in practice. ✅

---

**Now DS query:**

*"Which incentive programs drove the most incremental trips?"*

This is harder. Think about what "incremental" means:

- Not just total trips during the incentive period
- But trips **above what the driver would have done anyway** — the baseline

How would you approach this from a data modeling perspective? What data do you need and how do you structure the query?

> Say we have a target, and total_trips per incentive program, then where the max of total_trips-target occurs

Good instinct — but that's measuring **overachievement**, not **incrementality**.

A driver who completed 60 trips against a target of 50 overachieved by 10. But maybe they would have done 55 trips anyway without the incentive. The true incremental lift is only 5, not 10.

**True incrementality requires a baseline — what would the driver have done without the incentive?**

The standard approach in DS/analytics:

**Option 1 — Historical baseline**
Compare driver's trips during incentive week vs their average trips in the 4 weeks before the incentive started. The difference is the lift.

```
incremental_trips = trips_during_incentive - avg_trips_pre_incentive
```

**Option 2 — Control group**
Some drivers are enrolled in the program, some aren't. Compare trip counts between enrolled and non-enrolled drivers in the same city and tier. The difference is the lift.

---

**From a data modeling perspective — what do you need to support Option 1?**

You need:
- `fct_trips` — trip counts per driver per week, historical
- `fct_incentive` — which drivers were enrolled in which program and when
- `dim_date` — to calculate the 4-week pre-incentive window

**The query structure:**

```sql
WITH baseline AS (
    -- avg trips per driver in 4 weeks before incentive
    SELECT 
        t.driver_sk,
        AVG(weekly_trips) as baseline_trips
    FROM fct_trips t
    JOIN dim_date d ON t.date_sk = d.date_sk
    WHERE d.week BETWEEN incentive_start - 4 AND incentive_start - 1
    GROUP BY t.driver_sk
),

incentive_period AS (
    -- trips during incentive week
    SELECT
        t.driver_sk,
        i.program_sk,
        COUNT(t.trip_sk) as actual_trips
    FROM fct_trips t
    JOIN fct_incentive i ON t.driver_sk = i.driver_sk
    JOIN dim_date d ON t.date_sk = d.date_sk
    WHERE d.week = incentive_week
    GROUP BY t.driver_sk, i.program_sk
)

SELECT 
    p.program_sk,
    dp.program_name,
    SUM(ip.actual_trips - b.baseline_trips) as total_incremental_trips
FROM incentive_period ip
JOIN baseline b ON ip.driver_sk = b.driver_sk
JOIN dim_program dp ON ip.program_sk = dp.program_sk
GROUP BY p.program_sk, dp.program_name
ORDER BY total_incremental_trips DESC
```

---

**This is exactly what DS needs** — rank programs by true incremental lift, not just raw trip counts.

---

**Overall dimensional modeling assessment:**

| Area | Status |
|---|---|
| Fact table identification | Strong ✅ |
| Grain definition | Strong ✅ |
| Dimension identification | Good ✅ |
| SCD Type 2 reasoning | Strong ✅ |
| Star schema foreign keys | Good ✅ |
| SCD Type 2 join logic | Strong ✅ |
| Incrementality concept | Needed guidance |

You're ready for C2 dimensional modeling questions. The Uber driver incentives scenario is more complex than what they'll likely give you — movie booking and food delivery are simpler domains.

---

Smart — noting it on paper is the right move. Writing forces clarity.

**Key decision points to note for Uber Driver Incentives:**

```
Fact tables (3):
- fct_trips → grain: one row per trip_id
- fct_incentive → grain: one row per driver + week + program
- fct_payouts → grain: one row per driver + week (aggregated)

Dimensions (4):
- dim_driver → SCD Type 2 on tier, vehicle_type, city
- dim_program → incentive program details
- dim_city → conformed dimension
- dim_date → week, month, quarter

Key decisions:
- Vehicle_type and tier inside dim_driver not separate tables
- City separate — conformed, rich attributes
- SCD Type 2 join: payout_date BETWEEN start_date AND end_date
- Incrementality = actual trips - baseline (4-week pre-incentive avg)
```

---

**Now let's move fast — three scenarios to cover:**

1. Movie booking app
2. Food delivery app
3. End to end metric for Uber

I'll run these differently from the incentives exercise — faster pace, less hand-holding, more like the real interview. You walk through each one, I probe only where needed.

**Movie Booking App — start.**

Business context:
- Users book seats for movies across multiple theatres and cities
- Shows run multiple times per day per screen
- Finance needs revenue reporting by movie, theatre, city, week
- Product needs funnel analysis — search → view → select seat → book → pay

**Go straight to fact tables and grain. No warmup — just start.**

> We need bookings fact table which has booking_id, user_id, show_id, theatre_id, city_id, date, booking_amount, status, slot_id. Second we need a events fact table for funnel analysis.

Good start — two fact tables, right instinct. Now define the grain precisely for each.

**One probe before you continue:**

`show_id` in `fct_bookings` — does that capture everything you need about the show? A show has a movie, a screen, a theatre, a time slot. Should these be separate dimensions or collapsed into `show_id`?

Also — what's the grain of `fct_events` for funnel analysis? One row per what exactly?

Answer both then continue to dimensions.

> 1. fct_bookings: has show_id, say it's the movie name referencing, then it separately has theatre_id(or screen_id for better grain), city_id, and slot_id separately. 
> 2. fct_events: is the event captureing at the grain of user_id, session_id, event_id

Good — let me validate both:

**fct_bookings grain** ✅
One row per booking_id. The foreign keys you listed are correct:
- `show_id` → references `dim_show` (movie + time)
- `screen_id` → better than theatre_id, captures exact screen
- `city_id` → conformed dimension
- `slot_id` → time slot reference
- `user_id` → who booked

Good catch on screen_id over theatre_id — a theatre has multiple screens, so screen_id is more granular and accurate.

**fct_events grain** ✅
One row per event_id — each user action captured atomically. `session_id` groups events into a session, `user_id` identifies who, `event_type` identifies what (search, view, select, book, pay).

---

**Now dimensions — list them out quickly with SCD Type 2 where relevant.**

Don't overthink — fast pass.

> Dimensions are : 
`dim_show`: It has PK as show_id, and attributes, name and others regarding the movie, it connects to screen and slots. 

> `dim_screen`: screen_id as PK, and it has theatre details. It connects to dim_show and SCD type -2 applies here. This connects to other dimensions for city attributes as well. 
> `dim_city`: City details
> `dim_slot`: Slot details
> `dim_user`: User details

Good list — let me push back on a few things:

**`dim_show` — contains movie details?**
Think about this — a movie like "Interstellar" runs across 100 theatres in 50 cities with 500 shows. If movie details live in `dim_show`, you're repeating "Interstellar, Christopher Nolan, Sci-Fi, 169 mins" 500 times.

Should `dim_movie` be separate from `dim_show`?

**`dim_screen` — SCD Type 2?**
What changes on a screen over time that matters historically? Screen capacity, screen type (IMAX vs regular)? Think about whether history actually matters here for any business question.

**`dim_user` — SCD Type 2?**
User city changes, user tier (loyalty program) changes — do these affect historical booking analysis? Should Type 2 apply?

---

**Revised dimension list to think about:**

```
dim_movie → movie details, genre, language, duration
dim_show → movie_sk + screen_sk + slot_sk + date (bridge)
dim_screen → screen details, capacity, type, theatre_sk
dim_theatre → theatre details, city_sk
dim_city → conformed
dim_slot → time slot details
dim_user → SCD Type 2 on city, loyalty tier
dim_date → standard
```

```
Fact tables (2):
- fct_bookings → grain: one row per booking_id
  FKs: user_sk, show_sk, screen_sk, city_sk, slot_sk, date_sk
  Measures: booking_amount, seats_booked, status

- fct_events → grain: one row per event_id
  FKs: user_sk, session_id, date_sk
  Measures: event_type, event_timestamp, time_spent

Dimensions (8):
- dim_movie → movie details, genre, language, duration
- dim_show → movie_sk + screen_sk + slot_sk (bridge)
- dim_screen → capacity, type, theatre_sk
- dim_theatre → theatre details, city_sk
- dim_city → conformed
- dim_slot → time slot details
- dim_user → SCD Type 2 on city, loyalty tier
- dim_date → standard

Key decisions:
- dim_movie separate from dim_show — avoids repetition
- screen_id over theatre_id — better grain
- dim_screen SCD Type 2 not needed — screen attributes rarely change
- dim_user SCD Type 2 — loyalty tier affects historical analysis
```


**Food Delivery App — go.**

Business context:
- Users order food from restaurants via app
- Orders go through states: placed → confirmed → picked up → delivered → completed
- Drivers pick up and deliver orders
- Finance needs revenue by restaurant, city, week
- Product needs delivery time analysis and order funnel
- DS needs demand forecasting by area and time of day

**Fact tables and grain — go fast.**

Fact table: `fct_orders`, it has SCD Type 2 on order status. Hence it can have delivery time analysis and order funnel as well. The grain is order_id+order_status

Good instinct on capturing order status — but SCD Type 2 is the wrong pattern here.

**Why SCD Type 2 doesn't apply to fact tables:**

SCD Type 2 is for **dimensions** — slowly changing attributes of entities like drivers, users, restaurants. It tracks "who/what something was at a point in time."

For **order state transitions** — placed → confirmed → picked up → delivered — you're tracking events, not slowly changing attributes. Each state change is a measurable business event.

**Two better approaches:**

**Option 1 — One row per order (latest state)**
```
fct_orders → grain: one row per order_id
status, placed_at, confirmed_at, picked_at, delivered_at
```
Simple but loses intermediate state history.

**Option 2 — One row per order state transition**
```
fct_order_events → grain: one row per order_id + status
order_id, status, event_timestamp, previous_status
```
Full history, enables funnel analysis, delivery time calculations.

**Which one do you choose and why?**

For the business questions given — funnel analysis, delivery time — which grain serves better?

> Yes, I would go by option 2 for funnel analysis and delivery analysis. It's not SCD type -2 but state cahnges.

Exactly right — and the distinction matters:

- **SCD Type 2** — dimension attribute changes slowly, history preserved for accurate joins
- **State transitions** — fact events, each state change is a measurable business event

That's a senior-level distinction. In the interview say it explicitly:

*"Order status transitions are fact events, not slowly changing dimension attributes — so I'd model them as a state transition fact table, not SCD Type 2."*

---

**So your fact tables:**

```
fct_order_events → grain: one row per order_id + status
fct_orders → grain: one row per order_id (latest state, for simple reporting)
```

Having both is valid — `fct_orders` for Finance revenue reporting, `fct_order_events` for funnel and delivery time analysis.

Do you need a third fact table for anything?

Think about — drivers picking up and delivering orders. Is that captured in `fct_order_events` or does it need its own fact table?

> It gets captured in `fct_order_events` itself, not need of a third table here.

Correct — driver assignment and pickup are just state transitions within `fct_order_events`. No need for a separate fact table. ✅

---

**Now dimensions — fast pass. Same structure as before.**

What dimensions do you need for food delivery? List them with SCD Type 2 where relevant.

Think about: who are the entities, what are the conformed dimensions, what changes over time and matters historically.

```
`dim_status`: Has status id, staus name etc. 
`dim_date`: for date details
`dim_driver`: driver details, ca have SCD type 2 if required
`dim_restraunts`: restraunt details
`dim_city`: City details
`dim_user`: user details with type 2

As menu level details are not asked it can be skipped by saying. If need to include, we can have dim_restraunt_menu like all food items a particular restraunt can offer with is_active/is_available flag which can be SCD type 1
```

Strong list — and the menu reasoning is excellent. Let me give quick feedback on each:

**`dim_status`** — valid but lightweight. Status is a small lookup table with maybe 5-6 values. Some modelers keep it as a dimension, others just hardcode status as a string column in the fact table. Either is defensible — just be ready to justify.

**`dim_date`** ✅ — standard, always needed.

**`dim_driver`** — yes, SCD Type 2 on city and vehicle type. Same reasoning as Uber incentives. ✅

**`dim_restaurant`** — good. What would SCD Type 2 apply to here? Think about what changes on a restaurant that affects historical order analysis.

**`dim_city`** ✅ — conformed dimension, same as before.

**`dim_user`** ✅ — SCD Type 2 on city, delivery address area, loyalty tier.

**`dim_restaurant_menu`** — excellent reasoning. ✅
- `is_available` → Type 1, current availability only
- Price changes → actually Type 2 if DS needs to know what price was charged historically — but since `fct_orders` captures `order_amount` directly, price history is already in the fact. So Type 1 is fine here.

---

**One thing missing:**

What about the **delivery area or zone**? Uber Eats and Swiggy operate by zones/clusters — restaurants serve specific zones, demand forecasting is by zone and time of day. Do you need a `dim_zone` or does `dim_city` cover that?

> `dim_zone` is needed, and in fact `dim_zone` should be having city_sk to get `city_details` and `dim_zone` has more details on zone level things.


Exactly right. `dim_zone` as a child of `dim_city` — zone rolls up to city, city rolls up to region. That's a classic snowflake dimension hierarchy.

```
dim_zone
---------
zone_sk (PK)
city_sk (FK → dim_city)
zone_name
zone_area_sqkm
avg_delivery_time_mins
demand_tier  -- high/medium/low
```

This enables DS demand forecasting at zone level and Finance revenue reporting at city level — both from the same conformed hierarchy. ✅

---

**Lock the food delivery model:**

```
Fact tables (2):
- fct_order_events → grain: one row per order_id + status
  FKs: order_id, status_sk, driver_sk, user_sk, 
       restaurant_sk, zone_sk, date_sk
  Measures: event_timestamp, time_in_status_mins

- fct_orders → grain: one row per order_id
  FKs: user_sk, restaurant_sk, zone_sk, date_sk
  Measures: order_amount, delivery_fee, 
            total_delivery_time_mins, final_status

Dimensions (8):
- dim_status → status lookup
- dim_driver → SCD Type 2 on city, vehicle_type
- dim_restaurant → SCD Type 2 on city, cuisine_type
- dim_restaurant_menu → Type 1 on is_available, is_active
- dim_user → SCD Type 2 on city, loyalty_tier
- dim_zone → zone details, city_sk
- dim_city → conformed
- dim_date → standard

Key decisions:
- Order status = state transitions not SCD Type 2
- Two fact tables — events for funnel, orders for revenue
- dim_zone child of dim_city — snowflake hierarchy
- Menu as separate dimension, Type 1 only
```

---

**Last one — End to End Metric for Uber.**

This is different from the previous two. It's not about designing a data warehouse for an app — it's about how you define, calculate, govern, and serve a metric reliably across the organization.

The classic example: **"Trips per Active Driver"**

Business context:
- Multiple teams calculate this metric differently
- Finance uses one definition, Product uses another, Operations uses a third
- Leadership gets three different numbers in three different meetings
- You're asked to fix this

**Walk me through how you'd approach this end to end.**

Start with: how do you even define "active driver" and "trips" — what questions do you ask before writing a single line of SQL?

Strong answers on 1, 2, and 3. Let me validate and sharpen, then answer 4 for you.

**On point 1** ✅
Exactly right — sometimes multiple definitions are legitimate. The key is **explicit context labeling**:
- `active_drivers_finance` — completed 1+ trips this month
- `active_drivers_product` — logged in last 7 days
- `active_drivers_ops` — online 1+ hours today

Each has a clear owner, clear use case, and clear documentation. Ambiguity comes from undefined context, not from having multiple definitions.

**On point 2** ✅
Semantic layer is the right answer — tools like dbt Metrics, Looker LookML, or Cube.dev. Metrics are defined once, versioned, and served consistently to all consumers.

**On point 3** ✅
Views enforce a single calculation. Nobody can accidentally rewrite the logic because they're querying the view, not the underlying table. This is the simplest form of metric governance.

In dbt terms:
```yaml
metrics:
  - name: trips_per_active_driver
    label: Trips per Active Driver
    model: ref('fct_trips')
    description: "Completed trips divided by drivers with 1+ trips in last 30 days"
    calculation_method: derived
    expression: "{{ metric('completed_trips') }} / {{ metric('active_drivers') }}"
    timestamp: trip_date
    time_grains: [day, week, month]
```

One definition, version controlled, documented. ✅

**On point 4 — how do you ensure nobody diverges:**

Four mechanisms:

**1. Data contracts**
Upstream tables that feed the metric have schema contracts — column names, types, and business rules are locked. Any breaking change requires approval. Nobody can silently rename `completed_trips` to `finished_trips` and break the metric.

**2. Metric store as single source of truth**
All dashboards, reports, and notebooks must pull from the semantic layer — not write their own SQL. This is enforced through access controls — analysts get read access to the metric store, not to raw tables.

**3. Automated testing**
dbt tests run on every deployment:
- Volume checks — metric value shouldn't drop 30%+ day over day
- Consistency checks — `active_drivers_finance` should always be ≥ `active_drivers_ops`
- Freshness checks — metric must refresh within SLA

**4. Deprecation process**
When a definition needs to change, you version it — `active_drivers_v2` — run both in parallel, communicate the change, set a sunset date for v1. No silent changes.

---

**The complete end to end metric lifecycle:**

```
1. Definition → align stakeholders, document context
2. Governance → assign metric owner, approval process for changes
3. Implementation → dbt metric, semantic layer view
4. Serving → dashboards pull from semantic layer only
5. Testing → automated DQ checks on every run
6. Monitoring → alert on anomalies, freshness SLA
7. Deprecation → versioned changes, sunset process
```

---

**This is your strongest C2 answer** — it touches data contracts, semantic layer, dbt metrics, governance, and testing all in one. These are exactly the themes Slice also cares about deeply.

---

**Quick assessment of all three scenarios:**

| Scenario | Fact Tables | Dimensions | Key Decisions | Overall |
|---|---|---|---|---|
| Movie booking | Strong ✅ | Strong ✅ | dim_movie split, screen_id | Strong |
| Food delivery | Strong ✅ | Strong ✅ | State transitions vs SCD2 | Strong |
| Uber metric | Strong ✅ | N/A | Semantic layer, governance | Strong |

You're ready for C2 tomorrow.

---

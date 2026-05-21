# Prep: Streaming Events

```json
INGESTION:
Dashcam (edge AI detects event)
↓
HTTPS → API Gateway → Lambda
↓
Kafka topics:
- telemetry_raw (partitioned by vehicle_id)
- harsh_events (partitioned by vehicle_id)

HOT PATH (real-time):
harsh_events Kafka topic
↓
Flink application:
- Read event
- Enrich from Redis:
  → driver profile
  → location context (tile-based)
  → events_today counter
- Severity assessment
- If above threshold:
  → Publish to SNS
  → SNS fan-out:
    → Push notification (FCM/APNs)
    → SMS
    → Email (SES)
    → WebSocket → dashboard

COLD PATH (batch):
Kafka → Kinesis Firehose → S3
  (partitioned by date/vehicle_id)
  → Used for: training data, compliance, historical analysis

SAFETY SCORE UPDATE:
harsh_events → Flink → Redis
  → Update driver's running score
  → Persist to RDS every 5 minutes

ANALYTICS DASHBOARD:
Flink → analytics Kafka topic
→ Aggregation service:
  → Active vehicles count
  → Events last hour
  → Fleet safety score
→ DynamoDB (real-time metrics)
→ Dashboard polls every 30 seconds

MONITORING:
CloudWatch:
→ Kafka consumer lag — alert if Flink falling behind
→ End-to-end latency — alert if >20 seconds
→ SNS delivery failures
→ Redis cache hit rate
```

**Framework**: 

```json
1. Data ingestion — how telemetry and events get to cloud
2. Stream processing — how events are enriched and filtered
3. Alert generation — how fleet managers get notified in 30 seconds
4. Safety score update — how driver scores update in real time
5. Analytics pipeline — how dashboard gets fed
6. Monitoring — how you ensure 30-second SLA
```

**Ingestion**: 

```json
Device (MQTT/HTTPS)
↓
API Gateway+Lambda / IoT broker
  (handles 100K connections)
↓
Kafka producer
  (publishes to topics)
↓
Kafka cluster
  (telemetry_raw, harsh_events)
```

Options for the IoT broker layer:

- **AWS IoT Core** — managed, handles MQTT at scale
- **Custom API Gateway + Lambda** — HTTPS from device, Lambda publishes to Kafka
- **Confluent Kafka REST proxy** — devices POST directly via HTTPS

Since you said you don't know IoT Core — use the API Gateway + Lambda approach:

*"Devices send events via HTTPS to API Gateway. Lambda receives the request, validates the payload, and publishes to the appropriate Kafka topic — telemetry_raw or harsh_events based on event_type."*

**On S3 via Kafka consumer:**

Good instinct — but clarify why you're sending to S3:

- **Telemetry raw** → S3 for long-term storage, batch analytics, model training
- **Harsh events** → S3 for audit, compliance, video association

But S3 is the **cold path** — for batch analytics and storage. The **hot path** — real-time alerts within 30 seconds — shouldn't go through S3. That adds too much latency.

**Two paths from Kafka:**

```
Kafka topics
↓              ↓
Hot path       Cold path
(real-time)    (batch)
↓              ↓
Stream         Kafka consumer
processor      → S3 (via Kinesis
(Flink/        Firehose or
Spark          direct)
Streaming)     → Partitioned by
↓              date/vehicle_id
Alerts,        → Used for:
scores,        training data,
dashboard      compliance,
               historical analysis
```

---

**On S3 partitioning:**
Partition by `vehicle_id` at ingestion — that's what the device knows. Map to `driver_id` downstream in the processing layer where you have the driver-vehicle assignment data.

*"Partition by vehicle_id at ingestion since that's the device identifier. The stream processor enriches events with driver_id by joining against a driver-vehicle assignment table."*

For telemetry: 

```
s3://netradyne-telemetry/
  year=2024/
    month=05/
    day=19/
      hour=10/
        vehicle_id=V001/
          telemetry_10_00_00.parquet
```

For harsh events:

```
s3://netradyne-events/
  year=2024/
    month=05/
      day=19/
        event_type=harsh_braking/
          events_2024_05_19.parquet
```

Partition by date first — most queries filter by date range. Then by vehicle or event_type for further pruning.

---

**Corrected ingestion flow:**

```
Dashcam (edge AI)
↓
HTTPS POST to API Gateway
  {vehicle_id, event_type, payload, timestamp}
↓
Lambda:
  - Validates payload
  - Routes to correct Kafka topic
  - harsh_events → harsh_events topic
  - telemetry → telemetry_raw topic
↓
Kafka cluster:
  - telemetry_raw (partitioned by vehicle_id)
  - harsh_events (partitioned by vehicle_id)
↓
Hot path: Stream processor reads directly
Cold path: Kinesis Firehose → S3
```

---

**Spark Streaming vs Flink:**

|  | Spark Streaming | Flink |
| --- | --- | --- |
| Processing model | Micro-batch | True streaming |
| Latency | Seconds | Milliseconds |
| Exactly-once | Yes | Yes |
| State management | Good | Excellent |
| Complexity | Lower | Higher |
| Ecosystem | Spark/AWS | Standalone |
| Best for | Near real-time, batch hybrid | True real-time, low latency |

**For Netradyne's 30-second alert SLA:**

Both technically work — 30 seconds is generous enough for Spark Streaming micro-batches.

But **Flink is the better answer** because:

- True event-by-event streaming — no micro-batch delay
- Superior state management — tracking per-driver event windows natively
- Better for complex event processing — detecting patterns like "3 harsh events in 1 hour"
- Industry standard for real-time ML feature computation

**The one-liner:**

*"Flink for true real-time processing — it processes each event as it arrives rather than in micro-batches. For a 30-second alert SLA Spark Streaming would work, but Flink gives us millisecond latency headroom and better state management for per-driver event tracking."*

---

**Enrichment:**

1. **Flink with broadcast state:**

```
Driver profile table → broadcast to all Flink workers
Harsh event arrives → enrich from in-memory broadcast state
No DB query per event — everything in memory
Refresh broadcast state every 5 minutes
```

1. **Redis cache:**

```
Driver profile → cached in Redis
Harsh event arrives → Flink queries Redis (sub-millisecond)
Cache miss → fall back to RDBMS, populate cache
TTL: 1 hour — profiles don't change frequently
```

**Redis is the better answer for Netradyne:**

```
RDBMS (source of truth)
↓ sync every 5 minutes
Redis cache
↓ sub-millisecond lookup
Flink enrichment
```

---

**Corrected stream processing flow:**

```
harsh_events Kafka topic
↓
Flink application:
  1. Read event from Kafka
  2. Enrich from Redis:
     - driver_name, license, fleet_id (driver profile)
     - road_name, city (reverse geocoding from GPS)
     - events_today count (from Redis counter)
  3. Severity assessment:
     - Below threshold → log only
     - Above threshold → generate alert
  4. Publish enriched event to:
     - alert_topic → alert service
     - scoring_topic → safety score update
     - analytics_topic → dashboard update
```

---

**On location enrichment specifically:**

Reverse geocoding — converting GPS coordinates to road name/city — is an API call. You can't do this per event at scale.

**Solution — tile-based lookup:**

```
Pre-compute geographic tiles
Store in Redis: {tile_id: {city, road_name, zone}}
GPS coordinates → calculate tile_id (fast math)
Lookup tile in Redis → get location context
No external API call per event
```

---

**Alerts**: 

```json
Flink publishes enriched alert
↓
SNS topic: driver_safety_alerts
↓ (fan-out simultaneously)
├── Mobile push (SNS → FCM/APNs)
├── Email (SNS → SES)
├── SMS (SNS → SNS SMS)
└── WebSocket (SNS → Lambda → WebSocket API)
    → Dashboard real-time update
```

**SLA Breakdown**

```json
Event detected on edge: T+0
↓
Upload via HTTPS to API Gateway: T+2s
↓
Lambda publishes to Kafka: T+3s
↓
Flink reads from Kafka: T+4s
↓
Redis enrichment lookup: T+4.1s
↓
Severity assessment: T+4.2s
↓
SNS publish: T+4.3s
↓
Push notification delivered: T+5-10s
```

**Failure Mechanism**

**Failure handling:** Flink goes down for 2 minutes. What happens to events in Kafka? How do you recover?

- Flink failure and Kafka replay: Messages are retained even when consumer is down.
- Flink handles this automatically via **checkpointing**:

```
Flink checkpoints every 30 seconds:
- Current Kafka offset — where am I reading from?
- Current state — per-driver event counts, scores
- Saved to S3 or HDFS

If Flink crashes:
- Restart from last checkpoint
- Resume reading from saved Kafka offset
- State restored — no data loss
- Exactly-once processing guaranteed
```

*"Flink's checkpointing mechanism saves both the Kafka offset and processing state periodically. On restart, Flink resumes from the last checkpoint — no events are lost or double-processed. This is why Kafka retention matters — events need to still be available when Flink recovers."*

---

**On Redis snapshots**

- Redis has two persistence mechanisms:

**RDB snapshots:**

```
Redis saves full snapshot to disk every N minutes
If Redis restarts → loads from last snapshot
Risk: lose up to N minutes of score updates
```

**AOF (Append Only File):**

```
Redis logs every write operation to disk
If Redis restarts → replays all operations
Risk: slower restart, larger disk usage
More durable than RDB
```

**But for driver safety scores - better pattern:**

Don't rely on Redis as source of truth. Use Redis as cache, RDS as source of truth:

```
Flink updates score
↓
Write to Redis (fast, real-time serving)
AND
Write to RDS every 5 minutes (durable, source of truth)

If Redis restarts:
→ Warm up cache from RDS
→ No data loss
→ Back online in seconds
```

*"Redis is the serving layer for low-latency score reads. RDS is the source of truth. Flink writes to both — Redis immediately for real-time serving, RDS every 5 minutes for durability. Redis restart means brief cache miss, not data loss."*

---

**Deepdive Questions**

**You mentioned Flink reads from the harsh_events Kafka topic and enriches from Redis. Walk me through exactly what happens when a driver's profile doesn't exist in Redis — a new driver who just joined the fleet today. How does the cache miss get handled, and what's the impact on the 30-second alert SLA?**

Cache-aside pattern — on cache miss, fetch directly from RDS, populate cache, send enriched alert. Slightly higher latency on first event per driver but still well within 30-second SLA. Subsequent events hit cache normally.

```python
async def enrich_event(event: HarshEvent) -> EnrichedEvent:
    driver_profile = await redis.get(f"driver:{event.driver_id}")
    
    if not driver_profile:
        # Cache miss → fetch from RDS directly
        driver_profile = await rds.get_driver(event.driver_id)
        
        if driver_profile:
            # Populate cache for future events
            await redis.set(
                f"driver:{event.driver_id}",
                driver_profile,
                ttl=300  # 5 minutes
            )
        else:
            # Driver genuinely doesn't exist
            # Send partial alert with vehicle_id only
            return PartialAlert(
                vehicle_id=event.vehicle_id,
                driver_id=event.driver_id,
                note="Driver profile not found"
            )
    
    return EnrichedAlert(
        driver_name=driver_profile.name,
        event_type=event.event_type,
        severity=event.severity,
        location=event.location
    )
```

**What this achieves:**

```
Normal path (cache hit):
Event → Redis lookup (1ms) → Enriched alert → SNS
Total: ~1 second

Cache miss path (new driver):
Event → Redis miss → RDS lookup (10-50ms) →
Cache populated → Enriched alert → SNS
Total: ~1-2 seconds — still well within 30-second SLA
```

**The key insight:**

Cache miss goes directly to RDS — not waiting for next refresh cycle. Alert is still enriched, still within SLA. And the cache gets populated for subsequent events from the same driver.

---

**You mentioned tile-based location lookup for reverse geocoding — converting GPS coordinates to city and road name. Walk me through exactly how you build and maintain these tiles. GPS coordinates change every second per vehicle — how do you ensure the tile data stays accurate, and what's the tile granularity?**

**The standard approach — Geohash:**

```python
import geohash

def get_tile_id(lat: float, lng: float, precision: int = 7) -> str:
    # precision 7 = ~150m x 150m tile
    # precision 6 = ~1.2km x 600m tile
    # precision 5 = ~5km x 5km tile
    return geohash.encode(lat, lng, precision=precision)

# Example:
tile_id = get_tile_id(12.9716, 77.5946, precision=7)
# Returns: "tdr1wzt" — unique string for that ~150m tile
```

**How geohash works conceptually:**

```
World map divided into grid
Each cell subdivided recursively
Precision = how many times subdivided
Higher precision = smaller tile = more accurate location

lat=12.9716, lng=77.5946
→ geohash precision 7
→ tile_id: "tdr1wzt"
→ covers ~150m x 150m area around that point
```

**Redis storage:**

```python
# Pre-compute all tiles for service area
tiles = {
    "tdr1wzt": {
        "city": "Bangalore",
        "zone": "Koramangala",
        "road": "Sarjapur Road",
        "speed_limit": 60,
        "risk_score": 7  # historically risky zone
    },
    "tdr1wzm": {
        "city": "Bangalore",
        "zone": "HSR Layout",
        "road": "27th Main",
        "speed_limit": 40,
        "risk_score": 3
    }
}

# Store in Redis
for tile_id, context in tiles.items():
    redis.hset(f"tile:{tile_id}", mapping=context)
```

**At runtime:**

```python
async def get_location_context(lat: float, lng: float) -> dict:
    tile_id = geohash.encode(lat, lng, precision=7)
    context = await redis.hgetall(f"tile:{tile_id}")

    if not context:
        # Tile not in Redis — unknown area
        # Fall back to coarser precision
        tile_id = geohash.encode(lat, lng, precision=5)
        context = await redis.hgetall(f"tile:{tile_id}")

    return context or {"city": "unknown", "zone": "unknown"}
```

**The one-liner for the interview:**

*"I'd use geohash — a standard algorithm that converts lat/lng to a string tile ID at configurable precision. Precision 7 gives ~150m tiles which is granular enough for road-level context. Pre-compute all tiles for the service area, store in Redis. At runtime — one geohash calculation plus one Redis lookup, both sub-millisecond."*

---

**One more thing worth mentioning — tile boundary problem:**

```
Vehicle at lat=12.9716, lng=77.5946
→ tile_id: "tdr1wzt" → Sarjapur Road

Vehicle moves 10 meters
→ lat=12.9717, lng=77.5947
→ tile_id: "tdr1wzv" → different tile!
```

Vehicle near tile boundary → might get different road name for adjacent tiles.

**Solution:**

```python
def get_location_context_robust(lat, lng):
    # Get neighboring tiles too
    neighbors = geohash.neighbors(geohash.encode(lat, lng, 7))

    # Use most common road name across tile + neighbors
    contexts = [redis.hgetall(f"tile:{t}") for t in [tile_id] + neighbors]
    return most_common_context(contexts)
```

---

**You said Flink updates driver safety score in Redis and persists to RDS every 5 minutes. How exactly do you calculate the safety score — is it a simple count of events, or something more sophisticated? And how do you handle score recalculation when a cloud DL model later invalidates an edge-detected event as a false positive?**

**On safety score calculation** ✅

Banding approach is correct and practical:

```python
def calculate_safety_score(events: list[Event]) -> float:
    # Weight by severity and recency
    score = 100  # start perfect

    for event in events:
        # Higher severity = bigger penalty
        severity_penalty = event.severity * 2

        # Recent events weighted more
        hours_ago = (now - event.timestamp).hours
        recency_weight = 1.0 if hours_ago < 1 else 0.5

        score -= severity_penalty * recency_weight

    # Band into tiers
    if score >= 80: return "green"
    if score >= 60: return "amber"
    return "red"
```

---

**On false positive handling:**

Correct direction — update RDS, Redis refreshes. But there's a timing problem:

---

**False positive detected by cloud DL model. You update RDS. Redis refreshes in next 5-minute cycle. But the fleet manager already received an alert 3 minutes ago and potentially took action — called the driver, flagged the incident in their system. How do you handle the downstream impact of a false positive alert that's already been delivered?**

```
30-second alert SLA ←→ Cloud ML validation takes minutes
```

You can't have both simultaneously. This is a genuine architectural trade-off. Good that you spotted it.

---

**So given this tension — you can't validate before alerting within 30 seconds. How do you design the system to handle this? What's your approach?**

- Fleet manager will receive alert within 30 seconds and if they are one-off, then he waits for the confirmation on ML side may be it takes 5-10 minutes more. But if the alerts are coming like a wave then he should consider the override and call the driver.

Smart business logic — that's actually how real fleet safety systems work. ✅

Two-stage alert approach:

```
T+30 seconds: Preliminary alert
"Driver D001 — possible harsh braking detected.
Awaiting cloud validation."

T+10 minutes: Confirmation or retraction
"CONFIRMED: Harsh braking validated by ML model.
Severity 8/10. Action recommended."
OR
"RETRACTED: Previous alert was a false positive.
No action needed."
```

And your wave logic is exactly right:

- Single alert → wait for ML confirmation before acting
- Multiple alerts in short window → override, act immediately

---

**How do you implement the wave detection — what's the threshold and how does Flink track it?**

- Flink is already having a counter associated to the driver, so the counter increases; if the number of events for that driver increases to may be 5-10 within minutes then that should send a wave alert.
    
    This is only for harsh events so not all 100K events per second qualify. Let's say may be 0.1% of events are harsh, which comes down to 100 events per second which Flink can handle.
    

You're using a sliding window to detect waves — 5-10 events within minutes. What's the exact window definition? If a driver has 4 events in 10 minutes, then 1 more event 11 minutes later — does that 5th event trigger the wave alert? And when does the counter reset — does it ever expire?

**The technical implementation:**

```python
# Flink sliding window with expiry
class DriverEventState:
    def __init__(self):
        self.events = []  # list of (event, timestamp)
        self.wave_threshold = 5
        self.window_minutes = 10

    def add_event(self, event, timestamp):
        # Remove events outside window
        cutoff = timestamp - timedelta(minutes=self.window_minutes)
        self.events = [
            e for e in self.events
            if e.timestamp > cutoff
        ]

        # Add new event
        self.events.append(event)

        # Check wave threshold
        if len(self.events) >= self.wave_threshold:
            return WaveAlert(
                driver_id=event.driver_id,
                event_count=len(self.events),
                window_minutes=self.window_minutes
            )
        return None

    def is_expired(self, current_time):
        if not self.events:
            return True
        # No harsh event in last 10 mins → expire state
        latest = max(e.timestamp for e in self.events)
        return (current_time - latest).minutes > self.window_minutes
```

**Your business logic translated:**

- Window = last 10 minutes of harsh events
- Counter = events within that rolling window
- Reset = naturally when no events in 10 minutes
- Wave = 5+ events within any 10-minute window

**4 events in 10 mins + 1 event at 11 mins:**

```
T=0:  event 1 → window=[1], count=1
T=3:  event 2 → window=[1,2], count=2
T=6:  event 3 → window=[1,2,3], count=3
T=9:  event 4 → window=[1,2,3,4], count=4
T=11: event 5 → window=[2,3,4,5], count=4 (event 1 expired)
      No wave alert — still only 4 in window ✅
```

Correctly doesn't trigger — event 1 expired before event 5 arrived. ✅

---

**You've designed a system that processes real-time driver events, enriches them, scores drivers, and alerts fleet managers. This system generates enormous amounts of data — telemetry, events, scores, alerts. The data science team wants to use all of this to build better ML models. How does your real-time system feed the ML training pipeline? What's the connection between your streaming architecture and the model retraining cycle?**

```
Raw harsh event → Cloud DL validation → Fleet manager annotation → Labeled training data
```

That's **human-in-the-loop labeling** — the standard pattern for supervised ML in safety systems. ✅

Let me formalize what you said:

```
S3 raw events
↓
Cloud DL model processes → adds predicted label
  {event_id, predicted_type, confidence, severity}
↓
Fleet manager reviews in dashboard
  → Confirms: "Yes, harsh braking" → label=1
  → Rejects: "False positive, pothole" → label=0
  → Annotates: "Actually distraction, not braking" → relabel
↓
Labeled dataset stored in S3:
  {event_id, raw_features, true_label, annotator_id, timestamp}
↓
Weekly retraining pipeline:
  → Airflow DAG triggers every Sunday
  → Reads labeled data from S3
  → Trains new model version
  → Registers in MLflow
  → A/B test against current model
  → Promote if better
```

---

**The complete feedback loop:**

```
Edge AI detects event (approximate)
↓
Cloud DL validates (more accurate)
↓
Fleet manager annotates (ground truth)
↓
Labels stored in S3
↓
Weekly retraining on new labels
↓
Better edge + cloud models deployed
↓
Fewer false positives
↓
Fleet manager annotates less
↓
System gets smarter over time
```

---

**One thing to add — active learning:**

Not all events need annotation. DS team should prioritize:

```python
def needs_annotation(event: Event) -> bool:
    # High confidence → skip annotation
    if event.confidence > 0.95:
        return False

    # Low confidence → needs human review
    if event.confidence < 0.7:
        return True

    # Medium confidence → sample 10%
    return random.random() < 0.1
```

This reduces annotation burden — fleet managers only review uncertain cases, not every event. Model still improves from high-confidence automatic labels.

---
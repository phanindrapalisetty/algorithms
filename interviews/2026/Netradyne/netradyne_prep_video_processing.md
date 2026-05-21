# Prep: Video Processing Job

**Company**: Netradyne 

**Question**: 

*Netradyne has 100,000 dashcams on fleet vehicles. Each camera captures video continuously. When an event is detected on the edge — harsh braking, distraction, speeding — a 30-second video clip is uploaded to the cloud. Deep learning models then process each clip to validate the event and extract insights. There are 500+ video processing jobs per day. Each job must complete within 2 hours — that's the SLA. Design this system.*

**Assumptions**: 

- Say out of 100000 dashcams only 500 video processing jobs happen: meaning only when a harsh event occurs the clip is generated and uploaded.
- A single vehicle might generate 0-5 events per day depending on driver behavior.
- Each job runs one deep learning model to validate the event and classify severity.
- What does "process" mean exactly?
    - Each job runs 2-3 DL models sequentially — event validation → severity scoring → context extraction
- What's the output of each job?
    - Output is a structured JSON result stored in S3 and metadata in RDS

**Framework**: 

1. Video ingestion: how clips get from camera to cloud
2. Job queuing: how jobs are managed and prioritized
3. Job processing: how DL models run on video
4. Output storage: where results go
5. SLA monitoring: how you ensure 2-hour completion
6. Failure handling: what happens when jobs fail

Why is a 30 second clip taking 2 hours to process?

- **It's not just one clip in isolation**: 500+ jobs arrive throughout the day. The system processes them in a queue — your job might wait behind 200 others before compute becomes available. The 2-hour SLA is end-to-end wall clock time including queue wait time, not just processing time.
- **DL model inference is compute-intensive**: Running 2-3 deep learning models on video requires GPU compute:
    - Frame extraction — decode video into individual frames
    - Model 1: Event validation — did harsh braking actually happen?
    - Model 2: Severity scoring — how severe was it?
    - Model 3: Context extraction — what was happening around the event?
- **Spot instance provisioning time:** If using spot instances for cost savings, spinning up a new GPU instance takes 3-5 minutes. If the fleet is fully utilized, you wait for capacity.
- **Data transfer time:** 30-second video clip from a truck in a remote location — upload speed depends on cellular connectivity. Could take minutes just to upload.

So the 2-hour SLA breaks down roughly as:

```json
Upload time: 2-5 mins (connectivity dependent)
Queue wait time: 0-90 mins (depends on load)
Instance provisioning: 3-5 mins (spot instance)
Actual processing: 5-15 mins (3 DL models on GPU)
Output storage: 1-2 mins
Total: up to 2 hours end-to-end
```

HLD of the job: 

```json
INGESTION:
Dashcam (edge AI detects event)
→ Buffer clip locally
→ Request presigned S3 URL
→ Upload to S3 (exponential backoff retry)
→ S3 → EventBridge → Priority SQS
  (critical/standard/batch)

PROCESSING:
Lambda (lightweight trigger)
→ Validates S3 URI
→ Submits to EKS

EKS (GPU, warm pool 5 pods, KEDA autoscaling)
→ Download clip from S3
→ Extract frames
→ Model 1: Event validation
→ Model 2: Severity scoring  
→ Model 3: Context extraction
→ Store results

OUTPUT:
→ RDS: job metadata, SLA tracking
→ DynamoDB: real-time event results
→ S3: raw outputs, 90-day retention
→ Warehouse: aggregated analytics

MONITORING:
CloudWatch:
→ Queue depth alert (>200)
→ Job age alert (>90 mins)
→ Processing time alert (P95 >30 mins)
→ DLQ alert (any messages)
→ PagerDuty on-call notification

FAILURE HANDLING:
→ 3 retries → DLQ
→ On-call alerted with error context
→ Runbook for each error type
→ DLQ replayable after fix
```

---

**Typical 60-minute system design structure:**

```
0-5 mins   → Introductions, context setting
5-10 mins  → Clarifying questions (you ask)
10-25 mins → High level architecture (you design)
25-45 mins → Deep dives (interviewer probes)
45-55 mins → Scaling, failure handling, monitoring
55-60 mins → Your questions to interviewer
```

---

**They'd probe ingestion deeply:**

- "You said presigned URLs — what if 10,000 vehicles try to upload simultaneously?"
- "How do you handle partial uploads — network drops mid-clip?"
- "What's your retry strategy if S3 upload fails?"
- "How do you prevent duplicate uploads of the same clip?"

**Then probe job processing:**

- "How does KEDA scale exactly — what metric does it use?"
- "What happens if a GPU instance gets terminated mid-job by AWS?"
- "How do you handle a corrupt video file that crashes the DL model?"
- "Walk me through exactly what happens when a job exceeds 2-hour SLA"

**Then probe monitoring:**

- "Show me exactly which CloudWatch alarms you'd set up"
- "How do you distinguish between a slow job and a failed job?"
- "If queue depth spikes at 2am, who gets paged and what do they do?"

---

**Infrastructure depth:**

- "How exactly does EKS autoscaling work with KEDA?"
- "What's the difference between HPA and KEDA?"
- "How do you size GPU instances for your DL models?"
- "What happens when a spot instance gets terminated?"

**AWS specifics:**

- "How do you configure S3 EventBridge notifications?"
- "What's the difference between SQS standard and FIFO?"
- "How do you configure Kafka partitions for 100K devices?"

**High probability probes:**

- Spot instance handling — what if instance terminated mid-job?
- Model versioning — how do you deploy new model without downtime?
- Cold start mitigation — how exactly does warm pool work?
- SLA breach — what's the exact recovery procedure?

**Medium probability probes:**

- Kafka partition count — how do you decide number of partitions?
- Redis eviction policy — what happens when Redis runs out of memory?
- Flink checkpointing — how often and what's the trade-off?

**Lower probability but possible:**

- Kubernetes pod resource limits — CPU/memory/GPU allocation
- Docker image optimization — reducing cold start time
- Network bandwidth from 100K devices

---

**Pre-validation catches obviously corrupt files — wrong format, missing metadata. But what about files that pass validation but fail mid-processing? For example — video opens fine, first 100 frames process successfully, then frame 247 is corrupted and crashes the DL model. Your retry logic kicks in, re-downloads the same file, fails at frame 247 again, three times, then goes to DLQ. How do you prevent wasting GPU compute on two more retries of a file you already know will fail at frame 247?**

**Checkpointing within the job:**

```python
# Track progress within each job
class VideoProcessor:
    def process(self, job_id: str, s3_uri: str):
        checkpoint = self._get_checkpoint(job_id)
        start_frame = checkpoint.last_successful_frame or 0

        for frame_num in range(start_frame, total_frames):
            try:
                self._process_frame(frame_num)
                self._save_checkpoint(job_id, frame_num)
            except CorruptFrameError:
                self._mark_frame_corrupt(job_id, frame_num)
                continue  # skip corrupt frame, don't fail job
            except FatalError:
                raise  # genuine failure, retry makes sense
```

Two strategies:

**1. Skip corrupt frames:**

- If frame 247 is corrupt → log it, skip it, continue processing
- Job completes with note: "247 frames processed, 1 skipped"
- Only fail job if corruption exceeds threshold — say 10% of frames

**2. Job-level checkpointing:**

- Save progress every N frames to S3/Redis
- On retry → resume from last checkpoint, not from beginning
- Don't reprocess frames 1-246 that already succeeded

**Distinguishing retriable vs non-retriable errors:**

```python
 RETRIABLE_ERRORS = [
    NetworkTimeoutError,    # transient, retry makes sense
    GPUMemoryError,         # might succeed on different instance
    ModelLoadError,         # cold start issue, retry helps
]

NON_RETRIABLE_ERRORS = [
    CorruptVideoError,      # retrying won't fix corruption
    InvalidFormatError,     # pre-validation should catch this
    MissingS3FileError,     # file doesn't exist, retry won't help
]

def should_retry(error):
    return type(error) in RETRIABLE_ERRORS
```

Non-retriable errors → skip directly to DLQ, don't waste retries.

*"I'd distinguish retriable from non-retriable errors. Network timeouts and GPU memory errors are retriable — a different instance might succeed. Corrupt video frames are non-retriable — retrying won't fix the corruption. For corrupt frames I'd skip them and complete the job partially rather than failing entirely. For genuine failures I'd checkpoint progress so retries resume from where they left off."*

---

**You mentioned KEDA autoscaling based on SQS queue depth. A burst of 200 jobs arrives simultaneously at 9am — Monday morning, all fleet vehicles starting their routes. How long does it take for your system to scale from 5 warm pods to handle 200 concurrent jobs? And what happens to SLA for jobs that are waiting while new pods spin up?**

**Two mechanisms:**

**1. Kubernetes Scheduled Scaling (CronJob-based):**

```yaml
# Scale up before 9am burst
apiVersion: batch/v1
kind: CronJob
metadata:
  name: morning-scale-up
spec:
  schedule: "0 8 * * 1-5"  # 8am weekdays
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scaler
            command:
            - kubectl scale deployment video-processor
              --replicas=20
---
# Scale back down after burst
schedule: "0 11 * * 1-5"  # 11am weekdays
--replicas=5
```

Pre-warm 20 pods at 8am before burst arrives. Scale back at 11am when burst subsides.

**2. AWS Application Auto Scaling with scheduled actions:**

```python
# AWS scheduled scaling
client.put_scheduled_action(
    ServiceNamespace='ecs',
    ScheduledActionName='morning-scale-up',
    Schedule='cron(0 8 ? * MON-FRI *)',  # 8am weekdays
    ScalableTargetAction={
        'MinCapacity': 20,
        'MaxCapacity': 50
    }
)
```

**Combined approach — predictive + reactive:**

```
8:00am → Scheduled scale: 5 → 20 pods (predictive)
9:00am → Burst arrives, queue fills
         KEDA reactive: 20 → 50 pods if needed
11:00am → Burst subsides
          KEDA scales back: 50 → 20 pods
11:30am → Scheduled scale: 20 → 5 pods (predictive)
```

Predictive handles known patterns. Reactive handles unexpected spikes.

*"Predictive scaling uses Kubernetes CronJobs or AWS scheduled actions to pre-warm pods before known busy periods. KEDA reactive scaling handles unexpected spikes on top of that. Combined, you get cost efficiency during quiet periods and capacity during bursts."*

---

**On SLA impact during scale-up:**

Even with predictive scaling, if burst exceeds pre-warmed capacity:

- New pods take 2-3 minutes to start — image pre-pulled so faster
- Jobs arriving during scale-up wait in SQS
- Job age CloudWatch alarm fires at 90 minutes — 30 minute buffer before SLA breach
- On-call can manually scale if alarm fires

*"The 90-minute job age alarm gives us 30 minutes of buffer before the 2-hour SLA breaches. If predictive scaling undershoots, the alarm fires early enough for manual intervention."*

---

**You said EKS pods download video from S3 for processing. A 30-second clip at 1080p is roughly 150-200MB. With 20 concurrent pods each downloading simultaneously — that's 3-4GB of S3 data transfer happening at once. How does this affect processing time and cost?**

**Sequential processing with async download pipeline:**

This is actually the better approach — not truly concurrent jobs per pod:

```python
import asyncio

class VideoProcessorPod:
    def __init__(self):
        # Models loaded once, stay in GPU memory
        self.models = load_models()  # 8GB GPU memory
        self.download_queue = asyncio.Queue()

    async def run(self):
        # Two concurrent coroutines:
        # 1. Downloader — always fetching next job
        # 2. Processor — always processing current job
        await asyncio.gather(
            self.download_worker(),
            self.process_worker()
        )

    async def download_worker(self):
        while True:
            job = await get_next_job_from_sqs()
            video = await download_from_s3(job.s3_uri)
            await self.download_queue.put((job, video))

    async def process_worker(self):
        while True:
            job, video = await self.download_queue.get()
            # GPU processes one job at a time
            # No memory contention
            result = self.models.predict(video)
            await store_results(result)
```

**What this achieves:**

```
Timeline without pipelining:
Job 1: [download 30s][process 15s]
Job 2:                            [download 30s][process 15s]
Total: 90 seconds for 2 jobs

Timeline with async pipelining:
Job 1: [download 30s][process 15s]
Job 2:         [download 30s]     [process 15s]
Total: 60 seconds for 2 jobs — 33% faster
```

GPU processes one job at a time — no memory contention. Downloader pre-fetches next job while GPU is busy. GPU never sits idle waiting for download.

---

**The one-liner:**

*"I'd use async pipelining within each pod — a download coroutine pre-fetches the next job while the GPU processes the current one. GPU processes one job at a time so no memory contention, but it's never idle waiting for downloads. This gives roughly 30% throughput improvement without the complexity of concurrent GPU execution."*

---

**You mentioned 3 DL models run sequentially per job — event validation, severity scoring, context extraction. Each model takes 5 minutes. Total processing time is 15 minutes. Your SLA is 2 hours. What if you need to add a 4th model — say driver face verification for compliance? Total processing becomes 20 minutes. How does your architecture accommodate adding new models without redesigning the pipeline?**

**Model pipeline as configurable stages:**

Instead of hardcoding 3 models sequentially in one pod, make the pipeline configurable:

```python
# Config-driven pipeline
pipeline_config = {
    "stages": [
        {"model": "event_validation", "timeout": 300},
        {"model": "severity_scoring", "timeout": 300},
        {"model": "context_extraction", "timeout": 300},
        # Adding new model = just add here
        {"model": "face_verification", "timeout": 300}
    ]
}

class VideoProcessorPod:
    def process(self, video, config):
        results = {}
        for stage in config['stages']:
            model = self.models[stage['model']]
            results[stage['model']] = model.predict(video)
        return results
```

**But the real architectural solution — parallel model execution:**

Not all models need the same input or depend on each other:

```
Current (sequential):
Video → Model 1 → Model 2 → Model 3 → Results
Time: 5 + 5 + 5 = 15 minutes

Parallel where possible:
Video → Model 1 (event validation)
             ↓ (only if validated)
        Model 2 (severity) ──┐
        Model 3 (context) ──┤→ Merge results
        Model 4 (face)    ──┘
Time: 5 + 5 = 10 minutes (Models 2,3,4 run in parallel)
```

Models 2, 3, 4 don't depend on each other — only on Model 1's output. Run them in parallel on separate GPU threads or separate pods.

```python
async def process_parallel(video, validated=True):
    if not validated:
        return {"status": "invalid"}

    # Run models 2,3,4 concurrently
    results = await asyncio.gather(
        severity_model.predict(video),
        context_model.predict(video),
        face_model.predict(video)
    )
    return merge_results(results)
```

**Adding a 5th model:**

- If independent → add to parallel group, no extra time
- If dependent → add to sequential chain, adds time

**The one-liner:**

*"Make the pipeline config-driven so new models are added via configuration, not code changes. More importantly, identify which models are independent and run them in parallel — only sequential dependencies add latency. Adding a 4th independent model costs compute but not time."*

---
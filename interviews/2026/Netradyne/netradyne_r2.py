"""
Pick one project you owned end-to-end. Give me problem → architecture → your role → impact.

Document Digitisation: 

Initial Start: MB bill: 





System Design
Design a system to detect and alert on anomalies in driver behaviour (like harsh braking, overspeeding) from streaming vehicle data.


Focus Area

1. Data ingestion	
2. Streaming pipelines	
3. Batch processing	
4. Storage (RDBMS/NoSQL)	
5. ML basics	
6. GenAI awareness	
7. Scalability	
8. Reliability


10 vehicles: it is already detecting: Analytics(history) over it and driver beahviour(near-real time) over it: depending on criticality (top 3)

AWS Infra 

Ingestion: 
On-device -> events per second (it will detect if it's harsh, criticality) (API Gateway + ELB + Lambda) -> Kafka clusters -> different S3 buckets -> partition in the S3
Telemetry: Cold 
Harsh: Hot Kafka + Bucket

Kafka partitioning: 
For cold: may be basee on vehicle id
For Hot: may be on severity

Flink Processing: (Harsh)

1. Read from Kafka 
2. May be enrich the data (high, medium, low) -> 
3. Store it from here -> DynamoDB: driverID / RDS (persistence)
4. SNS topic: different SQS queues (mail, message)
5. SQS: Lambda Consumer just to send the message to the manager if high
6. What if driver says 'No': Fleet manager verifies it: have a key in DynamoDB for that event, what is my fleet manager judgement


Kafka: checkpoints
1. Metrics: Quick I'm, Accurate, 
2. Triggered vs Accurate: x% 
3. CloudWatch: 
4. Base data on which LLM acts/narrates

async 
caching: redis/enrich-flink broadcasting tables/
rds-redis; redis-rds
flink job: have the counter in flink job/redis
Improve ML model



3 step process: 
1. On-cevice
2. Cloud processing
3. Fleet manager is validing
"""
"""
Write a production-grade Python function that reads a list of dbt model run results and identifies models that exceeded their SLA. 
Each model has: model_name, run_duration_seconds, status, sla_seconds. 
Return a list of SLA breaches with model name, actual duration, and how many seconds over SLA.
"""
from pydantic import BaseModel
from typing import Optional, List 

class DBTModel(BaseModel): 
    model_name: str
    run_duration_seconds: int 
    status: str 
    sla_seconds: int 

class SLABreach(BaseModel): 
    model_name: str
    actual_duration_seconds: int 
    over_sla_seconds: int 


def _calculate_over_sla_breach(model: DBTModel) -> SLABreach: 
    return SLABreach(
        model_name = model.model_name,
        actual_duration_seconds = model.run_duration_seconds,
        over_sla_seconds = model.run_duration_seconds - model.sla_seconds
    )

def _is_sla_breach(model: DBTModel) -> bool: 
    return model.run_duration_seconds > model.sla_seconds 

def _sla_breached_models(models: List[DBTModel]) -> List[SLABreach]: 
    if models:
        return [
        _calculate_over_sla_breach(i) for i in models if _is_sla_breach(i)
    ]
    else: 
        return []


"""
Write a production-grade Python function that takes a list of pipeline run records and returns a summary — total runs, successful runs, failed runs, and success rate. 
A run has: run_id, status (success/failed/running), duration_seconds.
"""
from pydantic import BaseModel
from typing import Optional, List 

class Records(BaseModel):
    run_id: str
    status: str 
    duration_seconds: int 

class RecordsPipelineSummary(BaseModel): 
    total_runs: int 
    successful_runs: int 
    failed_runs: int 
    success_rate: float 

def count_by_status(models: List[Records], status_check) -> int: 
    _count = 0 
    for i in models: 
        if i.status == status_check: 
            _count += 1 
    return _count 

def count_total_runs(models: List[Records], status_check) -> int: 
    return len(models) 

def calculate_success_rate(success_runs: int, total_runs: int) -> float: 
    return round(success_runs/total_runs, 2) 

def get_pipeline_summary(models: List[Records]) -> Optional[RecordsPipelineSummary]: 
    if not models: 
        return None 
    
    else: 
        total_runs=count_total_runs(models), 
        successful_runs=count_by_status(models, status_check='success'),
        failed_runs=count_by_status(models, status_check='fail'),
        
        RecordsPipelineSummary(
            total_runs=total_runs, 
            successful_runs=successful_runs,
            failed_runs=failed_runs,
            success_rate=calculate_success_rate(success_runs=successful_runs, total_runs=total_runs)

        )


"""
Write a Python function that reads a list of transaction records, 
filters for completed transactions, calculates total revenue per user, and flags users above a threshold. 
Make it testable and production-grade."
"""

from pydantic import BaseModel 
from typing import List, Optional 

class TransactionRecord(BaseModel): 
    user_id: str
    record_id: str
    status: str
    amount: int 

class ThresholdConfig(BaseModel): 
    threshold: int 

def is_completed(record: TransactionRecord) -> bool: 
    return record.status == 'completed'

def get_revenue_per_user(records: List[TransactionRecord]) -> dict[str, int]: 
    revenue = {}
    for t in records: 
        if is_completed(t): 
            revenue[t.user_id] = revenue.get(t.user_id, 0) + t.amount
    return revenue

def flag_threshold(revenue: dict[str, int], config: ThresholdConfig) -> dict[str, dict]: 
    return {
        user_id: {
            "total_amount": total, 
            "is_high_amount": total>=config.threshold
        }
        for user_id, total in revenue.items()
    }

def process_transactions(records: List[TransactionRecord], config: Optional[ThresholdConfig]) -> dict[str, dict]:
    if not records:
        return {}
    if config is None: 
        config = ThresholdConfig() 
    revenue = get_revenue_per_user(records)
    return flag_threshold(revenue, config)


"""
Study the structure, not the code.
In the interview you won't write all of this — but the thinking should be visible:

Break into small functions immediately
Use Pydantic for any config or input validation
Handle edge cases before the interviewer asks
Write at least 2-3 tests showing you think about correctness

The Framework: SPEC
S — Structure
Break the problem into small single-responsibility functions. Each function does ONE thing. If you can't describe a function in one sentence, split it.
P — Pydantic for inputs
Any config, input schema, or external data → Pydantic model. Validates types, gives clear errors, self-documents.
E — Edge cases first
Before writing logic, ask:

What if input is empty?
What if a value is None/NULL?
What if the config is missing?
Handle these explicitly, not as afterthoughts.

C — Cover with tests
Write at least one test per function. Happy path + one edge case minimum.

Key things to internalize:

- Pydantic for both input (PipelineRun) and output (PipelineSummary) — not just input
- Small functions — count_by_status and calculate_success_rate are independently testable
- Edge cases — empty list, division by zero, all running
- Dot notation for Pydantic — r.status not r['status']
- List[Model] not List(Model)
- Consistent return type — always list, never None
- Small functions — is_sla_breached and calculate_breach separately testable
- Missing return statement is a common bug under pressure
"""
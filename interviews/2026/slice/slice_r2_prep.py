"""
₹20 lakh discrepancy — possible causes:

1. Data freshness issue
   → Source updated after ETL ran for April
   → Late arriving disbursements not captured
   → Check: max(updated_at) in source vs ETL run time

2. Deduplication difference
   → Excel deduplicating on different key than mart
   → Check: COUNT vs COUNT(DISTINCT disbursement_id)
   → Are there duplicate disbursement_ids in source?

3. Filter difference
   → Status filter behaving differently
   → Source has status = 'disbursed' AND 'completed'?
   → Mart only capturing 'disbursed'?

4. Grain difference
   → Excel summing at transaction level
   → Mart summing at disbursement level
   → One disbursement = multiple transactions?

5. Timezone issue
   → April 30th 11pm IST = May 1st UTC
   → Some records falling in wrong month

6. Currency/amount issue
   → Some amounts in paise, some in rupees?
   → Conversion happening inconsistently
"""

"""
Slice wants to build a data warehouse to support three business needs:
1. Finance — monthly P&L reporting: revenue from interest, fees, and UPI transactions
2. Risk — real-time delinquency monitoring: which users are at risk of defaulting
3. Product — cohort retention analysis: how users engage over time after onboarding
Source systems available:

loans — loan_id, user_id, amount, interest_rate, tenure, disbursed_at, status
repayments — repayment_id, loan_id, user_id, amount_due, amount_paid, due_date, paid_date, status
transactions — txn_id, user_id, amount, txn_type, payment_mode, created_at, status
users — user_id, name, city, credit_tier, kyc_status, signup_date*

Design the dimensional model.

Perfect — metrics before tables, refresh frequency before design. That's exactly the right instinct. ✅

The manager answers:

**Finance — monthly P&L:**
- Revenue from interest — monthly, accurate by month close
- Revenue from fees — processing fees, late fees, monthly
- UPI transaction revenue — per transaction fee, monthly
- Refresh: daily during month, final close on 1st of next month

**Risk — delinquency monitoring:**
- Users overdue by 1-30 days (DPD 30)
- Users overdue by 31-90 days (DPD 90)
- Users overdue by 90+ days (DPD 90+)
- Total outstanding at risk amount
- Refresh: real-time or near real-time — risk team needs current state

**Product — cohort retention:**
- Monthly cohort — users who signed up in same month
- Retention at Month 1, Month 2, Month 3, Month 6, Month 12
- Activity definition — at least one transaction in that month
- Refresh: daily is fine

Finance → Batch → Redshift DW → Monthly aggregation
Risk → Real-time + Batch → 
       Real-time: streaming pipeline + alerts
       Batch: Redshift for historical delinquency trends
Product → Batch → Redshift DW → Monthly cohort snapshots

You have the scenario:

Finance — monthly P&L: interest revenue, fees, UPI transaction revenue
Risk — delinquency monitoring: DPD 30, DPD 60, DPD 90
Product — cohort retention: signup → KYC → first loan → first repayment → repeat transaction

Source tables: loans, repayments, transactions, users

fct_transactions (revenue only)
--------------------------------
txn_sk (PK)
txn_id (NK)
user_sk (FK → dim_user)
date_sk (FK → dim_date)
txn_type
payment_mode
amount
revenue_category  -- interest/fee/upi
status

fct_loan_status (daily snapshot)
---------------------------------
loan_status_sk (PK)
loan_sk (FK → dim_loan)
user_sk (FK → dim_user)
date_sk (FK → dim_date)
outstanding_balance
amount_overdue
dpd  -- days past due
daily_interest_accrual
status  -- current/overdue/closed

fct_repayments (repayment events)
----------------------------------
repayment_sk (PK)
repayment_id (NK)
loan_sk (FK → dim_loan)
user_sk (FK → dim_user)
date_sk (FK → dim_date)
amount_due
amount_paid
days_overdue
is_on_time

fct_user_events (product funnel)
---------------------------------
event_sk (PK)
user_sk (FK → dim_user)
date_sk (FK → dim_date)
event_type
cohort_month
is_first_occurrence


fct_transactions
→ user_sk (dim_user)
→ loan_sk (dim_loan)
→ product_sk (dim_product)
→ date_sk (dim_date)
Measures: amount, revenue_category, payment_mode, status

fct_loan_status
→ user_sk (dim_user)
→ loan_sk (dim_loan)
→ date_sk (dim_date)
Measures: outstanding_balance, amount_overdue, 
          dpd, daily_interest_accrual, status

fct_repayments
→ user_sk (dim_user)
→ loan_sk (dim_loan)
→ date_sk (dim_date)
Measures: amount_due, amount_paid, 
          days_overdue, is_on_time

fct_user_events
→ user_sk (dim_user)
→ date_sk (dim_date)
→ cohort_date_sk (dim_date)
Measures: event_type, is_first_occurrence




-- DPD for a loan as of today
SELECT 
    loan_id,
    DATEDIFF('day', MIN(due_date), CURRENT_DATE) as dpd
FROM fct_repayments
WHERE status != 'completed'  -- only unpaid EMIs
AND due_date < CURRENT_DATE  -- only past due dates
GROUP BY loan_id



-- January 2024 cohort size
WITH jan_cohort AS (
    SELECT DISTINCT user_sk
    FROM fct_user_events e
    JOIN dim_date d ON e.cohort_date_sk = d.date_sk
    WHERE d.year_month = '2024-01'
    AND e.event_type = 'signup'
),

-- Users active in Month 3 (April 2024)
month_3_active AS (
    SELECT DISTINCT e.user_sk
    FROM fct_user_events e
    JOIN dim_date d ON e.date_sk = d.date_sk
    WHERE d.year_month = '2024-04'  -- Month 3 = April
    AND e.event_type = 'transaction'  -- active = made a transaction
)

-- Month 3 retention rate
SELECT 
    COUNT(m.user_sk) as retained_users,
    COUNT(j.user_sk) as cohort_size,
    ROUND(COUNT(m.user_sk) / COUNT(j.user_sk) * 100, 2) as retention_rate
FROM jan_cohort j
LEFT JOIN month_3_active m ON j.user_sk = m.user_sk



-- Step 1: Find changed records
WITH source AS (
    SELECT * FROM raw.users
),

current_dim AS (
    SELECT * FROM dim_user
    WHERE is_current = TRUE
),

changed AS (
    SELECT s.*
    FROM source s
    LEFT JOIN current_dim c 
        ON s.user_id = c.user_id
    WHERE c.user_id IS NULL  -- new user
    OR s.credit_tier != c.credit_tier  -- tier changed
    OR s.city != c.city  -- city changed
    OR s.kyc_status != c.kyc_status  -- kyc changed
),

-- Step 2: Expire old records
expired AS (
    UPDATE dim_user
    SET 
        end_date = CURRENT_DATE - 1,
        is_current = FALSE
    WHERE user_id IN (SELECT user_id FROM changed)
    AND is_current = TRUE
),

-- Step 3: Insert new records
INSERT INTO dim_user (
    driver_sk,
    user_id,
    name,
    city,
    credit_tier,
    kyc_status,
    signup_date,
    start_date,
    end_date,
    is_current
)
SELECT
    {{ dbt_utils.generate_surrogate_key(
        ['user_id', 'current_date']
    ) }} as user_sk,
    user_id,
    name,
    city,
    credit_tier,
    kyc_status,
    signup_date,
    CURRENT_DATE as start_date,
    '9999-12-31' as end_date,
    TRUE as is_current
FROM changed

"""
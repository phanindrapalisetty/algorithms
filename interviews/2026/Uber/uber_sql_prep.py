"""
Round 1 is BPS: Business 
"""

"""
SQL Questions
"""

"""
Problem 1 

You have a table trips with the following schema:
trips
-------
trip_id        INT
driver_id      INT
rider_id       INT
city           STRING
fare_amount    DECIMAL
trip_date      DATE
status         STRING  -- 'completed', 'cancelled'
Question:For each driver, find their 3-day moving average fare (only completed trips) ordered by date. 
Return driver_id, trip_date, daily_total_fare, and moving_avg_fare rounded to 2 decimal places.

Solution: 

with _daily as (
SELECT SUM(fare) as daily_total_fare, driver_id, trip_date FROM trips where status='complete'
) 

SELECT driver_id, trip_date, daily_total_fare, 
avg(daily_total_fare) over (partition by driver_id, trip_date order by trip_id rows between 2 preceeding and current row) as  moving_avg_fare
FROM _daily
"""


"""
Problem 2: 

Same trips table 

Question:
For each driver, find the first trip date and the revenue 
in their first 30 days of driving (from their first trip, not signup date). 
Only include drivers who have completed at least 5 trips in their first 30 days. 
Return driver_id, first_trip_date, trips_in_first_30_days, revenue_in_first_30_days.

Solution: 

with _first_trip as ( SELECT min(trip_date) as first_trip_date, driver_id FROM trips  GROUP BY driver_id ),
_first_30_days_trips as ( SELECT a.driver_id, a.trip_date, a.fare, a.trip_id, b.first_trip_date, a.status
FROM trips a  INNER JOIN _first_trip b  ON a.driver_id = b.driver_id AND a.trip_date BETWEEN b.first_trip_date AND DATEADD(DAY, 30, b.first_trip_date) )
SELECT driver_id, first_trip_date, sum(fare) as revenue_in_first_30_days, 
COUNT(trip_id) as trips_in_first_30_days
FROM _first_30_days_trips WHERE status = 'Complete' GROUP BY driver_id, first_trip_date HAVING COUNT(trip_id) >= 5
"""


"""
Problem 3 — window functions, trickier
trips
-------
trip_id        INT
driver_id      INT
fare_amount    DECIMAL
trip_date      DATE
status         STRING
Question:
Find all drivers who had a drop in daily earnings of more than 20% compared to the previous day they drove. 
Return driver_id, trip_date, daily_fare, prev_day_fare, and pct_drop. Only return rows where the drop occurred. 
Order by driver_id, trip_date.

Solution: 
with _cte as ( SELECT driver_id, trip_date, SUM(fare_amount) as daily_fare FROM trips GROUP BY driver_id, trip_date),
_prev_day as ( SELECT driver_id, trip_date, daily_fare, LAG(daily_fare) OVER (PARTITION BY driver_id ORDER BY trip_date) as prev_day_fare,  div0(prev_day_fare - daily_fare, prev_day_fare) as pct_change FROM _cte  )
SELECT * FROM _prev_day WHERE pct_change >= 0.2
"""


"""
SQL Problem 1
rides
-------
ride_id        INT
user_id        INT
driver_id      INT
city           STRING
ride_date      DATE
fare_amount    DECIMAL
ride_type      STRING  -- 'pool', 'premier', 'auto'
status         STRING  -- 'completed', 'cancelled'

Question:
For each city, find the cancellation rate per ride type for the month of January 2025. 
Cancellation rate = cancelled rides / total rides. Round to 2 decimal places. 
Only include city + ride_type combinations with more than 50 total rides. 
Order by city, cancellation rate descending.

Solution: 
with _calcualtions as ( 
SELECT city, ride_type,  COUNT(ride_id) as total_rides,  SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END ) as cancelled_rides 
FROM rides  
WHERE ride_date >= '2025-01-01' AND ride_date <= '2025-01-31'  
GROUP BY city, ride_type
), 
_filtering as ( 
SELECT *, round(cancelled_rides/total_rides, 2) as cancellation_rate 
FROM _calcualtions 
WHERE total_rides > 50 
) 

SELECT * FROM _filtering order by city asc, cancellation_rate desc
"""


"""
users
-------
user_id        INT
signup_date    DATE
city           STRING

rides
-------
ride_id        INT
user_id        INT
ride_date      DATE
fare_amount    DECIMAL
status         STRING  -- 'completed', 'cancelled'

Question:
Find all users who are retained in month 2 — 
meaning they signed up in January 2025 and took at least one completed ride in February 2025. 
Return user_id, signup_date, feb_rides, feb_total_fare. 
Order by feb_total_fare descending.

Solution: 
with _joining as ( 
SELECT a.user_id, b.signup_date, a.ride_id, a.fare_amount
FROM rides a 
LEFT JOIN users b 
ON a.user_id = b.user_id 
WHERE a.ride_date >= '2025-02-01' and a.ride_date <= '2025-02-28' 
AND b.signup_date >= '2025-01-01' and b.signup_date <= '2025-01-31' 
AND a.status = 'completed'
), 
_agg as (
SELECT user_id, signup_date, COUNT(ride_id) as feb_rides, 
SUM(fare_amount) as feb_total_fare
FROM _joining 
GROUP BY user_id, signup_date
) 

SELECT * FROM _agg ORDER BY feb_total_fare DESC
"""

"""
SQL Problem 3 — hardest of the three
trips
-------
trip_id        INT
driver_id      INT
rider_id       INT
trip_date      DATE
fare_amount    DECIMAL
status         STRING  -- 'completed', 'cancelled'
Question:
For each driver, find their longest streak of consecutive days with at least one completed trip. 
Return driver_id and longest_streak. 
Order by longest_streak descending.

with _filtering as (
SELECT DISTINCT trip_date, driver_id FROM tips WHERE status = 'completed' ), 

_streak_grouping as (
SELECT driver_id, trip_date, 
trip_date - INTERVAL '1 day' * ROW_NUMBER() OVER(PARTITION BY driver_id ORDER BY trip_date) as streak_group 
FROM _filtering
), 

_streak_formualtion as (
SELECT driver_id, streak_group, COUNT(1) as streak_count
FROM _streak_grouping GROUP BY driver_id, streak_group
) 

SELECT driver_id, max(streak_count) as longest_streak
FROM _streak_formualtion
ORDER BY longest_streak
"""
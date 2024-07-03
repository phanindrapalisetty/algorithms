"""

uber


Rides
ride_id 
user_id 
driver_id 
start_time
status 
updated_at 
city_id 
from_loc_lat_long
to_loc_lat_long
is_active
ride_type 


User 
user_id 
user_name 
user_mobile
user_email 
is_active 
created_at 
updated_at 


Driver 
driver_id 
driver_name 
driver_mobile
driver_email 
is_active 
created_at 
updated_at 
personal_meta {bloodgroup}
vehicle_type


payments 
payment_id 
ride_id 
payment_type
amount 
created_at 
is_successful



location 
city_id 
city
state
country 
created_at
updated_at

Rides
ride_id 
user_id 
driver_id 
start_time
status 
updated_at 
city_id 
from_loc_lat_long
to_loc_lat_long
is_active
ride_type 


SORTKEY 
DISTKEY -- 



-- Amount wrt to country 

WITH _cte AS (
SELECT a.payment_id, a.ride_id, a.amount, b.city_id, c.country, b.date_
FROM 
(
    SELECT payment_id, ride_id, amount from payments
    WHERE is_successful = 1
) a
LEFT JOIN (
    SELECT ride_id, city_id, date(start_time) as date_ FROM Rides
) b 
ON a.ride_id = b.ride_id 
LEFT JOIN 
(
    SELECT city_id, country FROM location
) c 
ON b.city_id = c.city_id
) 

SELECT SUM(amount), COUNT(ride_id), date_, country 
FROM _cte 
GROUP BY date_, country 





every date, driver_id -> no of trips, kms_driven, time_driven 


today = datetiem

SELECT * FROM Rides WHERE updated_at <= {today}

kms_driven, time_driven 

select date, driver_id, SUM(kms_driven), SUM(time_driven), (MAX(end_time) - MIN(start_time))
FROM Rides


idle time 

date   trip_id          start_time      end_time        ride_time       idel_time             
29-Jun      1               9AM             10:30AM     90                 0
29-Jun      2               11AM             12PM       60                  30
29-Jun      3               3PM             3:30PM         30 min           180
                                                                             210
                                                                    

SELECT *, start_time - lag(end_time) OVER(PARTITION BY driver_id ORDER BY start_time ASC) as prev_end_time
FROM Rides


"""
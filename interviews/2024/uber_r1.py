# Question

# We have logs about a restaurant's properties changes. Each entry in the logs is made when one of the property has changed.
# Data Science team is only interested in tracking onboarding_status, is_visible and type changes
# Build a table from the available logs, to get an output table where each row corresponds to a change in one of the 3 mentioned properties of interest.
# Add a column begin_timestamp and end_timestamp indicating start and end of a given state of a restaurant

# Note: a restaurant can go back an old state as well. Handle this scenario

# logs:

# id         onboarding_status  is_visible   type        timestamp                  ...other columns....
# 10ff2      onboarding         false        delivery    2019-03-21 07:07:41.000      
# 10ff2      onboarding         false        delivery    2019-03-22 04:07:41.000
# 10ff2      onboarding         false        delivery    2019-03-22 04:08:41.000
# 10ff2      activated          true         delivery    2019-03-23 12:07:41.000
# 10ff2      activated          true         delivery    2019-03-24 15:07:41.000
# 10ff2      activated          true         delivery    2019-03-25 15:07:41.000
# 322c4      activated          true         ott         2019-03-21 07:07:41.000
# 322c4      paused             false        ott         2019-03-22 07:07:41.000
# 322c4      paused             false        ott         2019-03-23 07:07:41.000
# 322c4      activated          true         delivery    2019-03-24 07:07:41.000
# 322c4      activated          true         ott         2019-03-25 07:07:41.000
# ac478      activated          true         delivery    2019-03-23 12:07:41.000
# ac478      activated          true         delivery    2019-03-24 12:07:41.000
# ac478      activated          true         delivery    2019-03-25 12:07:41.000


# restaurant status tracker:

# id         onboarding_status  is_visible   type        begin_timestamp            end_timestamp 
# 10ff2      onboarding         false        delivery    2019-03-21 07:07:41.000    2019-03-23 12:07:41.000      
# 10ff2      activated          true         delivery    2019-03-23 12:07:41.000    NULL
# 322c4      activated          true         ott         2019-03-21 07:07:41.000    2019-03-22 07:07:41.000
# 322c4      paused             false        ott         2019-03-22 07:07:41.000    2019-03-24 07:07:41.000
# 322c4      activated          true         delivery    2019-03-24 07:07:41.000    2019-03-25 07:07:41.000
# 322c4      activated          true         ott         2019-03-25 07:07:41.000    NULL
# ac478      activated          true         delivery    2019-03-23 12:07:41.000    NULL



# WITH _cte As (
#     SELECT *, lead(pre_status) OVER(PARTITION BY id ORDER BY timestamp ASC) as pre_status,
#     lead(is_visible) OVER(PARTITION BY id ORDER BY timestamp ASC) as pre_is_visible ,
#     lead(type) OVER(PARTITION BY id ORDER BY timestamp ASC) as pre_type 
#     FROM logs
# )


# (
# SELECT * FROM 
# (
# SELECT *, 
# CASE WHEN (pre_status <> onboarding_status) OR (is_visible <> pre_is_visible) OR (type <> pre_type) THEN 1 ELSE 0 END as tag_ 
# FROM _cte
# ) temp_ 
# WHERE tag_ = 1
# ) B 


# SEELCT id, onboarding_status, is_visible, type, timestamp as begin_timestamp, 
# LEAD(timestamp) OVER(PARTITION BY id ORDER BY timestamp) as end_timestamp 
# FROM B



# id         onboarding_status  is_visible   type        timestamp                  pre_status   pre_isvisible  next_type   tag_
# 10ff2      onboarding         false        delivery    2019-03-21 07:07:41.000    NULL          NULL            NULL        1
# 10ff2      activated          true         delivery    2019-03-23 12:07:41.000    onboarding    false           delivery    1
# 10ff2      activated          false        delivery    2019-03-24 15:07:41.000    activated     true            delivery    1
# 10ff2      activated          true         delivery    2019-03-25 15:07:41.000    activated     false           delivery    1

# -- 10ff2      onboarding         false        delivery    2019-03-22 04:07:41.000    onboarding    false           delivery    0
# -- 10ff2      onboarding         false        delivery    2019-03-22 04:08:41.000    onboarding    false           delivery    0





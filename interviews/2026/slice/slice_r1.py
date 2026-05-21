# SQL
# You have a transactions table:
# transactions
# column
# txn
# id


# account
# txn
# ts


# amount
# id


# merchant
# Write a SQL query to identify:
# 1. Each customer’s first transaction
# 2. Previous transaction amount
# 3. Percentage increase from previous transaction
# 4. Flag transactions where spend increased by more than 200%
# Option1:
# with


# row


# numbers as (
# SELECT txn
# ROW
# id, account
# id, txn
# ts, amount, merchant








# NUMBER() OVER (PARTITION BY account
# id ORDER BY txn




# ts ASC )
# as row
# num




# asc,
# ROW


# NUMBER() OVER (PARTITION BY account
# id ORDER BY txn




# ts DESC )
# as row
# num
# desc




# FROM transactions
# ),
# first




# transaction as (
# SELECT account
# FROM
# row
# id, txn
# id as first
# txn








# numbers
# id


# WHERE row


# num
# asc = 1




# ),
# last




# transaction as (
# SELECT account
# id, txn
# id as last
# txn
# id, amount as last
# txn












# amount
# WHERE
# row
# numbers


# WHERE row


# num
# desc = 1




# ),


# second
# last




# transaction as (
# SELECT account
# id, txn
# id as second
# last
# txn
# id, amount as second
# last
# txn
















# WHERE
# row
# numbers


# WHERE row


# num
# desc = 2




# amount
# ),


# final as (
# SELECT a.account
# id, a.first
# txn
# id, b.last
# txn
# amount,










# COALESCE(c.second
# last
# txn






# amount, 0) as second
# last
# txn
# amount,






# div0(b.last
# txn
# amount - c.second
# last
# txn
# amount,










# c.second
# last
# txn






# amount)*100.0 as pct


# change,
# CASE WHEN pct


# change > 200.00 then 1 ELSE 0 END AS flag_pct


# FROM
# first
# transaction a




# LEFT JOIN
# last
# transaction b ON a.account
# id = b.account
# id








# LEFT JOIN
# second
# last
# transaction b ON a.account
# id = c.account
# id










# increase
# )
# SELECT * FROM
# final


# Option 2:
# with
# row




# numbers as (
# SELECT txn
# ROW
# id, account
# id, txn
# ts, amount, merchant








# NUMBER() OVER (PARTITION BY account
# id ORDER BY txn




# ts ASC )
# as row
# num




# asc,
# ROW


# NUMBER() OVER (PARTITION BY account
# id ORDER BY txn




# ts DESC )
# as row
# num




# second
# last
# desc,
# LEAD(amount) OVER (PARTITION BY account
# id ORDER BY txn




# txn
# amount
# ts DESC ) as






# FROM transactions
# ),
# first




# transaction as (
# SELECT account
# FROM
# row
# id, txn
# id as first
# txn








# numbers
# id


# WHERE row


# num
# asc = 1




# ),
# last




# transaction as (
# second
# SELECT account
# id, txn


# id as last
# txn
# id, amount as last
# txn










# amount,
# last
# txn
# amount




# WHERE


# row
# numbers


# WHERE row


# num
# desc = 1




# ),


# final as (
# SELECT a.account
# id, a.first
# txn
# id, b.last
# txn
# amount,










# COALESCE(b.second
# last
# txn






# amount, 0) as second
# last
# txn
# amount,






# div0(b.last
# txn
# amount - b.second
# last
# txn
# amount,










# b.second
# last
# txn






# amount)*100.0 as pct


# change,
# CASE WHEN pct


# change > 200.00 then 1 ELSE 0 END AS flag_pct


# FROM
# first
# transaction a




# LEFT JOIN
# last
# transaction b ON a.account
# id = b.account
# id








# LEFT JOIN
# second
# last
# transaction b ON a.account
# id = c.account
# id










# increase
# )
# SELECT * FROM
# final


# ●
# If txn


# id is integer we can use it along with ts
# Problem Statement
# You are given 3 source tables, Assume all tables have created


# at and updated


# at column.
# transactions
# column type
# id bigint
# uuid string
# amount decimal
# transaction_status
# column type
# transaction


# id bigint
# status string
# user_details
# column type
# uuid string
# user


# name string
# You need to design and implement a Spark/dbt job to create an incremental fact table by
# joining these tables.
# Requirements
# 1. The pipeline should process data incrementally.
# 2. Existing records should be updated if transaction status changes.
# 3. The pipeline should be idempotent.
# 4. The solution should scale for large datasets.
# {{
# materialized = 'table'
# ,
# query_
# tag = 'fct
# transactions




# incremental


# strategy = 'merge'
# ,
# users'
# ,
# pre


# hook = '{{a delete macro which deletes the data which was there in last 1.5 hours}}'
# --frequency: 30 mins
# }}
# {% set execution


# date = get
# execution




# date() %} -- Write this somewhere in macros and this
# gets updated everytime on dbt run 30 mins incremenatlly
# with


# changes
# in
# transaction






# status as (
# SELECT transaction
# id, status , created
# at as status






# createdat, updated


# at as
# status


# updatedat from transaction
# status


# WHERE 1=1
# AND {{ if


# incremental() }}
# updated


# at >= datediff('minutes'
# , 90, execution


# date) -- Basically want to check
# for last 90 mins based on execution
# date


# ),


# changes
# in




# users as (
# SELECT uuid, user
# name, created
# at as user






# createdat, updated
# at as


# user


# updatedat from user
# details


# WHERE 1=1
# AND {{ if


# incremental() }}
# updated


# at >= datediff('minutes'
# , 90, execution


# date) -- Basically want to check
# for last 90 mins based on execution
# date


# ),
# transactions
# based
# on








# status as (
# SELECT id, uuid, amount, created


# at, updated
# at from transaction WHERE id in


# (SELECT transaction
# id from




# changes
# in
# transaction






# status)
# ),
# transactions


# based
# on






# user as (
# SELECT id, uuid, amount, created


# at, updated


# WHERE 1=1
# at from transaction
# AND updated


# at >= datediff('minutes'
# , 90, execution
# uuid in (SELECT uuid from


# changes
# in




# users)
# ),


# date)
# combined


# txn




# changes as (
# SELECT * FROM
# transactions
# based
# on
# status








# UNION
# SELECT * FROM
# transactions
# based
# on
# user








# ),


# final as (
# SELECT b.transaction
# id, a.uuid, a.amount, a.created
# at as txn
# created






# status, b.status
# createdat, b.status




# updatedat, c.user
# name, c.user
# createdat,




# c.user


# updatedat
# FROM
# combined a


# LEFT JOIN


# changes
# in
# transaction
# status b ON a.id = b.transaction
# id








# LEFT JOIN


# changes
# in
# users c ON a.uuid = c.uuid






# at, b.status as
# ),
# casting as (
# SELECT transaction
# id::BIGINT as transaction




# id,
# ......
# )
# SELECT * FROM casting
# 1. the changes rows in a df
# 2. copy to a staging table (temp table)
# 3. DELETE using txn


# id from main table using this temp table
# 4. INSERT the data from temp to main
# 5. DELETE data from temp table
# 3rd step happened -> queried main table -> you get a result -> INSERT happened -> you get a
# different result
# freshness and volumes they should be intact: yml file
# dq tests: not null, unique etc.
# fct


# table: not null, unique,
# datepart: for the last 90 days there should be data for everyday
# ranges:
# -- z-score: custom macro
# severity: error or warn
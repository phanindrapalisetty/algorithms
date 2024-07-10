# Given are two arrays of integers A and B, such that B is a permutation of A. However, some numbers went missing from A. Can you find the missing numbers?

# Notes:

# (a) If a number occurs multiple times in the arrays, you must ensure that the frequency of that number in both arrays is the same. If that is not the case, then it is also a missing number.

# (b) You have to print all the missing numbers in ascending order.

# (c) Print each missing number once, even if it is missing multiple times.

# (d) The difference between maximum and minimum number in B is less than or equal to 100.

# Input Format:

# There will be two parameters of input:

# (a) inputA the first array (b) inputB the second array

# A = [7,2,5,3,5,3]
# B = [7,2,5,4,6,3,5,3,3]

# Output Format

# Output the missing numbers in ascending order.

# Output = [3, 4, 6]

# Expected: Solution with O(n) time complexity with O(1) space


# # import requests
# # import mysql.connector
# # import pandas as pd

# print('Hello')

A = [7,2,5,3,5,3]
B = [7,2,5,4,6,3,5,3,3]

counter_a = {}
counter_b = {} 

for i in B:
    if i in counter_b:
        val_b = counter_b[i]
        counter_b.update({i:val_b+1})
    else:
        counter_b.update({i:1})

for i in A:
    if i in counter_a:
        val_a = counter_a[i]
        counter_a.update({i:val_a+1})
    else:
        counter_a.update({i:1})

result = [] 
for i in counter_b:
    if i in counter_a:
        if counter_a[i] != counter_b[i]:
            result.append(i)
    else:
        result.append(i)

# print(counter_a)
# print(counter_b)
# print(sorted(result) [3, 4, 6]
# print(result) [4, 6, 3]

"""
Feedback: Sorting part, how can point (d) can be used in sorting of elements in O(n) complexity.
"""

"""

Table: source_ph_number, dest_ph_number, call_start_time
TableName: call_records 

Output:
source_ph_number, Case when if last_dest_ph_num = first_dest_ph_num then 'Y' Else 'N'

Answer: 

WITH _CTE AS (
    SELECT *, 
        ROW_NUMBER() OVER(PARTITION BY source_ph_number ORDER BY call_start_time ASC) as row_asc, 
        ROW_NUMBER() OVER(PARTITION BY source_ph_number ORDER BY call_start_time DESC) as row_desc
    FROM call_records
)


SELECT source_ph_number, 
    CASE WHEN first_dest = last_dest THEN 'Y' ELSE 'N' END as flag
FROM (
    SELECT a.source_ph_number, a.dest_ph_number as first_dest, b.dest_ph_number as last_dest
    FROM (
        SELECT * FROM _CTE WHERE row_asc = 1
    )
    LEFT JOIN 
    (
        SELECT * FROM _CTE WHERE row_desc = 1
    )
    ON a.source_ph_number = b.source_ph_number
) temp_ 


Feedback/Followup: Read a level more on optimisation, where to use CTEs, where to use subqueries etc. 
"""
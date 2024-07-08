"""
Problem 1: Solved
Count vowels in a substring of length k
"""
def count_vowels(str_):
    cnt = 0 
    for i in str_:
        if i in ['a', 'e', 'i', 'o', 'u']:
            cnt += 1 
    return cnt 


s = 'aeiou'
k = 2
n = len(s)
max_ = 0
for i in range(0, n-k):
    sub_ = s[i:i+k]
    n_vow = count_vowels(sub_)
    if n_vow > max_:
        max_ = n_vow 
print(max_)

"""
Problem 2: Unsolved

Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i].
The product of any prefix or suffix of nums is guaranteed to fit in a 32-bit integer.

You must write an algorithm that runs in O(n) time and without using the division operation.


Example 1:
Input: nums = [1,2,3,4]
Output: [24,12,8,6]

Example 2:
Input: nums = [-1,1,0,-3,3]
Output: [0,0,9,0,0]

Constraints:

2 <= nums.length <= 105
-30 <= nums[i] <= 30
The product of any prefix or suffix of nums is guaranteed to fit in a 32-bit integer.

Follow up: Can you solve the problem in O(1) extra space complexity? (The output array does not count as extra space for space complexity analysis.)
"""


"""
Table: Logs
+-------------+---------+
| Column Name | Type |
+-------------+---------+
| id | int |
| num | varchar |
+-------------+---------+

In SQL, id is the primary key for this table.
id is an autoincrement column.

Find all numbers that appear at least three times consecutively.
Return the result table in any order.
The result format is in the following example.

Example 1:
Input:
Logs table:
+----+-----+
| id | num |
+----+-----+
| 1 | 1 |
| 2 | 1 |
| 3 | 1 |
| 4 | 2 |
| 5 | 1 |
| 6 | 2 |
| 7 | 2 |
+----+-----+

Output:
+-----------------+
| ConsecutiveNums |
+-----------------+
| 1 |
+-----------------+

Explanation: 1 is the only number that appears consecutively for at least three times.

"""
#%%
"""
You are given an integer array cookies, where cookies[i] denotes the number of cookies in the ith bag. 
You are also given an integer k that denotes the number of children to distribute all the bags of cookies to. 
All the cookies in the same bag must go to the same child and cannot be split up.

The unfairness of a distribution is defined as the maximum total cookies obtained by a single child in the distribution.

Return the minimum unfairness of all distributions.
Example 1:

Input: cookies = [8,15,10,20,8], k = 2
Output: 31
Explanation: One optimal distribution is [8,15,8] and [10,20]
- The 1st child receives [8,15,8] which has a total of 8 + 15 + 8 = 31 cookies.
- The 2nd child receives [10,20] which has a total of 10 + 20 = 30 cookies.
The unfairness of the distribution is max(31,30) = 31.
It can be shown that there is no distribution with an unfairness less than 31.
Example 2:

Input: cookies = [6,1,3,2,2,4,1,2], k = 3
Output: 7
Explanation: One optimal distribution is [6,1], [3,2,2], and [4,1,2]
- The 1st child receives [6,1] which has a total of 6 + 1 = 7 cookies.
- The 2nd child receives [3,2,2] which has a total of 3 + 2 + 2 = 7 cookies.
- The 3rd child receives [4,1,2] which has a total of 4 + 1 + 2 = 7 cookies.
The unfairness of the distribution is max(7,7,7) = 7.
It can be shown that there is no distribution with an unfairness less than 7.
"""
#%%
# [6,1,3,2,2,4,1,2] --> [6, 4, 3, 2, 2, 2, 1]

"""[8, 12, 15], n = 2  [8, 15], [12] --> ncr """

cookies = [6,1,3,2,2,4,1,2]
k = 3 
n = len(cookies)

def partition_helper(nums, k, start, current_part, result):
    if start == len(nums):
        if len(current_part) == k:
            result.append([list(part) for part in current_part])
        return result
    
    for i in range(len(current_part)):
        current_part[i].append(nums[start])
        partition_helper(nums, k, start + 1, current_part, result)
        current_part[i].pop()
    
    if len(current_part) < k:
        current_part.append([nums[start]])
        partition_helper(nums, k, start + 1, current_part, result)
        current_part.pop()

def find_partitions(nums, k):
    result = []
    partition_helper(nums, k, 0, [], result)
    return result

# Example usage:
nums = [1, 2, 3, 4]
k = 2
partitions = find_partitions(nums, k)
for partition in partitions:
    print(partition)

#%%
"""
You are given a 0-indexed integer array nums. Rearrange the values of nums according to the following rules:

Sort the values at odd indices of nums in non-increasing order.
For example, if nums = [4,1,2,3] before this step, it becomes [4,3,2,1] after. The values at odd indices 1 and 3 are sorted in non-increasing order.
Sort the values at even indices of nums in non-decreasing order.
For example, if nums = [4,1,2,3] before this step, it becomes [2,1,4,3] after. The values at even indices
he values at even indices 0 and 2 are sorted in non-decreasing order.
Return the array formed after rearranging the values of nums.
"""

list_ = [2, 1]

evens = []
odds = [] 

for i in range(0, len(list_)):
    if (i+1)%2 == 0:
        evens.append(list_[i])
    else:
        odds.append(list_[i])

evens = sorted(evens, reverse=True)
odds = sorted(odds)

result = []
for i in range (0, len(list_)):
    if (i+1)%2 == 0:
        result.append(evens[i//2])
    else:
        result.append(odds[i//2])

# print(result)
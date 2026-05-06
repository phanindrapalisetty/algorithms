#%%
"""
Problem 1
You have a list of trip fares as an array:
fares = [10, 20, 30, 40, 50]

Write a Python function that returns the maximum profit you could make by choosing a buy price and a sell price, 
where the sell must come after the buy in the array. 
You can only buy and sell once.

Example: [10, 20, 30, 40, 50] → profit = 40 (buy at 10, sell at 50)
Example: [50, 40, 30, 20, 10] → profit = 0 (prices only drop, no profit possible)

"""

fares = [10, 20, 30, 40, 50]
_min = fares[0]
_diff = 0 

for i in range (1, len(fares)):
    _min = min(_min, fares[i])
    _diff = max(_diff, fares[i] - _min)

print(_min, _diff)
# %%
"""
Q1: 
Given a string "aabbcc", find the first non-repeating character. 
What data structure do you reach for first and why?

Q2: 
Given two arrays [1,3,5] and [2,4,6], merge them into a sorted array. 
What's your approach?

Q3: 
Given a string, check if it's a palindrome. 
Ignoring built-in reverse functions, how do you do it?
"""

#%%
"""Palindrome or not"""
s = 'racecar' 

i, j = 0, len(s)-1
while i < j: 
    if s[i] != s[j]: print(False)
print(True)

#%%
"""
Problem: 
Given a sorted array of integers, find two numbers that add up to a target sum. Return their indices.
pythonnums = [1, 3, 5, 7, 9]
target = 10
# expected output: (1, 3) → nums[1]=3, nums[3]=7
"""

nums = [1, 3, 5, 7, 9] 
target = 10 
i, j = 0, len(nums)-1
while i < j: 
    if nums[i] + nums[j] == target: 
        print(i, j)
    elif nums[i] + nums[j] > target:
       j -= 1
    elif nums[i] + nums[j] < target: 
       i += 1
print(None, None)

#%%
"""
Problem: maximum sum subarray of size k.
pythonnums = [2, 1, 5, 1, 3, 2]
k = 3
# Find the maximum sum of any contiguous subarray of size k
# Expected output: 9 → [5, 1, 3]
"""

nums = [2, 1, 5, 1, 3, 2]
k = 3

# Step 1: first window sum
window_sum = sum(nums[0:k])  # 2+1+5 = 8
_max = window_sum

# Step 2: slide forward
for i in range(k, len(nums)):
    window_sum += nums[i]      # add incoming right element
    window_sum -= nums[i-k]    # drop outgoing left element
    _max = max(_max, window_sum)

print(_max)

#%%
"""
Problem — HashMap:
pythons = "aabbccdde"
# Find the first non-repeating character
# Expected output: "e"
"""

_dict = {} 

for i in s: 
    if i in _dict: 
       _dict.update({i : _dict[i]+1})
    else: 
       _dict.update({i:1})

for i in _dict: 
   if _dict[i] == 1: print(i)


#%%
"""
Given a string, find the length of the longest 
substring without repeating characters.

s = "abcabcbb"
# Expected output: 3 → "abc"
"""

## My solution 
print('##### My Solution #####')
s = "abcabcbb"
seen = {}

max_len = 0
left, right = 0, 1
while left < right and left < len(s)-1 and right < len(s)-1:
    
    if s[right] not in s[left:right]:
        print(s[right], s[left:right+1], max_len, left-right+1)
        max_len = max(right-left+1, max_len)
        right += 1
    else: 
        left += 1
        right = left + 1

print(max_len)

## Claude's Solution
print('##### Claude Solution #####')

seen = set()
left = 0
max_len = 0

for right in range(len(s)):
    while s[right] in seen:
        seen.remove(s[left])
        left += 1
    seen.add(s[right])
    max_len = max(max_len, right - left + 1)

#%%
"""
# Given an array of integers, return the two numbers 
# that add up to a target. Return their indices.
# Each input has exactly one solution.

nums = [2, 7, 11, 15]
target = 9
# Expected output: [0, 1] → nums[0]=2, nums[1]=7

Solution: 
_map = {}
nums = [2, 7, 11, 15] 
 target = 9 
left = 0

for i in range(0, len(nums)):      
    if target - nums[i] in _map: 
        return i, _map[target - nums[i]]
    else: 
        _map.update({nums[i]: i})
"""

#%%
"""
# Given a string s, find the longest palindromic substring.

s = "babad"
# Expected output: "bab" or "aba" (either is valid)

s = "cbbd"  
# Expected output: "bb"
"""
# Brute force
n = len(str) 
start = 0
max_len = 1 

for i in range(n): 
    for j in range (i, n): 
       flag = 1 
       for k in range (0, (j-i)//2 +1): 
         if (str[i + k] != str[j - k]):
           flag = 0 
       if flag != 0 and j-i+1 > max_len: 
          max_len = j-i+1
          start = i 

print(str[start: start+max_len-1])

# Claude's solution
s = "babad"
max_palindrome = ""

def expand(s, left, right):
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1
    # when loop exits, s[left] != s[right]
    # so valid palindrome is s[left+1:right]
    return s[left+1:right]

for i in range(len(s)):
    odd = expand(s, i, i)        # odd length center
    even = expand(s, i, i+1)     # even length center
    
    # keep the longest of odd, even, current max
    max_palindrome = max(odd, even, max_palindrome, key=len)

print(max_palindrome)
# %%

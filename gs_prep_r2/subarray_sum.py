"""
Problem: 
Given a list of integers and a sum_total, 
find the subarray such that indexes between which the sum can occur. 

Input: 
List: [1, 4, 20, 3, 10, 5]; Sum: 33
Output: 
Sum found between 2 and 4

Input: 
List: [10, 2, -2, -20, 10]; Sum: -10
Output: 
Sum found between 0 and 3
"""
#%%
input_ = [1, 4, 20, 3, 10, 5]
# target_ = 33
target_ = 1


def get_index_one(input_, target_): 
    """
    This is a basic approach.
    For every element, traverse trough other elements to get the indices. 
    Time Complexity: O(n*n)
    Handles negative numbers as well.
    """
    n = len(input_)
    for i in range(n):
        sum = 0
        for j in range(i, n):
            sum += input_[j]
            print(i, j, sum)
            if sum == target_:
                return i, j
    return -1, -1
# %%
# input_ = [1, 4, 20, 3, 10, 5]
# target_ = 37

input_ = [2, 3, 1, 2, 4, 3]
target_ = 7 


n = len(input_)
map = {}
curr_sum = 0 

for i in range(n):
    print('map', map)
    print('curr_sum', curr_sum-target_)
    curr_sum += input_[i]

    if curr_sum == target_:
        print('first loop', 0, i)
    
    if curr_sum-target_ in map:
        print('Map', map[curr_sum-target_]+1 , i)
    map[curr_sum] = i
# %%
"""
Tweaking the question.. 

Let's say, if not for sub-array, find the elements in the array
which make up to the sum. 
"""


def find_combinations(nums, sum_total):
    def backtrack(start, target, path):
        if target == 0:
            result.append(path)
            return
        if target < 0:
            return
        for i in range(start, len(nums)):
            backtrack(i + 1, target - nums[i], path + [nums[i]])
    
    result = []
    backtrack(0, sum_total, [])
    return result
# %%

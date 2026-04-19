#%%
"""
Round 1: Hiring Manager Screening
"""

"""
About digitisation project:
What are the stages? 
About SQS
Docker: Difference between Entry point and CMD
Routing and Security
"""

"""
Problem 1:
Given a list with elements that increase in values until max, then it will decrease. Find the max. 

Input: [1, 2, 4, 7, 8, 10, 12, 11, 9]
Output: 12 
"""

# This is a O(n) approach. 
def get_largest_number(arr):
    max_ = arr[0]
    for i in arr:
        if i > max_:
            max_ = i 
    return max_ 

arr = [1, 2, 4, 7, 8, 10, 12, 11, 9]
# print(get_largest_number(arr))

# Binary search type of an approach 
# Catch is before max: arr[i-1] < arr[i] < arr[i+1]
# After max: arr[i-1] > arr[i] > arr[i+1]
# At max, arr[i-1] < arr[i] and arr[i] > arr[i+1]
# Find the i which satisfies this condition
left_ = 0 
right_ = len(arr)

while left_ <= right_:
    mid = left_ + (right_-left_)//2
    print(mid, left_, right_)

    if arr[mid-1] > arr[mid] > arr[mid+1]:
        print(1)
        right_ = mid -1
    elif arr[mid-1] < arr[mid] < arr[mid+1]:
        print(2)
        left_ = mid + 1
    else:
        print(3)
        break 
    
print(arr[mid])
# %%
"""
Round 2:

Movie streaming intervals, find the total time he watched. 
Input can be of any order

Input: [[0, 30], [50, 60], [25, 45]]
Output: 55: 0-45 + 50-60 
"""

def get_minutes_watched(arr):
    arr = sorted(arr, key=lambda x: x[0])
    merged = [arr[0]]
    for i in arr[1:]:
        if merged[-1][1] >= i[0]:
            merged[-1][1] = i[1]
        else:
            merged.append(i)
    return merged
# %%
"""
Basic SQL Question 
Questions on NULL Joins
"""
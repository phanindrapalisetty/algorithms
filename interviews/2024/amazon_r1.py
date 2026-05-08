#%%
"""
Problem 1:
Given a list of number, get the maximum possible number

Input: [3, 30, 34, 5, 9]
Output: 9534330
"""

list_ = [3, 30, 34, 5, 9]
str_nums = [str(x) for x in list_]
# Define a comparator based on the custom sorting logic
def compare(x, y):
    # Compare combined numbers x+y and y+x
    if x + y > y + x:
        return -1
    elif x + y < y + x:
        return 1
    else:
        return 0
    
from functools import cmp_to_key
def largest_number(nums):
    
    str_nums = list(map(str, nums))
    str_nums.sort(key=cmp_to_key(compare), reverse=True)
    result = ''.join(str_nums)
    
    return str(int(result))  # handles edge case like [0, 0]

# Sort numbers based on the comparator
str_nums = sorted(str_nums, key=lambda x: (x*10)[:10], reverse=True)
largest_num = ''.join(str_nums)
#%%
"""
Problem 2:
Given a list with elements that increase in values until max, then it will decrease. Find the max. 

Input: [1, 2, 4, 7, 8, 10, 12, 11, 9]
Output: 12 

Time complexity should be O(logn) 
"""

def find_max_in_bitonic_array(arr):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        # Check if mid is the maximum
        if (mid == 0 or arr[mid] > arr[mid - 1]) and (mid == len(arr) - 1 or arr[mid] > arr[mid + 1]):
            return arr[mid]
        # If the middle element is part of the increasing sequence
        elif mid > 0 and arr[mid] > arr[mid - 1]:
            left = mid + 1
        # If the middle element is part of the decreasing sequence
        else:
            right = mid - 1

# Example usage:
arr = [1, 2, 4, 7, 8, 10, 12, 11, 9]
print(find_max_in_bitonic_array(arr)) 

#%%
"""
Problem 3:
Find the column number for the column names on MS Excel 

Input: Z
Output: 26 

Input: AY
Output: 51

Input: BA
Output: 53

Input: AAB 
Output: 704
"""
input_ = 'BA'
char_to_value = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6,
        'G': 7, 'H': 8, 'I': 9, 'J': 10, 'K': 11, 'L': 12,
        'M': 13, 'N': 14, 'O': 15, 'P': 16, 'Q': 17, 'R': 18,
        'S': 19, 'T': 20, 'U': 21, 'V': 22, 'W': 23, 'X': 24,
        'Y': 25, 'Z': 26
    }

# Approach 1
def get_value(input_):
    result = 0
    for i in input_:
        result = result * 26 + char_to_value[i]
    return result 

# Approach 2
def get_value(input_):
    rev = input_[::-1]
    ans = 0 
    for i in range(0, len(rev)):
        ans += pow(26, i) * char_to_value[rev[i]]
    return ans 
#%%
"""
Problem 4:
What is the result when we do FULL OUTER JOIN on A and B?

Table A, Col A:
1, 2, 3, 5, NULL, NULL 

Table B, Col B:
1, 1, 2, 4, NULL 
"""

"""
Answer:
1 1 
1 1 
2 2 
3 NULL 
5 NULL 
NULL 4
NULL NULL 
NULL NULL 
"""
#%%
"""
Question: 
Where did you show Customer Obsession in your project? 
Like request did not come from customer, but you solved it. 
"""
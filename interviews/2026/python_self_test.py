#%%
"""
Palindrone check
"""

def _check_palindrome(s):
    left, right = 0, len(s)-1
    while left <= right:
        if s[left] != s[right]:
            return False 
        else:
            left += 1
            right -= 1
    return True
s = 'raceecar'
print(_check_palindrome(s))
# %%
"""
Problem 2:
Given a list with elements that increase in values until max, then it will decrease. Find the max. 

Input: [1, 2, 4, 7, 8, 10, 12, 11, 9]
Output: 12 

Time complexity should be O(logn) 
"""
_list = [12, 11, 9]

def _get_max(_list):
    left, right = 0, len(_list)-1

    while left <= right: 
        mid = left + (right - left) // 2

        if (_list[mid] > _list[mid - 1]) and (_list[mid] > _list[mid+1]) :
            return _list[mid]
        elif _list[mid] > _list[mid-1]:
            left = mid + 1
        else: 
            right = mid - 1

    left, right = 0, len(_list) - 1

print(_get_max(_list))
# %%
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

# n = len(input_)-1
# _sum = 0
# while n >= 0:
#     _sum = _sum*26 + char_to_value[input_[n]]
#     n -= 1

# print(_sum)

_sum = 0 
_str = input_[::-1]
for i in range(0, len(input_)):
    _sum += pow(26, i) * char_to_value[_str[i]]

print(_sum)
# %%

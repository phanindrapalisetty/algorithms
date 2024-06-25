# #%%
# """
# Find longest palindromic substring

# Input: abbac 
# Output: abba
# """

# str_ = "geeksforgeegs"
# length = len(str_)
# maxLength = 0 

# for i in range(length): 
#     for j in range(i, length):
#         isPalindrome = 1
#         for k in range (0, (j-i)//2 + 1):
#             sub_ = str_[i:j+1]
            
#             if sub_ == sub_[::-1] and (j+1-i) > maxLength:
#                 # print(sub_)
#                 maxLength = j+1-i 
#                 index = i 
                
# # %%
# print("i ==>", i, "j ==>", j, "k ==>", k, str_[index:index+maxLength])
# # %%

# # %%
# """
# Find the largest palindromic string
# """

# input_ = "geeksforgeeks"

# n = len(input_)
# maxLength = 1
# index = 0 

# for i in range(n):
#     for j in range(i, n):
#         flag = 0 
#         for k in range(0, (j-i)//2+1):
#             sub_ = input_[i:j+1]
#             if sub_ == sub_[::-1] and maxLength < (j+1-i):
#                 maxLength = j+1-i 
#                 index = i 

# print('Find the largest palindromic string')
# print(input_[index:index+maxLength])
#%%
from typing import List
def helper(target: int, list_of_int: List[int]):
    min_rem = min(list_of_int, key = lambda x: target%x)
    return min_rem

def coinChange(coins: List[int], amount: int) -> int:
    output = 0 
    while amount > 0:
        if coins:
            poped = helper(amount, coins)
            coins.remove(poped)
            output += amount//poped
            amount -= ((amount//poped)*(poped))
            print('poped:', poped, 'mul:', (amount//poped), 'amount:', amount)
        else:
            break 
    
    if not amount: return -1
    else: return output

coins = [186,419,83,408]
amount = 6249

print(coinChange(coins=coins, amount=amount))


def find_combination(integers, target):
    # Memoization dictionary
    memo = {}

    def helper(remaining):
        # If the remaining target is 0, return an empty list (base case)
        if remaining == 0:
            return []
        # If the remaining target is negative, return None (not possible)
        if remaining < 0:
            return None
        # If the result is already computed, return it from the memo dictionary
        if remaining in memo:
            return memo[remaining]

        # Try each integer in the list
        for num in integers:
            # Recursive call to find the combination for the remaining target
            result = helper(remaining - num)
            if result is not None:
                # If a valid combination is found, store it in memo and return it
                memo[remaining] = result + [num]
                return memo[remaining]

        # If no combination is found, store None in memo and return None
        memo[remaining] = None
        return None

    # Initial call to the helper function
    combination = helper(target)

    # Return the combination if found, otherwise return -1
    return combination if combination is not None else -1

# Example usage:
# integers = [186, 419, 83, 408]
# target = 6249
# print('find_combination', find_combination(integers, target))  # Output will be calculated below

# 408*3 + 9*83
# [
# 408, 408, 408, 
# 83, 83, 83, 83, 83, 83, 83, 83, 83,
# 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186, 186
#]
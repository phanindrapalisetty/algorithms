#%%
"""
Find longest palindromic substring

Input: abbac 
Output: abba
"""

str_ = "aabaad"
length = len(str_)
maxLength = 0 

for i in range(length): 
    for j in range(i, length):
        isPalindrome = 1
        for k in range (0, (j-i)//2 + 1):
            sub_ = str_[i:j+1]
            if sub_ == sub_[::-1]:
                print("i ==>", i, "j ==>", j, "k ==>", k, str_[i:j+1])
# %%

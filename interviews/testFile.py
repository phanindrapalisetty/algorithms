#%%
"""
Find longest palindromic substring

Input: abbac 
Output: abba
"""

str_ = "geeksforgeegs"
length = len(str_)
maxLength = 0 

for i in range(length): 
    for j in range(i, length):
        isPalindrome = 1
        for k in range (0, (j-i)//2 + 1):
            sub_ = str_[i:j+1]
            
            if sub_ == sub_[::-1] and (j+1-i) > maxLength:
                print(sub_)
                maxLength = j+1-i 
                index = i 
                
# %%
print("i ==>", i, "j ==>", j, "k ==>", k, str_[index:index+maxLength])
# %%
[1, 2, 3].sum()
# %%
" Jon Doe".strip()
# %%
def som():
    if not some():
        return False 
    return True



def some():
    if 1==1:
        raise ValueError(1)
    return True
    
# %%

#%%
### P1 — Time to Second Event per User

# **Difficulty**: Easy–Medium  
# **Concepts**: GroupBy, sort, first/second row extraction, timedelta

# **Scenario**:
# """python
# import pandas as pd

# data = {
#     'user_id':    [1, 1, 1, 2, 2, 3, 3, 3],
#     'event_type': ['login','purchase','logout','login','purchase','login','login','purchase'],
#     'timestamp':  [
#         '2024-01-01 08:00', '2024-01-01 08:30', '2024-01-01 09:00',
#         '2024-01-02 10:00', '2024-01-02 10:45',
#         '2024-01-03 07:00', '2024-01-03 07:10', '2024-01-03 08:00'
#     ]
# }
# df = pd.DataFrame(data)
# df['timestamp'] = pd.to_datetime(df['timestamp'])
# """

#%%
arr = [1, 2, 4, 7, 8, 10, 12, 11, 9]

left, right = 0, len(arr) - 1

while left < right:
    mid = (left + right) // 2
    if arr[mid] < arr[mid + 1]:
        left = mid + 1
    else:
        right = mid

print(arr[left])
# %%
def majorityElement(A):
    _dict = {}
    N = len(A)
    for i in A: 
        if i in _dict: 
            _dict.update({i: _dict[i]+1})
        else: 
            _dict.update({i:1})
    print(_dict)
    
    for n in _dict: 
        print(_dict[n], N/2)
        if _dict[n] > N/2: 
            return n
print(majorityElement([100]))
# %%
def solve(A):
    _triplets = 0
    for i in range(0, len(A)-2):
        for j in range (i+1, len(A)-1):
            for k in range(j+1, len(A)):
                print(A[i], A[j], A[k])
                if A[i] < A[j] and A[j] < A[k]:
                    _triplets += 1
    
    return _triplets

print(solve([18,26,17,30,13,30,20,13,10,19]))
# %%
# s = "abcabcbb"
s = "abba"

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
# %%
nums = [2, 7, 11, 15]
target = 9



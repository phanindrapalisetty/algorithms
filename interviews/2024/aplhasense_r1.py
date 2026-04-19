#%%
"""
m*n matrix: can have 3 values: 0, 1, 2 
0: Emplty Cell 
1: Healthy Person 
2: Covid Patient

Every minute a healthy person can get covid if he gets 

Minimum time in which all the cells can get covid, else return -1 

Example Input: [[2,1,1],[1,1,0],[0,1,1]]

 2 1 1
 1 1 0
 0 1 1 

 2 2 1
 2 1 0 
 0 1 1 

 2 2 2
 2 2 0 
 0 1 1 

 2 2 2 
 2 2 0 
 0 2 1 

return: 4 
"""

list_ = [[2,1,1],[1,1,0],[0,1,1]] 
arr_ = [[[0,0]]]

# def get_some(list_):
# while True: 
#     arr_[-1].append([])
#     counter_ = 0
#     len_ = len(list_)
#     for i in range (0, len_):
#         for j in range(i, len_):
#             if list_[i][j] == 2:
#                 try:
#                     if list_[i-1][j] == 1:
#                         list_[i-1][j] = 2
#                         arr_[-1].append([i-1, j])
#                 except: 
#                     pass 
#                 try:
#                     if list_[i+1][j] == 1:
#                         list_[i+1][j] = 2
#                         arr_[-1].append([i+1, j])
#                 except: 
#                     pass
#                 try:
#                     if list_[i][j-1] == 1:
#                         list_[i][j-1] = 2
#                         arr_[-1].append(i, j-1)
#                 except: 
#                     pass
#                 try:
#                     if list_[i][j+1] == 1:
#                         list_[i][j+1] = 2
#                         arr_[-1].append([i, j+1])
#                 except: 
#                     pass
#         counter_ += 1
#     if len(arr_[-1]) == 0:
#         break 
    
#     # return counter_ if counter_ != 0 else -1
# print(arr_[-1])
# print(list_)
# %%
list_ = [[2,1,1],[1,1,0],[0,1,1]] 
arr_ = [[[0,0]]]
len_ = len(list_)
counter_ = 0

while True:
    x_arr = arr_[-1]
    some_ = [] 
    for m in x_arr: 
        i = m[0]
        j = m[1]
        if i in range (0, len_) and j in range(i, len_):
            if list_[i][j] == 2:
                try:
                    if list_[i-1][j] == 1:
                        list_[i-1][j] = 2
                        some_.append([i-1, j])
                except: 
                    pass 
                try:
                    if list_[i+1][j] == 1:
                        list_[i+1][j] = 2
                        some_.append([i+1, j])
                except: 
                    pass
                try:
                    if list_[i][j-1] == 1:
                        list_[i][j-1] = 2
                        some_.append(i, j-1)
                except: 
                    pass
                try:
                    if list_[i][j+1] == 1:
                        list_[i][j+1] = 2
                        some_.append([i, j+1])
                except: 
                    pass
    counter_ += 1
    arr_.append(some_)
    # print(len(some_))
    if len(some_) == 0:
        break 


# x_arr = arr_[-1]
# for m in x_arr: 
#     i = m[0]
#     j = m[1]
#     if i in range (0, len_) and j in range(i, len_):

#         if list_[i][j] == 2:
#             try:
#                 if list_[i-1][j] == 1:
#                     list_[i-1][j] = 2
#                     some_.append([i-1, j])
#             except: 
#                 pass 
#             try:
#                 if list_[i+1][j] == 1:
#                     list_[i+1][j] = 2
#                     some_.append([i+1, j])
#             except: 
#                 pass
#             try:
#                 if list_[i][j-1] == 1:
#                     list_[i][j-1] = 2
#                     some_.append(i, j-1)
#             except: 
#                 pass
#             try:
#                 if list_[i][j+1] == 1:
#                     list_[i][j+1] = 2
#                     some_.append([i, j+1])
#             except: 
#                 pass
# counter_ += 1
# arr_.append(some_)
 

print(counter_)
print(list_)
print(arr_[-1])
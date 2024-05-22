#%%
"""
There are several frogs on a line, each with an integer coordinate and a specific tongue size. 
More precisely the ith frog is on the coordinaste Xi and its tongue size is Si. 
Additionally there are flies also positioned on integer coordinates. The ith fly is positioned on Yi coordinate. 
A frog i manages to eat a fly j if and only if: (Xi-Yj) <= Si. 
The task is to determine for each frog how many flies it can eat.

Input1: 
X = []
S = []
Y = []
Output: 

Input2: 
X = []
S = []
Y = []
Output: 
"""

#%%
"""
Relative position in array:
given an array of integers modify each element to reflect it's relativce position in the sorted array. 
Integers of same value will have same relative position

Input: [40, 10, 20, 30]
Output: [4, 1, 2, 3]

Input: [30, 10, 20, 20, 40, 30]
Output: [3, 1, 2, 2, 4, 3]
"""

from typing import List
def get_relative_position(
        input_list: List[int]
) -> List[int]:
    
    sorted_list = sorted(list(set(input_list)))

    output_list = []
    for i in range(len(input_list)):
        for j in range(len(sorted_list)):
            if input_list[i] == sorted_list[j]:
                output_list.append(j+1)
    return output_list
# %%
def get_relative_position_two(input_list: List[int]) -> List[int]:
    
    sorted_list = sorted(list(set(input_list)))

    dict_ = {}
    for i in sorted_list:
        dict_.update({i: sorted_list.index(i)})
    
    output_list = []
    for j in input_list:
        output_list.append(dict_[j] + 1)

    return output_list
# %%
"""
Alternate 0s and 1s: Longest substring.

You are given a list X, which is a sequence composed exclusively of 0s and 1s. 
The task is to compute the length of longest subsequence within this array that alrenates between 0 and 1.

Input: [0, 1, 0, 1, 0]
Output: 5

Input: [0, 0, 1, 0, 0, 1]
Output: 3
"""

def get_alternate_substrings(list_: List[int]):
    output_ = [0]
    ini_ = list_[0]

    for i in range(1, len(list_)):
        if list_[i] + list_[i-1] != 1:
            output_.append(i)

    if output_ == [0]:
        return list_
    else:
    
        out_ = []
        for i in output_[1:]:
            x = i-1
            y = i
            out_.append(list_[x:y])
        out_.append(list_[output_[-1]:])

        return output_, out_
# %%

# %%

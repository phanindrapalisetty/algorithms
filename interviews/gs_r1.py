#%%
"""
Problem: 
Find the first non repeating character in a word. 

Input: "racecars"; Output: "e" 
Input: "goldman"; Output: "g"
"""

from typing import List

def get_non_repeating_one(input_: str) -> str:
    len_ = len(input_)
    for i in range(0, len_):
        if input_[i] not in input_[:i] + input_[i+1:]:
            return input_[i]
    else: 
        return ""

print(get_non_repeating_one("racecars"))

def get_non_repeating_two(input_: str) -> str:
    len_ = len(input_)
    dict_ = {}
    for i in input_:
        if i in dict_:
            dict_.update({i: dict_[i]+1})
        else:
            dict_.update({i: 1})
    print(dict_)
    for key_, values_ in dict_.items():
        if values_ == 1:
            return key_
        
print(get_non_repeating_two("racecars"))
# %%
"""
Problem:
Given array of students and marks find the student with best average marks.

Input:
[{"John": "89"}, {"Charlie": "100"}, {"Sam": "50"}, {"Charlie": "62"}]
Output: John
"""

input_ = [
    ["John", "89"], 
    ["Charlie", "100"], 
    ["Sam", "50"], 
    ["Charlie", "62"]
]

def get_max_average_values_one(input_):
    dict_ = {}

    for i in input_:
        if i[0] in dict_:
            dict_[i[0]].append(int(i[1]))
        else:
            dict_.update({i[0]: [int(i[1])]})

    for i in dict_:
        dict_.update({i: sum(dict_[i])/len(dict_[i])})

    averages =[] 

    for i in dict_:
        averages.append(dict_[i])
    
    return max(averages)

def get_max_average_values_two(input_):
    dict_ = {}

    for i in input_:
        if i[0] in dict_:
            dict_[i[0]].append(int(i[1]))
        else:
            dict_.update({i[0]: [int(i[1])]})
    print(dict_)
    
    averages = {name: sum(values)/len(values) for name, values in dict_.items()}
    return max(averages.values())

print(get_max_average_values_two(input_))
# %%

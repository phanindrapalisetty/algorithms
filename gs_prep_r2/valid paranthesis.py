#%%
def get_valid_paranthesis(string: str): 
    map_dict = {
        ")": "(",
        "]": "[",
        "}": "{"
    }
    arr_ = []
    index_start = 0
    max_length = 0 
    for index, i in string.enumerate():
        index_end = index
        if i in map_dict.values():
            arr_.append(i)
        if i in map_dict.keys():
            if not arr_ or arr_[-1] != map_dict[i]:
                index_start = index_end+1 
                return False 
    return True 

input_ = "{}[]()"

print(get_valid_paranthesis(input_))
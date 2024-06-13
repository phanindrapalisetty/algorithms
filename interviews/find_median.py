#%%
"""
What is a Median? 
    1. When sorted, it is the mid-value
        a. If a list sorted is the then it is mid-value if odd number, 
            else average of both mid values 
        b. Mathematical formula for frequencied data
        c. Mathematical formula for grouped data
"""


#%%
import random 
# list_ = [random.randint(1, 1000000) for _ in range(10)]
list_ = [633133, 628334, 609212, 359973, 864776, 354437, 798932, 48907, 241121, 41675]
# %%
"""
1. This method is based on sorting of the list
2. sort() method uses timsort, which is derived from merge sort and insertion sort
3. It has a time complexity of O(nlogn) 
    -- How?? Need to find. 
"""
def get_median_small_dataset(number_list: list[int]) -> float:
    number_list.sort()
    length = len(number_list)

    if length%2 != 0:
        return number_list[length//2]
    else:
        return (number_list[length//2 - 1] + number_list[length//2])/2

print(get_median_small_dataset([5, 2, 8, 10, 3, 15, 7, 1, 9, 6, 12, 4, 11, 14]))
# %%
"""
Next question: Can we optimise this for a larger dataset?

The best time complexity it can have is O(n)

Approach:
1. Something similar to quicksort algorithm 
2. Find the kth smallest element in the list and return it will be the median, 
    where in `k` is `n//2` element. 
3. Function `kth_smallest` recursively partitions and selects the pivot until the kth smallest element is found. 
"""

def partition(lst, low, high):
    pivot = lst[high]
    i = low - 1
    for j in range(low, high):
        if lst[j] <= pivot:
            i += 1
            lst[i], lst[j] = lst[j], lst[i]
    lst[i + 1], lst[high] = lst[high], lst[i + 1]
    return i + 1

def kth_smallest(lst, low, high, k):
    if low <= high:
        pivot_index = partition(lst, low, high)
        if pivot_index == k:
            return lst[pivot_index]
        elif pivot_index < k:
            return kth_smallest(lst, pivot_index + 1, high, k)
        else:
            return kth_smallest(lst, low, pivot_index - 1, k)

def find_median(lst):
    n = len(lst)
    if n % 2 == 0:
        median1 = kth_smallest(lst, 0, n - 1, n // 2 - 1)
        median2 = kth_smallest(lst, 0, n - 1, n // 2)
        return (median1 + median2) / 2
    else:
        return kth_smallest(lst, 0, n - 1, n // 2)
# %%

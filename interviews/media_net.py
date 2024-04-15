#%%
"""
Given an array of number, find which two numbers give the maximum product

Input: arr[] = {1, 4, 3, 6, 7, 0} 
Output: [6,7]

Input: arr[] = {-1, -3, -4, 2, 0, -5} 
Output: [-4,-5]
"""
def getSortedArray(arr:list):
    return arr.sort(reverse=False)

def method_one(arr:list):
    getSortedArray(arr)
    num = len(arr)
    if arr[0]*arr[1] > arr[num-1]*arr[num-2]:
        return arr[0],arr[1]
    else:
        return arr[num-1], arr[num-2]

def method_two(arr:list):
    """Brute Force Approach"""
    len_ = len(arr)

    mul_ = arr[0]*arr[1]
    a, b = arr[0], arr[1]
    for i in range(0, len_):
        for j in range(i+1, len_):
            # print(a, b)
            some_ = arr[i]*arr[j]
            if some_ > mul_:
                a = arr[i]
                b = arr[j]
                mul_ = some_ 
    return a, b
# %%
"""
Given N intervals, where each interval denotes startTime and endTime,
merge overlapping intervals and return a list of overlapping intervals
in sorted order of their startTime. 

Input: [[1,3], [2,6], [8, 10], [15,18]]
Output: [[1,6], [8, 10], [15,18]]
"""

def get_merged_stack(arr:list):
    arr.sort(reverse=False, key=lambda x: x[0])
    merged_stack = [arr[0]]

    for i in arr[1:]:
        if merged_stack[-1][0] <= i[0] and i[0] <= merged_stack[-1][1]:
            merged_stack[-1][-1] = max(merged_stack[-1][-1], i[-1])
        else:
            merged_stack.append(i)
    
    return merged_stack
# %%
print(get_merged_stack([[1,3], [2,6], [8, 10], [15,18]]))
# %%
"""
Given string is a palindrome or not

Input: 'abcba' Output: True
"""

def find_palindrome_one(string_:str):
    len_ = len(string_)
    for i in range(0, len_):
        if string_[i] != string_[len_-1-i]:
            return False 
    return True

def find_palindrome_two(string_:str):
    return string_ == string_[::-1]
# %%
"""
Given a string, return the longest palindromic substring

Input: s = "babad"
Output: "bab"
Explanation: "aba" is also a valid answer.

Input: s = "cbbd"
Output: "bb"
"""

# Function to print a subString str[low..high]
def printSubStr(str, low, high):
    for i in range(low, high + 1):
        print(str[i], end="")
 
 
# This function prints the
# longest palindrome subString
# It also returns the length
# of the longest palindrome
def longestPalSubstr(str):
 
    # Get length of input String
    n = len(str)
 
    # All subStrings of length 1
    # are palindromes
    maxLength = 1
    start = 0
 
    # Nested loop to mark start
    # and end index
    for i in range(n):
        for j in range(i, n):
            flag = 1
 
            # Check palindrome
            for k in range(0, ((j - i) // 2) + 1):
                if (str[i + k] != str[j - k]):
                    flag = 0
 
            # Palindrome
            if (flag != 0 and (j - i + 1) > maxLength):
                start = i
                maxLength = j - i + 1
 
    print("Longest palindrome substring is: ", end="")
    printSubStr(str, start, start + maxLength - 1)
 
    # Return length of LPS
    return maxLength
# %%
"""
Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.
Notice that the solution set must not contain duplicate triplets.


Example 1:

Input: nums = [-1,0,1,2,-1,-4]
Output: [[-1,-1,2],[-1,0,1]]
Explanation: 
nums[0] + nums[1] + nums[2] = (-1) + 0 + 1 = 0.
nums[1] + nums[2] + nums[4] = 0 + 1 + (-1) = 0.
nums[0] + nums[3] + nums[4] = (-1) + 2 + (-1) = 0.
The distinct triplets are [-1,0,1] and [-1,-1,2].
Notice that the order of the output and the order of the triplets does not matter.
Example 2:

Input: nums = [0,1,1]
Output: []
Explanation: The only possible triplet does not sum up to 0.
Example 3:

Input: nums = [0,0,0]
Output: [[0,0,0]]
Explanation: The only possible triplet sums up to 0.

Approach:

"""


def threeSum_one(self, nums: list[int]) -> list[list[int]]:
    nums.sort()
    arr = []
    for i in range(len(nums)):
        if (i>0 and ( nums[i] == nums[i-1])): continue
        st = i+1
        en = len(nums) - 1
        while(st < en):
            ans = nums[i]
            ans +=  + nums[en] + nums[st]
            if ans == 0:
                arr.append([nums[i],nums[st],nums[en]])
                st+=1
                en-=1
                while(st<en and (nums[st] == nums[st-1])):
                    st+=1
                while(st<en and (nums[en] == nums[en+1])):
                    en-=1
            elif ans < 0:
                st+=1
            else:
                en-=1
    return arr

def threeSum_one_two(self, nums: list[int]) -> list[list[int]]:
    ans=set()
    nums.sort()
    n=len(nums)
    for i in range(n-2):
        j=i+1
        k=n-1
        while j<k:
            temp=nums[i]+nums[j]+nums[k]
            if temp==0:
                ans.add((nums[i],nums[j],nums[k]))
                j+=1
            elif temp>0:
                k-=1
            else:
                j+=1
    return ans


def threeSum_two(self, nums: list[int]) -> list[list[int]]:

	res = set()

	#1. Split nums into three lists: negative numbers, positive numbers, and zeros
	n, p, z = [], [], []
	for num in nums:
		if num > 0:
			p.append(num)
		elif num < 0: 
			n.append(num)
		else:
			z.append(num)

	#2. Create a separate set for negatives and positives for O(1) look-up times
	N, P = set(n), set(p)

	#3. If there is at least 1 zero in the list, add all cases where -num exists in N and num exists in P
	#   i.e. (-3, 0, 3) = 0
	if z:
		for num in P:
			if -1*num in N:
				res.add((-1*num, 0, num))

	#3. If there are at least 3 zeros in the list then also include (0, 0, 0) = 0
	if len(z) >= 3:
		res.add((0,0,0))

	#4. For all pairs of negative numbers (-3, -1), check to see if their complement (4)
	#   exists in the positive number set
	for i in range(len(n)):
		for j in range(i+1,len(n)):
			target = -1*(n[i]+n[j])
			if target in P:
				res.add(tuple(sorted([n[i],n[j],target])))

	#5. For all pairs of positive numbers (1, 1), check to see if their complement (-2)
	#   exists in the negative number set
	for i in range(len(p)):
		for j in range(i+1,len(p)):
			target = -1*(p[i]+p[j])
			if target in N:
				res.add(tuple(sorted([p[i],p[j],target])))

	return res

#%%
"""
Palindrome with one character removed
"""

def isPalindrome(string: str, low: int, high: int) -> bool:
    while low < high:
        if string[low] != string[high]:
            return False
        low += 1
        high -= 1
    return True
 
# This method returns -1 if it 
# is not possible to make string
# a palindrome. It returns -2 if 
# string is already a palindrome.
# Otherwise it returns index of
# character whose removal can
# make the whole string palindrome.
def possiblepalinByRemovingOneChar(string: str) -> int:
 
    # Initialize low and right by
    # both the ends of the string
    low = 0
    high = len(string) - 1
 
    # loop until low and high cross each other
    while low < high:
 
        # If both characters are equal then
        # move both pointer towards end
        if string[low] == string[high]:
            low += 1
            high -= 1
        else:
 
            # If removing str[low] makes the whole string palindrome.
            # We basically check if substring str[low+1..high] is
            # palindrome or not.
            if isPalindrome(string, low + 1, high):
                return low
 
            # If removing str[high] makes the whole string palindrome
            # We basically check if substring str[low+1..high] is
            # palindrome or not
            if isPalindrome(string, low, high - 1):
                return high
            return -1
 
    # We reach here when complete string will be palindrome
    # if complete string is palindrome then return mid character
    return -2
# S = S[:Index] + S[Index + 1:]

def validPalindrome_two(self, s: str) -> bool:
            p1=0
            p2=len(s)-1
            while p1<=p2:
                if s[p1]!=s[p2]:
                    string1=s[:p1]+s[p1+1:]
                    string2=s[:p2]+s[p2+1:]
                    return string1==string1[::-1] or string2==string2[::-1]
                p1+=1
                p2-=1
            return True

"""
Select c_id, start_date, end_date, 
        end_date - lead (start_date) 
        over (order by start_date) 
               + 1 as 'no_of_days' 
                   from contest;

EXTRACT(DAY FROM MAX(joindate)-MIN(joindate)) AS DateDifference
"""


def is_palindrome_with_2_removals(string):
    # Helper function to check if a string is palindrome
    def is_palindrome(s):
        return s == s[::-1]

    # If the string is already a palindrome, return True
    if is_palindrome(string):
        return True

    # Try removing at most two characters and check if the resulting string is palindrome
    for i in range(len(string)):
        # Create a new string with character at index i removed
        temp_string = string[:i] + string[i + 1:]
        # Check if the modified string is a palindrome
        if is_palindrome(temp_string):
            return True

    # Try removing two characters 
    for i in range(len(string)):
        for j in range(i + 1, len(string)):
            # Create a new string with characters at index i and j removed
            temp_string = string[:i] + string[i + 1:j] + string[j + 1:]
            # Check if the modified string is a palindrome
            if is_palindrome(temp_string):
                return True

    # If no palindrome found after at most two removals, return False
    return False





def merge(self, nums1, m, nums2, n):
        """
        :type nums1: List[int]
        :type m: int
        :type nums2: List[int]
        :type n: int
        :rtype: None Do not return anything, modify nums1 in-place instead.
        """
        if n == 0 :return
        len1 = len(nums1)
        end_idx = len1-1
        while n > 0 and m > 0 :
            if nums2[n-1] >= nums1[m-1]:
                nums1[end_idx] = nums2[n-1]
                n-=1
            else:
                nums1[end_idx] = nums1[m-1]
                m-=1
            end_idx-=1
        while n > 0:
            nums1[end_idx] = nums2[n-1]
            n-=1
            end_idx-=1


#%%
def get_rev_number(num_:int) -> int:
    rev = 0
    while num_ > 0:
        rem = num_ % 10
        rev = rev * 10 + rem
        num_ //= 10
    return rev 

def get_reversed_number_one(num: int) -> int: 
    abs_num = abs(num)
    if num < 0:
        flag = -1*get_rev_number(abs_num)
    elif num > 0: 
        flag = get_rev_number(abs_num)
    else:
        flag = 0 

    
    return flag 
# %%
def get_reversed_number_one(num: int) -> int: 
    str_num = str(num) if num >= 0 else str(num)[1::]
    if num >= 0:
        return int(str_num[::-1])
    if num < 0:
        return -1*int(str_num[::-1])
# %%
#%%
class Square:
    def draw(self):
        print(f'Inside Square::draw()')
    def resize(self):
        print(f'Inside Square::resize()')
class Circle:
    def draw(self):
        print(f'Inside Circle::draw()')
    def resize(self):
        print(f'Inside Circle::resize()')
class ShapeManager:
    def _init_(self, shapes):
        self._shapes = shapes
    def manage(self):
        for shape in self._shapes:
            shape.draw()
            shape. resize()
if __name__ == '__main__':
    shapes = [Square(), Circle()]
    shape_manager = ShapeManager (shapes)
    shape_manager.manage()
# %%
document = (20001, 'Petry', (101, 102), ['List', 'Some'])
# %%
document[-1].append('Poerty')
# %%
A = [6, 4, 7, 10, 11]
B = [2, 4, 6, 8, 10]
C = [x for x in A if x in B]
print(C)
# %%
word1 = 'abc'
word2 = 'pqrq'
def mergeAlternately(word1: str, word2: str) -> str:
    len1 = len(word1)
    len2 = len(word2)
    res = ''
    i = 0
    if len1 >= len2:
        while i < len2:
            res = res + word1[i] + word2[i]
            i+=1
        res = res + word1[i::]
    else:
        while i < len1:
            res = res + word1[i] + word2[i]
            i+=1
        res = res + word2[i::]
    return res

def mergeAlternately(self, word1: str, word2: str) -> str:
    result = ""
    for i in range(0, min(len(word1), len(word2))):
        result += word1[i]
        result += word2[i]
    if len(word1) > len(word2):
        result += word1[len(word2):]
    elif len(word1) < len(word2):
        result += word2[len(word1):]
    return result
# %%
word2 = 'ABABAB'
word1 = 'ABAB'
def gcdOfStrings(str1: str, str2: str) -> str:
    if str1 + str2 != str2 + str1:
        return ''

    a = len(str1)
    b = len(str2)

    #Finding gcd
    while b != 0:
        a, b = b, a % b
    return str2[:a]

print(gcdOfStrings(word1, word2))
# %%
candies = [2,3,5,1,3]
extraCandies = 3
def kidsWithCandies(candies, extraCandies):
        max_ = candies[0]
        res = ['true']
        for i in range(1, len(candies)):
            if candies[i] + extraCandies > max_:
                max_ = candies[i]
                res.append('true')
            else:
                res.append('false')
        return res
# %%
def find_maximum(numbers):
    if not numbers:
        return None  # Return None if the list is empty

    left, right = 0, len(numbers) - 1

    while left < right:
        mid = (left + right) // 2
        if numbers[mid] < numbers[mid + 1]:
            left = mid + 1
        else:
            right = mid

    return numbers[left]

# Example usage
numbers = [1, 3, 5, 7, 9, 8, 6, 4, 2]
maximum = find_maximum(numbers)
print("Maximum:", maximum)  # Output: 9

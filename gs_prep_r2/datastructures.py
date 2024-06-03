class MedianFinder:

    def __init__(self):
        self.minHeap = []
        heapq.heapify(self.minHeap)
        self.maxHeap = []
        heapq.heapify(self.maxHeap)

    def addNum(self, num: int) -> None:
        if len(self.minHeap) > 0 and num > -self.minHeap[0]:
            heapq.heappush(self.maxHeap, num)
            if len(self.maxHeap) > len(self.minHeap):
                item = heapq.heappop(self.maxHeap)
                heapq.heappush(self.minHeap, -item)
        else:
            heapq.heappush(self.minHeap, -num)
            if len(self.minHeap) - len(self.maxHeap) > 1:
                item = heapq.heappop(self.minHeap)
                heapq.heappush(self.maxHeap, -item)

    def findMedian(self) -> float:
        if len(self.minHeap) == len(self.maxHeap):
            return (-self.minHeap[0] + self.maxHeap[0]) / 2
        else:
            return -self.minHeap[0]


class MyHashMap:
    def __init__(self):
        self.keys = []
        self.values = []

    def put(self, key: int, value: int) -> None:
        try:
            pos = self.keys.index(key)
            self.values[pos] = value
        except ValueError:
            self.keys.append(key)
            self.values.append(value)

    def get(self, key: int) -> int:
        try:
            pos = self.keys.index(key)
            return self.values[pos]
        except ValueError:
            return -1

    def remove(self, key: int) -> None:
        if key in self.keys:
            pos = self.keys.index(key)
            self.keys[pos] = None

#Validate Binary Tree
class Solution:
    def helper(self, root, prev, result):
        if root is None: return
        self.helper(root.left, prev, result)
        if prev[0] and root.val <= prev[0].val:
            result[0] = False
            return
        prev[0] = root
        self.helper(root.right, prev, result)

    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        prev = [None]  
        result = [True]
        self.helper(root, prev, result)
        return result[0]

  #SumTree
  # Python3 program to implement 
# the above approach

# A binary tree node has data, 
# left child and right child
class node:

	def __init__(self, x):
	
		self.data = x
		self.left = None
		self.right = None

# A utility function to get the sum
# of values in tree with root as root 
def sum(root):

	if(root == None):
		return 0
	return (sum(root.left) +
			root.data +
			sum(root.right))

# returns 1 if sum property holds 
# for the given node and both of 
# its children 
def isSumTree(node):

	# ls, rs

	# If node is None or it's a leaf 
	# node then return true
	if(node == None or
	(node.left == None and
	node.right == None)):
		return 1

	# Get sum of nodes in left and 
	# right subtrees 
	ls = sum(node.left)
	rs = sum(node.right)

	# if the node and both of its children
	# satisfy the property return 1 else 0
	if((node.data == ls + rs) and
		isSumTree(node.left) and
		isSumTree(node.right)):
		return 1

	return 0

# Driver code
if __name__ == '__main__':

	root = node(26)
	root.left= node(10)
	root.right = node(3)
	root.left.left = node(4)
	root.left.right = node(6)
	root.right.right = node(3)
	
	if(isSumTree(root)):
		print("The given tree is a SumTree ")
	else:
		print("The given tree is not a SumTree ")

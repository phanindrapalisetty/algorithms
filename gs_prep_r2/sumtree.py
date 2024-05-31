"""
For a given binary tree, find if it's a SumTree or not. 
A SumTree is a BinaryTree where the value of a node is equal to the 
sum of nodes present in int's left subtree and right subtree

  26
  /\ 
 10 3
 /\  \ 
4  6  3
"""

#%%
"""
Class an an example tree implementation
"""

class node:
    def __init__(self, x) -> None:
        self.data = x
        self.left = None 
        self.right = None 

root = node(26)
root.left = node(10) 
root.left.left = node(4)
root.left.right = node(6)
root.right = node(3)
root.right.right = node(3)

def isSumTree(x: node) -> bool:
    if (x == None) or (x.left == None and x.right == None):
        return True 
    
    ls = sum(node.left)
    rs = sum(node.right)

    if (node.data == ls + rs) and isSumTree(node.left) and isSumTree(node.right):
        return True 
    else:
        return False 
# %%

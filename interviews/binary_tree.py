#%%

# %%
a = 19
b = 17
while b != 0:
    a, b = b, a%b 
    print(a)
# %%
"""
Print nodes when direction is given 
"""
class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

def print_tree(root, direction):
    if root is None:
        return
    
    if direction == "left_to_right":
        print("Printing tree from left to right:")
        print_left_to_right(root)
    elif direction == "right_to_left":
        print("Printing tree from right to left:")
        print_right_to_left(root)
    else:
        print("Invalid direction. Please choose 'left_to_right' or 'right_to_left'.")

def print_left_to_right(node):
    if node is None:
        return
    print(node.data, end=" ")
    print_left_to_right(node.left)
    print_left_to_right(node.right)

def print_right_to_left(node):
    if node is None:
        return
    print_right_to_left(node.right)
    print(node.data, end=" ")
    print_right_to_left(node.left)

# Example usage:
# Create a sample binary tree
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)
root.right.left = TreeNode(6)
root.right.right = TreeNode(7)

# Prompt user for direction
direction = "left_to_right"

# Print the tree according to the chosen direction
print_tree(root, direction)

# %%
"""
Print all left leaf nodes
"""
class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

def print_left_leaves(root):
    if root is None:
        return
    
    print("Left leaf nodes of the binary tree:")
    print_left_leaves_util(root)

def print_left_leaves_util(node):
    if node is None:
        return

    if node.left is not None and node.left.left is None and node.left.right is None:
        print(node.left.data, end=" ")

    print_left_leaves_util(node.left)
    print_left_leaves_util(node.right)

# Example usage:
# Create a sample binary tree
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)
root.right.right = TreeNode(6)
root.left.left.left = TreeNode(7)
root.left.left.right = TreeNode(8)

# Print the left leaf nodes
print_left_leaves(root)

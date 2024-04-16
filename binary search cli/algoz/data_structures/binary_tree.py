from algoz.data_structures.node import Node
from algoz.data_structures.queue import Queue

class BinaryTree:
    def __init__(self):
        self.root = None

    def level_order_insert(self, data):
        if self.root is None:
            self.root = Node(data)
            return

        queue = Queue()
        queue.enqueue(self.root)

        while queue.get_len():
            # pop left from the queue
            node = queue.dequeue()
            
            # if node.left is None, data is pass to node.left, then return
            if not node.left:
                node.left = Node(data)
                return
            # if node.left exists, enqueue the left child
            else:
                queue.enqueue(node.left)
            
            # if node.right is None, data is pass to node.right, then return
            if not node.right:
                node.right = Node(data)
                return
            # if node.right exists, enqueue the right child
            else:
                queue.enqueue(node.right)

    def bst_insert_recursive(self, data, root):

        if int(data) < int(root.data):
            if root.left is None:
                root.left = Node(data)
            else:
                self.bst_insert_recursive(data, root.left)

        if int(data) > int(root.data):
            if root.right is None:
                root.right = Node(data)
            else:
                self.bst_insert_recursive(data, root.right)

    def bst_insert(self, data):
        if self.root is None:
            self.root = Node(data)
        else:
            self.bst_insert_recursive(data, self.root)
    
    # build a binary tree with file
    def create_from_file(self, path):
        with open(path, "r") as a_file:
            for line in a_file:
                # remove leading and trailing white spaces from each line
                stripped_line = line.strip()
                if stripped_line:
                    # split line into words (not to be confused with strip())
                    words = stripped_line.split()
                    # insert word into the binary tree with level order insert method for every word in line
                    for word in words:
                        self.level_order_insert(word)

    # build a binary search tree with file
    def create_bst_from_file(self, path):
        with open(path, "r") as a_file:
            for line in a_file:
                # remove leading and trailing white spaces from each line
                stripped_line = line.strip()
                if stripped_line:
                    # split line into words (not to be confused with strip())
                    words = stripped_line.split()
                    # insert word into the binary search tree with insert method for every word in line
                    for word in words:
                        self.bst_insert(word)

    def in_order_print(self, root):
        if root:
            self.in_order_print(root.left)
            print(root.data)
            self.in_order_print(root.right)

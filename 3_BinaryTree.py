class BinaryTree:
    def __init__(self, data=None, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right

    def insert(self, data):
        if self.data is None:
            self.data = data
        else:
            if data < self.data:
                if self.left is None:
                    self.left = BinaryTree(data)
                else:
                    self.left.insert(data)
            elif data > self.data:
                if self.right is None:
                    self.right = BinaryTree(data)
                else:
                    self.right.insert(data)

    def inorder_traversal(self):
        result = []
        if self.left:
            result += self.left.inorder_traversal()
        result.append(self.data)
        if self.right:
            result += self.right.inorder_traversal()
        return result

    def preorder_traversal(self):
        result = [self.data]
        if self.left:
            result += self.left.preorder_traversal()
        if self.right:
            result += self.right.preorder_traversal()
        return result

    def postorder_traversal(self):
        result = []
        if self.left:
            result += self.left.postorder_traversal()
        if self.right:
            result += self.right.postorder_traversal()
        result.append(self.data)
        return result



tree = BinaryTree()
a = True
while a:
    try:
        choice = input("\nEnter 'i' to insert a node, 't' to perform traversals, or 'q' to quit : ")

        if choice == 'i':
            try:
                value = int(input("Enter the value of the node to insert: "))
                tree.insert(value)
                print(f"Sorted list of values: {tree.inorder_traversal()}")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

        elif choice == 't':
            traversal_type = input("Enter 'inorder', 'preorder', or 'postorder' for traversal: ")

            try:
                if traversal_type == 'inorder':
                    print(f"Inorder traversal: {tree.inorder_traversal()}")
                elif traversal_type == 'preorder':
                    print(f"Preorder traversal: {tree.preorder_traversal()}")
                elif traversal_type == 'postorder':
                    print(f"Postorder traversal: {tree.postorder_traversal()}")
                else:
                    print("Invalid traversal type. Please enter 'inorder', 'preorder', or 'postorder'.")
            except:
                print("Tree is empty. Please insert nodes.")

        elif choice == 'q':
            print("Exiting the program. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 'i', 't', or 'q'.")
    except:
        print("Invalid Entry")
        

        
'''

 PRE-ORDER --> root-L-R
  IN-ORDER --> L-root-R
POST-ORDER --> L-R-root

'''
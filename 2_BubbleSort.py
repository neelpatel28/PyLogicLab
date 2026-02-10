class BubbleSort:
    def __init__(self):
        self.comparisons = 0
        self.swaps1 = 0
    
    def bubble_sort(self,lst):
        self.comparisons = 0
        self.swaps1 = 0
        
        print("\nSorting the list using bubble sort...")
        #print("Original list of numbers:",lst)
        for i in range(0,len(lst)-1):
            #self.comparisons += 1
            for j in range(0,len(lst)-1-i):
                self.comparisons += 1
                if lst[j] > lst[j+1]:
                    lst[j], lst[j+1] = lst[j+1], lst[j]
                    self.swaps1 += 1
        
        return lst
    
    def display_results(self,og,sortedlst):
        print("\nOriginal list of numbers : ",og)
        print("Sorted list of numbers : ",sortedlst)
        print("Number of comparisons : ",self.comparisons)
        print("Number of swaps : ",self.swaps1)
                    
a = True
while a:
    try:
        us_ip = input("\nEnter a list of elements separated by spaces or 'exit' to quit: ")
        
        if us_ip.lower() == 'exit':
            print("Exiting the program. Goodbye!")
            break
        lst = [int(num) for num in us_ip.split()]
        og = lst.copy()
        example = BubbleSort()
        sortedlst = example.bubble_sort(lst)
        example.display_results(og, sortedlst)
        
    except:
        print("Error: Please enter a valid list of lst.")
        
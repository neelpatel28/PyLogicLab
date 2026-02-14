def InsertionSort(lst):
    for i in range(len(lst)):
        x = lst[i]
        j = i-1
        while x < lst[j] and j>=0:
          lst[j+1] = lst[j]
          j = j-1
        lst[j+1] = x
    return lst

def BinarySearch(lst,i,j,val):
    if i <= j:
        mid = (i+j)//2
        
        if lst[mid] == val:
            return mid
        
        elif lst[mid] > val:
            return BinarySearch(lst,i,mid-1,val)
        
        elif lst[mid] < val:
            return BinarySearch(lst,mid+1,j,val)
    else:
        return -1

a = True
while a:
    try:
        input_values = input("\nEnter a list of integers separated by space : ")
        lst1 = [int(x) for x in input_values.split()]

        sorted_list = InsertionSort(lst1.copy())
        print("\nSorted List :", sorted_list)
        
        b = True
        while b:
            val = int(input("\nEnter the target element to search for: "))
            i = 0
            j = len(lst1)-1
            result = BinarySearch(sorted_list,i,j,val)

            if result != -1:
                print(f"Target element {val} found at index {result}.\n")
            else:
                print("Target element not found in the list.\n")
            try:
                repeat = input("Do you want to search again? (yes/no): ").lower()
                if repeat == 'no'or repeat == "n":
                    print("Exiting the program. Goodbye!")
                    a = False
                    break
                elif repeat == "yes" or repeat == "y":
                    b = True
                
            except:
                print("Enter either 'yes' to continue or 'no' to exit.")

    except ValueError:
        print("Error: Please enter valid integer inputs.")

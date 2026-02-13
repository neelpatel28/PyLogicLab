def SelectionSort(lst):
    for i in range(len(lst)-1):
        min_ind = i
        min_val = lst[i]
        for j in range(i+1, len(lst)):
            if lst[j] < min_val:
                min_ind = j
                min_val = lst[j]
        lst[min_ind], lst[i] = lst[i], min_val
    return lst

def BinarySearch(lst, val):
    i, j = 0, len(lst) - 1
    while i <= j:
        mid = (i + j) // 2
        if lst[mid] == val:
            return mid
        elif lst[mid] > val:
            j = mid - 1
        elif lst[mid] < val:
            i = mid + 1
    return -1

a = True
while a:
    try:
        input_values = input("\nEnter a list of integers separated by space : ")
        lst1 = [int(x) for x in input_values.split()]

        sorted_list = SelectionSort(lst1.copy())
        print("\nSorted List :", sorted_list)
        
        b = True
        while b:
            c = True
            while c:
                try:
                    val = int(input("\nEnter the target element to search for: "))
                    result = BinarySearch(sorted_list, val)
                    c = False
                except:
                    print("Enter integer value")
                    c = True

            if result != -1:
                print(f"Target element {val} found at index {result}.\n")
            else:
                print("Target element not found in the list.\n")
            try:
                repeat = input("Do you want to search again? (yes/no): ")
                
                if repeat == 'no':
                    print("Exiting the program. Goodbye!")
                    a = False
                    break
                elif repeat == "yes":
                    b = True
            except:
                print("Enter either 'yes' to continue or 'no' to exit.")

    except:
        print("Error: Please enter valid integer inputs.")

def linear_search(lst, val):
    found = False
    for i in range(len(lst)):
        if lst[i] == val:
            return i
    return -1


a = True
while a:
    lst = input("\nEnter a list of elements separated by spaces : ")
    
    try:
        lst = [int(item) for item in lst.split()]
    except:
        print("Invalid input. Please enter integer values only.")
        continue
    b = True
    while b:
        val = input("\nEnter the target element to search for (or type 'quit' to exit): ")

        if val.lower() == 'quit':
            print("Exiting the program. Goodbye!\n")
            b = False
            a = False
            break

        try:
            val = int(val)
        except:
            print("Invalid input. Please enter an integer or type 'quit' to exit.")
            continue

        op = linear_search(lst, val)

        if op != -1:
            print(f"Target element {val} found at index {op}.")
        else:
            print(f"Target element {val} not found in the list.")

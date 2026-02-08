def is_palindrome(s):

    if len(s) <= 1:
        return True
    
    if s[0].upper() == s[-1].upper():
        return is_palindrome(s[1:-1])
    elif s[0].upper() != s[-1].upper():
        return False        
    
print("\nPalindrome Checking Program   \n")
a = True
while a:
    try:
        b = True
        while b:
            ch = int(input("\nEnter '1' to check palindrome or '0' to exit : "))
            if ch == 0:
                print("Program exited\n")
                a = False
                b = False
                break
                
            elif ch == 1:
                user_ip = input("Enter the string : ")    
                if is_palindrome(user_ip):
                    print(f"The string '{user_ip}' is a palindrome.")
                else:
                    print(f"The string '{user_ip}' is not a palindrome.")
            
            else:
                print("Enter valid entry!Please retry")
    except:
        print("Invalid Input! Retry")
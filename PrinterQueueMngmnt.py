class PrinterQueue:
    def __init__(self):
        self.queue = []
    
    def add_print_jobs(self,priority,job_id):
        self.queue.append((priority,job_id))
        print("Print job added successfully.")
    
    def sort_keys(self,item):
        return (item[0],item[1])
    
    def process_print_job(self):
        if not self.queue:
            print("No pending printing jobs!")
            return
        
        self.queue.sort(key=self.sort_keys, reverse = True)
        priority, job_id = self.queue.pop(0)
        print(f"Processing job : {job_id}")
        
printer1 = PrinterQueue()
print("\nPrinter Queue Management System.")
print("\nOptions:\n1. Add a print job\n2. Process print job\n3. Exit")
while True:
    try:
        choice = int(input("\nEnter your choice: "))

        if choice == 1:
            input_data = input("Enter priority level and job ID (separated by a space): ").split()
            priority, job_id = int(input_data[0]), int(input_data[1])
            printer1.add_print_jobs(priority, job_id)

        elif choice == 2:
            printer1.process_print_job()

        elif choice == 3:
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please enter a valid option.")

    except:
        print("Invalid input. Please enter a valid integer.")
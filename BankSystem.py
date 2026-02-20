import csv
import os
import hashlib
from datetime import datetime, date
from collections import defaultdict

CUSTOMERS_FILE = "customers.csv"
ACCOUNTS_FILE = "accounts.csv"
TXN_FILE = "transactions.csv"
AUDIT_FILE = "audit.csv"
LOGIN_FILE = "login_attempts.csv"

DAILY_LIMIT = 50000
MIN_BAL_CURRENT = 2000
SAVINGS_INTEREST_RATE = 0.03

def ensure_files():
    files = {
        CUSTOMERS_FILE: ["mobile","name","password_hash","blocked"],
        ACCOUNTS_FILE: ["acc_no","mobile","type","balance","active"],
        TXN_FILE: ["txn_id","acc_no","type","amount","timestamp","note"],
        AUDIT_FILE: ["event","details","timestamp"],
        LOGIN_FILE: ["mobile","failed_attempts","last_attempt"]
    }
    for f, headers in files.items():
        if not os.path.exists(f):
            with open(f, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(headers)

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def read_csv(file):
    with open(file, newline="") as f:
        return list(csv.DictReader(f))

def write_csv(file, rows, headers):
    with open(file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

def log_audit(event, details):
    with open(AUDIT_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([event, details, datetime.now()])

def generate_acc_no():
    return "AC" + datetime.now().strftime("%H%M%S%f")

def create_customer():
    mobile = input("Mobile: ")
    customers = read_csv(CUSTOMERS_FILE)
    if any(c["mobile"] == mobile for c in customers):
        print("Customer already exists")
        return
    name = input("Name: ")
    pwd = input("Password: ")
    with open(CUSTOMERS_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([mobile, name, hash_password(pwd), "no"])
    with open(LOGIN_FILE, "a", newline="") as f:
        csv.writer(f).writerow([mobile, 0, ""])
    log_audit("NEW_CUSTOMER", mobile)
    print("Customer created")

def login():
    mobile = input("Mobile: ")
    pwd = input("Password: ")
    customers = read_csv(CUSTOMERS_FILE)
    login_data = read_csv(LOGIN_FILE)
    cust = next((c for c in customers if c["mobile"] == mobile), None)
    if not cust or cust["blocked"] == "yes":
        print("Blocked or invalid")
        return None
    rec = next(l for l in login_data if l["mobile"] == mobile)
    if cust["password_hash"] != hash_password(pwd):
        rec["failed_attempts"] = str(int(rec["failed_attempts"]) + 1)
        if int(rec["failed_attempts"]) >= 3:
            cust["blocked"] = "yes"
            print("Account blocked")
        write_csv(LOGIN_FILE, login_data, login_data[0].keys())
        write_csv(CUSTOMERS_FILE, customers, customers[0].keys())
        return None
    rec["failed_attempts"] = "0"
    write_csv(LOGIN_FILE, login_data, login_data[0].keys())
    print("Login successful")
    return mobile

def open_account(mobile, acc_type):
    accs = read_csv(ACCOUNTS_FILE)
    if any(a["mobile"] == mobile and a["type"] == acc_type and a["active"] == "yes" for a in accs):
        print("Already has this account type")
        return
    acc_no = generate_acc_no()
    with open(ACCOUNTS_FILE, "a", newline="") as f:
        csv.writer(f).writerow([acc_no, mobile, acc_type, 0, "yes"])
    log_audit("OPEN_ACCOUNT", f"{mobile}-{acc_type}")
    print("Account created:", acc_no)

def record_txn(acc_no, ttype, amount, note=""):
    with open(TXN_FILE, "a", newline="") as f:
        csv.writer(f).writerow([generate_acc_no(), acc_no, ttype, amount, datetime.now(), note])

def get_daily_withdrawal(acc_no):
    txns = read_csv(TXN_FILE)
    today = str(date.today())
    return sum(float(t["amount"]) for t in txns if t["acc_no"] == acc_no and t["type"] == "withdraw" and today in t["timestamp"])

def transfer(mobile):
    accs = read_csv(ACCOUNTS_FILE)
    src = input("From Acc No: ")
    dst = input("To Acc No: ")
    amt = float(input("Amount: "))
    a1 = next(a for a in accs if a["acc_no"] == src and a["mobile"] == mobile and a["active"] == "yes")
    a2 = next(a for a in accs if a["acc_no"] == dst and a["active"] == "yes")
    if float(a1["balance"]) < amt:
        print("Insufficient funds")
        return
    if get_daily_withdrawal(src) + amt > DAILY_LIMIT:
        print("Daily limit exceeded")
        return
    a1["balance"] = str(float(a1["balance"]) - amt)
    a2["balance"] = str(float(a2["balance"]) + amt)
    write_csv(ACCOUNTS_FILE, accs, accs[0].keys())
    record_txn(src, "transfer_out", amt, dst)
    record_txn(dst, "transfer_in", amt, src)
    log_audit("TRANSFER", f"{src}->{dst}:{amt}")
    print("Transfer successful")

def close_account(mobile):
    accs = read_csv(ACCOUNTS_FILE)
    acc_no = input("Account to close: ")
    acc = next(a for a in accs if a["acc_no"] == acc_no and a["mobile"] == mobile)
    if float(acc["balance"]) != 0:
        print("Balance must be zero")
        return
    acc["active"] = "no"
    write_csv(ACCOUNTS_FILE, accs, accs[0].keys())
    log_audit("CLOSE_ACCOUNT", acc_no)
    print("Account closed")

def monthly_statement(mobile):
    month = input("YYYY-MM: ")
    txns = read_csv(TXN_FILE)
    accs = read_csv(ACCOUNTS_FILE)
    user_accs = [a["acc_no"] for a in accs if a["mobile"] == mobile]
    print("\n       STATEMENT      ")
    for t in txns:
        if t["acc_no"] in user_accs and month in t["timestamp"]:
            print(t)

def main():
    ensure_files()
    while True:
        print("\n1 Register\n2 Login\n3 Exit")
        ch = input("Choice: ")
        if ch == "1":
            create_customer()
        elif ch == "2":
            mobile = login()
            if not mobile:
                continue
            while True:
                print("\n1 Open Savings\n2 Open Current\n3 Transfer\n4 Statement\n5 Close Account\n6 Logout")
                c = input("Choice: ")
                if c == "1":
                    open_account(mobile, "savings")
                elif c == "2":
                    open_account(mobile, "current")
                elif c == "3":
                    transfer(mobile)
                elif c == "4":
                    monthly_statement(mobile)
                elif c == "5":
                    close_account(mobile)
                elif c == "6":
                    break
        else:
            break

if __name__ == "__main__":
    main()
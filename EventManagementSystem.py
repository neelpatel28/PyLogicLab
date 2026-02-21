import csv, os, hashlib, uuid, qrcode
from datetime import datetime, date

USERS_FILE = "users.csv"
EVENTS_FILE = "events.csv"
PASSES_FILE = "passes.csv"
ENTRIES_FILE = "entries.csv"
AUDIT_FILE = "audit.csv"
LOGIN_FILE = "login_attempts.csv"
VIOLATIONS_FILE = "violations.csv"

MAX_DAILY_DEFAULT = 3
LOCK_VIOLATIONS = 3
MAX_TRANSFERS = 1

def ensure_files():
    files = {
        USERS_FILE: ["user_id","name","mobile","role","password_hash","blocked","active"],
        EVENTS_FILE: ["event_id","name","start_date","end_date","daily_limit","capacity","transfer_allowed","active"],
        PASSES_FILE: ["pass_id","event_id","owner_user_id","token","transfers_used","first_used_at","active","issued_at"],
        ENTRIES_FILE: ["entry_id","event_id","pass_id","user_id","action","timestamp"],
        AUDIT_FILE: ["event","details","timestamp"],
        LOGIN_FILE: ["mobile","failed_attempts","last_attempt"],
        VIOLATIONS_FILE: ["user_id","count"]
    }
    for f, headers in files.items():
        if not os.path.exists(f):
            with open(f, "w", newline="") as file:
                csv.writer(file).writerow(headers)

def read_csv(file):
    with open(file, newline="") as f:
        return list(csv.DictReader(f))

def write_csv(file, rows, headers):
    with open(file, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def log_audit(event, details):
    with open(AUDIT_FILE, "a", newline="") as f:
        csv.writer(f).writerow([event, details, datetime.now().isoformat()])

def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"

def get_violation(users, uid):
    rows = read_csv(VIOLATIONS_FILE)
    r = next((x for x in rows if x["user_id"] == uid), None)
    if not r:
        rows.append({"user_id": uid, "count": "0"})
        write_csv(VIOLATIONS_FILE, rows, rows[0].keys())
        return 0
    return int(r["count"])

def inc_violation(users, uid):
    rows = read_csv(VIOLATIONS_FILE)
    r = next((x for x in rows if x["user_id"] == uid), None)
    if not r:
        rows.append({"user_id": uid, "count": "1"})
        write_csv(VIOLATIONS_FILE, rows, rows[0].keys())
        return 1
    r["count"] = str(int(r["count"]) + 1)
    write_csv(VIOLATIONS_FILE, rows, rows[0].keys())
    if int(r["count"]) >= LOCK_VIOLATIONS:
        u = next((x for x in users if x["user_id"] == uid), None)
        if u:
            u["blocked"] = "yes"
            write_csv(USERS_FILE, users, users[0].keys())
            log_audit("USER_LOCKED", uid)
    return int(r["count"])

def register(role):
    name = input("Name: ").strip()
    mobile = input("Mobile: ").strip()
    pwd = input("Password: ").strip()
    users = read_csv(USERS_FILE)
    if any(u["mobile"] == mobile and u["active"] == "yes" for u in users):
        print("User exists")
        return
    uid = new_id("USR")
    with open(USERS_FILE, "a", newline="") as f:
        csv.writer(f).writerow([uid, name, mobile, role, hash_password(pwd), "no", "yes"])
    with open(LOGIN_FILE, "a", newline="") as f:
        csv.writer(f).writerow([mobile, 0, ""])
    with open(VIOLATIONS_FILE, "a", newline="") as f:
        csv.writer(f).writerow([uid, 0])
    log_audit("USER_REGISTERED", f"{uid}:{role}")
    print("Registered:", uid)

def login():
    mobile = input("Mobile: ").strip()
    pwd = input("Password: ").strip()
    users = read_csv(USERS_FILE)
    attempts = read_csv(LOGIN_FILE)
    u = next((x for x in users if x["mobile"] == mobile and x["active"] == "yes"), None)
    if not u or u["blocked"] == "yes":
        print("Blocked or invalid")
        return None
    rec = next((a for a in attempts if a["mobile"] == mobile), None)
    if not rec:
        attempts.append({"mobile": mobile, "failed_attempts": "0", "last_attempt": ""})
        rec = attempts[-1]
    if u["password_hash"] != hash_password(pwd):
        rec["failed_attempts"] = str(int(rec["failed_attempts"]) + 1)
        rec["last_attempt"] = datetime.now().isoformat()
        if int(rec["failed_attempts"]) >= 3:
            u["blocked"] = "yes"
            log_audit("USER_LOCKED_LOGIN", u["user_id"])
            print("User locked")
        write_csv(LOGIN_FILE, attempts, attempts[0].keys())
        write_csv(USERS_FILE, users, users[0].keys())
        return None
    rec["failed_attempts"] = "0"
    rec["last_attempt"] = datetime.now().isoformat()
    write_csv(LOGIN_FILE, attempts, attempts[0].keys())
    print("Login ok")
    return u

def create_event():
    name = input("Event name: ").strip()
    sd = input("Start date YYYY-MM-DD: ").strip()
    ed = input("End date YYYY-MM-DD: ").strip()
    try:
        dl = int(input("Daily entry limit: ").strip())
        cap = int(input("Capacity: ").strip())
    except:
        print("Invalid numbers")
        return
    ta = input("Transfer allowed (yes/no): ").strip().lower()
    eid = new_id("EVT")
    with open(EVENTS_FILE, "a", newline="") as f:
        csv.writer(f).writerow([eid, name, sd, ed, dl, cap, ta, "yes"])
    log_audit("EVENT_CREATED", eid)
    print("Event created:", eid)

def close_event():
    eid = input("Event ID to close: ").strip()
    events = read_csv(EVENTS_FILE)
    ev = next((e for e in events if e["event_id"] == eid), None)
    if not ev:
        print("Invalid event")
        return
    ev["active"] = "no"
    write_csv(EVENTS_FILE, events, events[0].keys())
    log_audit("EVENT_CLOSED", eid)
    print("Event closed")

def list_events():
    for e in read_csv(EVENTS_FILE):
        print(e)

def issue_pass(user):
    eid = input("Event ID: ").strip()
    events = read_csv(EVENTS_FILE)
    passes = read_csv(PASSES_FILE)
    ev = next((e for e in events if e["event_id"] == eid and e["active"] == "yes"), None)
    if not ev:
        print("Invalid or closed event")
        return
    if any(p["event_id"] == eid and p["owner_user_id"] == user["user_id"] and p["active"] == "yes" for p in passes):
        print("Already has pass for this event")
        return
    pid = new_id("PAS")
    token = uuid.uuid4().hex
    os.makedirs("qrcodes", exist_ok=True)
    qrcode.make(f"{pid}:{token}").save(f"qrcodes/{pid}.png")
    with open(PASSES_FILE, "a", newline="") as f:
        csv.writer(f).writerow([pid, eid, user["user_id"], token, 0, "", "yes", datetime.now().isoformat()])
    log_audit("PASS_ISSUED", pid)
    print("Pass issued:", pid, "QR saved in qrcodes/")

def current_inside_state(pass_id):
    entries = read_csv(ENTRIES_FILE)
    last = None
    for e in entries:
        if e["pass_id"] == pass_id:
            last = e
    return last and last["action"] == "IN"

def today_entries_for_pass(pass_id):
    entries = read_csv(ENTRIES_FILE)
    today = str(date.today())
    return [e for e in entries if e["pass_id"] == pass_id and e["action"] == "IN" and today in e["timestamp"]]

def current_inside_count(event_id):
    entries = read_csv(ENTRIES_FILE)
    inside = {}
    for e in entries:
        if e["event_id"] == event_id:
            inside[e["pass_id"]] = e["action"]
    return sum(1 for v in inside.values() if v == "IN")

def enter_exit(user):
    pid = input("Pass ID: ").strip()
    token = input("Token from QR: ").strip()
    action = input("IN or OUT: ").strip().upper()
    users = read_csv(USERS_FILE)
    passes = read_csv(PASSES_FILE)
    events = read_csv(EVENTS_FILE)
    p = next((x for x in passes if x["pass_id"] == pid and x["active"] == "yes"), None)
    if not p or p["token"] != token:
        cnt = inc_violation(users, user["user_id"])
        print("Invalid pass/token. Violations:", cnt)
        return
    ev = next((e for e in events if e["event_id"] == p["event_id"]), None)
    if not ev or ev["active"] != "yes":
        print("Event closed")
        return
    today = date.today().isoformat()
    if not (ev["start_date"] <= today <= ev["end_date"]):
        print("Event not active today")
        return
    if action == "IN":
        if current_inside_state(pid):
            cnt = inc_violation(users, user["user_id"])
            print("Already inside. Violations:", cnt)
            return
        daily_limit = int(ev["daily_limit"]) if ev["daily_limit"] else MAX_DAILY_DEFAULT
        if len(today_entries_for_pass(pid)) >= daily_limit:
            cnt = inc_violation(users, user["user_id"])
            print("Daily entry limit exceeded. Violations:", cnt)
            return
        if current_inside_count(ev["event_id"]) >= int(ev["capacity"]):
            print("Event at capacity")
            return
        with open(ENTRIES_FILE, "a", newline="") as f:
            csv.writer(f).writerow([new_id("EN"), ev["event_id"], pid, user["user_id"], "IN", datetime.now().isoformat()])
        if not p["first_used_at"]:
            p["first_used_at"] = datetime.now().isoformat()
            write_csv(PASSES_FILE, passes, passes[0].keys())
        log_audit("ENTRY_IN", pid)
        print("Entry recorded")
    elif action == "OUT":
        if not current_inside_state(pid):
            cnt = inc_violation(users, user["user_id"])
            print("Not inside. Violations:", cnt)
            return
        with open(ENTRIES_FILE, "a", newline="") as f:
            csv.writer(f).writerow([new_id("EX"), ev["event_id"], pid, user["user_id"], "OUT", datetime.now().isoformat()])
        log_audit("ENTRY_OUT", pid)
        print("Exit recorded")
    else:
        print("Invalid action")

def transfer_pass(user):
    pid = input("Pass ID: ").strip()
    to_mobile = input("Transfer to mobile: ").strip()
    users = read_csv(USERS_FILE)
    passes = read_csv(PASSES_FILE)
    events = read_csv(EVENTS_FILE)
    p = next((x for x in passes if x["pass_id"] == pid and x["owner_user_id"] == user["user_id"] and x["active"] == "yes"), None)
    if not p:
        print("Invalid pass")
        return
    ev = next((e for e in events if e["event_id"] == p["event_id"]), None)
    if not ev or ev["transfer_allowed"] != "yes":
        print("Transfer not allowed")
        return
    if p["first_used_at"]:
        print("Cannot transfer after first use")
        return
    if int(p["transfers_used"]) >= MAX_TRANSFERS:
        print("Transfer limit reached")
        return
    to_user = next((u for u in users if u["mobile"] == to_mobile and u["active"] == "yes"), None)
    if not to_user:
        print("Invalid target user")
        return
    if any(x["event_id"] == p["event_id"] and x["owner_user_id"] == to_user["user_id"] and x["active"] == "yes" for x in passes):
        print("Target already has a pass for this event")
        return
    p["owner_user_id"] = to_user["user_id"]
    p["transfers_used"] = str(int(p["transfers_used"]) + 1)
    write_csv(PASSES_FILE, passes, passes[0].keys())
    log_audit("PASS_TRANSFER", f"{pid} to {to_user['user_id']}")
    print("Transferred")

def monthly_report():
    month = input("YYYY-MM: ").strip()
    entries = read_csv(ENTRIES_FILE)
    stats = {}
    for e in entries:
        if e["action"] == "IN" and month in e["timestamp"]:
            stats[e["event_id"]] = stats.get(e["event_id"], 0) + 1
    print("Monthly attendance:")
    for k,v in stats.items():
        print(k, v)

def main():
    ensure_files()
    while True:
        print("\n1 Register User\n2 Register Organizer\n3 Login\n4 Exit")
        ch = input("Choice: ").strip()
        if ch == "1":
            register("user")
        elif ch == "2":
            register("organizer")
        elif ch == "3":
            u = login()
            if not u:
                continue
            if u["role"] == "organizer":
                while True:
                    print("\n1 Create Event\n2 List Events\n3 Close Event\n4 Monthly Report\n5 Logout")
                    c = input("Choice: ").strip()
                    if c == "1": create_event()
                    elif c == "2": list_events()
                    elif c == "3": close_event()
                    elif c == "4": monthly_report()
                    elif c == "5": break
            else:
                while True:
                    print("\n1 List Events\n2 Get Pass\n3 Enter/Exit\n4 Transfer Pass\n5 Logout")
                    c = input("Choice: ").strip()
                    if c == "1": list_events()
                    elif c == "2": issue_pass(u)
                    elif c == "3": enter_exit(u)
                    elif c == "4": transfer_pass(u)
                    elif c == "5": break
        elif ch == "4":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
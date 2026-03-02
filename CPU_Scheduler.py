import heapq
import json
from dataclasses import dataclass
import sys

@dataclass
class CPU:
    name: str
    power: int

@dataclass
class Process:
    id: int
    burst_time: int
    deadline: int
    completed: bool = False

def parse_cpu_json(json_string):
    data = json.loads(json_string)

    cpus = []
    processes = []

    for c in data["CPUs"]:
        cpus.append(CPU(c["Name"], int(c["Power"])))

    for p in data["Processes"]:
        processes.append(Process(int(p["id"]), int(p["BurstTime"]), int(p["Deadline"])))

    return cpus, processes

def cpu_scheduler(cpus, processes):
    time = 0
    log = []

    while True:
        active = []
        for p in processes:
            if not p.completed and time < p.deadline:
                heapq.heappush(active, (p.deadline - time, -p.burst_time, p.id))

        if not active:
            break

        cpu = max(cpus, key=lambda c: c.power)
        _, _, pid = heapq.heappop(active)
        proc = next(p for p in processes if p.id == pid)

        proc.burst_time -= cpu.power
        log.append(f"t={time} | {cpu.name} executes Process-{proc.id} for {cpu.power}")

        if proc.burst_time <= 0:
            proc.burst_time = 0
            proc.completed = True
            log.append(f"Process-{proc.id} completed")

        time += 1

    return processes, log

def process_queries(processes, queries):
    completed = [(p.id, p.burst_time) for p in processes if p.completed]
    remaining = [(p.id, p.burst_time) for p in processes if not p.completed]

    for q in queries:
        q = q.strip().lower()

        if q == "print completed processes":
            print(f"{len(completed)}, {completed}")

        elif q == "print remaining processes":
            print(f"{len(remaining)}, {remaining}")

        elif q == "exit":
            break

json_input = """
{
  "CPUs": [
    {"Name": "Core-1", "Power": 5},
    {"Name": "Core-2", "Power": 10}
  ],
  "Processes": [
    {"id": "1", "BurstTime": "12", "Deadline": "4"},
    {"id": "2", "BurstTime": "3", "Deadline": "1"},
    {"id": "3", "BurstTime": "9", "Deadline": "5"}
  ]
}
"""

if __name__ == "__main__":
    queries = sys.argv[1:]
    cpus, processes = parse_cpu_json(json_input)
    processes, log = cpu_scheduler(cpus, processes)

    for l in log:
        print(l)

    process_queries(processes, queries)
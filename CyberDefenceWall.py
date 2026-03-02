import heapq
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import sys

@dataclass
class Firewall:
    name: str
    power: int

@dataclass
class Attack:
    id: int
    threat: int
    time_limit: int
    active: bool = True


def parse_network_xml(xml_string):
    root = ET.fromstring(xml_string)

    firewalls = []
    attacks = []

    for fw in root.findall("Firewall"):
        name = fw.find("Name").text.strip()
        power = int(fw.find("Power").text.strip())
        firewalls.append(Firewall(name, power))

    for atk in root.findall("Attack"):
        atk_id = int(atk.attrib["id"])
        threat = int(atk.find("Threat").text.strip())
        time_limit = int(atk.find("TimeLimit").text.strip())
        attacks.append(Attack(atk_id, threat, time_limit))

    return firewalls, attacks


def defend_network(firewalls, attacks):
    time = 0
    log = []

    while True:
        active_attacks = []
        for a in attacks:
            if a.active and time < a.time_limit:
                heapq.heappush(active_attacks, (a.time_limit - time, -a.threat, a.id))

        if not active_attacks:
            break

        firewall = max(firewalls, key=lambda f: f.power)
        _, _, aid = heapq.heappop(active_attacks)
        attack = next(a for a in attacks if a.id == aid)

        attack.threat -= firewall.power
        log.append(f"t={time} | {firewall.name} blocks Attack-{attack.id} for {firewall.power}")

        if attack.threat <= 0:
            attack.threat = 0
            attack.active = False
            log.append(f"Attack-{attack.id} neutralized")

        time += 1

    return attacks, log


def process_queries(attacks, queries):
    blocked = [(a.id, a.threat) for a in attacks if not a.active]
    remaining = [(a.id, a.threat) for a in attacks if a.active]

    for q in queries:
        q = q.strip().lower()

        if q == "print blocked attacks":
            print(f"{len(blocked)}, {blocked}")

        elif q == "print remaining attacks":
            print(f"{len(remaining)}, {remaining}")

        elif q == "exit":
            break


xml_input = """
<Network>
    <Firewall>
        <Name>FortiGate</Name>
        <Power>15</Power>
    </Firewall>
    <Firewall>
        <Name>PaloAlto</Name>
        <Power>5</Power>
    </Firewall>
    <Attack id="1">
        <Threat>12</Threat>
        <TimeLimit>5</TimeLimit>
    </Attack>
    <Attack id="2">
        <Threat>20</Threat>
        <TimeLimit>6</TimeLimit>
    </Attack>
</Network>
"""

if __name__ == "__main__":
    queries = sys.argv[1:]
    firewalls, attacks = parse_network_xml(xml_input)
    attacks, log = defend_network(firewalls, attacks)

    for l in log:
        print(l)

    process_queries(attacks, queries)
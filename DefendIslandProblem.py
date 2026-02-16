import heapq
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import sys

@dataclass
class Troop:
    name: str
    damage: int

@dataclass
class Ship:
    id: int
    strength: int
    time_limit: int
    alive: bool = True

def parse_island_xml(xml_string):
    root = ET.fromstring(xml_string)

    troops = []
    ships = []

    for troop_node in root.findall("Troop"):
        name = troop_node.find("Name").text.strip()
        dmg = int(troop_node.find("RateOfDamage").text.strip())
        troops.append(Troop(name, dmg))

    for ship_node in root.findall("Ship"):
        ship_id = int(ship_node.attrib["id"])
        strength = int(ship_node.find("Strength").text.strip())
        time_limit = int(ship_node.find("TimeLimit").text.strip())
        ships.append(Ship(ship_id, strength, time_limit))

    return troops, ships

# Greedy + Priority Queue Defense
def defend_island(troops, ships):
    time = 0
    log = []

    while True:
        active_ships = []
        for ship in ships:
            if ship.alive and time < ship.time_limit:
                heapq.heappush(active_ships, (ship.time_limit - time, -ship.strength, ship.id))

        if not active_ships:
            break

        troop = max(troops, key=lambda t: t.damage)
        _, _, ship_id = heapq.heappop(active_ships)
        ship = next(s for s in ships if s.id == ship_id)

        ship.strength -= troop.damage
        log.append(f"t={time} | {troop.name} attacks Ship-{ship.id} for {troop.damage}")

        if ship.strength <= 0:
            ship.strength = 0
            ship.alive = False
            log.append(f"Ship-{ship.id} destroyed")

        time += 1

    return ships, log

# CLI Query Processor
def process_queries(ships, queries):
    destroyed = [(s.id, s.strength) for s in ships if not s.alive]
    remaining = [(s.id, s.strength) for s in ships if s.alive]

    for q in queries:
        q = q.strip().lower()

        if q == "print destroyed ships":
            print(f"{len(destroyed)}, {destroyed}")

        elif q == "print remaining ships":
            print(f"{len(remaining)}, {remaining}")

        elif q == "exit":
            break


xml_input = """
<Island>
    <Troop>
        <Name>VirtualSamurai</Name>
        <RateOfDamage>20</RateOfDamage>
    </Troop>
    <Troop>
        <Name>CyberNinja</Name>
        <RateOfDamage>2</RateOfDamage>
    </Troop>
    <Troop>
        <Name>DigitalPirate</Name>
        <RateOfDamage>5</RateOfDamage>
    </Troop>
    <Ship id="1">
        <Strength>2</Strength>
        <TimeLimit>20</TimeLimit>
    </Ship>
</Island>
"""

if __name__ == "__main__":
    queries = sys.argv[1:]

    troops, ships = parse_island_xml(xml_input)
    ships, _ = defend_island(troops, ships)

    process_queries(ships, queries)

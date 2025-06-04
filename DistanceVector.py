import sys
from collections import defaultdict
import copy

def read_topology():
    """Read topology from standard input."""
    graph = defaultdict(dict)
    
    nodes = []
    # Read nodes until START
    while True:
        line = input().strip()
        if line == "START":
            break
        nodes.append(line)

    # Read initial topology until UPDATE
    while True:
        line = input().strip()
        if line == "UPDATE":
            break
        src, dest, cost = line.split()
        cost = int(cost)
        if cost != -1:
            graph[src][dest] = cost
            graph[dest][src] = cost

    # Read updates until END
    updates = []
    while True:
        line = input().strip()
        if line == "END":
            break
        src, dest, cost = line.split()
        cost = int(cost)
        updates.append((src, dest, cost))

    return graph, nodes, updates

def apply_updates(graph, updates):
    """Apply topology updates."""
    for src, dest, cost in updates:
        # Remove link if weight is unapplicable
        if cost == -1:
            if dest in graph[src]:
                del graph[src][dest]
            if src in graph[dest]:
                del graph[dest][src]
        else:
            graph[src][dest] = cost
            graph[dest][src] = cost
    
    return

def initialise_tables(nodes):
    """Initialize distance and routing tables."""

    return

def print_distance_tables(step, distance_tables, nodes):
    """Print distance tables in the specified format."""

    return

def print_routing_tables(routing_tables, nodes):
    """Print routing tables in the specified format."""

    return

def distance_vector(graph, nodes):
    """Run the Distance Vector algorithm until convergence."""

    return

def main():
    return

if __name__ == "__main__":
    main()

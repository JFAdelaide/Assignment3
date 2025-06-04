#!/usr/bin/env python3
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
        # Remove link/edge from the topology if present
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
    """Initialise distance and routing tables."""
    distance_tables = {node: {dest: float('inf') for dest in nodes} for node in nodes}
    routing_tables = {node: {dest: None for dest in nodes} for node in nodes}
    for node in nodes:
        distance_tables[node][node] = 0  # Distance to self is 0
        for neighbor, cost in graph[node].items():
            distance_tables[node][neighbor] = cost
            routing_tables[node][neighbor] = neighbor
    return distance_tables, routing_tables

def print_distance_tables(step, distance_tables, nodes):
    """Print distance tables in the specified format."""
    for node in sorted(nodes):
        print(f"\nDistance Table of router {node} at t={step}:")
        print("     ", "    ".join(sorted(nodes)))
        for dest in sorted(nodes):
            costs = [distance_tables[node][dest] for dest in sorted(nodes)]
            formatted_costs = ["INF" if cost == float('inf') else str(int(cost)) for cost in costs]
            print(f"{dest}    {'    '.join(formatted_costs)}")

def print_routing_tables(routing_tables, distance_tables, nodes):
    """Print routing tables in the specified format."""
    for node in sorted(nodes):
        print(f"\nRouting Table of router {node}:")
        for dest in sorted(nodes):
            if dest != node:
                next_hop = routing_tables[node][dest]
                cost = distance_tables[node][dest]
                if cost != float('inf'):
                    print(f"{dest},{next_hop},{int(cost)}")

def distance_vector(graph, nodes, start_step):
    """Run the Distance Vector algorithm until convergence."""
    distance_tables, routing_tables = initialise_tables(nodes)
    step = start_step
    converged = False

    while not converged:
        print_distance_tables(step, distance_tables, nodes)
        converged = True
        new_distances = copy.deepcopy(distance_tables)

        for node in nodes:
            for dest in nodes:
                if dest == node:
                    continue
                min_cost = distance_tables[node][dest]
                next_hop = routing_tables[node][dest]
                for neighbor in graph[node]:
                    if neighbor in distance_tables and dest in distance_tables[neighbor]:
                        cost = graph[node][neighbor] + distance_tables[neighbor][dest]
                        if cost < min_cost:
                            min_cost = cost
                            next_hop = neighbor
                            converged = False
                new_distances[node][dest] = min_cost
                routing_tables[node][dest] = next_hop

        distance_tables = new_distances
        step += 1

    print_routing_tables(routing_tables, distance_tables, nodes)
    return distance_tables, routing_tables, step

def main():
    # Generate graph
    global graph
    graph, nodes, updates = read_topology()
    
    # Confirm graph is input correctly
    if not graph or not nodes:
        return

    # Process initial topology
    distance_tables, routing_tables, step = distance_vector(graph, nodes, 0)

    # Apply updates and run DV again
    if updates:
        apply_updates(graph, updates)
        distance_vector(graph, nodes, step)

if __name__ == "__main__":
    main()

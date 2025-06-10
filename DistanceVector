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

def initialise_tables(nodes, graph):
    """Initialise distance and routing tables."""
    distance_tables = {node: {dest: float('inf') for dest in nodes if dest != node} for node in nodes}
    routing_tables = {node: {dest: None for dest in nodes if dest != node} for node in nodes}
    for node in nodes:
        for neighbor, cost in graph[node].items():
            if neighbor != node:
                distance_tables[node][neighbor] = cost
                routing_tables[node][neighbor] = neighbor
    return distance_tables, routing_tables

def print_distance_tables(step, distance_tables, nodes):
    """Print distance tables in the specified format."""
    for node in sorted(nodes):
        print(f"\nDistance Table of router {node} at t={step}:")
        # Print header with destinations excluding the node itself
        destinations = sorted([dest for dest in nodes if dest != node])
        print(f"     {'    '.join(destinations)}")
        # Print rows for each destination excluding the node itself
        for row_dest in destinations:
            costs = []
            for dest in destinations:
                if row_dest == dest:
                    costs.append(distance_tables[node][dest])
                else:
                    costs.append(float('inf'))
            formatted_costs = ["INF" if cost == float('inf') else str(int(cost)) for cost in costs]
            print(f"{row_dest}    {'    '.join(formatted_costs)}")

def print_routing_tables(routing_tables, distance_tables, nodes):
    """Print routing tables in the specified format."""
    for node in sorted(nodes):
        print(f"\nRouting Table of router {node}:")
        for dest in sorted(nodes):
            if dest != node:
                next_hop = routing_tables[node][dest]
                cost = distance_tables[node][dest]
                if cost != float('inf') and next_hop is not None:
                    print(f"{dest},{next_hop},{int(cost)}")

def distance_vector(graph, nodes, start_step):
    """Run the Distance Vector algorithm until convergence."""
    distance_tables, routing_tables = initialise_tables(nodes, graph)
    step = start_step
    converged = False

    # Print initial tables at step 0
    print_distance_tables(step, distance_tables, nodes)
    step += 1

    while not converged:
        converged = True
        new_distances = copy.deepcopy(distance_tables)
        new_routing = copy.deepcopy(routing_tables)

        for node in nodes:
            for dest in [d for d in nodes if d != node]:
                # Initialize with infinity to reset unreachable paths
                min_cost = float('inf')
                next_hop = None
                
                # Check direct link
                if dest in graph[node]:
                    min_cost = graph[node][dest]
                    next_hop = dest
                
                # Check paths through neighbors
                for neighbor in graph[node]:
                    if neighbor != node and dest in distance_tables[neighbor]:
                        cost = graph[node][neighbor] + distance_tables[neighbor][dest]
                        if cost < min_cost:
                            min_cost = cost
                            next_hop = neighbor
                
                # Update only if cost or next-hop has changed
                if min_cost != distance_tables[node][dest] or next_hop != routing_tables[node][dest]:
                    new_distances[node][dest] = min_cost
                    new_routing[node][dest] = next_hop
                    converged = False

        distance_tables = new_distances
        routing_tables = new_routing

        # Print tables for this step
        print_distance_tables(step, distance_tables, nodes)
        
        # Break if converged
        if converged:
            break
            
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
        # Reinitialize tables to reflect updated graph
        distance_tables, routing_tables = initialise_tables(nodes, graph)
        distance_vector(graph, nodes, step)

if __name__ == "__main__":
    main()
    
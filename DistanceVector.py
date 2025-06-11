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
    # Distance tables: {node: {neighbour: {dest: cost}}}
    distance_tables = {
        node: {
            neighbour: {dest: float('inf') for dest in nodes if dest != node}
            for neighbour in (list(graph[node].keys()) + [node])  # Include node itself
        }
        for node in nodes
    }
    # Routing tables: {node: {dest: next_hop}}
    routing_tables = {node: {dest: None for dest in nodes if dest != node} for node in nodes}

    # Initialise with direct links
    for node in nodes:
        for neighbour in graph[node]:
            if neighbour != node:
                # Direct link cost to neighbour
                distance_tables[node][neighbour][neighbour] = graph[node][neighbour]
                routing_tables[node][neighbour] = neighbour
        # Initialise node's own table with direct links
        for dest in graph[node]:
            if dest != node:
                distance_tables[node][node][dest] = graph[node][dest]

    return distance_tables, routing_tables

def print_distance_tables(step, distance_tables, nodes):
    """Print distance tables in the specified format."""
    for node in sorted(nodes):
        print(f"\nDistance Table of router {node} at t={step}:")
        # Destinations excluding the node itself
        destinations = sorted([dest for dest in nodes if dest != node])
        # Neighbors excluding the node itself
        neighbors = sorted([neighbour for neighbour in nodes if neighbour != node])
        # Print header with destinations
        print(f"     {'    '.join(destinations)}")
        # Print rows for each neighbour
        for neighbour in neighbors:
            costs = []
            for dest in destinations:
                cost = distance_tables[node][neighbour][dest]
                costs.append("INF" if cost == float('inf') else str(int(cost)))
            print(f"{neighbour}    {'    '.join(costs)}")

def print_routing_tables(routing_tables, distance_tables, nodes):
    """Print routing tables in the specified format."""
    for node in sorted(nodes):
        print(f"\nRouting Table of router {node}:")
        for dest in sorted(nodes):
            if dest != node:
                next_hop = routing_tables[node][dest]
                # Find minimum cost to dest across all neighbors
                min_cost = float('inf')
                if next_hop:
                    min_cost = min(
                        distance_tables[node][neighbour][dest]
                        for neighbour in distance_tables[node]
                        if dest in distance_tables[node][neighbour]
                    )
                if min_cost != float('inf') and next_hop is not None:
                    print(f"{dest},{next_hop},{int(min_cost)}")

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
                # Track minimum cost and next hop for routing table
                min_cost = float('inf')
                next_hop = None

                # Check direct link
                if dest in graph[node]:
                    min_cost = graph[node][dest]
                    next_hop = dest

                # Update costs via each neighbour
                for neighbour in graph[node]:
                    if neighbour != node:
                        # Cost to dest via neighbour
                        cost = graph[node][neighbour]
                        if dest in distance_tables[neighbour][neighbour]:
                            cost += distance_tables[neighbour][neighbour][dest]
                        new_distances[node][neighbour][dest] = cost

                        # Update minimum cost for routing table
                        if cost < min_cost:
                            min_cost = cost
                            next_hop = neighbour

                # Update routing table if cost or next-hop changed
                if min_cost != float('inf') and (
                    min_cost != min([distance_tables[node][n][dest] for n in distance_tables[node] if dest in distance_tables[node][n]] or float('inf'))
                    or next_hop != routing_tables[node][dest]
                ):
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
        print(f"\nAPPLYING UPDATES")
        apply_updates(graph, updates)
        # Reinitialise tables to reflect updated graph
        distance_tables, routing_tables = initialise_tables(nodes, graph)
        distance_vector(graph, nodes, step+1)

if __name__ == "__main__":
    main()

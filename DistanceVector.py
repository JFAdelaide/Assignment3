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

def apply_updates(graph, nodes, updates, distance_tables):
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

def update_distance_tables(graph, nodes, updates, distance_tables):
    """Update distance tables after topology changes without reinitialising."""
    # Track removed link costs for invalidation
    removed_links = {}
    for src, dest, cost in updates:
        if cost == -1 and dest in graph[src]:
            removed_links[(src, dest)] = graph[src][dest]
            removed_links[(dest, src)] = graph[dest][src]

    # Apply updates to direct links in distance_tables
    for src, dest, cost in updates:
        if cost == -1:
            # Remove link: set direct link costs to INF
            if dest in graph[src]:
                del graph[src][dest]
            if src in graph[dest]:
                del graph[dest][src]
            # Update distance_tables for affected direct links
            for node in [src, dest]:
                for neighbour in nodes:
                    if neighbour != node:
                        if neighbour == dest and node == src or neighbour == src and node == dest:
                            distance_tables[node][neighbour][neighbour] = float('inf')
                            # Invalidate multi-hop paths that used this link
                            for d in nodes:
                                if d != node and d != neighbour:
                                    # Check all paths through this neighbour
                                    link_cost = removed_links.get((node, neighbour), float('inf'))
                                    min_neighbour_cost = min(
                                        distance_tables[neighbour][n].get(d, float('inf'))
                                        for n in nodes if n != node
                                    )
                                    expected_cost = link_cost + min_neighbour_cost if min_neighbour_cost != float('inf') else float('inf')
                                    if distance_tables[node][neighbour][d] == expected_cost:
                                        distance_tables[node][neighbour][d] = float('inf')
        else:
            # Update link cost
            graph[src][dest] = cost
            graph[dest][src] = cost
            # Update distance_tables for direct links
            distance_tables[src][dest][dest] = cost
            distance_tables[dest][src][src] = cost
            # Update node's own table
            distance_tables[src][src][dest] = cost
            distance_tables[dest][dest][src] = cost

    # Recompute all multi-hop paths for all neighbours
    for node in nodes:
        for neighbour in nodes:
            if neighbour != node:
                for dest in nodes:
                    if dest != node and dest != neighbour:
                        # Recompute path using updated graph
                        if neighbour in graph[node]:
                            cost = graph[node][neighbour]
                            # Use direct link costs for neighbour to dest if available
                            neighbour_cost = graph[neighbour].get(dest, float('inf'))
                            if neighbour_cost == float('inf'):
                                # Otherwise, use minimum cost from neighbour's table
                                neighbour_cost = min(
                                    distance_tables[neighbour][n].get(dest, float('inf'))
                                    for n in nodes if n != node
                                )
                            cost += neighbour_cost if neighbour_cost != float('inf') else float('inf')
                            distance_tables[node][neighbour][dest] = cost
                        else:
                            distance_tables[node][neighbour][dest] = float('inf')

    return distance_tables

def initialise_tables(nodes, graph):
    """Initialise distance and routing tables."""
    # Distance tables: {node: {neighbour: {dest: cost}}}
    distance_tables = {
        node: {
            neighbour: {dest: float('inf') for dest in nodes if dest != node}
            for neighbour in nodes  # Include all nodes as potential neighbours
        }
        for node in nodes
    }
    # Routing tables: {node: {dest: next_hop}}
    routing_tables = {node: {dest: None for dest in nodes if dest != node} for node in nodes}

    # Initialise with direct links only
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
        # Neighbours excluding the node itself
        neighbours = sorted([neighbour for neighbour in nodes if neighbour != node])
        # Print header with destinations
        print(f"     {'    '.join(destinations)}")
        # Print rows for each neighbour
        for neighbour in neighbours:
            costs = []
            for dest in destinations:
                # Safely access cost, default to INF if key missing
                cost = distance_tables[node].get(dest, {}).get(neighbour, float('inf'))
                costs.append("INF" if cost == float('inf') else str(int(cost)))
            print(f"{neighbour}    {'    '.join(costs)}")

def print_routing_tables(routing_tables, distance_tables, nodes):
    """Print routing tables in the specified format."""
    for node in sorted(nodes):
        print(f"\nRouting Table of router {node}:")
        for dest in sorted(nodes):
            if dest != node:
                next_hop = routing_tables[node][dest]
                # Find minimum cost to dest across all neighbours
                min_cost = float('inf')
                if next_hop:
                    min_cost = min(
                        distance_tables[node][neighbour][dest]
                        for neighbour in distance_tables[node]
                        if dest in distance_tables[node][neighbour]
                    )
                if min_cost != float('inf') and next_hop is not None:
                    print(f"{dest},{next_hop},{int(min_cost)}")

def distance_vector(graph, nodes, updates):
    """Run the Distance Vector algorithm and apply updates until convergence."""
    distance_tables, routing_tables = initialise_tables(nodes, graph)
    step = 0
    converged = False
    updates_applied = False

    # Print tables before running DV
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

                # Update costs via actual neighbours
                for neighbour in graph[node]:
                    if neighbour != node:
                        # Cost to dest via neighbour
                        if neighbour == dest:
                            # Direct link cost
                            cost = graph[node][neighbour]
                        else:
                            # Multi-hop cost via neighbour
                            cost = graph[node][neighbour]
                            neighbour_cost = min(
                                distance_tables[neighbour][n].get(dest, float('inf'))
                                for n in nodes if n != neighbour
                            )
                            cost += neighbour_cost if neighbour_cost != float('inf') else float('inf')
                        new_distances[node][neighbour][dest] = cost

                        # Update minimum cost for routing table
                        if cost < min_cost:
                            min_cost = cost
                            next_hop = neighbour

                # Update routing table if cost or next-hop changed
                if min_cost != float('inf'):
                    old_cost = min(
                        distance_tables[node][n].get(dest, float('inf'))
                        for n in distance_tables[node]
                    ) if any(dest in distance_tables[node][n] for n in distance_tables[node]) else float('inf')
                    if min_cost != old_cost or next_hop != routing_tables[node][dest]:
                        new_routing[node][dest] = next_hop
                        converged = False

        distance_tables = new_distances
        routing_tables = new_routing

        # Print tables for this step
        print_distance_tables(step, distance_tables, nodes)

        # Apply updates and update distance tables, then run one DV iteration
        if converged and updates and not updates_applied:
            print_routing_tables(routing_tables, distance_tables, nodes)
            # Update distance tables instead of reinitializing
            distance_tables = update_distance_tables(graph, nodes, updates, distance_tables)
            updates_applied = True
            converged = False
            step += 1
            print_distance_tables(step, distance_tables, nodes)
            step += 1
            # Run one DV iteration immediately to compute multi-hop paths
            new_distances = copy.deepcopy(distance_tables)
            new_routing = copy.deepcopy(routing_tables)
            for node in nodes:
                for dest in [d for d in nodes if d != node]:
                    min_cost = float('inf')
                    next_hop = None
                    if dest in graph[node]:
                        min_cost = graph[node][dest]
                        next_hop = dest
                    for neighbour in graph[node]:
                        if neighbour != node:
                            if neighbour == dest:
                                cost = graph[node][neighbour]
                            else:
                                cost = graph[node][neighbour]
                                neighbour_cost = min(
                                    distance_tables[neighbour][n].get(dest, float('inf'))
                                    for n in nodes if n != neighbour
                                )
                                cost += neighbour_cost if neighbour_cost != float('inf') else float('inf')
                            new_distances[node][neighbour][dest] = cost
                            if cost < min_cost:
                                min_cost = cost
                                next_hop = neighbour
                    if min_cost != float('inf'):
                        old_cost = min(
                            distance_tables[node][n].get(dest, float('inf'))
                            for n in distance_tables[node]
                        ) if any(dest in distance_tables[node][n] for n in distance_tables[node]) else float('inf')
                        if min_cost != old_cost or next_hop != routing_tables[node][dest]:
                            new_routing[node][dest] = next_hop
                            converged = False
            distance_tables = new_distances
            routing_tables = new_routing
            print_distance_tables(step, distance_tables, nodes)
            step += 1
            continue

        if converged:
            break

        step += 1

    print_routing_tables(routing_tables, distance_tables, nodes)
    return

def main():
    # Generate graph
    global graph
    graph, nodes, updates = read_topology()
    
    # Confirm graph is input correctly
    if not graph or not nodes:
        return

    # Process initial topology
    distance_vector(graph, nodes, updates)

if __name__ == "__main__":
    main()

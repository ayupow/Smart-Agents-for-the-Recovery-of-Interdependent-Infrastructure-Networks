import json
import random
import math

def resource_allocation_considering_cost(global_json_path):
    # Load global data
    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    # File paths
    network_path = global_data[
        "interdependent_infrastructure_networks_with_different_resource_demand"]
    resource_constraints_path = global_data["resource_constraints_per_day_4_cost"]
    cascading_failure_path = global_data["cascading_failure_information"]

    # Load datasets
    with open(network_path, 'r') as f:
        network_data = json.load(f)
    with open(resource_constraints_path, 'r') as f:
        rc_data = json.load(f)["resource_constraints"]
    with open(cascading_failure_path, 'r') as f:
        failed_nodes = json.load(f)["failed_nodes"]

    # Build capacity, cost, and availability per (demand_type, team)
    capacity = {}    # units repaired per team per day
    cost_per_day = {}  # cost for each team per day
    avail_teams = {}   # maximum teams available each day

    for demand_type, specs in rc_data["repair_teams"].items():
        for team in ['A', 'B', 'C']:
            hours = specs.get(f"hours_per_day_{team}", 0)
            rate  = specs.get(f"repair_rate_per_hour_{team}", 0)
            capacity[(demand_type, team)] = hours * rate
            cost_per_day[(demand_type, team)] = specs.get(f"cost_per_day_{team}", 0)
            avail_teams[(demand_type, team)] = specs.get(f"number_of_teams_{team}", 0)

    # Recovery-day upper bound
    day_limit = rc_data["recovery_day_constraint"]["recovery_day_constraint"]

    # Initial unmet demands per failed node
    node_demands = {
        node['Code']: {
            dt: node.get(dt, 0)
            for dt in ['resource_demand_type_1', 'resource_demand_type_2', 'resource_demand_type_3']
        }
        for node in network_data['nodes'] if node['Code'] in failed_nodes
    }

    # Fitness evaluates total cost including penalty for days > limit
    def fitness(sequence):
        # Copy demands
        demands = {n: dict(node_demands[n]) for n in sequence}
        total_cost = 0
        days = 0

        # Simulate until all demands satisfied
        while any(any(v > 0 for v in demands[n].values()) for n in sequence):
            days += 1
            daily_avail = dict(avail_teams)
            for node in sequence:
                for dt, rem in demands[node].items():
                    if rem <= 0:
                        continue
                    # Try each team on this demand
                    for team in ['A', 'B', 'C']:
                        cap = capacity[(dt, team)]
                        if cap <= 0 or daily_avail[(dt, team)] <= 0:
                            continue
                        # Number of teams needed to finish today's requirement
                        needed = math.ceil(rem / cap)
                        assigned = min(needed, daily_avail[(dt, team)])
                        # Perform repair and accrue cost
                        repaired = assigned * cap
                        demands[node][dt] = max(0, rem - repaired)
                        total_cost += assigned * cost_per_day[(dt, team)]
                        daily_avail[(dt, team)] -= assigned
                        rem = demands[node][dt]
                        if rem <= 0:
                            break
            # Safety break
            if days > 1e4:
                break

        # Add penalty for exceeding duration
        if days > day_limit:
            total_cost += (days - day_limit) * 1e4
        return total_cost

    # Genetic algorithm parameters
    pop_size, generations, mutation_rate = 50, 100, 0.1
    elite_k = 10

    def mutate(seq):
        if random.random() < mutation_rate:
            i, j = random.sample(range(len(seq)), 2)
            seq[i], seq[j] = seq[j], seq[i]
        return seq

    def crossover(p1, p2):
        idx = random.randrange(len(p1))
        return p1[:idx] + [n for n in p2 if n not in p1[:idx]]

    # Initialize population of sequences
    population = [random.sample(list(node_demands.keys()),
                                len(node_demands)) for _ in range(pop_size)]

    # Evolve
    for _ in range(generations):
        population.sort(key=fitness)
        next_pop = population[:elite_k]
        while len(next_pop) < pop_size:
            parents = random.sample(population[:2*elite_k], 2)
            child = mutate(crossover(parents[0], parents[1]))
            next_pop.append(child)
        population = next_pop

    # Best sequence and schedule generation
    best_seq = population[0]
    demands = {n: dict(node_demands[n]) for n in best_seq}
    schedule = []
    total_cost = 0
    day = 1

    # Simulate final schedule with cost tracking
    while any(any(v > 0 for v in demands[n].values()) for n in best_seq):
        daily_avail = dict(avail_teams)
        day_alloc = []
        for node in best_seq:
            alloc = {}
            for dt, rem in demands[node].items():
                if rem <= 0:
                    continue
                for team in ['A', 'B', 'C']:
                    cap = capacity[(dt, team)]
                    if cap <= 0 or daily_avail[(dt, team)] <= 0:
                        continue
                    needed = math.ceil(rem / cap)
                    assigned = min(needed, daily_avail[(dt, team)])
                    demands[node][dt] = max(0, rem - assigned * cap)
                    daily_avail[(dt, team)] -= assigned
                    alloc[f"teams_{team}_{dt}"] = assigned
                    total_cost += assigned * cost_per_day[(dt, team)]
            if alloc:
                day_alloc.append({"node": node, "teams_assigned": alloc})
        schedule.append({"day": day, "allocations": day_alloc})
        day += 1

    # Package output
    result = {
        "daily_schedule": schedule,
        "total_recovery_cost": total_cost
    }
    out_path = 'resource_allocation_considering_cost.json'
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=4)

    # Update global data
    global_data[
        'resource_allocation_considering_cost'] = out_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return f"Results saved to {out_path}"

if __name__ == '__main__':
    print(resource_allocation_considering_cost('Global_Data.json'))

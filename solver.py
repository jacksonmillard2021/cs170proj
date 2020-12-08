import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, \
    calculate_stress_for_room
import sys
from os.path import basename, normpath
import glob


def solve(G, s):
    """
    Args:
        G: networkx.Graph
        s: stress_budget
    Returns:
        D: Dictionary mapping for student to breakout room r e.g. {0:2, 1:0, 2:1, 3:2}
        k: Number of breakout rooms
    """
    g_new = G.copy()
    groups = nx.Graph()  # Graph to store groupings of students
    for i in range(G.number_of_nodes()):
        groups.add_node(i, ppl=[i])
    curr_stress = 0  # Total stress from room assignment
    max_stress, remaining_stress = s, s
    while remaining_stress >= 0:  # While remaining stress is greater than 0
        curr_stress = findopt(g_new, G, s, groups, curr_stress)
        if curr_stress == 'done':
            break
        for node in list(groups.nodes):
            curr_stress += calculate_stress_for_room(groups.nodes[node]['ppl'],
                                                     G)
        max_stress = s / groups.number_of_nodes()
        remaining_stress = max_stress - curr_stress

    k = groups.number_of_nodes()
    # Convert the groupings into a dictionary
    d = dict()
    nodes = list(groups.nodes)
    for i in range(k):
        for student in groups.nodes[nodes[i]]['ppl']:
            d[student] = i
    d = dict(sorted(d.items(), key=lambda x: x[0]))
    return d, k


def findopt(G_new, G, s, groups, curr_stress):
    """
    mutates the networkx graphs 'G' and 'groups', and
    returns the increase in total stress.
    """
    students = G_new.number_of_nodes()
    max_value = 0
    merge_nodes = ('a', 'a')
    # Check all edges, find the best one to merge
    new_stress_capacity = s / (
            groups.number_of_nodes() - 1)  # new stress capacity if a
    # merge is made
    remaining_stress = new_stress_capacity - curr_stress
    for edge in list(G_new.edges):
        i = edge[0]
        j = edge[1]
        if G_new.get_edge_data(i, j) is not None:
            edge_happiness = G_new.get_edge_data(i, j)['happiness']
            edge_stress = G_new.get_edge_data(i, j)['stress']
            if edge_stress <= remaining_stress:
                value = heuristic(edge_stress, edge_happiness, remaining_stress)
                if value > max_value:
                    max_value = value
                    merge_nodes = (i, j)
            else:
                continue

    # Calculate the increase in stress
    i, j = merge_nodes[0], merge_nodes[1]
    if i == 'a' or j == 'a':
        return 'done'
    old_stress = calculate_stress_for_room(groups.nodes[i]['ppl'], G)
    copy = groups.copy()
    copy.nodes[i]['ppl'] += copy.nodes[j]['ppl']
    if calculate_stress_for_room(copy.nodes[i]['ppl'], G) > G.number_of_nodes() \
            / s:
        return 0
    else:
        groups.nodes[i]['ppl'] += groups.nodes[j]['ppl']
    groups.remove_node(j)
    new_stress = calculate_stress_for_room(groups.nodes[i]['ppl'], G)

    # Merge the 2 nodes from chosen edge, update G
    l1 = list(G_new.edges(i))
    l1.remove((i, j))
    l2 = list(G_new.edges(j))
    l2.remove((j, i))
    n = len(l1)
    for i in range(n):
        G_new.get_edge_data(l1[i][0], l1[i][1])['happiness'] += \
            G_new.get_edge_data(l2[i][0], l2[i][1])['happiness']
        G_new.get_edge_data(l1[i][0], l1[i][1])['stress'] += \
            G_new.get_edge_data(l2[i][0], l2[i][1])['stress']
    G_new.remove_node(j)

    return 0


# Heuristic to see which edge to merge
def heuristic(edge_stress, edge_happiness, remaining_stress):
    if edge_stress > remaining_stress:
        return float('-inf')
    else:
        return edge_happiness - edge_stress


# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

# if __name__ == '__main__':
#     assert len(sys.argv) == 2
#     path = sys.argv[1]
#     G, s = read_input_file(path)
#     D, k = solve(G, s)
#     assert is_valid_solution(D, G, s, k)
#     print("Total Happiness: {}".format(calculate_happiness(D, G)))
#     write_output_file(D, 'outputs/small-1.out')


# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
# if __name__ == '__main__':
#     inputs = glob.glob('inputs/*')
#     for input_path in inputs:
#         output_path = 'outputs/' + basename(normpath(input_path))[:-3] + '.out'
#         G, s = read_input_file(input_path)
#         D, k = solve(G, s)
#         assert is_valid_solution(D, G, s, k)
#         happiness = calculate_happiness(D, G)
#         write_output_file(D, output_path)

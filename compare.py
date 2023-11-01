import argparse
import math
from ete3 import Tree

def map_leaves_to_nodes(tree):
    leaves_to_node = {}
    for node in tree.traverse("preorder"):
        all_leaves = [leaf.name for leaf in node.get_leaves() ]
        all_leaves = sorted(all_leaves)
        leaves_to_node[tuple(all_leaves)] = node
    return leaves_to_node

def compute_rmse(path1, path2):
    # Load trees from Newick or Nexus files
    if path1.endswith(".nexus"):
        # we need to grab from between "Begin Trees;" and "End;"
        with open(path1, "rt") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
               
                if line.startswith("Begin "):
                    start = i + 1
                elif line.startswith("End;"):
                    end = i
                    
            nexus = "".join(lines[start:end])
        # strip off everything before "="
        nexus = nexus[nexus.find("=")+1:] 
        # strip comments
      
        import re
        nexus = re.sub(r'\[[^\]]*\]', '', nexus)
        print(nexus)
        comparator_tree = Tree(nexus, format=1)


    else:
        comparator_tree = Tree(path1)
    groundtruth_tree = Tree(path2)

    # Map leaves to nodes
    comparator_leaves_to_node = map_leaves_to_nodes(comparator_tree)
    groundtruth_nodes_to_leaves = map_leaves_to_nodes(groundtruth_tree)

    # Initialize lists for storing branch lengths
    lengths1 = []
    lengths2 = []

    # For each leaf set in the ground truth tree, find the corresponding node in the comparator tree and store their lengths
    for leaf_set, node1 in comparator_leaves_to_node.items():
        if leaf_set in groundtruth_nodes_to_leaves:
            node2 = groundtruth_nodes_to_leaves[leaf_set]
            lengths1.append(node1.dist)
            lengths2.append(node2.dist)

    # Compute the root-mean-square error (RMSE) between lengths of two trees
    differences_squared = [(a - b)**2 for a, b in zip(lengths1, lengths2)]
    rmse = math.sqrt(sum(differences_squared) / len(differences_squared))
    lengths_length = len(lengths1) 

    return rmse, lengths_length

import datetime

def parse_date(date_str):
    # Assuming dates are in the format YYYY-MM-DD
    return datetime.datetime.strptime(date_str, '%Y-%m-%d')

def compute_rmse_tsv(path1, path2):
    dates1 = {}
    dates2 = {}

    # Read first TSV file
    with open(path1, 'r') as file:
        # Skip the header
        next(file)
        for line in file:
            parts= line.strip().split('\t')
            strain = parts[0]
            date_str = parts[1]
            # if date_str has spaces, take the first one
            if " " in date_str:
                date_str = date_str.split(" ")[0]
            dates1[strain] = parse_date(date_str)

    # Read second TSV file
    with open(path2, 'r') as file:
        # Skip the header
        next(file)
        for line in file:
            parts= line.strip().split('\t')
            strain = parts[0]
            date_str = parts[1]
            # if date_str has spaces, take the first one
            if " " in date_str:
                date_str = date_str.split(" ")[0]
            dates2[strain] = parse_date(date_str)

    differences_squared = []
    common_strains = 0

    # Compute squared differences in days for common strains
    for strain, date1 in dates1.items():
        if strain in dates2:
            common_strains += 1
            difference = (date1 - dates2[strain]).days
            differences_squared.append(difference ** 2)

    # Compute the root-mean-square error (RMSE) in days
    rmse = math.sqrt(sum(differences_squared) / common_strains)
    median = sorted(differences_squared)[len(differences_squared) // 2]

    return rmse, median

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("path1", help="Path to the first  file")
    parser.add_argument("path2", help="Path to the second  file")
    # tsv1 and tsv2 are optional
    parser.add_argument("--tsv1", help="Path to the first TSV file", required=False)
    parser.add_argument("--tsv2", help="Path to the second TSV file", required=False)
    args = parser.parse_args()

    # Compute RMSE and print it
    rmse, lengths_length= compute_rmse(args.path1, args.path2)
    if args.tsv1 and args.tsv2:
        rmsedays,median = compute_rmse_tsv(args.tsv1, args.tsv2)
    else:
        rmsedays,median = -1,-1

    print(f"{rmse},{rmsedays},{median}")

if __name__ == "__main__":
    main()
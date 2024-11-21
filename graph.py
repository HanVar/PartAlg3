import subprocess
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import networkx as nx
import numpy as np
import re

def run_cpp_program(input_file, output_file):
    compile_cmd = ['g++', 'Pseudo-knots-corr5-01-19.cpp', '-o', 'pseudo_knots']
    subprocess.run(compile_cmd, check=True)
    
    run_cmd = ['./pseudo_knots']
    process = subprocess.Popen(run_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    
    vertices = input("Enter the number of vertices: ")
    motif_id = input("Enter the motif ID: ")
    
    process.communicate(f"{vertices}\n{motif_id}\n".encode())

def extract_blocks_with_types(output_file):
    blocks = []
    block_types = []
    current_block = []

    # Map phrases to block types
    type_mapping = {
        "The block is a recursive PK": "Recursive PK",
        "this block represents a regular-region": "Regular",
        "this block represents a pseudoknot": "Non-recursive PK",
    }

    with open(output_file, 'r') as file:
        block_started = False
        for line in file:
            if "New Block" in line:
                if current_block:  # Save the current block before starting a new one
                    blocks.append(current_block)
                    # Ensure block_types aligns with blocks
                    if len(block_types) < len(blocks):
                        block_types.append("Unknown")  # Default type
                    current_block = []
                block_started = True
            elif block_started and re.search(r'\(\d+,\d+\)', line):
                matches = re.findall(r'\((\d+),(\d+)\)', line)
                for match in matches:
                    v1, v2 = int(match[0]), int(match[1])
                    current_block.append((v1, v2))
            elif any(phrase in line for phrase in type_mapping.keys()):
                # Identify the type from the line
                for phrase, label in type_mapping.items():
                    if phrase in line:
                        block_types.append(label)
                        break
            elif "Summary information" in line:
                if current_block:  # Add the last block before exiting
                    blocks.append(current_block)
                    if len(block_types) < len(blocks):
                        block_types.append("Unknown")  # Default type
                break

    return blocks, block_types

def read_adjacency_matrix(input_file):
    """Reads the adjacency matrix from a file."""
    with open(input_file, 'r') as file:
        matrix = []
        for line in file:
            row = list(map(int, line.strip().split()))
            matrix.append(row)
    return matrix

def add_edges_from_matrix(G, matrix):
    """Adds edges to the graph G based on the adjacency matrix, excluding self-loops."""
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            weight = matrix[i][j]
            if weight > 0 and i != j:  # Skip self-loops (i != j)
                # For a MultiGraph, we add multiple edges if needed
                for _ in range(weight):  # Add multiple edges based on weight
                    G.add_edge(i, j, weight=weight)

def draw_combined_graph(matrix, blocks, block_types, G):
    """Draws the graph based on the adjacency matrix, colored edges by blocks, and labels for weights."""
    # Generate positions for all nodes
    pos = nx.spring_layout(G)
    
    # Generate a large number of distinct colors using a colormap
    num_blocks = len(blocks)
    cmap = plt.colormaps['tab20']
    block_colors = [cmap(i / num_blocks) for i in range(num_blocks)]
    
    edge_colors = {}
    for i, edges in enumerate(blocks):
        block_color = block_colors[i]
        G.add_edges_from(edges)
        
        for edge in edges:
            edge_colors[edge] = block_color
    
    # Draw the graph
    plt.figure(figsize=(12, 12))
    plt.title("Graph with Colored Blocks and Weights", fontsize=16)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color="skyblue")
    
    # Draw edges with their respective block colors
    for edge, color in edge_colors.items():
        nx.draw_networkx_edges(G, pos, edgelist=[edge], edge_color=[color], width=2)
    
    # Draw labels for nodes
    nx.draw_networkx_labels(G, pos, font_size=12, font_color="black")
    
    # Add edge labels (weights)
    edge_labels = {(u, v): G[u][v][0]['weight'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, font_color="red")
    
    # Add legend for block types and colors
    legend_handles = []
    for i, block_type in enumerate(block_types):
        handle = plt.Line2D([], [], color=block_colors[i], label=block_type, linewidth=2)
        legend_handles.append(handle)
    
    # Position the legend outside the graph
    plt.legend(
        handles=legend_handles, 
        title="Block Types", 
        loc="center left", 
        bbox_to_anchor=(1.00, 0.5),  # Position to the right of the graph
        fontsize=10
    )
    
    plt.tight_layout()  # Adjust layout to ensure everything fits
    plt.show()

# Use your provided file paths for input and output files
input_file = "/Users/just/Documents/GitHub/PartAlg3-master/PKB236.txt"
output_file = "/Users/just/Documents/GitHub/PartAlg3-master/PKB236_out.txt"

# Run the C++ program (if needed)
run_cpp_program(input_file, output_file)

# Extract blocks and their types from the output
blocks, block_types = extract_blocks_with_types(output_file)

# Read the adjacency matrix from the input file
matrix = read_adjacency_matrix(input_file)

# Create a MultiGraph to allow multiple edges between nodes
G = nx.MultiGraph()

# Add edges to the graph based on the adjacency matrix, excluding self-loops
add_edges_from_matrix(G, matrix)

# Draw the combined graph with block type labels and edge weights
draw_combined_graph(matrix, blocks, block_types, G)

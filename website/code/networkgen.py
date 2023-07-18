# networkgen.py
# @Brendan Baker
# Sample network creation

from pyvis.network import Network
import pandas as pd
import textnets as tn
import networkx as nx
import igraph as ig
import leidenalg
import matplotlib.pyplot as plt
import seaborn as sns
import random
import numpy as np
from textnets import Corpus

# Read data
agg = pd.read_csv('../data/agg.csv')

# Set seed
tn.config.params['seed'] = 16

# Separate only the Qualifications and Category Columns
qualifications = agg[['Qualifications', 'category']]

# Expand each listed value in every row to a new row, with the same category
qualifications = qualifications.explode('Qualifications')

# Set the index column to be the category
qualifications = qualifications.set_index('category')

corpus = Corpus(qualifications['Qualifications'])

noun_phrases = corpus.noun_phrases()

#t = tn.Textnet(corpus.tokenized(), min_docs=8, remove_weak_edges=True)
t = tn.Textnet(noun_phrases, min_docs=8, remove_weak_edges=True)

tn.viz.BASE_COLORS = ['#A72608', '#CABAC8', '#C29598', '#B97068', '#581905', '#653715', '#DB9D47','#B6B27C','#A4BD97','#91C7B1']
# Set seed
random.seed(123)
np.random.seed(123)

# Function to get distinct colors
def get_color_list(num_colors):
    color_list = ['#EFB988', '#EB9486','#B58A90','#9A8595','#7E7F9A','#272838', '#8D8361', '#F3DE8A', '#BCBCC9', '#F9F8F8']
    return color_list[:num_colors]

corpus = tn.Corpus(qualifications['Qualifications'])
noun_phrases = corpus.noun_phrases()
t = tn.Textnet(noun_phrases, min_docs=8, remove_weak_edges=True)

# Convert the Textnet to an igraph.Graph object
igraph_graph = t.graph

# Apply the Leiden algorithm on the igraph graph
partition = leidenalg.find_partition(igraph_graph, leidenalg.RBConfigurationVertexPartition, seed=123)

# Convert the Textnet to a networkx.Graph object
nx_graph = t.graph.to_networkx()

# Create a mapping between node indices and community IDs
index_to_community_mapping = {v.index: partition.membership[v.index] for v in igraph_graph.vs}

# Update community information in the networkx graph
for node in nx_graph.nodes:
    node_index = nx_graph.nodes[node]['_igraph_index']
    nx_graph.nodes[node]['community_id'] = index_to_community_mapping[node_index]

# Get distinct colors for each community
num_communities = max([nx_graph.nodes[node]['community_id'] for node in nx_graph.nodes])
color_list = get_color_list(num_communities + 1)

# Remove unconnected nodes
connected_components = list(nx.connected_components(nx_graph))
largest_component = max(connected_components, key=len)
nx_graph = nx_graph.subgraph(largest_component).copy()

# Set node attributes for labels and community groupings
for node in nx_graph.nodes:
    if 'label' not in nx_graph.nodes[node]:
        nx_graph.nodes[node]['title'] = nx_graph.nodes[node]['id']
        nx_graph.nodes[node]['label'] = nx_graph.nodes[node]['id']
    else:
        nx_graph.nodes[node]['title'] = nx_graph.nodes[node]['label']
        nx_graph.nodes[node]['label'] = nx_graph.nodes[node]['label']
    
    node_type = nx_graph.nodes[node]['type']
    if node_type == 'doc':
        nx_graph.nodes[node]['shape'] = 'square'
    
    # Set the color of the node based on its community ID
    community_id = nx_graph.nodes[node]['community_id']
    color = color_list[community_id]
    nx_graph.nodes[node]['color'] = color

# Create a Pyvis network and populate it with the nodes and edges from the networkx graph
nt = Network('800', width='100%', bgcolor='#272838', font_color='white', notebook=True)
nt.from_nx(nx_graph)

# Set physics and other configurations
nt.set_options("""
{
  "nodes": {
    "borderWidth": 3,
    "size": 60,
    "color": {
      "border": "rgba(0,0,0,1)"
    },
    "font": {
      "size": 20,
      "face": "tahoma"
    }
  },
  "edges": {
    "color": "darkgray",
    "smooth": false,
    "width": 1,
    "selectionWidth": 6
  },
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -80000,
      "centralGravity": 0.3,
      "springLength": 225,
      "springConstant": 0.01,
      "damping": 0.09,
      "avoidOverlap": 5
    },
    "minVelocity": 0.75
  }
}
""")

# Display the interactive plot
# nt.show('./website/viz/textnet_qualifications.html')

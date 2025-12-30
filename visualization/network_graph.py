import networkx as nx
import plotly.graph_objects as go
from typing import List

def render_skill_network(user_skills: List[str], missing_skills: List[str]):
    """
    Renders a physics-based network graph separating "Owned" (Green) vs "Missing" (Red) skills.
    Uses NetworkX for layout and Plotly for rendering.
    """
    G = nx.Graph()
    
    # Central Node
    G.add_node("YOU", type="center", size=20)
    
    # User Skills (Owned)
    for s in user_skills[:15]: # Limit for visual clarity
        G.add_node(s, type="owned", size=10)
        G.add_edge("YOU", s, weight=1)
        
    # Missing Skills (Target)
    for s in missing_skills[:10]:
        G.add_node(s, type="missing", size=15)
        # We can add edges if we had ontology relations, e.g. Python -> Django
        # For MVP V2, we connect them to YOU with dashed lines or just visualize them in a cluster
        G.add_edge("YOU", s, weight=0.5)

    # Spring Layout
    pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)
    
    edge_x = []
    edge_y = []
    edge_colors = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Color logic
        target = edge[1] if edge[0] == "YOU" else edge[0]
        node_type = G.nodes[target].get("type", "center")
        if node_type == "missing":
            edge_colors.append("rgba(255, 50, 50, 0.3)")
        else:
            edge_colors.append("rgba(0, 209, 255, 0.3)")

    # Draw Nodes
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        
        ntype = G.nodes[node]["type"]
        if ntype == "center":
            node_color.append("#ffffff")
            node_size.append(25)
        elif ntype == "owned":
            node_color.append("#0072FF") # Blue
            node_size.append(15)
        elif ntype == "missing":
            node_color.append("#FF3366") # Red/Pink
            node_size.append(18)

    # Edge Trace (Lines)
    # Plotly Edge trace with single color is easier, multi-color strictly needs segments
    # For MVP V2 using simple single trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Node Trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="top center",
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=0,l=0,r=0,t=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
                
    return fig

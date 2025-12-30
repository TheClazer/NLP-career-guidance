import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any

def render_radar_chart(user_scores: Dict[str, float], role_scores: Dict[str, float]):
    """
    Creates a high-fidelity cyberpunk-style radar chart comparing User vs Role.
    """
    categories = list(user_scores.keys())
    user_values = list(user_scores.values())
    role_values = [role_scores.get(c, 50) for c in categories] # Default baseline
    
    # Close the loop
    categories = [*categories, categories[0]]
    user_values = [*user_values, user_values[0]]
    role_values = [*role_values, role_values[0]]

    fig = go.Figure()

    # Role Baseline (The Target)
    fig.add_trace(go.Scatterpolar(
        r=role_values,
        theta=categories,
        fill='toself',
        name='Target Role',
        line_color='rgba(0, 209, 255, 0.4)',
        fillcolor='rgba(0, 209, 255, 0.1)',
        line_shape='spline'
    ))

    # User Profile (The Candidate)
    fig.add_trace(go.Scatterpolar(
        r=user_values,
        theta=categories,
        fill='toself',
        name='Your Profile',
        line_color='#0072FF',
        fillcolor='rgba(0, 114, 255, 0.3)',
        line_shape='spline'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False,
                gridcolor='rgba(255, 255, 255, 0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='white'),
                gridcolor='rgba(255, 255, 255, 0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color="white"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=20, b=40)
    )

    return fig

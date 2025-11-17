# helpers/viz_utils.py
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List

def create_budget_pie_chart(budget_allocation: Dict[str, float]) -> go.Figure:
    labels = list(budget_allocation.keys())
    values = list(budget_allocation.values())
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320, showlegend=True)
    return fig

def create_price_comparison_chart(price_categories: Dict[str, float]) -> go.Figure:
    categories = list(price_categories.keys())
    prices = [price_categories[k] or 0 for k in categories]
    fig = px.bar(x=categories, y=prices, labels={'x':'Price Category', 'y':'Average Price (PKR)'})
    fig.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=320, showlegend=False)
    fig.update_traces(texttemplate='PKR %{y:,.0f}', textposition='outside')
    return fig

def create_swot_visualization(swot_data: Dict[str, List[str]]) -> go.Figure:
    fig = go.Figure()
    annotations = []
    strengths = swot_data.get('Strengths', [])
    weaknesses = swot_data.get('Weaknesses', [])
    opportunities = swot_data.get('Opportunities', [])
    threats = swot_data.get('Threats', [])
    for i, s in enumerate(strengths[:3]):
        annotations.append(dict(x=0.75, y=0.8 - i*0.2, xref="paper", yref="paper", text=f"💪 {s}", showarrow=False, bgcolor="rgba(40,167,69,0.2)"))
    for i, s in enumerate(weaknesses[:3]):
        annotations.append(dict(x=0.25, y=0.8 - i*0.2, xref="paper", yref="paper", text=f"⚠️ {s}", showarrow=False, bgcolor="rgba(220,53,69,0.2)"))
    for i, s in enumerate(opportunities[:3]):
        annotations.append(dict(x=0.75, y=0.2 - i*0.2, xref="paper", yref="paper", text=f"🚀 {s}", showarrow=False, bgcolor="rgba(23,162,184,0.2)"))
    for i, s in enumerate(threats[:3]):
        annotations.append(dict(x=0.25, y=0.2 - i*0.2, xref="paper", yref="paper", text=f"🔴 {s}", showarrow=False, bgcolor="rgba(255,193,7,0.2)"))
    fig.update_layout(title="SWOT Analysis Matrix", annotations=annotations, xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False), margin=dict(t=50,b=20,l=20,r=20), height=500, showlegend=False)
    return fig

def create_strategy_timeline(strategy_phases: List[str]) -> go.Figure:
    phases_data = []
    for i, phase in enumerate(strategy_phases):
        phases_data.append({'Phase': f'Phase {i+1}', 'Start': i*30, 'End': (i+1)*30, 'Description': phase})
    df = pd.DataFrame(phases_data)
    fig = px.timeline(df, x_start="Start", x_end="End", y="Phase", color="Phase")
    fig.update_layout(height=300, showlegend=False, margin=dict(t=30,b=20,l=20,r=20))
    return fig

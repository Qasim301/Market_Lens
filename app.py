import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Any, Dict, List
import requests
import re
# 2. Import your modules
from helpers import viz_utils
# --- Make.com Configuration --
MAKE_WEBHOOK_URL = st.secrets.get("MAKE_WEBHOOK_URL")
# --- 0. COLOR & FONT DEFINITIONS --
COLOR_DARKEST = "#9AA6B2"
COLOR_LIGHTEST = "#F8FAFC"
COLOR_MEDIUM = "#BCCCDC"
COLOR_LIGHT_ACCENT = "#D9EAFD"
COLOR_GLASS = "rgba(255, 255, 255, 0.1)"
COLOR_GLASS_DARK = "rgba(154, 166, 178, 0.2)"
FONT_FAMILY = 'Inter, sans-serif'
FONT_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    layout="wide", 
    page_title="MarketLens AI",
    page_icon=None,
    initial_sidebar_state="collapsed"
)

def load_css():
    st.markdown(f"""
    <style>
    @import url('{FONT_URL}');
    
    /* Main container styling */
    .main .block-container {{
        padding-top: 2rem;
        max-width: 100%;
    }}
    
    div[data-testid="stAppViewContainer"] {{
        background: linear-gradient(135deg, {COLOR_LIGHTEST} 0%, {COLOR_MEDIUM} 100%);
        background-attachment: fixed;
        min-height: 100vh;
    }}
    
    section[data-testid="stSidebar"] {{
        display: none;
    }}
    
    * {{ 
        font-family: {FONT_FAMILY}; 
        color: #4e5252; 
    }}
    
    h1, h2, h3, h4, h5, h6 {{ 
        font-weight: 700; 
        color: {COLOR_DARKEST};
        margin-bottom: 1rem;
    }}
    
    h1 {{ font-size: 2.5rem; font-weight: 800; }}
    h2 {{ font-size: 2rem; font-weight: 700; }}
    h3 {{ font-size: 1.5rem; font-weight: 600; }}
    
    /* Glass card styling */
    .glass-card {{
        background: {COLOR_GLASS};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 
            0 8px 32px 0 rgba(31, 38, 135, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
    }}
    
    .glass-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.6s;
    }}
    
    .glass-card:hover::before {{
        left: 100%;
    }}
    
    .glass-card:hover {{
        transform: translateY(-12px) scale(1.02);
        box-shadow: 
            0 20px 40px 0 rgba(31, 38, 135, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }}
    .glass-header {{
    background: rgba(154, 166, 178, 0.85);
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    border-radius: 25px;
    padding: 3rem 2rem;
    margin-bottom: 2rem;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.25);
    box-shadow: 
        0 15px 35px 0 rgba(31, 38, 135, 0.25),
        inset 0 2px 0 rgba(255, 255, 255, 0.4);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}}

.glass-header::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
    transition: left 0.6s;
}}

.glass-header:hover::before {{
    left: 100%;
}}

.glass-header:hover {{
    transform: translateY(-10px) scale(1.02);
    box-shadow: 
        0 25px 50px 0 rgba(31, 38, 135, 0.3),
        inset 0 2px 0 rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.35);

    }}
    .glass-header h1 {{
        color: white;
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }}
    
    .glass-header p {{
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        font-weight: 400;
        margin: 0;
    }}
    
    /* Differentiator box styling */
    .differentiator-box {{
        background: rgba(217, 234, 253, 0.3);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 4px solid {COLOR_DARKEST};
    }}
    
    /* Status indicators */
    .status-processing {{
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }}
    </style>
    """, unsafe_allow_html=True)

load_css()

# --- Make.com Integration Function ---
def send_to_make_com(business_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send business data to Make.com for market analysis and strategy generation"""
    
    # Proper URL validation
    if not MAKE_WEBHOOK_URL or MAKE_WEBHOOK_URL == "https://hook.us2.make.com/your_webhook_here":
        st.error("Make.com webhook URL not properly configured")
        st.info("Please update the MAKE_WEBHOOK_URL in the code with your actual webhook URL")
        return None
    
    try:
        # Prepare payload matching your Make.com scenario structure
        payload = {
            "business_profile": business_data
        }
        
        headers = {"Content-Type": "application/json"}
        
        # Show processing status
        st.markdown(f"""
        <div class='status-processing'>
            <h4>Processing Your Request</h4>
            <p><strong>Business:</strong> {business_data['business_name']}</p>
            <p><strong>Query:</strong> {business_data['business_type']} in {business_data['location']}</p>
            <p><strong>Target:</strong> {business_data['target_audience']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Send to Make.com with timeout
        response = requests.post(
            MAKE_WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=180  # Increased timeout
        )
        
        if response.status_code == 200:
            raw_response = response.text.strip()
        else:
            st.error(f"Make.com returned error {response.status_code}")
            st.info("Please check your Make.com scenario is active and properly configured")
            return None

    except requests.exceptions.Timeout:
        st.error("Request timeout - Make.com took too long to respond")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Connection error - Could not reach Make.com")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

# --- HEADER ---
st.markdown("""
<div class="glass-header">
    <h1>MarketLens: AI Strategy Generator</h1>
    <p>Intelligent 90-Day Marketing Strategy Powered by Make.com & Gemini</p>
</div>
""", unsafe_allow_html=True)

# --- USER INPUT FORM ---
st.markdown("""
<div class="glass-card">
    <h2>Business Profile & Strategy Controls</h2>
    <p>Fill in your business details to generate a customized marketing strategy</p>
</div>
""", unsafe_allow_html=True)

with st.form("business_form", clear_on_submit=False):
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("#### Business Information")
        name = st.text_input("Business Name", placeholder="e.g., PerfumeVerse")
        business_type = st.text_input("Product / Service Type", placeholder="e.g., Perfumes, Electronics, Clothing")
        location = st.text_input("Target Market / City", placeholder="e.g., Pakistan, Karachi, Lahore")
        target_audience = st.text_input("Target Audience", placeholder="e.g., 18-45 Male, Students, Professionals")
        more_details = st.text_area("More About Your Business", placeholder="Additional details for strategy")

    with col2:
        st.markdown("#### Strategy Settings")
        budget = st.number_input("Marketing Budget (PKR)", min_value=1000, step=1000, value=100000)
        strategy_mode = st.selectbox("Strategy Mode", ["Balanced", "Aggressive Growth", "Low Budget", "Creative Marketing"])
    
    submitted = st.form_submit_button("Generate Marketing Strategy", use_container_width=True)

# --- Initialize Session State ---
if 'make_result' not in st.session_state:
    st.session_state.make_result = None
if 'business_data' not in st.session_state:
    st.session_state.business_data = None

# --- ON SUBMIT LOGIC - Optimized ---
if submitted:
    if not all([name, business_type, location, target_audience]):
        st.error("Please fill in all mandatory fields.")
    else:
        # Prepare data for Make.com
        business_data = {
            "business_name": name,
            "business_type": business_type,
            "location": location,
            "target_audience": target_audience,
            "budget": budget,
            "strategy_mode": strategy_mode,
            "more_details": more_details or ""
        }

        # Send to Make.com for processing
        with st.spinner(" Analyzing market data and generating strategy..."):
            result = send_to_make_com(business_data)
        
        # Store result in session state
        if result:
            st.session_state.make_result = result
            st.session_state.business_data = business_data
            st.success("Market analysis complete! Strategy generated successfully.")
        else:
            st.warning("No valid response received. Please try any other query")

# --- Display Strategy & Visualizations ---
if st.session_state.make_result and st.session_state.business_data:
    parsed = st.session_state.make_result
    business_data = st.session_state.business_data
    
    st.markdown("---")
    
    # Strategy Report Header
    st.markdown(f"""
    <div class="glass-card">
        <h2>Strategy Report for {business_data['business_name']}</h2>
        <p>Your customized 90-day marketing strategy based on market analysis is ready!</p>
    </div>
    """, unsafe_allow_html=True)

    # 90-Day Strategy Roadmap Card
    key_diff = parsed.get("Key_Differentiator_Idea", "N/A")
    strategy_steps = parsed.get("Strategy_Summary", [])
    
    st.markdown(f"""
    <div class="glass-card">
        <h3>90-Day Strategy Roadmap</h3>
        <div class="differentiator-box">
            <strong>Key Differentiator:</strong> {key_diff}
        </div>
        <ul style="font-size:1.05rem; line-height:1.7;">
    """ + "".join([f"<li style='margin-bottom: 10px;'>{step}</li>" for step in strategy_steps]) + "</ul></div>", unsafe_allow_html=True)

    # Strategy Timeline (Plotly)
    if strategy_steps and hasattr(viz_utils, 'create_strategy_timeline'):
        try:
            fig_timeline = viz_utils.create_strategy_timeline(strategy_steps)
            fig_timeline.update_layout(
                plot_bgcolor=COLOR_LIGHTEST,
                paper_bgcolor=COLOR_LIGHTEST,
                font_color=COLOR_DARKEST
            )
            st.plotly_chart(fig_timeline, use_container_width=True, config={'displayModeBar': False})
        except Exception as e:
            st.warning(f"Could not generate timeline visualization: {e}")

    # Budget Allocation Card + Pie Chart
    st.markdown("<div class='glass-card'><h3>Budget Allocation</h3></div>", unsafe_allow_html=True)
    budget_alloc = parsed.get("Budget_Allocation_PKR", {})
    
    if budget_alloc:
        # Create budget visualization
        if hasattr(viz_utils, 'create_budget_pie_chart'):
            try:
                fig_budget = viz_utils.create_budget_pie_chart(budget_alloc)
                fig_budget.update_traces(marker=dict(colors=[COLOR_DARKEST, COLOR_MEDIUM, COLOR_LIGHT_ACCENT, '#6C757D', '#ADB5BD']))
                fig_budget.update_layout(
                    plot_bgcolor=COLOR_LIGHTEST,
                    paper_bgcolor=COLOR_LIGHTEST,
                    font_color=COLOR_DARKEST
                )
                st.plotly_chart(fig_budget, use_container_width=True, config={'displayModeBar': False})
            except Exception as e:
                st.warning(f"Could not generate budget chart: {e}")

        # Budget breakdown table
        budget_data = [
            {
                "Category": cat, 
                "Percentage": f"{pct}%", 
                "Amount": f"PKR {business_data['budget'] * pct / 100:,.0f}"
            }
            for cat, pct in budget_alloc.items()
        ]
        st.dataframe(pd.DataFrame(budget_data), use_container_width=True, hide_index=True)
    else:
        st.warning("No budget allocation data available in the response.")

    # SWOT Analysis as Glass Cards
    st.markdown("## SWOT Analysis")
    sw = parsed.get("SWOT_Analysis", {})
    swot_keys = ["Strengths", "Weaknesses", "Opportunities", "Threats"]
    cols = st.columns(4)
    
    for i, key in enumerate(swot_keys):
        items = sw.get(key, [])
        
        card_html = f"""
        <div class="glass-card">
            <h3>{key}</h3>
            <ul style="padding-left: 20px;">
        """
        if items:
            for item in items:
                card_html += f"<li style='margin-bottom: 8px;'>{item}</li>"
        else:
            card_html += "<li>No data available</li>"
        card_html += "</ul></div>"

        with cols[i]:
            st.markdown(card_html, unsafe_allow_html=True)

    # Export / Download Options
    st.markdown("---")
    st.markdown("""
    <div class="glass-card">
        <h3>Export Strategy</h3>
        <p>Download your complete strategy report for future reference</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download Full Report (JSON)",
            data=json.dumps(parsed, indent=2, ensure_ascii=False),
            file_name=f"{business_data['business_name']}_MarketLens_Report.json",
            mime="application/json",
            use_container_width=True
        )
    with col2:
        summary_text = f"""
MARKETLENS STRATEGY REPORT
==========================

Business: {business_data['business_name']}
Type: {business_data['business_type']}
Location: {business_data['location']}
Target Audience: {business_data['target_audience']}
Budget: PKR {business_data['budget']:,}
Strategy Mode: {business_data['strategy_mode']}

KEY INSIGHTS:
-------------
Key Differentiator: {parsed.get('Key_Differentiator_Idea', 'N/A')}

90-DAY STRATEGY:
----------------
{chr(10).join([f'{i+1}. {phase}' for i, phase in enumerate(parsed.get('Strategy_Summary', []))])}

BUDGET ALLOCATION:
-----------------
{chr(10).join([f'{cat}: {pct}% (PKR {(business_data["budget"] * pct / 100):,.0f})' for cat, pct in parsed.get('Budget_Allocation_PKR', {}).items()])}

SWOT ANALYSIS:
---------------
Strengths:
{chr(10).join([f'- {item}' for item in sw.get('Strengths', [])])}

Weaknesses:
{chr(10).join([f'- {item}' for item in sw.get('Weaknesses', [])])}

Opportunities:
{chr(10).join([f'- {item}' for item in sw.get('Opportunities', [])])}

Threats:
{chr(10).join([f'- {item}' for item in sw.get('Threats', [])])}
"""
        st.download_button(
            label="Download Executive Summary",
            data=summary_text,
            file_name=f"{business_data['business_name']}_Executive_Summary.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- Footer ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6c757d; padding: 20px;'>"
    "MarketLens AI © 2025"
    "</div>",
    unsafe_allow_html=True
)

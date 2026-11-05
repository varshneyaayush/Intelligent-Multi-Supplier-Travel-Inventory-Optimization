import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@1,500;1,600&display=swap');

/* Global Font & App Canvas */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    color: #2A2B27;
}

.stApp {
    background-color: #A5A79B;
    background-image: radial-gradient(circle at 10% 20%, rgba(232, 210, 181, 0.25) 0%, transparent 40%),
                      radial-gradient(circle at 90% 80%, rgba(89, 9, 7, 0.12) 0%, transparent 40%);
    background-attachment: fixed;
}

/* Remove Streamlit default header decoration */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    z-index: 10;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background: rgba(232, 210, 181, 0.92) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(165, 167, 155, 0.5) !important;
    box-shadow: 0 8px 32px 0 rgba(42, 43, 39, 0.12) !important;
}

section[data-testid="stSidebar"] div.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Hide default streamlit multipage navigation if present */
div[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Main Content Area */
.main .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1400px;
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(253, 252, 249, 0.88) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(232, 210, 181, 0.75) !important;
    box-shadow: 0 8px 32px 0 rgba(42, 43, 39, 0.08) !important;
    border-radius: 16px !important;
    padding: 1.25rem 1.5rem !important;
    margin-bottom: 1.25rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.glass-card:hover {
    box-shadow: 0 12px 40px 0 rgba(42, 43, 39, 0.16) !important;
}

.glass-panel {
    background: rgba(232, 210, 181, 0.80) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.55) !important;
    border-radius: 16px !important;
    padding: 1.25rem !important;
}

/* Burgundy Spotlight Banner */
.banner-burgundy {
    background: linear-gradient(135deg, #590907 0%, #690C0A 50%, #841513 100%) !important;
    color: #FDFCF9 !important;
    border-radius: 20px !important;
    padding: 1.75rem 2rem !important;
    box-shadow: 0 12px 40px 0 rgba(89, 9, 7, 0.35) !important;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.75rem !important;
}

.banner-burgundy h2 {
    color: #FDFCF9 !important;
    font-weight: 800 !important;
    margin-bottom: 0.5rem !important;
}

.banner-burgundy p {
    color: #E8D2B5 !important;
    font-size: 0.925rem !important;
    line-height: 1.55 !important;
}

/* Brand Typography */
h1, h2, h3, h4, h5, h6 {
    color: #590907 !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

/* Top Sticky Header */
.top-header-bar {
    background: rgba(232, 210, 181, 0.85) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(165, 167, 155, 0.5) !important;
    border-radius: 16px !important;
    padding: 0.9rem 1.5rem !important;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.75rem !important;
    box-shadow: 0 4px 20px rgba(42, 43, 39, 0.08) !important;
}

/* Pills and Badges */
.badge-pill {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-burgundy {
    background-color: #590907;
    color: #E8D2B5;
}

.badge-cream {
    background-color: #E8D2B5;
    color: #590907;
    border: 1px solid rgba(89, 9, 7, 0.25);
}

.badge-sage {
    background-color: rgba(165, 167, 155, 0.35);
    color: #2A2B27;
    border: 1px solid rgba(165, 167, 155, 0.6);
}

.badge-emerald {
    background-color: #d1fae5;
    color: #065f46;
    border: 1px solid #6ee7b7;
}

.badge-amber {
    background-color: #fef3c7;
    color: #92400e;
    border: 1px solid #fcd34d;
}

.badge-rose {
    background-color: #ffe4e6;
    color: #9f1239;
    border: 1px solid #fecdd3;
}

/* KPI Cards */
.kpi-card {
    background: rgba(253, 252, 249, 0.92) !important;
    border: 1px solid rgba(232, 210, 181, 0.9) !important;
    border-radius: 16px !important;
    padding: 1.25rem !important;
    box-shadow: 0 4px 24px rgba(42, 43, 39, 0.08) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(89, 9, 7, 0.15) !important;
}

.kpi-title {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #5C5E55;
    margin-bottom: 0.5rem;
}

.kpi-value {
    font-size: 2.1rem;
    font-weight: 800;
    color: #590907;
    line-height: 1;
}

.kpi-subtitle {
    font-size: 0.78rem;
    color: #75776C;
    margin-top: 0.4rem;
}

/* Streamlit Buttons Customization */
div.stButton > button {
    background-color: #590907 !important;
    color: #FDFCF9 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 0.5rem 1.1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(89, 9, 7, 0.25) !important;
}

div.stButton > button:hover {
    background-color: #751412 !important;
    color: #FFFFFF !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(89, 9, 7, 0.35) !important;
}

div.stButton > button:active {
    transform: translateY(0);
}

/* Secondary Button styling */
div.stButton > button[kind="secondary"] {
    background-color: rgba(253, 252, 249, 0.9) !important;
    color: #590907 !important;
    border: 1px solid rgba(89, 9, 7, 0.3) !important;
}

/* Sidebar Custom Nav Buttons */
.nav-item-btn {
    width: 100%;
    text-align: left;
    padding: 0.65rem 0.9rem;
    border-radius: 12px;
    font-size: 0.825rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    text-decoration: none !important;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.2s ease;
}

.nav-item-active {
    background: #590907 !important;
    color: #FDFCF9 !important;
    box-shadow: 0 4px 16px rgba(89, 9, 7, 0.35) !important;
    transform: translateX(4px);
}

.nav-item-inactive {
    background: rgba(253, 252, 249, 0.45);
    color: #2A2B27;
}

.nav-item-inactive:hover {
    background: rgba(253, 252, 249, 0.85);
    color: #590907;
    transform: translateX(2px);
}

/* Form Inputs, Selects, Sliders */
div[data-baseweb="select"] {
    border-radius: 10px !important;
}

div[data-baseweb="select"] > div {
    background-color: rgba(253, 252, 249, 0.9) !important;
    border-color: rgba(165, 167, 155, 0.6) !important;
    border-radius: 10px !important;
    color: #2A2B27 !important;
}

div[data-baseweb="input"] {
    background-color: rgba(253, 252, 249, 0.9) !important;
    border: 1px solid rgba(165, 167, 155, 0.6) !important;
    border-radius: 10px !important;
}

/* Streamlit Tabs */
button[data-baseweb="tab"] {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #5C5E55 !important;
    background: transparent !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 0.6rem 1.2rem !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #590907 !important;
    font-weight: 700 !important;
    border-bottom: 3px solid #590907 !important;
}

/* Dataframe & Table Styling */
div[data-testid="stDataFrame"] {
    background: rgba(253, 252, 249, 0.9) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(232, 210, 181, 0.8) !important;
    box-shadow: 0 4px 20px rgba(42, 43, 39, 0.06) !important;
    overflow: hidden !important;
}

/* Custom Table in HTML */
.custom-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.825rem;
}

.custom-table th {
    background: rgba(232, 210, 181, 0.5);
    color: #590907;
    font-weight: 700;
    text-align: left;
    padding: 0.75rem 1rem;
    border-bottom: 2px solid rgba(165, 167, 155, 0.4);
}

.custom-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid rgba(165, 167, 155, 0.25);
    color: #2A2B27;
}

.custom-table tr:hover td {
    background: rgba(232, 210, 181, 0.2);
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(165, 167, 155, 0.2);
}
::-webkit-scrollbar-thumb {
    background: rgba(89, 9, 7, 0.35);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(89, 9, 7, 0.6);
}
</style>
"""

def inject_custom_theme():
    """Injects high-fidelity custom CSS matching the original React OptiSupply AI application."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import pytz
from supabase import create_client, Client

# ==============================================================================
# --- 1. CONFIGURATION & FULL COLOUR DARK THEME STYLING ---
# ==============================================================================

# Initialize page configuration as the very first Streamlit command
st.set_page_config(
    page_title="World Cup 2026 Prediction League",
    page_icon="🏆",
    layout="wide"
)
def is_tournament_locked():
    """
    Returns True if the current time has passed the tournament kickoff:
    Thursday, June 12, 2026, at 5:00 PM UK Time (Europe/London).
    """
    try:
        uk_tz = pytz.timezone('Europe/London')
        deadline = uk_tz.localize(datetime(2026, 7, 12, 17, 0, 0))
        now_uk = datetime.now(uk_tz)
        return now_uk >= deadline
    except Exception:
        # Fallback safeguard
        return False

# Evaluate global tournament lockout status
global_tournament_lock = is_tournament_locked()

# Comprehensive sidebar override to forcefully darken all navigation text elements
st.markdown(
    """
    <style>
    /* Absolute target for Streamlit's sidebar wrapper to force dark text */
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div {
        color: #0f172a !important;
        font-weight: 700 !important;
        text-shadow: none !important;
        -webkit-text-fill-color: #0f172a !important;
    }
    
    /* Target the unselected radio item labels explicitly */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] .st-emotion-cache-170701z,
    [data-testid="stSidebar"] [data-checked="false"] {
        color: #0f172a !important;
        font-weight: 700 !important;
        text-shadow: none !important;
    }

    /* EXCLUSIVE FIX: Force white text inside the Select Box container elements */
    [data-testid="stSidebar"] div[data-baseweb="select"] *,
    [data-testid="stSidebar"] div[data-baseweb="select"] span,
    [data-testid="stSidebar"] div[data-baseweb="select"] div,
    [data-testid="stSidebar"] svg {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Unified Main Application Styling, Background & Match Card Setup
st.markdown("""
    <style>
    /* Background Image setup */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.2), rgba(15, 23, 42, 0.4)),
                    url("https://cdn-media.theathletic.com/cdn-cgi/image/width=1000,quality=70,format=auto/https://cdn-media.theathletic.com/vwYC1qZfTwfm_3qmyXkIC5Rja_1440x960.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Main body typography - Explicitly isolated only to the main content panel */
    [data-testid="stMain"] p, 
    [data-testid="stMain"] label, 
    [data-testid="stMain"] .stMarkdown, 
    [data-testid="stMain"] .stText, 
    [data-testid="stMain"] [data-testid="stWidgetLabel"] p {
        color: #f8fafc !important;
        font-weight: 500 !important;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8);
    }
    
    /* Main header styling rules */
    [data-testid="stMain"] h1, 
    [data-testid="stMain"] h2, 
    [data-testid="stMain"] h3, 
    [data-testid="stMain"] h4 {
        color: #ffffff !important;
        text-transform: uppercase;
        font-weight: 800 !important;
        letter-spacing: 0.5px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9);
    }

    /* Container blocks for content panels */
    [data-testid="stExpander"], [data-testid="stTabContent"], .stTabs {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
    }

    /* Select boxes styling */
    div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.95) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }
    
    /* GLOBAL BUTTON RULE: Unified targets for standalone buttons, form submit buttons, and disabled layouts */
    div.stButton > button,
    div.stFormSubmitButton > button,
    div.stButton > button:disabled,
    div.stFormSubmitButton > button:disabled {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        width: 100% !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 6px !important;
        padding: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
    }
    
    /* Maintains a clear blue backdrop context if elements get toggled to unclickable states */
    div.stButton > button:disabled,
    div.stFormSubmitButton > button:disabled {
        opacity: 0.75 !important;
        cursor: not-allowed !important;
    }
    
    /* Interactive states configuration rule mapping */
    div.stButton > button:hover:not(:disabled),
    div.stFormSubmitButton > button:hover:not(:disabled) {
        background-color: #1d4ed8 !important;
    }
    
    .lock-badge-banner {
        background-color: rgba(220, 38, 38, 0.9);
        color: #ffffff !important;
        border: 1px solid #ef4444;
        padding: 12px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }

    /* MATCH CARD IMPROVEMENTS: Centered larger flags sitting above single line text */
    .mc-team-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .mc-flag {
        font-size: 2.2rem !important;
        line-height: 1.1 !important;
        margin-bottom: 4px;
        display: block;
    }
    .mc-name {
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        width: 100%;
        display: block;
        text-transform: uppercase;
    }
    .mc-vs-block {
        color: #94a3b8;
        font-weight: 800;
        font-size: 0.9rem;
        text-align: center;
        align-self: center;
        margin-top: 15px; /* Pushes 'VS' downward to align better horizontally with the names below the flags */
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 2. SECURITY HELPER ---
# ==============================================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==============================================================================
# --- 3. GLOBAL SUPABASE CONNECTION INIT ---
# ==============================================================================
@st.cache_resource
def init_supabase():
    try:
        SUPABASE_URL = st.secrets["connections"]["supabase"]["url"]
        SUPABASE_KEY = st.secrets["connections"]["supabase"]["key"]
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error("Could not establish a connection to your Supabase database. Please double check your secrets parameters.")
        st.stop()

# Initialize the cached connection
supabase = init_supabase()

# ==============================================================================
# --- 4. GLOBAL TEAMS & FLAGS MAP ---
# ==============================================================================
FLAGS = {
    "Mexico": "🇲🇽 MEXICO", "South Africa": "🇿🇦 SOUTH AFRICA", "Rep. of Korea": "🇰🇷 REP. OF KOREA", "Czech Rep.": "🇨🇿 CZECH REP.",
    "Canada": "🇨🇦 CANADA", "Bosnia/Herzeg Mom.": "🇧🇦 BOSNIA/HERZEG.", "Bosnia/Herzeg.": "🇧🇦 BOSNIA/HERZEG.", "Qatar": "🇶🇦 QATAR", "Switzerland": "🇨🇭 SWITZERLAND",
    "Brazil": "🇧🇷 BRAZIL", "Morocco": "🇲🇦 MOROCCO", "Haiti": "🇲🇹 HAITI", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 SCOTLAND",
    "USA": "🇺🇸 USA", "Paraguay": "🇵🇾 PARAGUAY", "Australia": "🇦🇺 AUSTRALIA", "Turkey": "🇹🇷 TURKEY",
    "Germany": "🇩🇪 GERMANY", "Curaçao": "🇨🇼 CURAÇAO", "Ivory Coast": "🇨🇮 IVORY COAST", "Ecuador": "🇪🇨 ECUADOR",
    "Netherlands": "🇳🇱 NETHERLANDS", "Japan": "🇯🇵 JAPAN", "Sweden": "🇸🇪 SWEDEN", "Tunisia": "🇹🇳 TUNISIA",
    "Belgium": "🇧🇪 BELGIUM", "Egypt": "🇪🇬 EGYPT", "IR Iran": "🇮🇷 IR IRAN", "New Zealand": "🇳🇿 NEW ZEALAND",
    "Spain": "🇪🇸 SPAIN", "Cape Verde": "🇨🇻 CAPE VERDE", "Saudi Arabia": "🇸🇦 SAUDI ARABIA", "Uruguay": "🇺🇾 URUGUAY",
    "France": "🇫🇷 FRANCE", "Senegal": "🇸🇳 SENEGAL", "Iraq": "🇮🇶 IRAQ", "Norway": "🇳🇴 NORWAY",
    "Argentina": "🇦🇷 ARGENTINA", "Algeria": "🇩🇿 ALGERIA", "Austria": "🇦🇹 AUSTRIA", "Jordan": "🇯🇴 JORDAN",
    "Portugal": "🇵🇹 PORTUGAL", "DR Congo": "🇨🇩 DR CONGO", "Uzbekistan": "🇺🇿 UZBEKISTAN", "Colombia": "🇨🇴 COLOMBIA",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENGLAND", "Croatia": "🇭🇷 CROATIA", "Ghana": "🇬🇭 GHANA", "Panama": "🇵🇦 PANAMA"
}

def fmt_team(name):
    return FLAGS.get(name, str(name).upper()) if name else "TBD"

# Helper to split flag emoji out from text name safely for custom formatting layout layers
def split_flag_and_name(formatted_string):
    if not formatted_string or formatted_string == "TBD":
        return "", "TBD"
    parts = formatted_string.split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", formatted_string

# ==============================================================================

# --- 5. DATA STRUCTURES (GROUPS & CHRONOLOGICAL FIXTURES) ---
# ==============================================================================
GROUPS = {
    "Group A": ["Mexico", "South Africa", "Rep. of Korea", "Czech Rep."],
    "Group B": ["Canada", "Bosnia/Herzeg.", "Qatar", "Switzerland"],
    "Group C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "Group D": ["USA", "Paraguay", "Australia", "Turkey"],
    "Group E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "Group F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "Group G": ["Belgium", "Egypt", "IR Iran", "New Zealand"],
    "Group H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "Group I": ["France", "Senegal", "Iraq", "Norway"],
    "Group J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "Group K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "Group L": ["England", "Croatia", "Ghana", "Panama"]
}

CHRONO_MATCHES = {
    "Group A": [
        {"id": 1, "home": "Mexico", "away": "South Africa"},
        {"id": 2, "home": "Rep. of Korea", "away": "Czech Rep."},
        {"id": 25, "home": "Czech Rep.", "away": "South Africa"},
        {"id": 28, "home": "Mexico", "away": "Rep. of Korea"},
        {"id": 53, "home": "Czech Rep.", "away": "Mexico"},
        {"id": 54, "home": "South Africa", "away": "Rep. of Korea"}
    ],
    "Group B": [
        {"id": 3, "home": "Canada", "away": "Bosnia/Herzeg."},
        {"id": 8, "home": "Qatar", "away": "Switzerland"},
        {"id": 26, "home": "Switzerland", "away": "Bosnia/Herzeg."},
        {"id": 27, "home": "Canada", "away": "Qatar"},
        {"id": 51, "home": "Switzerland", "away": "Canada"},
        {"id": 52, "home": "Bosnia/Herzeg.", "away": "Qatar"}
    ],
    "Group C": [
        {"id": 7, "home": "Brazil", "away": "Morocco"},
        {"id": 5, "home": "Haiti", "away": "Scotland"},
        {"id": 30, "home": "Scotland", "away": "Morocco"},
        {"id": 29, "home": "Brazil", "away": "Haiti"},
        {"id": 49, "home": "Scotland", "away": "Brazil"},
        {"id": 50, "home": "Morocco", "away": "Haiti"}
    ],
    "Group D": [
        {"id": 4, "home": "USA", "away": "Paraguay"},
        {"id": 6, "home": "Australia", "away": "Turkey"},
        {"id": 32, "home": "USA", "away": "Australia"},
        {"id": 31, "home": "Turkey", "away": "Paraguay"},
        {"id": 59, "home": "Turkey", "away": "USA"},
        {"id": 60, "home": "Paraguay", "away": "Australia"}
    ],
    "Group E": [
        {"id": 10, "home": "Germany", "away": "Curaçao"},
        {"id": 9, "home": "Ivory Coast", "away": "Ecuador"},
        {"id": 33, "home": "Germany", "away": "Ivory Coast"},
        {"id": 34, "home": "Ecuador", "away": "Curaçao"},
        {"id": 56, "home": "Ecuador", "away": "Germany"},
        {"id": 55, "home": "Curaçao", "away": "Ivory Coast"}
    ],
    "Group F": [
        {"id": 11, "home": "Netherlands", "away": "Japan"},
        {"id": 12, "home": "Sweden", "away": "Tunisia"},
        {"id": 35, "home": "Netherlands", "away": "Sweden"},
        {"id": 36, "home": "Tunisia", "away": "Japan"},
        {"id": 58, "home": "Tunisia", "away": "Netherlands"},
        {"id": 57, "home": "Japan", "away": "Sweden"}
    ],
    "Group G": [
        {"id": 16, "home": "Belgium", "away": "Egypt"},
        {"id": 15, "home": "IR Iran", "away": "New Zealand"},
        {"id": 39, "home": "Belgium", "away": "IR Iran"},
        {"id": 40, "home": "New Zealand", "away": "Egypt"},
        {"id": 64, "home": "New Zealand", "away": "Belgium"},
        {"id": 63, "home": "Egypt", "away": "IR Iran"}
    ],
    "Group H": [
        {"id": 14, "home": "Spain", "away": "Cape Verde"},
        {"id": 13, "home": "Saudi Arabia", "away": "Uruguay"},
        {"id": 38, "home": "Spain", "away": "Saudi Arabia"},
        {"id": 37, "home": "Uruguay", "away": "Cape Verde"},
        {"id": 66, "home": "Uruguay", "away": "Spain"},
        {"id": 65, "home": "Cape Verde", "away": "Saudi Arabia"}
    ],
    "Group I": [
        {"id": 17, "home": "France", "away": "Senegal"},
        {"id": 18, "home": "Iraq", "away": "Norway"},
        {"id": 42, "home": "France", "away": "Iraq"},
        {"id": 41, "home": "Norway", "away": "Senegal"},
        {"id": 61, "home": "Norway", "away": "France"},
        {"id": 62, "home": "Senegal", "away": "Iraq"}
    ],
    "Group J": [
        {"id": 19, "home": "Argentina", "away": "Algeria"},
        {"id": 20, "home": "Austria", "away": "Jordan"},
        {"id": 43, "home": "Argentina", "away": "Austria"},
        {"id": 44, "home": "Jordan", "away": "Algeria"},
        {"id": 70, "home": "Jordan", "away": "Argentina"},
        {"id": 69, "home": "Algeria", "away": "Austria"}
    ],
    "Group K": [
        {"id": 23, "home": "Portugal", "away": "DR Congo"},
        {"id": 24, "home": "Uzbekistan", "away": "Colombia"},
        {"id": 47, "home": "Portugal", "away": "Uzbekistan"},
        {"id": 48, "home": "Colombia", "away": "DR Congo"},
        {"id": 71, "home": "Colombia", "away": "Portugal"},
        {"id": 72, "home": "DR Congo", "away": "Uzbekistan"}
    ],
    "Group L": [
        {"id": 22, "home": "England", "away": "Croatia"},
        {"id": 21, "home": "Ghana", "away": "Panama"},
        {"id": 45, "home": "England", "away": "Ghana"},
        {"id": 46, "home": "Panama", "away": "Croatia"},
        {"id": 67, "home": "Panama", "away": "England"},
        {"id": 68, "home": "Croatia", "away": "Ghana"}
    ]
}

FIFA_REAL_METADATA = {
    # --- Group Stages ---
    1: {"date": "11 June", "time": "8:00 PM BST", "venue": "Mexico City"},
    2: {"date": "12 June", "time": "3:00 AM BST", "venue": "Guadalajara"},
    3: {"date": "12 June", "time": "8:00 PM BST", "venue": "Toronto"},
    4: {"date": "13 June", "time": "2:00 AM BST", "venue": "Los Angeles"},
    5: {"date": "14 June", "time": "2:00 AM BST", "venue": "Boston"},
    6: {"date": "14 June", "time": "5:00 AM BST", "venue": "Vancouver"},
    7: {"date": "13 June", "time": "11:00 PM BST", "venue": "New York/NJ"},
    8: {"date": "13 June", "time": "8:00 PM BST", "venue": "San Francisco"},
    9: {"date": "15 June", "time": "12:00 AM BST", "venue": "Philadelphia"},
    10: {"date": "14 June", "time": "6:00 PM BST", "venue": "Houston"},
    11: {"date": "14 June", "time": "9:00 PM BST", "venue": "Dallas"},
    12: {"date": "15 June", "time": "3:00 AM BST", "venue": "Monterrey"},
    13: {"date": "15 June", "time": "11:00 PM BST", "venue": "Miami"},
    14: {"date": "15 June", "time": "5:00 PM BST", "venue": "Atlanta"},
    15: {"date": "16 June", "time": "2:00 AM BST", "venue": "Los Angeles"},
    16: {"date": "15 June", "time": "8:00 PM BST", "venue": "Seattle"},
    17: {"date": "16 June", "time": "8:00 PM BST", "venue": "New York/NJ"},
    18: {"date": "16 June", "time": "11:00 PM BST", "venue": "Boston"},
    19: {"date": "17 June", "time": "2:00 AM BST", "venue": "Kansas City"},
    20: {"date": "17 June", "time": "5:00 AM BST", "venue": "San Francisco"},
    21: {"date": "18 June", "time": "12:00 AM BST", "venue": "Toronto"},
    22: {"date": "17 June", "time": "9:00 PM BST", "venue": "Dallas"},
    23: {"date": "17 June", "time": "6:00 PM BST", "venue": "Houston"},
    24: {"date": "18 June", "time": "3:00 AM BST", "venue": "Mexico City"},
    25: {"date": "18 June", "time": "5:00 PM BST", "venue": "Atlanta"},
    26: {"date": "18 June", "time": "8:00 PM BST", "venue": "Los Angeles"},
    27: {"date": "18 June", "time": "11:00 PM BST", "venue": "Vancouver"},
    28: {"date": "19 June", "time": "2:00 AM BST", "venue": "Guadalajara"},
    29: {"date": "20 June", "time": "1:30 AM BST", "venue": "Philadelphia"},
    30: {"date": "19 June", "time": "11:00 PM BST", "venue": "Boston"},
    31: {"date": "20 June", "time": "4:00 AM BST", "venue": "San Francisco"},
    32: {"date": "19 June", "time": "8:00 PM BST", "venue": "Seattle"},
    33: {"date": "20 June", "time": "9:00 PM BST", "venue": "Toronto"},
    34: {"date": "21 June", "time": "1:00 AM BST", "venue": "Kansas City"},
    35: {"date": "20 June", "time": "6:00 PM BST", "venue": "Houston"},
    36: {"date": "21 June", "time": "5:00 AM BST", "venue": "Monterrey"},
    37: {"date": "21 June", "time": "11:00 PM BST", "venue": "Miami"},
    38: {"date": "21 June", "time": "5:00 PM BST", "venue": "Atlanta"},
    39: {"date": "21 June", "time": "8:00 PM BST", "venue": "Los Angeles"},
    40: {"date": "22 June", "time": "2:00 AM BST", "venue": "Vancouver"},
    41: {"date": "23 June", "time": "1:00 AM BST", "venue": "New York/NJ"},
    42: {"date": "22 June", "time": "10:00 PM BST", "venue": "Philadelphia"},
    43: {"date": "22 June", "time": "6:00 PM BST", "venue": "Dallas"},
    44: {"date": "23 June", "time": "4:00 AM BST", "venue": "San Francisco"},
    45: {"date": "23 June", "time": "9:00 PM BST", "venue": "Boston"},
    46: {"date": "24 June", "time": "12:00 AM BST", "venue": "Toronto"},
    47: {"date": "23 June", "time": "6:00 PM BST", "venue": "Houston"},
    48: {"date": "24 June", "time": "3:00 AM BST", "venue": "Guadalajara"},
    49: {"date": "24 June", "time": "11:00 PM BST", "venue": "Miami"},
    50: {"date": "24 June", "time": "11:00 PM BST", "venue": "Atlanta"},
    51: {"date": "24 June", "time": "8:00 PM BST", "venue": "Vancouver"},
    52: {"date": "24 June", "time": "8:00 PM BST", "venue": "Seattle"},
    53: {"date": "25 June", "time": "2:00 AM BST", "venue": "Mexico City"},
    54: {"date": "25 June", "time": "2:00 AM BST", "venue": "Monterrey"},
    55: {"date": "25 June", "time": "9:00 PM BST", "venue": "Philadelphia"},
    56: {"date": "25 June", "time": "9:00 PM BST", "venue": "New York/NJ"},
    57: {"date": "26 June", "time": "12:00 AM BST", "venue": "Dallas"},
    58: {"date": "26 June", "time": "12:00 AM BST", "venue": "Kansas City"},
    59: {"date": "26 June", "time": "3:00 AM BST", "venue": "Los Angeles"},
    60: {"date": "26 June", "time": "3:00 AM BST", "venue": "San Francisco"},
    61: {"date": "26 June", "time": "8:00 PM BST", "venue": "Boston"},
    62: {"date": "26 June", "time": "8:00 PM BST", "venue": "Toronto"},
    63: {"date": "27 June", "time": "4:00 AM BST", "venue": "Seattle"},
    64: {"date": "27 June", "time": "4:00 AM BST", "venue": "Vancouver"},
    65: {"date": "27 June", "time": "1:00 AM BST", "venue": "Houston"},
    66: {"date": "27 June", "time": "1:00 AM BST", "venue": "Guadalajara"},
    67: {"date": "27 June", "time": "10:00 PM BST", "venue": "New York/NJ"},
    68: {"date": "27 June", "time": "10:00 PM BST", "venue": "Philadelphia"},
    69: {"date": "28 June", "time": "3:00 AM BST", "venue": "Kansas City"},
    70: {"date": "28 June", "time": "3:00 AM BST", "venue": "Dallas"},
    71: {"date": "28 June", "time": "12:30 AM BST", "venue": "Miami"},
    72: {"date": "28 June", "time": "12:30 AM BST", "venue": "Atlanta"},
    # --- Knockout Rounds ---
    73: {"date": "28 June", "time": "8:00 PM BST", "venue": "Los Angeles"},
    76: {"date": "29 June", "time": "6:00 PM BST", "venue": "Houston"},
    74: {"date": "29 June", "time": "9:30 PM BST", "venue": "Boston"},
    75: {"date": "30 June", "time": "2:00 AM BST", "venue": "Monterrey"},
    78: {"date": "30 June", "time": "6:00 PM BST", "venue": "Dallas"},
    77: {"date": "30 June", "time": "10:00 PM BST", "venue": "New York/NJ"},
    79: {"date": "1 July", "time": "2:00 AM BST", "venue": "Mexico City"},
    80: {"date": "1 July", "time": "5:00 PM BST", "venue": "Atlanta"},
    82: {"date": "1 July", "time": "9:00 PM BST", "venue": "Seattle"},
    81: {"date": "2 July", "time": "1:00 AM BST", "venue": "San Francisco"},
    84: {"date": "2 July", "time": "8:00 PM BST", "venue": "Los Angeles"},
    83: {"date": "3 July", "time": "12:00 AM BST", "venue": "Toronto"},
    85: {"date": "3 July", "time": "4:00 AM BST", "venue": "Vancouver"},
    88: {"date": "3 July", "time": "7:00 PM BST", "venue": "Dallas"},
    86: {"date": "3 July", "time": "11:00 PM BST", "venue": "Miami"},
    87: {"date": "4 July", "time": "2:30 AM BST", "venue": "Kansas City"},
    90: {"date": "4 July", "time": "6:00 PM BST", "venue": "Houston"},
    89: {"date": "4 July", "time": "10:00 PM BST", "venue": "Philadelphia"},
    91: {"date": "5 July", "time": "9:00 PM BST", "venue": "New York/NJ"},
    92: {"date": "6 July", "time": "1:00 AM BST", "venue": "Mexico City"},
    93: {"date": "6 July", "time": "8:00 PM BST", "venue": "Dallas"},
    94: {"date": "7 July", "time": "1:00 AM BST", "venue": "Seattle"},
    95: {"date": "7 July", "time": "5:00 PM BST", "venue": "Atlanta"},
    96: {"date": "7 July", "time": "9:00 PM BST", "venue": "Vancouver"},
    97: {"date": "9 July", "time": "9:00 PM BST", "venue": "Boston"},
    98: {"date": "10 July", "time": "8:00 PM BST", "venue": "Los Angeles"},
    99: {"date": "11 July", "time": "10:00 PM BST", "venue": "Miami"},
    100: {"date": "12 July", "time": "2:00 AM BST", "venue": "Kansas City"},
    101: {"date": "14 July", "time": "8:00 PM BST", "venue": "Dallas"},
    102: {"date": "15 July", "time": "8:00 PM BST", "venue": "Atlanta"},
    103: {"date": "18 July", "time": "10:00 PM BST", "venue": "Miami"},
    104: {"date": "19 July", "time": "8:00 PM BST", "venue": "New York/NJ"}
}

# Dynamic identifier-driven layout tracking structure replacing the old static list maps
DYNAMIC_R32_CONFIG = {
    "Match_73": {"home": ("Group A", "2nd"), "away": ("Group B", "2nd")},
    "Match_74": {"home": ("Group E", "1st"), "away_lookup": "3-ABCDF"},
    "Match_75": {"home": ("Group F", "1st"), "away": ("Group C", "2nd")},
    "Match_76": {"home": ("Group C", "1st"), "away": ("Group F", "2nd")},
    "Match_77": {"home": ("Group I", "1st"), "away_lookup": "3-CDFGH"},
    "Match_78": {"home": ("Group E", "2nd"), "away": ("Group I", "2nd")},
    "Match_79": {"home": ("Group A", "1st"), "away_lookup": "3-CEFHI"},
    "Match_80": {"home": ("Group L", "1st"), "away_lookup": "3-EHIJK"},
    "Match_81": {"home": ("Group D", "1st"), "away_lookup": "3-BEFIJ"},
    "Match_82": {"home": ("Group G", "1st"), "away_lookup": "3-AEHIJ"},
    "Match_83": {"home": ("Group K", "2nd"), "away": ("Group L", "2nd")},
    "Match_84": {"home": ("Group H", "1st"), "away": ("Group J", "2nd")},
    "Match_85": {"home": ("Group B", "1st"), "away_lookup": "3-EFGIJ"},
    "Match_86": {"home": ("Group J", "1st"), "away": ("Group H", "2nd")},
    "Match_87": {"home": ("Group K", "1st"), "away_lookup": "3-DEIJL"},
    "Match_88": {"home": ("Group D", "2nd"), "away": ("Group G", "2nd")}
}

# ==============================================================================
# --- 6. DATABASE HELPER WRAPPERS ---
# ==============================================================================
@st.cache_data
def db_fetch_user_predictions(user_id, league_id):
    res = supabase.table("predictions").select("match_key, score_value").eq("user_id", user_id).eq("league_id", league_id).execute()
    preds = {}
    if res.data:
        for row in res.data:
            preds[row["match_key"]] = row["score_value"]
    return preds

def db_save_prediction(user_id, league_id, match_key, value):
    if value is None:
        return
    val_str = str(value).strip()
    if (val_str == "" or val_str.startswith("Select") or val_str.startswith("W") or val_str.startswith("1st") or val_str.startswith("2nd") or "Winner" in val_str):
        return

    try:
        score_val = int(val_str)
    except ValueError:
        return

    supabase.table("predictions").upsert({
        "user_id": user_id,
        "league_id": league_id,
        "match_key": match_key,
        "score_value": score_val
    }, on_conflict="user_id,league_id,match_key").execute()

@st.cache_data
def db_fetch_locked_status(user_id, league_id):
    res = supabase.table("predictions").select("match_key, is_locked").eq("user_id", user_id).eq("league_id", league_id).execute()
    locked_keys = set()
    if res.data:
        for row in res.data:
            if row["is_locked"]:
                locked_keys.add(row["match_key"])
    return locked_keys

def db_lock_predictions(user_id, league_id, match_keys_list):
    """Updates all selected match keys for a user in ONE single network request."""
    if not match_keys_list:
        return
    try:
        supabase.table("predictions") \
            .update({"is_locked": True}) \
            .eq("user_id", user_id) \
            .eq("league_id", league_id) \
            .in_("match_key", match_keys_list) \
            .execute()
    except Exception as e:
        st.error(f"Failed to bulk update predictions: {e}")

@st.cache_data
def db_fetch_user_leagues(user_id):
    res = supabase.table("league_members").select("leagues(id, name, creator_id)").eq("user_id", user_id).execute()
    leagues_list = []
    if res.data:
        for row in res.data:
            if row.get("leagues"):
                leagues_list.append({
                    "name": row["leagues"]["name"],
                    "id": row["leagues"]["id"],
                    "creator_id": row["leagues"]["creator_id"]
                })
    return leagues_list

@st.cache_data
def db_fetch_league_actual_results(league_id):
    res = supabase.table("actual_results").select("match_key, score_value").eq("league_id", league_id).execute()
    results = {"group": {}, "ko_winners": {}, "third_place": "", "finalists": []}
    if res.data:
        for row in res.data:
            key = row["match_key"]
            val = row["score_value"]
            if key.startswith("Match_") and (key.endswith("_h") or key.endswith("_a")):
                results["group"][key] = val
            elif key == "Match_103_winner":
                results["third_place"] = val
            else:
                try:
                    results["ko_winners"][key] = int(val)
                except:
                    results["ko_winners"][key] = val
    return results

def db_save_league_actual_result(league_id, match_key, value):
    supabase.table("actual_results").upsert({
        "league_id": league_id,
        "match_key": match_key,
        "score_value": str(value)
    }, on_conflict="league_id,match_key").execute()

def db_delete_league_actual_result(league_id, match_key):
    supabase.table("actual_results").delete().eq("league_id", league_id).eq("match_key", match_key).execute()

# --- PERSISTENT TIE BREAKER EXTRA DRIVERS ---
@st.cache_data
def db_fetch_group_tie_breakers(user_id, league_id):
    """Retrieves all locked tie breakers from the database table."""
    try:
        res = supabase.table("tie_breakers").select("group_name, team_order, is_locked").eq("user_id", user_id).eq("league_id", league_id).execute()
        return res.data if res.data else []
    except Exception:
        return []

def db_save_group_tie_breaker(user_id, league_id, group_name, team_order):
    """Saves or updates manual level point group resolution listings inside Supabase."""
    try:
        supabase.table("tie_breakers").upsert({
            "user_id": user_id,
            "league_id": league_id,
            "group_name": group_name,
            "team_order": team_order,
            "is_locked": True
        }, on_conflict="user_id,league_id,group_name").execute()
    except Exception as e:
        st.error(f"Failed to persist tie-breaker structure to database: {e}")

@st.cache_data
def fetch_supabase_wildcard_mapping(combination_str):
    try:
        res = supabase.table("assign_third").select("*").eq("group_combination", combination_str).execute()
        if res.data:
            return res.data[0]
    except Exception:
        pass
    return None

# --- NEW HELPER FUNCTION: GROUP STAGE COMPLETENESS CHECK ---
def check_group_stage_completion(user_preds):
    total_group_matches = 72
    completed_matches = 0

    for mid in range(1, total_group_matches + 1):
        kh = f"Match_{mid}_h"
        ka = f"Match_{mid}_a"
        if user_preds.get(kh) is not None and user_preds.get(ka) is not None:
            completed_matches += 1

    percent = int((completed_matches / total_group_matches) * 100)
    return completed_matches, total_group_matches, percent

# --- FINAL TICKER WORKSPACE ENGINE (DYNAMIC ALL ROUNDS + DISPLAY STRINGS) ---
@st.cache_data
def calculate_live_ticker_html(league_id):
    # Fetch existing official admin results
    actual = db_fetch_league_actual_results(league_id)

    # Helper: Fetch custom display string from the new table
    def get_display_text(mid):
        try:
            res = supabase.table("actual_display_strings").select("display_text")\
                .eq("league_id", league_id).eq("match_key", f"Match_{mid}").execute()
            return res.data[0]["display_text"] if res.data else None
        except:
            return None

    # 1. Start with our baseline group stage match data
    flat_matches = {}
    for g_name, fixtures in CHRONO_MATCHES.items():
        for f in fixtures:
            flat_matches[int(f["id"])] = {"home": f["home"], "away": f["away"]}

    # 2. Dynamically extract live knockout participants
    try:
        bracket = resolve_bracket_teams(None, target_is_actual=True, actual_results_obj=actual)
        r32 = bracket.get("r32_pairings", {})
        ko_choices = actual.get("ko_winners", {})

        def clean_slot(team_val, fallback):
            if not team_val or str(team_val).strip() in ["", "None", "1", "2", "TBD"]:
                return fallback
            return str(team_val).strip()

        def get_match_winner_name(m_id):
            choice = str(ko_choices.get(f"Match_{m_id}", ""))
            if choice == "1" or choice == "2":
                if m_id <= 88:
                    pair = r32.get(f"Match_{m_id}", ("TBD", "TBD"))
                    return clean_slot(pair[0] if choice == "1" else pair[1], f"Winner M{m_id}")
                else:
                    parents = {
                        89: (74, 77), 90: (73, 75), 91: (76, 78), 92: (79, 80),
                        93: (83, 84), 94: (81, 82), 95: (86, 88), 96: (85, 87),
                        97: (89, 90), 98: (93, 94), 99: (91, 92), 100: (95, 96),
                        101: (97, 98), 102: (99, 100), 104: (101, 102)
                    }
                    if m_id in parents:
                        p1, p2 = parents[m_id]
                        return get_match_winner_name(p1 if choice == "1" else p2)
            elif choice != "": return choice
            return f"Winner M{m_id}"

        def get_match_loser_name(m_id):
            choice = str(ko_choices.get(f"Match_{m_id}", ""))
            if choice == "1" or choice == "2":
                opposite = "2" if choice == "1" else "1"
                parents = {101: (97, 98), 102: (99, 100)}
                p1, p2 = parents.get(m_id, (0, 0))
                if p1: return get_match_winner_name(p1 if opposite == "1" else p2)
            return f"Loser M{m_id}"

        for m in range(73, 105):
            m_key = f"Match_{m}"
            if m <= 88:
                pair = r32.get(m_key, ("TBD", "TBD"))
                h, a = clean_slot(pair[0], f"{m_key}_H"), clean_slot(pair[1], f"{m_key}_A")
            elif m in [89, 90, 91, 92, 93, 94, 95, 96]:
                p1, p2 = {89:(74,77), 90:(73,75), 91:(76,78), 92:(79,80), 93:(83,84), 94:(81,82), 95:(86,88), 96:(85,87)}[m]
                h, a = get_match_winner_name(p1), get_match_winner_name(p2)
            elif m in [97, 98, 99, 100]:
                p1, p2 = {97:(89,90), 98:(93,94), 99:(91,92), 100:(95,96)}[m]
                h, a = get_match_winner_name(p1), get_match_winner_name(p2)
            elif m in [101, 102]:
                p1, p2 = {101:(97,98), 102:(99,100)}[m]
                h, a = get_match_winner_name(p1), get_match_winner_name(p2)
            elif m == 103: h, a = get_match_loser_name(101), get_match_loser_name(102)
            elif m == 104: h, a = get_match_winner_name(101), get_match_winner_name(102)
            flat_matches[m] = {"home": h, "away": a}
    except Exception:
        for m in range(73, 105):
            if m not in flat_matches: flat_matches[m] = {"home": f"TBD (M{m})", "away": f"TBD (M{m})"}

    CHRONO_SEQUENCE = [
        1, 2, 3, 4, 8, 7, 5, 6, 10, 11, 9, 12, 14, 16, 13, 15, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 30, 27, 28, 29, 31, 32, 33, 34, 35, 36, 37, 38,
        39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
        57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72,
        73, 76, 74, 75, 78, 77, 79, 80, 82, 81, 84, 83, 85, 88, 86, 87,
        90, 89, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104
    ]

    completed_elements = []
    completed_ids = set()
    for mid in CHRONO_SEQUENCE:
        if mid in flat_matches:
            kh, ka = f"Match_{mid}_h", f"Match_{mid}_a"
            display_text = get_display_text(mid)
            if (kh in actual["group"] and ka in actual["group"]) or (f"Match_{mid}" in actual["ko_winners"]) or display_text:
                if display_text: output_text = display_text
                else:
                    sh, sa = actual["group"].get(kh, "?"), actual["group"].get(ka, "?")
                    output_text = f"{FLAGS.get(flat_matches[mid]['home'], flat_matches[mid]['home'].upper())} {sh} - {sa} {FLAGS.get(flat_matches[mid]['away'], flat_matches[mid]['away'].upper())}"
                completed_elements.append(
                    f"<span style='color: #ffffff;'>💥 Match #{mid}:</span> {output_text} "
                    f"<span style='color: #ffffff; font-size: 11px; vertical-align: super;'>FT</span>"
                )
                completed_ids.add(mid)

    past_ticker_elements = completed_elements[-4:]
    upcoming_ticker_elements = []
    upcoming_count = 0
    for mid in CHRONO_SEQUENCE:
        if mid in flat_matches and mid not in completed_ids:
            meta = FIFA_REAL_METADATA.get(mid, {"date": "TBD", "time": "TBD", "venue": "TBD"})
            upcoming_ticker_elements.append(
                f"<span style='color: #ffffff;'>⏳ UPCOMING Match #{mid}:</span> {FLAGS.get(flat_matches[mid]['home'], flat_matches[mid]['home'].upper())} VS {FLAGS.get(flat_matches[mid]['away'], flat_matches[mid]['away'].upper())} "
                f"<span style='color: #ffffff; font-weight: normal; font-size: 13px;'>({meta['date']} @ {meta['time']} - {meta['venue']})</span>"
            )
            upcoming_count += 1
            if upcoming_count >= 4: break

    ticker_elements = past_ticker_elements + upcoming_ticker_elements
    if not ticker_elements: ticker_elements = ["🏆 WORLD CUP 2026 PREDICTION LEAGUE — NO ACTIVE RESULTS RECORDED"]

    ticker_string = " &nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;&nbsp; ".join(ticker_elements)
    marquee_html = f"""
    <style>
        @keyframes marquee {{ 0% {{ transform: translate3d(0, 0, 0); }} 100% {{ transform: translate3d(-50%, 0, 0); }} }}
        .ticker-container {{ width: 100%; overflow: hidden; background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 8px; padding: 10px 0; box-sizing: border-box; margin-bottom: 20px; }}
        .ticker-wrapper {{ display: flex; width: fit-content; }}
        .ticker-content {{ display: inline-block; white-space: nowrap; padding-right: 50px; animation: marquee 42s linear infinite; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: bold; font-size: 14px; color: #ffffff !important; letter-spacing: 0.5px; }}
        .ticker-content * {{ color: #ffffff !important; }}
        .ticker-content:hover {{ animation-play-state: paused; cursor: pointer; }}
    </style>
    <div class="ticker-container"><div class="ticker-wrapper"><div class="ticker-content">{ticker_string} &nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;&nbsp; {ticker_string}</div></div></div>
    """
    return marquee_html

def generate_live_ticker_stream(league_id):
    marquee_html = calculate_live_ticker_html(league_id)
    st.components.v1.html(marquee_html, height=46)


# ==============================================================================
# --- 7. SESSION INITIALIZATION ---
# ==============================================================================
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None
if "current_username" not in st.session_state:
    st.session_state.current_username = None

# ==============================================================================
# --- 8. UNIFIED MATCH CARD RENDERER ---
# ==============================================================================
def render_match_card(home, away, label, key_prefix, disabled=False, score_mode=False, scores_dict=None):
    disp1 = fmt_team(name=home)
    disp2 = fmt_team(name=away)

    # Isolate flags from the string names to render them centered above
    flag1, name1 = split_flag_and_name(disp1)
    flag2, name2 = split_flag_and_name(disp2)

    st.markdown(f"""
        <div style="border: 1px solid rgba(255,255,255,0.2); border-radius: 10px; background: rgba(15, 23, 42, 0.8); padding: 14px; margin-top: 10px; margin-bottom: 2px;">
            <div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-bottom: 8px; font-weight: bold; text-transform: uppercase;">{label}</div>
            <div style="display: flex; justify-content: space-between; align-items: stretch; margin-bottom: 10px;">
                <div style="width: 42%;" class="mc-team-wrapper">
                    <span class="mc-flag">{flag1}</span>
                    <span class="mc-name">{name1}</span>
                </div>
                <div style="width: 16%;" class="mc-vs-block">VS</div>
                <div style="width: 42%;" class="mc-team-wrapper">
                    <span class="mc-flag">{flag2}</span>
                    <span class="mc-name">{name2}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if score_mode and scores_dict is not None:
        kh, ka = f"{key_prefix}_h", f"{key_prefix}_a"
        c1, c2 = st.columns(2)
        with c1:
            val_h = scores_dict.get(kh, 0)
            if isinstance(val_h, str) or val_h is None: val_h = 0
            scores_dict[kh] = st.number_input("Home Score", min_value=0, max_value=15, value=int(val_h), step=1, key=f"inp_{kh}", disabled=disabled)
        with c2:
            val_a = scores_dict.get(ka, 0)
            if isinstance(val_a, str) or val_a is None: val_a = 0
            scores_dict[ka] = st.number_input("Away Score", min_value=0, max_value=15, value=int(val_a), step=1, key=f"inp_{ka}", disabled=disabled)
        return scores_dict
    else:
        options = ["Select Winner", home, away]
        saved_db_val = scores_dict.get(key_prefix, "Select Winner") if scores_dict else "Select Winner"

        if str(saved_db_val) == "1":
            curr = home
        elif str(saved_db_val) == "2":
            curr = away
        else:
            curr = saved_db_val if saved_db_val in options else "Select Winner"

        idx_val = options.index(curr) if curr in options else 0
        val_select = st.selectbox("Winner Selection", options, index=idx_val, format_func=fmt_team, key=f"sel_{key_prefix}", label_visibility="collapsed", disabled=disabled)

        if scores_dict is not None:
            scores_dict[key_prefix] = val_select
        return val_select

# ==============================================================================
# --- 9. COMPUTATION ENGINES ---
# ==============================================================================
@st.cache_data
def run_standings_engine(scores_dict, manual_tb_locks=None, manual_tb_orders=None):
    if manual_tb_locks is None: manual_tb_locks = {}
    if manual_tb_orders is None: manual_tb_orders = {}
    
    all_group_results = {}
    third_place_pool = []

    # Step 1: Compute baseline statistics for all groups
    for g_name, teams in GROUPS.items():
        standings = {t: {"Group": g_name, "Pts": 0, "GD": 0, "GF": 0} for t in teams}

        # Accumulate scores
        for match in CHRONO_MATCHES[g_name]:
            m_id = match["id"]
            home, away = match["home"], match["away"]
            kh, ka = f"Match_{m_id}_h", f"Match_{m_id}_a"
            h_score = int(scores_dict.get(kh, 0) or 0)
            a_score = int(scores_dict.get(ka, 0) or 0)

            standings[home]["GF"] += h_score
            standings[away]["GF"] += a_score
            standings[home]["GD"] += (h_score - a_score)
            standings[away]["GD"] += (a_score - h_score)
            if h_score > a_score: standings[home]["Pts"] += 3
            elif a_score > h_score: standings[away]["Pts"] += 3
            else:
                standings[home]["Pts"] += 1
                standings[away]["Pts"] += 1

        df_g = pd.DataFrame.from_dict(standings, orient='index').reset_index().rename(columns={'index': 'Team'})
        
        # [Your existing H2H point_clusters logic here]
        df_g['h2h_pts'] = 0
        df_g['h2h_gd'] = 0
        df_g['h2h_gf'] = 0

        # Sort based on tie-breakers
        df_g = df_g.sort_values(by=["Pts", "h2h_pts", "h2h_gd", "h2h_gf", "GD", "GF"], ascending=False).reset_index(drop=True)

        # Apply manual tie-breaker locks
        tb_lock_val = manual_tb_locks.get(f"tb_locked_{g_name}", False)
        tb_order_val = manual_tb_orders.get(f"tb_order_{g_name}", [])
        if tb_lock_val and tb_order_val:
            saved_order = tb_order_val
            if sorted(saved_order) == sorted(df_g['Team'].tolist()):
                df_g['Team'] = pd.Categorical(df_g['Team'], categories=saved_order, ordered=True)
                df_g = df_g.sort_values(by='Team', ascending=True).reset_index(drop=True)
                df_g['Team'] = df_g['Team'].astype(str)

        # Assign explicit Position for indexing
        df_g['Position'] = range(1, len(df_g) + 1)
        all_group_results[g_name] = df_g.drop(columns=['h2h_pts', 'h2h_gd', 'h2h_gf'])

    # Step 2: Resolve 3rd place wildcard layout
    third_place_pool = [df[df['Position'] == 3].iloc[0].to_dict() for df in all_group_results.values() if not df[df['Position'] == 3].empty]
    
    wildcard_df = pd.DataFrame(third_place_pool).sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
    adv_wildcards = wildcard_df.head(8).to_dict(orient="records")

    return all_group_results, adv_wildcards


@st.cache_data
def build_full_third_place_table(scores_dict, manual_tb_locks=None, manual_tb_orders=None):
    all_group_results, top8_list = run_standings_engine(scores_dict, manual_tb_locks, manual_tb_orders)

    third_place_rows = []
    for df in all_group_results.values():
        third_row = df[df['Position'] == 3]
        if not third_row.empty:
            third_place_rows.append(third_row.iloc[0].to_dict())
    
    if not third_place_rows:
        return pd.DataFrame(), pd.DataFrame(), ""

    full_wildcards_df = pd.DataFrame(third_place_rows).sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)

    top8_df = pd.DataFrame(top8_list)
    top8_teams = set(top8_df["Team"].tolist()) if not top8_df.empty else set()
    full_wildcards_df["Qualifies (Top 8)"] = full_wildcards_df["Team"].isin(top8_teams)

    qualifying_group_letters = sorted([row["Group"].replace("Group ", "").strip() for row in top8_list])
    combo_code = "".join(qualifying_group_letters)

    return full_wildcards_df, top8_df, combo_code


@st.cache_data
def resolve_bracket_teams(scores_dict, target_is_actual=False, actual_results_obj=None, manual_tb_locks=None, manual_tb_orders=None):
    """
    Resolves the exact names of teams progressing through each round.
    Handles user selections (which save as '1' or '2') and parses them relative
    to that specific user's generated bracket mapping.
    """
    if target_is_actual and actual_results_obj is not None:
        g_scores = actual_results_obj.get("group", {})
        ko_choices = actual_results_obj.get("ko_winners", {})
    else:
        g_scores = scores_dict if scores_dict is not None else {}
        ko_choices = scores_dict if scores_dict is not None else {}

    # Build underlying group standings structures safely
    g_tables, qualifying_wildcards = run_standings_engine(g_scores, manual_tb_locks, manual_tb_orders)

    def get_1st(g): 
        if g not in g_tables or g_tables[g].empty: return ""
        return g_tables[g].iloc[0]["Team"]

    def get_2nd(g): 
        if g not in g_tables or g_tables[g].empty: return ""
        return g_tables[g].iloc[1]["Team"]

    wildcards_by_group = {}
    qualifying_group_letters = []
    for row in qualifying_wildcards:
        g_letter = row["Group"].replace("Group ", "").strip()
        qualifying_group_letters.append(g_letter)
        wildcards_by_group[g_letter] = row["Team"]

    qualifying_group_letters.sort()
    combination_lookup_string = "".join(qualifying_group_letters)

    db_mapping_row = None
    if len(combination_lookup_string) == 8:
        db_mapping_row = fetch_supabase_wildcard_mapping(combination_lookup_string)

    # Reconstruct Round of 32 baseline starting lines
    r32_teams = {}
    r32_flat_list = set()  # Set collection to accumulate all unique teams reaching R32
    
    for m_id, structure in DYNAMIC_R32_CONFIG.items():
        home_g, home_pos = structure["home"][0], structure["home"][1]
        h_team = get_1st(home_g) if home_pos == "1st" else get_2nd(home_g)

        if "away" in structure:
            away_g, away_pos = structure["away"][0], structure["away"][1]
            a_team = get_1st(away_g) if away_pos == "1st" else get_2nd(away_g)
        elif "away_lookup" in structure:
            lookup_col_header = structure["away_lookup"]
            if db_mapping_row and lookup_col_header in db_mapping_row:
                resolved_target_group_letter = db_mapping_row[lookup_col_header]
                a_team = wildcards_by_group.get(resolved_target_group_letter, "TBD")
            else:
                a_team = "TBD"
        else:
            a_team = "TBD"

        r32_teams[m_id] = (h_team, a_team)
        
        # Track both qualified teams seamlessly if they aren't empty placeholders
        if h_team and h_team != "TBD" and h_team != "": r32_flat_list.add(h_team)
        if a_team and a_team != "TBD" and a_team != "": r32_flat_list.add(a_team)

    # Helper to resolve selection strings safely ('1', '2', or literal team names)
    def clean_choice_resolution(match_key, current_pair):
        raw = str(ko_choices.get(match_key, "")).strip()
        if raw == "1": return current_pair[0]
        if raw == "2": return current_pair[1]
        return raw

    # 1. Evaluate Round of 16 Progressors
    r16_teams = set()
    for m in range(73, 89):
        m_key = f"Match_{m}"
        pair = r32_teams.get(m_key, ("", ""))
        winner = clean_choice_resolution(m_key, pair)
        if winner and winner != "Select Winner" and not winner.startswith("W"):
            r16_teams.add(winner)

    # 2. Evaluate Quarter-Final Progressors
    qf_pairings = {
        "Match_89": ("Match_74", "Match_77"), "Match_90": ("Match_73", "Match_75"),
        "Match_93": ("Match_83", "Match_84"), "Match_94": ("Match_81", "Match_82"),
        "Match_91": ("Match_76", "Match_78"), "Match_92": ("Match_79", "Match_80"),
        "Match_95": ("Match_86", "Match_88"), "Match_96": ("Match_85", "Match_87")
    }
    qf_teams = set()
    r16_match_winners = {}

    # First cache winners of R32 to feed into R16 matches correctly
    for m in range(73, 89):
        m_id = f"Match_{m}"
        r16_match_winners[m_id] = clean_choice_resolution(m_id, r32_teams.get(m_id, ("", "")))

    for m_id, (prev1, prev2) in qf_pairings.items():
        t1 = r16_match_winners.get(prev1, "")
        t2 = r16_match_winners.get(prev2, "")
        winner = clean_choice_resolution(m_id, (t1, t2))
        if winner and winner != "Select Winner" and not winner.startswith("W"):
            qf_teams.add(winner)

    # 3. Evaluate Semi-Final Progressors
    sf_pairings = {
        "Match_97": ("Match_89", "Match_90"), "Match_98": ("Match_93", "Match_94"),
        "Match_99": ("Match_91", "Match_92"), "Match_100": ("Match_95", "Match_96")
    }
    sf_teams = set()
    qf_match_winners = {}

    for m_id, (prev1, prev2) in sf_pairings.items():
        # Trace back to find who won the QF feeding branches
        t1_r16_1, t1_r16_2 = qf_pairings[prev1]
        t1 = clean_choice_resolution(prev1, (r16_match_winners.get(t1_r16_1, ""), r16_match_winners.get(t1_r16_2, "")))
        
        t2_r16_1, t2_r16_2 = qf_pairings[prev2]
        t2 = clean_choice_resolution(prev2, (r16_match_winners.get(t2_r16_1, ""), r16_match_winners.get(t2_r16_2, "")))

        winner = clean_choice_resolution(m_id, (t1, t2))
        qf_match_winners[m_id] = winner
        if winner and winner != "Select Winner" and not winner.startswith("W"):
            sf_teams.add(winner)

    # 4. Evaluate Finalists, 3rd place, and Grand Champion
    sf1_h = qf_match_winners.get("Match_97", "")
    sf1_a = qf_match_winners.get("Match_98", "")
    sf2_h = qf_match_winners.get("Match_99", "")
    sf2_a = qf_match_winners.get("Match_100", "")

    f1_winner = clean_choice_resolution("Match_101", (sf1_h, sf1_a))
    f2_winner = clean_choice_resolution("Match_102", (sf2_h, sf2_a))
    finalists = set([f1_winner, f2_winner]) if (f1_winner and f2_winner) else set()

    champ = clean_choice_resolution("Match_104", (f1_winner, f2_winner))

    sf1_loser = sf1_a if f1_winner == sf1_h else sf1_h
    sf2_loser = sf2_a if f2_winner == sf2_h else sf2_h
    third = clean_choice_resolution("Match_103", (sf1_loser, sf2_loser))

    return {
        "r32_pairings": r32_teams,
        "r32": list(r32_flat_list),
        "r16": r16_teams,
        "qf": qf_teams,
        "sf": sf_teams,
        "finalists": finalists,
        "champ": champ,
        "third": third,
        "third_place_top8": qualifying_wildcards,
        "third_place_code": combination_lookup_string
    }


def calculate_user_points(user_id, league_id):
    user_preds = db_fetch_user_predictions(user_id, league_id)
    actual = db_fetch_league_actual_results(league_id)
    points = 0

    # Safety exit check if live truth data is empty
    if not actual or "group" not in actual:
        return 0

    # Feed manual group tie-breakers if saved by user
    tb_saved_records = db_fetch_group_tie_breakers(user_id, league_id)
    local_tb_orders = {}
    local_tb_locks = {}
    for row in tb_saved_records:
        local_tb_orders[f"tb_order_{row['group_name']}"] = row["team_order"]
        local_tb_locks[f"tb_locked_{row['group_name']}"] = row["is_locked"]

    # --- PART 1: GROUP STAGE CALCULATIONS ---
    for g_name, matches in CHRONO_MATCHES.items():
        for match in matches:
            m_id = match["id"]
            kh, ka = f"Match_{m_id}_h", f"Match_{m_id}_a"
            p_h, p_a = user_preds.get(kh, None), user_preds.get(ka, None)
            a_h, a_a = actual["group"].get(kh, None), actual["group"].get(ka, None)
            if p_h is not None and p_a is not None and a_h is not None and a_a is not None:
                if int(p_h) == int(a_h) and int(p_a) == int(a_a): 
                    points += 3  
                elif (int(p_h) > int(p_a) and int(a_h) > int(a_a)) or (int(p_a) > int(p_h) and int(a_a) > int(a_h)) or (int(p_h) == int(p_a) and int(a_h) == int(a_a)): 
                    points += 1  

    # --- PART 2: KNOCKOUT TEAM INTERSECTION MATCHES ---
    user_bracket = resolve_bracket_teams(user_preds, target_is_actual=False, manual_tb_locks=local_tb_locks, manual_tb_orders=local_tb_orders)
    actual_bracket = resolve_bracket_teams(None, target_is_actual=True, actual_results_obj=actual, manual_tb_locks={}, manual_tb_orders={})

    # 1. Round of 32 Intersection - 3 Points Per Correct Team (Calculated from user group output vs actual)
    user_r32 = user_bracket.get("r32", [])
    actual_r32 = actual_bracket.get("r32", [])
    for team in user_r32:
        if team and team in actual_r32: 
            points += 3

    # 2. Round of 16 Intersection - 5 Points Per Correct Team
    for team in user_bracket.get("r16", []):
        if team and team in actual_bracket.get("r16", []): 
            points += 5

    # 3. Quarterfinals Intersection - 10 Points Per Correct Team
    for team in user_bracket.get("qf", []):
        if team and team in actual_bracket.get("qf", []): 
            points += 10

    # 4. Semifinals Intersection - 15 Points Per Correct Team
    for team in user_bracket.get("sf", []):
        if team and team in actual_bracket.get("sf", []): 
            points += 15

    # 5. Third Place Winner - 15 Points (Exactly 1 team matched)
    if user_bracket.get("third") and user_bracket.get("third") == actual_bracket.get("third"): 
        points += 15

    # 6. Finalists Intersection (Reached the Final) - 20 Points Per Correct Team
    for team in user_bracket.get("finalists", []):
        if team and team in actual_bracket.get("finalists", []): 
            points += 20
        
    # 7. Tournament Champion - 25 Points
    if user_bracket.get("champ") and user_bracket.get("champ") == actual_bracket.get("champ"): 
        points += 25

    return points







# ==============================================================================
# --- 10. SIGN IN GATEWAY ---
# ==============================================================================
if st.session_state.current_user_id is None:
    with st.container():
        st.title("🔐 Tournament Sign-In")
        t1, t2 = st.tabs(["Login", "Create Account"])
        with t1:
            lin_user = st.text_input("Username")
            lin_pass = st.text_input("Password", type="password")
            if st.button("Log In", use_container_width=True):
                hashed_p = hash_password(lin_pass)
                res = supabase.table("users").select("*").eq("username", lin_user).execute()
                if res.data and res.data[0]["password_hash"] == hashed_p:
                    st.session_state.current_user_id = res.data[0]["id"]
                    st.session_state.current_username = res.data[0]["username"]
                    st.rerun()
                else: st.error("Invalid credentials.")
        with t2:
            reg_user = st.text_input("Choose Username")
            reg_pass = st.text_input("Choose Password", type="password")
            if st.button("Register Account", use_container_width=True):
                if reg_user.strip() == "" or reg_pass.strip() == "": st.error("Fields cannot be empty.")
                else:
                    dup_check = supabase.table("users").select("id").eq("username", reg_user).execute()
                    if dup_check.data: st.error("Username already exists.")
                    else:
                        hashed_p = hash_password(reg_pass)
                        supabase.table("users").insert({"username": reg_user, "password_hash": hashed_p}).execute()
                        st.success("Registered successfully! Proceed to log in via the left tab.")
    st.stop()

c_uid = st.session_state.current_user_id
c_user = st.session_state.current_username

user_leagues_list = db_fetch_user_leagues(c_uid)

# ==============================================================================
# --- 11. STRICT LEAGUE LOCK CHECK ---
# ==============================================================================
if not user_leagues_list:
    st.title("🛡️ Secure Onboarding")
    st.warning("Welcome! To proceed into the dashboard, you must first create or join a league.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Join an Existing League")
        join_code_input = st.text_input("Enter Invite Code Provided By Your Admin")
        if st.button("🔑 Access League", use_container_width=True):
            if join_code_input.strip() != "":
                code_query = supabase.table("leagues").select("id, name").eq("invite_code", join_code_input).execute()
                if code_query.data:
                    target_l_id = code_query.data[0]["id"]
                    supabase.table("league_members").insert({"user_id": c_uid, "league_id": target_l_id}).execute()
                    st.success("Successfully authenticated and added to your league environment!")
                    st.rerun()
                else: st.error("Invite code not verified.")
    with c2:
        st.subheader("Request A New League Setup")
        master_pass = st.text_input("Enter Master Passcode", type="password")
        new_lg_name = st.text_input("Proposed League Name")
        new_lg_code = st.text_input("Create Custom Invite Code For Friends")

        if st.button("✨ Initialize Authorized League", use_container_width=True):
            if master_pass != "WORLD_CUP_2026":
                st.error("Invalid Master Creation Passcode.")
            elif new_lg_name.strip() == "" or new_lg_code.strip() == "":
                st.error("Fields cannot be left blank.")
            else:
                ins_res = supabase.table("leagues").insert({"name": new_lg_name, "invite_code": new_lg_code, "creator_id": c_uid}).execute()
                if ins_res.data:
                    new_id = ins_res.data[0]["id"]
                    supabase.table("league_members").insert({"user_id": c_uid, "league_id": new_id}).execute()
                    st.rerun()
    st.stop()

# Dropdown management configuration handles
leagues_dropdown_options = {lg["name"]: lg for lg in user_leagues_list}
selected_league_name = st.sidebar.selectbox("Current League Environment:", list(leagues_dropdown_options.keys()))
active_league_meta = leagues_dropdown_options[selected_league_name]
active_league_id = active_league_meta["id"]
is_league_admin = (active_league_meta["creator_id"] == c_uid)

# --- HYDRATE ACTIVE PROFILE SESSION STORAGE TIE BREAKERS FROM SUPABASE ---
if "tie_breakers_hydrated" not in st.session_state or st.session_state.get("last_league_id") != active_league_id:
    db_tb_rows = db_fetch_group_tie_breakers(c_uid, active_league_id)
    for row in db_tb_rows:
        st.session_state[f"tb_order_{row['group_name']}"] = row["team_order"]
        st.session_state[f"tb_locked_{row['group_name']}"] = row["is_locked"]
    st.session_state["tie_breakers_hydrated"] = True
    st.session_state["last_league_id"] = active_league_id

# --- GLOBAL LIVE SPORTS TICKER INJECTION ---
# Renders at the very top of the app workspace dashboard interface for all views
generate_live_ticker_stream(active_league_id)

col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.markdown(f"👥 Active Profile: **{c_user}**")
with col_nav2:
    if st.button("🚪 Log Out", use_container_width=True):
        # Flush local memory explicitly to eliminate lingering cross-user bleeding variables
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

main_tabs = ["🏆 Leaderboards", "📝 Submit Predictions", "🛡️ Create/Join a League"]
if is_league_admin: 
    main_tabs.append("🛠️ Admin Dashboard")
app_tab = st.sidebar.radio("Main Menu Navigation", main_tabs)


# ==============================================================================
# --- 12. LEADERBOARD WORKSPACE ---
# ==============================================================================
@st.cache_data
def get_cached_leaderboard(active_league_id, member_rows_json):
    """Assembles and calculates scores across all league participants in a single cached pass."""
    import json
    rows = json.loads(member_rows_json)
    leaderboard_data = []
    
    for row in rows:
        if row.get("users"):
            m_id = row["users"]["id"]
            m_name = row["users"]["username"]
            leaderboard_data.append({
                "POS": 0,
                "NAME": m_name, 
                "POINTS": calculate_user_points(m_id, active_league_id)
            })
    return leaderboard_data

if app_tab == "🏆 Leaderboards":
    st.header(f"🏆 {selected_league_name} Standings")
    members_res = supabase.table("league_members").select("users(id, username)").eq("league_id", active_league_id).execute()
    
    if members_res.data:
        import json
        # Serialize database rows to act as a stable cache string key
        serialized_rows = json.dumps(members_res.data, sort_keys=True)
        leaderboard_data = get_cached_leaderboard(active_league_id, serialized_rows)
    else:
        leaderboard_data = []
        
    df_leaderboard = pd.DataFrame(leaderboard_data)
    if not df_leaderboard.empty:
        # Sort and recalculate global position sequence numbers dynamically 
        df_leaderboard = df_leaderboard.sort_values(by="POINTS", ascending=False).reset_index(drop=True)
        df_leaderboard["POS"] = df_leaderboard.index + 1

                        # Calculate dynamic pixel height based on row count to prevent inner scrolling safely
        # 40px for header + 35px per competitor row
        dynamic_height = 40 + (len(df_leaderboard) * 35)

        # EXCLUSIVE COHESIVE STREAMLIT RENDER THEME RULE FIX WITH ALIGNMENT AND DYNAMIC HEIGHT
        st.dataframe(
            df_leaderboard[["POS", "NAME", "POINTS"]], 
            use_container_width=True, 
            hide_index=True,
            height=dynamic_height,  # <-- Seamlessly feeds exact pixels to pass validation
            column_config={
                "POS": st.column_config.Column(alignment="center"),
                "NAME": st.column_config.Column(alignment="center"),
                "POINTS": st.column_config.Column(alignment="center"),
            }
        )




# ==============================================================================
# --- 13. CREATE / JOIN LEAGUE HUB ---
# ==============================================================================
elif app_tab == "🛡️ Create/Join a League":
    st.header("🛡️ League Management Hub")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Join Another League")
        sec_join_code = st.text_input("Enter Additional Invite Code")
        if st.button("🔑 Join League", use_container_width=True):
            if sec_join_code.strip() != "":
                code_query = supabase.table("leagues").select("id, name").eq("invite_code", sec_join_code).execute()
                if code_query.data:
                    t_id = code_query.data[0]["id"]
                    supabase.table("league_members").insert({"user_id": c_uid, "league_id": t_id}).execute()
                    st.success("Successfully registered into new League!")
                    st.rerun()



# ==============================================================================
# --- 14. USER PREDICTIONS DESK (TWO-STAGE WORKFLOW VERSION) ---
# ==============================================================================
elif app_tab == "📝 Submit Predictions":
    st.header(f"📝 Match Setup — {selected_league_name}")

    # Display tournament lockout warning if time has run out
    if global_tournament_lock:
        st.markdown("<div class='lock-badge-banner'>🔒 Tournament Started: All setup inputs are locked as read-only.</div>", unsafe_allow_html=True)

    # Natively fetch the current user state context
    user_preds = db_fetch_user_predictions(c_uid, active_league_id)
    locked_keys_set = db_fetch_locked_status(c_uid, active_league_id)

    # Reconstruct local tie-breaker variables to feed the cached computation engines cleanly
    local_tb_orders = {}
    local_tb_locks = {}
    for g_name in GROUPS.keys():
        local_tb_orders[f"tb_order_{g_name}"] = st.session_state.get(f"tb_order_{g_name}", [])
        local_tb_locks[f"tb_locked_{g_name}"] = st.session_state.get(f"tb_locked_{g_name}", False)

    # Initialize session state for tracking master league-wide knockout progression
    if "knockouts_generated" not in st.session_state:
        st.session_state.knockouts_generated = False

    # NEW: insert 3rd-Place League tab in the middle
    pred_sub_tabs = st.tabs(["Group Matches", "3rd‑Place League", "Knockout Rounds"])

    # Fetch group stage completeness metrics globally for these tabs
    comp_matches, tot_matches, comp_percent = check_group_stage_completion(user_preds)

    # Pre-check all groups globally to detect any pending un-finalized tie-breakers
    has_unfinalized_tiebreaker = False
    for g_name in GROUPS.keys():
        g_tables, _ = run_standings_engine(user_preds, manual_tb_locks=local_tb_locks, manual_tb_orders=local_tb_orders)
        df_g_check = g_tables[g_name]
        tied_mask_check = df_g_check.duplicated(subset=['Pts', 'GD', 'GF'], keep=False)
        if tied_mask_check.any():
            if not local_tb_locks.get(f"tb_locked_{g_name}"):
                has_unfinalized_tiebreaker = True
                break

    # If everything is already legally locked and there's no ongoing tiebreaker, auto-trip the state
    if comp_percent == 100 and not has_unfinalized_tiebreaker:
        # Check if the user has already loaded/rendered knockouts successfully before
        if "third_place_code" in st.session_state:
            st.session_state.knockouts_generated = True

    with pred_sub_tabs[0]:
        # Progress Bar Dashboard UI Configuration
        st.markdown(f"### 📊 Overall Group Predictions Progress: {comp_percent}%")
        st.progress(comp_percent / 100.0)
        
        if comp_percent < 100:
            st.info(f"💡 You have completed **{comp_matches}** out of **{tot_matches}** group stage fixtures. Submit and lock all 12 groups to unlock manual tie-breakers.")
        elif has_unfinalized_tiebreaker:
            st.warning("⚠️ Group matches predicted, but there are unfinalized tie-break scenarios. Please resolve and lock all active tie-breakers to open the Master Lock Gate below.")
        elif not st.session_state.knockouts_generated:
            st.success("✅ Success! All 72 group matches predicted and locked. Proceed to knockout round predictions.")
        else:
            st.success("🔒 Standings and Tie-Breakers verified. Knockout stage brackets are fully live and updated.")

        st.markdown("<br />", unsafe_allow_html=True)

        selected_group = st.selectbox("Choose Group Stage Pool", list(GROUPS.keys()))
        group_match_ids = [m["id"] for m in CHRONO_MATCHES[selected_group]]
        group_keys = [f"Match_{mid}_h" for mid in group_match_ids] + [f"Match_{mid}_a" for mid in group_match_ids]

        # Combine local lock status with global lockout status
        is_group_locked = global_tournament_lock or any(k in locked_keys_set for k in group_keys)

        col_input, col_table = st.columns([1, 1])
        with col_input:
            if is_group_locked:
                if global_tournament_lock:
                    st.markdown(f"<div class='lock-badge-banner'>🔒 {selected_group} Locked (Tournament Started)</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='lock-badge-banner'>🔒 {selected_group} Locked In</div>", unsafe_allow_html=True)

                for match in CHRONO_MATCHES[selected_group]:
                    render_match_card(
                        home=match["home"], away=match["away"], label=f"Match #{match['id']}", 
                        key_prefix=f"Match_{match['id']}", disabled=is_group_locked, score_mode=True, scores_dict=user_preds
                    )
            else:
                with st.form(key=f"form_{selected_group}", clear_on_submit=False):
                    for match in CHRONO_MATCHES[selected_group]:
                        # Natively pull from session state if updated dynamically by user inputs
                        kh = f"Match_{match['id']}_h"
                        ka = f"Match_{match['id']}_a"
                        if kh in st.session_state: user_preds[kh] = st.session_state[kh]
                        if ka in st.session_state: user_preds[ka] = st.session_state[ka]

                        render_match_card(
                            home=match["home"], away=match["away"], label=f"Match #{match['id']}", 
                            key_prefix=f"Match_{match['id']}", disabled=is_group_locked, score_mode=True, scores_dict=user_preds
                        )
                    
                    if st.form_submit_button(f"🔒 Finalize & Lock {selected_group} Predictions", use_container_width=True):
                        # Force update from session inputs inside the form scope execution context
                        for match in CHRONO_MATCHES[selected_group]:
                            kh = f"Match_{match['id']}_h"
                            ka = f"Match_{match['id']}_a"
                            val_h = st.session_state.get(kh, user_preds.get(kh, 0))
                            val_a = st.session_state.get(ka, user_preds.get(ka, 0))
                            
                            db_save_prediction(c_uid, active_league_id, kh, int(val_h or 0))
                            db_save_prediction(c_uid, active_league_id, ka, int(val_a or 0))
                        
                        db_lock_predictions(c_uid, active_league_id, group_keys)
                        st.success(f"Group {selected_group} successfully committed to database!")
                        st.cache_data.clear()  # Safe, precise cache cleanup function call
                        st.rerun()

        with col_table:
            st.subheader("Simulated Group Table")
            u_results, _ = run_standings_engine(user_preds, manual_tb_locks=local_tb_locks, manual_tb_orders=local_tb_orders)
            df_display = u_results[selected_group].copy()

            # CRITICAL FIX: Ensure values are calculated as numbers and sorted according to strict FIFA rules
            df_display['Pts'] = pd.to_numeric(df_display['Pts'])
            df_display['GD'] = pd.to_numeric(df_display['GD'])
            df_display['GF'] = pd.to_numeric(df_display['GF'])
            df_display = df_display.sort_values(by=['Pts', 'GD', 'GF'], ascending=[False, False, False]).reset_index(drop=True)

            # --- START OF MANUAL TIE-BREAKER OVERRIDE INJECTION ---
            tied_mask = df_display.duplicated(subset=['Pts', 'GD', 'GF'], keep=False)
            if tied_mask.any() and is_group_locked:
                tb_lock_key = f"tb_locked_{selected_group}"
                tb_order_key = f"tb_order_{selected_group}"

                # Force true if tournament level lockout condition evaluates true
                is_tb_locked = global_tournament_lock or local_tb_locks.get(tb_lock_key, False)

                if global_tournament_lock:
                    st.info("🔒 Tie-break sequence completed. Standings locked due to tournament initialization rules.")
                else:
                    st.warning(
                        "⚠️ **Tie Break Alert:** Teams are perfectly level on point parameters, GD, and GF metrics. "
                        "Please arrange the final positions below. Note: Final positions will be decided based on "
                        "FIFA Fair Play points / drawing of lots. Once confirmed, lock your choices."
                    )

                tied_indices = df_display[tied_mask].index.tolist()
                tied_teams = df_display.loc[tied_indices, 'Team'].tolist()

                selected_order = []
                temp_pool = tied_teams.copy()

                # Render positional selectbox dropdown interfaces side by side
                override_cols = st.columns(len(tied_indices))
                for i, idx in enumerate(tied_indices):
                    with override_cols[i]:
                        pos_label = f"Position {idx + 1}"

                        # Set default dropdown selections gracefully
                        default_team = temp_pool[0] if temp_pool else tied_teams[i]
                        if (is_tb_locked or global_tournament_lock) and local_tb_orders.get(tb_order_key):
                            default_team = local_tb_orders[tb_order_key][idx]

                        chosen_team = st.selectbox(
                            f"Select {pos_label}",
                            options=tied_teams,
                            index=tied_teams.index(default_team) if default_team in tied_teams else 0,
                            key=f"manual_tb_{selected_group}_{idx}",
                            format_func=lambda x: x.upper(),
                            disabled=is_tb_locked
                        )
                        selected_order.append(chosen_team)
                        if chosen_team in temp_pool:
                            temp_pool.remove(chosen_team)

                st.markdown("<br />", unsafe_allow_html=True)
                if not is_tb_locked:
                    if st.button("🔒 Lock Tie-Break Order", key=f"btn_lock_tb_{selected_group}", use_container_width=True):
                        if len(set(selected_order)) == len(tied_indices):
                            # Construct complete 4-team array containing the locked sequence layout
                            full_group_order = list(df_display['Team'])
                            for local_i, global_idx in enumerate(tied_indices):
                                full_group_order[global_idx] = selected_order[local_i]

                            st.session_state[tb_order_key] = full_group_order
                            st.session_state[tb_lock_key] = True

                            # CRITICAL FIX: Save directly down into your Supabase database table
                            db_save_group_tie_breaker(c_uid, active_league_id, selected_group, full_group_order)

                            st.success("Tie-break sequence locked successfully!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Invalid Selection: Please ensure you haven't assigned the same team to multiple positions.")
                elif not global_tournament_lock:
                    st.info("🔒 Tie-break resolved. Group standings are locked.")

                # If selection mapping matches layout requirements, rebuild ordering structure
                if len(set(selected_order)) == len(tied_indices):
                    # Cache matching rows from origin layout
                    cached_rows = {r['Team']: r for _, r in df_display[df_display['Team'].isin(tied_teams)].iterrows()}
                    for local_i, global_idx in enumerate(tied_indices):
                        target_team = selected_order[local_i]
                        for col in df_display.columns:
                            df_display.at[global_idx, col] = cached_rows[target_team][col]
            # --- END OF MANUAL TIE-BREAKER OVERRIDE INJECTION ---

            df_final_render = df_display[["Team", "Pts", "GD", "GF"]].copy()
            df_final_render["Team"] = df_final_render["Team"].apply(fmt_team)
            st.dataframe(df_final_render, use_container_width=True, hide_index=True)

    # NEW TAB: 3rd-Place League
    with pred_sub_tabs[1]:
        st.subheader("🌍 3rd‑Place League Rankings")

        # The 3rd-Place league now renders as long as predictions exist
        if not user_preds:
            st.info("Start predicting group scores to see the 3rd-place rankings.")
        else:
            # Build the 12-team 3rd-place league
            full_wildcards_df, top8_df, combo_code_table = build_full_third_place_table(user_preds, manual_tb_locks=local_tb_locks, manual_tb_orders=local_tb_orders)

            if full_wildcards_df.empty:
                st.warning("No 3rd‑place data available yet.")
            else:
                # Style: highlight top 8 green
                def highlight_top8(row):
                    if row["Qualifies (Top 8)"]:
                        return ["background-color: #14532d; color: #bbf7d0; font-weight: 700;"] * len(row)
                    return [""] * len(row)

                df_display = full_wildcards_df.copy()
                df_display["Team"] = df_display["Team"].apply(fmt_team)

                st.markdown("#### All 12 Third‑Place Teams")
                st.dataframe(
                    df_display[["Team", "Group", "Pts", "GD", "GF", "Qualifies (Top 8)"]]
                    .style.apply(highlight_top8, axis=1),
                    use_container_width=True,
                    hide_index=True,
                )

                if not top8_df.empty:
                    st.markdown("#### Qualified 3rd‑Place Teams (Top 8)")
                    df_top8 = top8_df.copy()
                    df_top8["Team"] = df_top8["Team"].apply(fmt_team)
                    st.dataframe(
                        df_top8[["Team", "Group", "Pts", "GD", "GF"]],
                        use_container_width=True,
                        hide_index=True,
                    )

                # Get the exact code used by the bracket engine for consistency
                user_bracket_view = resolve_bracket_teams(user_preds, target_is_actual=False, manual_tb_locks=local_tb_locks, manual_tb_orders=local_tb_orders)
                combo_code = user_bracket_view.get("third_place_code", combo_code_table)

                st.markdown("---")
                if combo_code:
                    st.session_state["third_place_code"] = combo_code
                    group_letters_human = ", ".join(list(combo_code))
                    st.markdown(
                        f"**Third‑Place Qualifier Code (alphabetical by group):** `{combo_code}`  \n"
                        f"*Groups represented:* {group_letters_human}"
                    )
                else:
                    st.info("Third‑place qualifier code not available yet.")

    with pred_sub_tabs[2]:
        # Knockout Rounds remain active once group stage is 100% complete and tie-breakers are locked
        if comp_percent < 100 or has_unfinalized_tiebreaker:
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            st.warning(
                "⚠️ **Knockout Stage Locked:** You must complete 100% of your Group Stage predictions "
                "and resolve/lock all group tie-breakers before the knockout brackets will unlock."
            )
        else:
            # The bracket engine runs automatically now since the condition above passed
            user_calc_bracket = resolve_bracket_teams(user_preds, target_is_actual=False, manual_tb_locks=local_tb_locks, manual_tb_orders=local_tb_orders)
            o_r32 = user_calc_bracket["r32_pairings"]
            
            # --- DEBUG: 3rd-place R32 mapping (focus on Match_81) ---
            with st.expander("🔍 Debug 3rd-Place R32 Mapping"):
                combo_code = user_calc_bracket.get("third_place_code", "")
                st.write("Third-place code:", combo_code or "(none)")
                if combo_code:
                    mapping_row = fetch_supabase_wildcard_mapping(combo_code)
                    st.write("Supabase row:", mapping_row if mapping_row else "(no row found)")
                    # Rebuild wildcards_by_group from the same engine
                    _, qualifying_wildcards = run_standings_engine(user_preds, manual_tb_locks=local_tb_locks, manual_tb_orders=local_tb_orders)
                    wildcards_by_group = {
                        row["Group"].replace("Group ", "").strip(): row["Team"]
                        for row in qualifying_wildcards
                    }
                    st.write("Wildcards by group:", wildcards_by_group)
                    # Focus specifically on Match_81
                    m_id = "Match_81"
                    structure = DYNAMIC_R32_CONFIG[m_id]
                    lookup_col = structure.get("away_lookup")
                    st.write("Match_81 away_lookup key:", lookup_col)
                    if mapping_row and lookup_col in mapping_row:
                        gl = mapping_row[lookup_col]
                        team = wildcards_by_group.get(gl, "TBD")
                        st.write("→ Group letter from matrix:", repr(gl))
                        st.write("→ Team selected for Match_81:", team)
                    else:
                        st.write("→ Mapping row missing or column not found for Match_81")
                else:
                    st.write("No 3rd-place code computed yet.")
            
            ko_tabs = st.tabs(["Round of 32", "Round of 16", "Quarter-Finals", "Finals"])

            with ko_tabs[0]:
                r32_keys = list(o_r32.keys())
                is_r32_locked = global_tournament_lock or all(k in locked_keys_set for k in r32_keys)

                if is_r32_locked:
                    if global_tournament_lock:
                        st.markdown("<div class='lock-badge-banner'>🔒 Round of 32 Selections Locked (Tournament Started)</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='lock-badge-banner'>🔒 Round of 32 Selections Locked</div>", unsafe_allow_html=True)

                for m_id, (h, a) in o_r32.items():
                    # Preserve selections directly inside the live user predictions map
                    if m_id in st.session_state:
                        user_preds[m_id] = st.session_state[m_id]
                    render_match_card(h, a, m_id.replace("_", " "), m_id, disabled=is_r32_locked, score_mode=False, scores_dict=user_preds)

                if not is_r32_locked:
                    if st.button("🔒 Lock Round of 32 Predictions", use_container_width=True):
                        for m_key in r32_keys:
                            val = st.session_state.get(m_key, user_preds.get(m_key))
                            if val and val != "Select Winner" and not str(val).startswith("W"):
                                opts = o_r32[m_key]
                                if val == opts[0]: db_save_prediction(c_uid, active_league_id, m_key, 1)
                                elif val == opts[1]: db_save_prediction(c_uid, active_league_id, m_key, 2)
                        db_lock_predictions(c_uid, active_league_id, r32_keys)
                        st.success("Round of 32 predictions successfully locked!")
                        st.cache_data.clear()
                        st.rerun()

            with ko_tabs[1]:
                def get_ko_prev(m_key):
                    val = st.session_state.get(m_key, user_preds.get(m_key))
                    if val == o_r32.get(m_key, ("",""))[0]: return val
                    if val == o_r32.get(m_key, ("",""))[1]: return val
                    return f"W{m_key.split('_')[1]}"

                o_r16 = {
                    "Match_89": (get_ko_prev("Match_74"), get_ko_prev("Match_77")), "Match_90": (get_ko_prev("Match_73"), get_ko_prev("Match_75")),
                    "Match_93": (get_ko_prev("Match_83"), get_ko_prev("Match_84")), "Match_94": (get_ko_prev("Match_81"), get_ko_prev("Match_82")),
                    "Match_91": (get_ko_prev("Match_76"), get_ko_prev("Match_78")), "Match_92": (get_ko_prev("Match_79"), get_ko_prev("Match_80")),
                    "Match_95": (get_ko_prev("Match_86"), get_ko_prev("Match_88")), "Match_96": (get_ko_prev("Match_85"), get_ko_prev("Match_87"))
                }
                r16_keys = list(o_r16.keys())
                is_r16_locked = global_tournament_lock or all(k in locked_keys_set for k in r16_keys)

                if is_r16_locked:
                    if global_tournament_lock:
                        st.markdown("<div class='lock-badge-banner'>🔒 Round of 16 Selections Locked (Tournament Started)</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='lock-badge-banner'>🔒 Round of 16 Selections Locked</div>", unsafe_allow_html=True)

                for m_id, (h, a) in o_r16.items():
                    if m_id in st.session_state:
                        user_preds[m_id] = st.session_state[m_id]
                    render_match_card(h, a, m_id.replace("_", " "), m_id, disabled=is_r16_locked, score_mode=False, scores_dict=user_preds)

                if not is_r16_locked:
                    if st.button("🔒 Lock Round of 16 Predictions", use_container_width=True):
                        for m_key in r16_keys:
                            val = st.session_state.get(m_key, user_preds.get(m_key))
                            if val and val != "Select Winner" and not str(val).startswith("W"):
                                opts = o_r16[m_key]
                                if val == opts[0]: db_save_prediction(c_uid, active_league_id, m_key, 1)
                                elif val == opts[1]: db_save_prediction(c_uid, active_league_id, m_key, 2)
                        db_lock_predictions(c_uid, active_league_id, r16_keys)
                        st.success("Round of 16 predictions successfully locked!")
                        st.cache_data.clear()
                        st.rerun()

            with ko_tabs[2]:
                def get_ko_prev_r16(m_key):
                    val = st.session_state.get(m_key, user_preds.get(m_key))
                    if val in o_r16.get(m_key, ("","")): return val
                    return f"W{m_key.split('_')[1]}"

                o_qf = {
                    "Match_97": (get_ko_prev_r16("Match_89"), get_ko_prev_r16("Match_90")), "Match_98": (get_ko_prev_r16("Match_93"), get_ko_prev_r16("Match_94")),
                    "Match_99": (get_ko_prev_r16("Match_91"), get_ko_prev_r16("Match_92")), "Match_100": (get_ko_prev_r16("Match_95"), get_ko_prev_r16("Match_96"))
                }
                qf_keys = list(o_qf.keys())
                is_qf_locked = global_tournament_lock or all(k in locked_keys_set for k in qf_keys)

                if is_qf_locked:
                    if global_tournament_lock:
                        st.markdown("<div class='lock-badge-banner'>🔒 Quarter-Final Selections Locked (Tournament Started)</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='lock-badge-banner'>🔒 Quarter-Final Selections Locked</div>", unsafe_allow_html=True)

                for m_id, (h, a) in o_qf.items():
                    if m_id in st.session_state:
                        user_preds[m_id] = st.session_state[m_id]
                    render_match_card(h, a, m_id.replace("_", " "), m_id, disabled=is_qf_locked, score_mode=False, scores_dict=user_preds)

                if not is_qf_locked:
                    if st.button("🔒 Lock Quarter-Final Predictions", use_container_width=True):
                        for m_key in qf_keys:
                            val = st.session_state.get(m_key, user_preds.get(m_key))
                            if val and val != "Select Winner" and not str(val).startswith("W"):
                                opts = o_qf[m_key]
                                if val == opts[0]: db_save_prediction(c_uid, active_league_id, m_key, 1)
                                elif val == opts[1]: db_save_prediction(c_uid, active_league_id, m_key, 2)
                        db_lock_predictions(c_uid, active_league_id, qf_keys)
                        st.success("Quarter-Final predictions successfully locked!")
                        st.cache_data.clear()
                        st.rerun()

            with ko_tabs[3]:
                def get_ko_prev_qf(m_key):
                    val = st.session_state.get(m_key, user_preds.get(m_key))
                    if val in o_qf.get(m_key, ("","")): return val
                    return f"W{m_key.split('_')[1]}"

                sf1_h, sf1_a = get_ko_prev_qf("Match_97"), get_ko_prev_qf("Match_98")
                sf2_h, sf2_a = get_ko_prev_qf("Match_99"), get_ko_prev_qf("Match_100")

                finals_keys = ["Match_101", "Match_102", "Match_103", "Match_104"]
                is_finals_locked = global_tournament_lock or all(k in locked_keys_set for k in finals_keys)

                if is_finals_locked:
                    if global_tournament_lock:
                        st.markdown("<div class='lock-badge-banner'>🔒 Finals Selections Locked (Tournament Started)</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='lock-badge-banner'>🔒 Finals Selections Locked</div>", unsafe_allow_html=True)

                sf1_opts = ["Select Winner", sf1_h, sf1_a]
                curr_sf1 = user_preds.get("Match_101", "Select Winner")
                if str(curr_sf1) == "1": curr_sf1 = sf1_h
                elif str(curr_sf1) == "2": curr_sf1 = sf1_a
                idx_sf1 = sf1_opts.index(curr_sf1) if curr_sf1 in sf1_opts else 0
                chosen_sf1 = st.selectbox("Semi Final 1 Winner", sf1_opts, index=idx_sf1, format_func=fmt_team, key="final_sf1_sel", disabled=is_finals_locked)
                user_preds["Match_101"] = chosen_sf1

                sf2_opts = ["Select Winner", sf2_h, sf2_a]
                curr_sf2 = user_preds.get("Match_102", "Select Winner")
                if str(curr_sf2) == "1": curr_sf2 = sf2_h
                elif str(curr_sf2) == "2": curr_sf2 = sf2_a
                idx_sf2 = sf2_opts.index(curr_sf2) if curr_sf2 in sf2_opts else 0
                chosen_sf2 = st.selectbox("Semi Final 2 Winner", sf2_opts, index=idx_sf2, format_func=fmt_team, key="final_sf2_sel", disabled=is_finals_locked)
                user_preds["Match_102"] = chosen_sf2

                sf1_l = sf1_a if user_preds["Match_101"] == sf1_h else sf1_h
                sf2_l = sf2_a if user_preds["Match_102"] == sf2_h else sf2_h

                p3_opts = ["Select Winner", sf1_l, sf2_l]
                curr_p3 = user_preds.get("Match_103", "Select Winner")
                if str(curr_p3) == "1": curr_p3 = sf1_l
                elif str(curr_p3) == "2": curr_p3 = sf2_l
                idx_p3 = p3_opts.index(curr_p3) if curr_p3 in p3_opts else 0
                chosen_p3 = st.selectbox("🥉 3rd Place Winner Selection", p3_opts, index=idx_p3, format_func=fmt_team, key="final_p3_sel", disabled=is_finals_locked)
                user_preds["Match_103"] = chosen_p3

                f_opts = ["Select Winner", user_preds["Match_101"], user_preds["Match_102"]]
                curr_f = user_preds.get("Match_104", "Select Winner")
                if str(curr_f) == "1": curr_f = user_preds["Match_101"]
                elif str(curr_f) == "2": curr_f = user_preds["Match_102"]
                idx_f = f_opts.index(curr_f) if curr_f in f_opts else 0
                chosen_f = st.selectbox("🥇 Grand Champion Prediction", f_opts, index=idx_f, format_func=fmt_team, key="final_champ_sel", disabled=is_finals_locked)
                user_preds["Match_104"] = chosen_f

                if not is_finals_locked:
                    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
                    if st.button("🔒 Lock Finals Brackets Predictions", use_container_width=True):
                        if user_preds["Match_101"] in sf1_opts[1:]:
                            db_save_prediction(c_uid, active_league_id, "Match_101", 1 if user_preds["Match_101"] == sf1_h else 2)
                        if user_preds["Match_102"] in sf2_opts[1:]:
                            db_save_prediction(c_uid, active_league_id, "Match_102", 1 if user_preds["Match_102"] == sf2_h else 2)
                        if user_preds["Match_103"] in p3_opts[1:]:
                            db_save_prediction(c_uid, active_league_id, "Match_103", 1 if user_preds["Match_103"] == sf1_l else 2)
                        if user_preds["Match_104"] in f_opts[1:]:
                            db_save_prediction(c_uid, active_league_id, "Match_104", 1 if user_preds["Match_104"] == user_preds["Match_101"] else 2)

                        db_lock_predictions(c_uid, active_league_id, finals_keys)
                        st.success("Finals brackets predictions successfully locked!")
                        st.cache_data.clear()
                        st.rerun()




# ==============================================================================
# ==============================================================================
# --- 15. ADMINISTRATIVE CONTROL PANEL ---
# ==============================================================================
elif app_tab == "🛠️ Admin Dashboard" and is_league_admin:
    st.header(f"🛠️ {selected_league_name} Admin Control Panel")
    actual = db_fetch_league_actual_results(active_league_id)
    admin_tabs = st.tabs(["Group Stage Results", "Knockout Round Results"])

    with admin_tabs[0]:
        st.subheader("📆 All Group Matches (Match Order)")

        # Toggle to auto-hide matches that already have an official score locked in
        hide_completed = st.checkbox("🔍 Hide games with locked scores", value=True, key="admin_hide_completed")

        flat_chrono_list = []
        for g_name, matches in CHRONO_MATCHES.items():
            for m in matches:
                flat_chrono_list.append({
                    "id": m["id"],
                    "home": m["home"],
                    "away": m["away"],
                    "group": g_name
                })
        flat_chrono_list = sorted(flat_chrono_list, key=lambda x: x["id"])

        for match in flat_chrono_list:
            m_id = match["id"]
            kh, ka = f"Match_{m_id}_h", f"Match_{m_id}_a"

            is_score_saved = (kh in actual["group"] and ka in actual["group"])

            # Skip rendering this match card entirely if it's locked and the hide filter is enabled
            if hide_completed and is_score_saved:
                continue

            actual["group"] = render_match_card(
                home=match["home"], away=match["away"], label=f"Match #{m_id} ({match['group']}) Official Score",
                key_prefix=f"Match_{m_id}", disabled=is_score_saved, score_mode=True, scores_dict=actual["group"]
            )

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if not is_score_saved:
                    if st.button("📢 Save Match Score", key=f"btn_pub_Match_{m_id}", use_container_width=True):
                        db_save_league_actual_result(active_league_id, kh, actual["group"][kh])
                        db_save_league_actual_result(active_league_id, ka, actual["group"][ka])
                        st.cache_data.clear()  
                        st.success(f"Match #{m_id} score locked and live!")
                        st.rerun()
                else:
                    st.markdown("<div style='color: #22c55e; font-weight: bold; padding-top: 10px;'>✅ Confirmed Locked</div>", unsafe_allow_html=True)
            with col_b2:
                if is_score_saved:
                    if st.button("🔓 Reset / Unlock Match Score", key=f"btn_unl_Match_{m_id}", use_container_width=True):
                        db_delete_league_actual_result(active_league_id, kh)
                        db_delete_league_actual_result(active_league_id, ka)
                        st.cache_data.clear()  
                        st.warning(f"Match #{m_id} score cleared from records.")
                        st.rerun()
            st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);' />", unsafe_allow_html=True)

    with admin_tabs[1]:
        # Pass empty tie-breaker structures into the bracket manager for official standings
        actual_calc_bracket = resolve_bracket_teams(
            None, target_is_actual=True, actual_results_obj=actual,
            manual_tb_locks={}, manual_tb_orders={}
        )

        adm_ko_tabs = st.tabs(["Round of 32", "Round of 16", "Quarter-Finals", "Finals","Canteen Print Station"])

        # --- ADMIN WORKSPACE: ROUND OF 32 ---
        with adm_ko_tabs[0]:
            st.subheader("🌳 Round of 32 Matches (Populated via Real Group Standings)")
            
            st.markdown("### 📊 Official Third-Place Standings Calculation")
            
            if "third_place_top8" in actual_calc_bracket:
                admin_3rd_table = actual_calc_bracket["third_place_top8"]
                admin_combo_str = actual_calc_bracket.get("third_place_code", "UNKNOWN")
                
                st.write("Below is the official ranking of all third-placed teams across the 12 groups. The top 8 teams qualify for the Round of 32 layout matrix.")
                
                st.dataframe(
                    admin_3rd_table,
                    column_config={
                        "Group": "Group",
                        "Team": "Team Name",
                        "Pts": "Pts",
                        "GD": "GD",
                        "GF": "GS",
                        "Position": "Status"
                    },
                    use_container_width=True
                )
                
                st.info(f"🧬 **Generated 8-Letter Matrix String:** `{admin_combo_str}`")
                st.caption("This 8-letter key has matched against the database lookup configuration to route the correct groups into their corresponding bracket paths below.")
            else:
                st.warning("⚠️ Engine calculated successfully, but intermediate third-place table arrays aren't exposed in actual_calc_bracket yet. Displaying brackets directly.")
            
            st.markdown("<hr style='margin: 15px 0; border-top: 2px dashed rgba(255,255,255,0.1);' />", unsafe_allow_html=True)
            
            # --- ROUND OF 32 MATCH LIST ---
            adm_r32_pairings = actual_calc_bracket["r32_pairings"]
            for m_id, (h, a) in adm_r32_pairings.items():
                is_ko_saved = (m_id in actual["ko_winners"])

                # Unified resolution mapping helper path tracking
                saved_winner = actual["ko_winners"].get(m_id)
                if str(saved_winner) == "1": actual["ko_winners"][m_id] = h
                elif str(saved_winner) == "2": actual["ko_winners"][m_id] = a

                actual["ko_winners"][m_id] = render_match_card(h, a, f"Winner: {m_id.replace('_', ' ')}", m_id, disabled=is_ko_saved, score_mode=False, scores_dict=actual["ko_winners"])

                col_ko1, col_ko2 = st.columns(2)
                with col_ko1:
                    if not is_ko_saved:
                        if st.button("📢 Lock Knockout Winner", key=f"btn_ko_{m_id}", use_container_width=True):
                            flag_val = 1 if actual["ko_winners"][m_id] == h else (2 if actual["ko_winners"][m_id] == a else 0)
                            if flag_val > 0:
                                db_save_league_actual_result(active_league_id, m_id, flag_val)
                                st.cache_data.clear()
                                st.success(f"{m_id.replace('_', ' ')} progression locked!")
                                st.rerun()
                    else:
                        st.markdown("<div style='color: #22c55e; font-weight: bold; padding-top: 10px;'>✅ Confirmed Locked</div>", unsafe_allow_html=True)
                with col_ko2:
                    if is_ko_saved:
                        if st.button("🔓 Reset / Unlock Winner", key=f"btn_unl_ko_{m_id}", use_container_width=True):
                            db_delete_league_actual_result(active_league_id, m_id)
                            st.cache_data.clear()
                            st.warning(f"{m_id.replace('_', ' ')} status cleared.")
                            st.rerun()
                st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);' />", unsafe_allow_html=True)

        # --- ADMIN WORKSPACE: ROUND OF 16 ---
        with adm_ko_tabs[1]:
            def get_adm_ko_prev(m_key):
                val = actual["ko_winners"].get(m_key)
                if str(val) == "1": return actual_calc_bracket["r32_pairings"].get(m_key, ("",""))[0]
                if str(val) == "2": return actual_calc_bracket["r32_pairings"].get(m_key, ("",""))[1]
                if val and not (str(val).startswith("W") and "_" not in str(val)): return str(val)
                return f"W{m_key.split('_')[1]}"

            adm_r16 = {
                "Match_89": (get_adm_ko_prev("Match_74"), get_adm_ko_prev("Match_77")), "Match_90": (get_adm_ko_prev("Match_73"), get_adm_ko_prev("Match_75")),
                "Match_93": (get_adm_ko_prev("Match_83"), get_adm_ko_prev("Match_84")), "Match_94": (get_adm_ko_prev("Match_81"), get_adm_ko_prev("Match_82")),
                "Match_91": (get_adm_ko_prev("Match_76"), get_adm_ko_prev("Match_78")), "Match_92": (get_adm_ko_prev("Match_79"), get_adm_ko_prev("Match_80")),
                "Match_95": (get_adm_ko_prev("Match_86"), get_adm_ko_prev("Match_88")), "Match_96": (get_adm_ko_prev("Match_85"), get_adm_ko_prev("Match_87"))
            }
            st.subheader("🌳 Round of 16 Matches")
            for m_id, (h, a) in adm_r16.items():
                is_ko_saved = (m_id in actual["ko_winners"])

                saved_winner = actual["ko_winners"].get(m_id)
                if str(saved_winner) == "1": actual["ko_winners"][m_id] = h
                elif str(saved_winner) == "2": actual["ko_winners"][m_id] = a

                actual["ko_winners"][m_id] = render_match_card(h, a, f"Winner: {m_id.replace('_', ' ')}", m_id, disabled=is_ko_saved, score_mode=False, scores_dict=actual["ko_winners"])

                col_ko1, col_ko2 = st.columns(2)
                with col_ko1:
                    if not is_ko_saved:
                        if st.button("📢 Lock Knockout Winner", key=f"btn_ko_{m_id}", use_container_width=True):
                            flag_val = 1 if actual["ko_winners"][m_id] == h else (2 if actual["ko_winners"][m_id] == a else 0)
                            if flag_val > 0:
                                db_save_league_actual_result(active_league_id, m_id, flag_val)
                                st.cache_data.clear()
                                st.success(f"{m_id.replace('_', ' ')} progression locked!")
                                st.rerun()
                    else:
                        st.markdown("<div style='color: #22c55e; font-weight: bold; padding-top: 10px;'>✅ Confirmed Locked</div>", unsafe_allow_html=True)
                with col_ko2:
                    if is_ko_saved:
                        if st.button("🔓 Reset / Unlock Winner", key=f"btn_unl_ko_{m_id}", use_container_width=True):
                            db_delete_league_actual_result(active_league_id, m_id)
                            st.cache_data.clear()
                            st.warning(f"{m_id.replace('_', ' ')} status cleared.")
                            st.rerun()
                st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);' />", unsafe_allow_html=True)

        # --- ADMIN WORKSPACE: QUARTER-FINALS ---
        with adm_ko_tabs[2]:
            def get_adm_ko_prev_r16(m_key):
                val = actual["ko_winners"].get(m_key)
                if str(val) == "1": return adm_r16.get(m_key, ("",""))[0]
                if str(val) == "2": return adm_r16.get(m_key, ("",""))[1]
                if val and not (str(val).startswith("W") and "_" not in str(val)): return str(val)
                return f"W{m_key.split('_')[1]}"

            adm_qf = {
                "Match_97": (get_adm_ko_prev_r16("Match_89"), get_adm_ko_prev_r16("Match_90")), 
                "Match_98": (get_adm_ko_prev_r16("Match_93"), get_adm_ko_prev_r16("Match_94")),
                "Match_99": (get_adm_ko_prev_r16("Match_91"), get_adm_ko_prev_r16("Match_92")), 
                "Match_100": (get_adm_ko_prev_r16("Match_95"), get_adm_ko_prev_r16("Match_96"))
            }
            st.subheader("🌳 Quarter-Final Matches")
            for m_id, (h, a) in adm_qf.items():
                is_ko_saved = (m_id in actual["ko_winners"])

                saved_winner = actual["ko_winners"].get(m_id)
                if str(saved_winner) == "1": actual["ko_winners"][m_id] = h
                elif str(saved_winner) == "2": actual["ko_winners"][m_id] = a

                actual["ko_winners"][m_id] = render_match_card(h, a, f"Winner: {m_id.replace('_', ' ')}", m_id, disabled=is_ko_saved, score_mode=False, scores_dict=actual["ko_winners"])

                col_ko1, col_ko2 = st.columns(2)
                with col_ko1:
                    if not is_ko_saved:
                        if st.button("📢 Lock Knockout Winner", key=f"btn_ko_{m_id}", use_container_width=True):
                            flag_val = 1 if actual["ko_winners"][m_id] == h else (2 if actual["ko_winners"][m_id] == a else 0)
                            if flag_val > 0:
                                db_save_league_actual_result(active_league_id, m_id, flag_val)
                                st.cache_data.clear()
                                st.success(f"{m_id.replace('_', ' ')} progression locked!")
                                st.rerun()
                    else:
                        st.markdown("<div style='color: #22c55e; font-weight: bold; padding-top: 10px;'>✅ Confirmed Locked</div>", unsafe_allow_html=True)
                with col_ko2:
                    if is_ko_saved:
                        if st.button("🔓 Reset / Unlock Winner", key=f"btn_unl_ko_{m_id}", use_container_width=True):
                            db_delete_league_actual_result(active_league_id, m_id)
                            st.cache_data.clear()
                            st.warning(f"{m_id.replace('_', ' ')} status cleared.")
                            st.rerun()
                st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);' />", unsafe_allow_html=True)

        # --- ADMIN WORKSPACE: FINALS & THIRD PLACE ---
        with adm_ko_tabs[3]:
            def get_adm_ko_prev_qf(m_key):
                val = actual["ko_winners"].get(m_key)
                if str(val) == "1": return adm_qf.get(m_key, ("",""))[0]
                if str(val) == "2": return adm_qf.get(m_key, ("",""))[1]
                if val and not (str(val).startswith("W") and "_" not in str(val)): return str(val)
                return f"W{m_key.split('_')[1]}"

            sf1_h, sf1_a = get_adm_ko_prev_qf("Match_97"), get_adm_ko_prev_qf("Match_98")
            sf2_h, sf2_a = get_adm_ko_prev_qf("Match_99"), get_adm_ko_prev_qf("Match_100")

            st.subheader("🏆 Semifinals, 3rd Place & Grand Final Results Setup")

            # Match 101 (Semi Final 1)
            is_m101_saved = ("Match_101" in actual["ko_winners"])
            
            saved_m101 = actual["ko_winners"].get("Match_101")
            if str(saved_m101) == "1": actual["ko_winners"]["Match_101"] = sf1_h
            elif str(saved_m101) == "2": actual["ko_winners"]["Match_101"] = sf1_a
            
            actual["ko_winners"]["Match_101"] = render_match_card(sf1_h, sf1_a, "Semi Final 1 Official Winner", "Match_101", disabled=is_m101_saved, score_mode=False, scores_dict=actual["ko_winners"])
            c_sf1_1, c_sf1_2 = st.columns(2)
            with c_sf1_1:
                if not is_m101_saved:
                    if st.button("📢 Lock Semi Final 1 Winner", key="btn_lock_m101", use_container_width=True):
                        f_v = 1 if actual["ko_winners"]["Match_101"] == sf1_h else (2 if actual["ko_winners"]["Match_101"] == sf1_a else 0)
                        if f_v > 0:
                            db_save_league_actual_result(active_league_id, "Match_101", f_v)
                            st.cache_data.clear()
                            st.rerun()
                else: st.markdown("<div style='color: #22c55e; font-weight: bold;'>✅ SF1 Locked</div>", unsafe_allow_html=True)
            with c_sf1_2:
                if is_m101_saved and st.button("🔓 Unlock Semi Final 1", key="btn_unl_m101", use_container_width=True):
                    db_delete_league_actual_result(active_league_id, "Match_101")
                    st.cache_data.clear()
                    st.rerun()

            st.markdown("<hr style='margin: 15px 0; border-top: 1px solid rgba(255,255,255,0.1);' />", unsafe_allow_html=True)

            # Match 102 (Semi Final 2)
            is_m102_saved = ("Match_102" in actual["ko_winners"])
            
            saved_m102 = actual["ko_winners"].get("Match_102")
            if str(saved_m102) == "1": actual["ko_winners"]["Match_102"] = sf2_h
            elif str(saved_m102) == "2": actual["ko_winners"]["Match_102"] = sf2_a

            actual["ko_winners"]["Match_102"] = render_match_card(sf2_h, sf2_a, "Semi Final 2 Official Winner", "Match_102", disabled=is_m102_saved, score_mode=False, scores_dict=actual["ko_winners"])
            c_sf2_1, c_sf2_2 = st.columns(2)
            with c_sf2_1:
                if not is_m102_saved:
                    if st.button("📢 Lock Semi Final 2 Winner", key="btn_lock_m102", use_container_width=True):
                        f_v = 1 if actual["ko_winners"]["Match_102"] == sf2_h else (2 if actual["ko_winners"]["Match_102"] == sf2_a else 0)
                        if f_v > 0:
                            db_save_league_actual_result(active_league_id, "Match_102", f_v)
                            st.cache_data.clear()
                            st.rerun()
                else: st.markdown("<div style='color: #22c55e; font-weight: bold;'>✅ SF2 Locked</div>", unsafe_allow_html=True)
            with c_sf2_2:
                if is_m102_saved and st.button("🔓 Unlock Semi Final 2", key="btn_unl_m102", use_container_width=True):
                    db_delete_league_actual_result(active_league_id, "Match_102")
                    st.cache_data.clear()
                    st.rerun()

            st.markdown("<hr style='margin: 15px 0; border-top: 1px solid rgba(255,255,255,0.1);' />", unsafe_allow_html=True)

            # --- DYNAMICALLY RESOLVE SEMIFINAL WINNERS & LOSERS ---
            sf1_winner_saved = actual["ko_winners"].get("Match_101")
            sf2_winner_saved = actual["ko_winners"].get("Match_102")

            if str(sf1_winner_saved) == "1" or sf1_winner_saved == sf1_h: sf1_w, sf1_l = sf1_h, sf1_a
            elif str(sf1_winner_saved) == "2" or sf1_winner_saved == sf1_a: sf1_w, sf1_l = sf1_a, sf1_h
            else: sf1_w, sf1_l = None, "TBD (Loser SF1)"

            if str(sf2_winner_saved) == "1" or sf2_winner_saved == sf2_h: sf2_w, sf2_l = sf2_h, sf2_a
            elif str(sf2_winner_saved) == "2" or sf2_winner_saved == sf2_a: sf2_w, sf2_l = sf2_a, sf2_h
            else: sf2_w, sf2_l = None, "TBD (Loser SF2)"

            # Match 103 (3rd Place Playoff)
            is_m103_saved = ("Match_103" in actual["ko_winners"])
            
            saved_m103 = actual["ko_winners"].get("Match_103")
            if str(saved_m103) == "1": actual["ko_winners"]["Match_103"] = sf1_l
            elif str(saved_m103) == "2": actual["ko_winners"]["Match_103"] = sf2_l

            actual["ko_winners"]["Match_103"] = render_match_card(sf1_l, sf2_l, "🥉 3rd Place Playoff Winner", "Match_103", disabled=is_m103_saved, score_mode=False, scores_dict=actual["ko_winners"])
            c_p3_1, c_p3_2 = st.columns(2)
            with c_p3_1:
                if not is_m103_saved:
                    if st.button("📢 Lock 3rd Place Winner", key="btn_lock_m103", use_container_width=True):
                        f_v = 1 if actual["ko_winners"]["Match_103"] == sf1_l else (2 if actual["ko_winners"]["Match_103"] == sf2_l else 0)
                        if f_v > 0:
                            db_save_league_actual_result(active_league_id, "Match_103", f_v)
                            st.cache_data.clear()
                            st.rerun()
                else: st.markdown("<div style='color: #22c55e; font-weight: bold;'>✅ 3rd Place Locked</div>", unsafe_allow_html=True)
            with c_p3_2:
                if is_m103_saved and st.button("🔓 Unlock 3rd Place Playoff", key="btn_unl_m103", use_container_width=True):
                    db_delete_league_actual_result(active_league_id, "Match_103")
                    st.cache_data.clear()
                    st.rerun()

            st.markdown("<hr style='margin: 15px 0; border-top: 1px solid rgba(255,255,255,0.1);' />", unsafe_allow_html=True)

            # Match 104 (Grand Final)
            f_h = sf1_w if sf1_w else "TBD (Winner SF1)"
            f_a = sf2_w if sf2_w else "TBD (Winner SF2)"

            is_m104_saved = ("Match_104" in actual["ko_winners"])
            
            saved_m104 = actual["ko_winners"].get("Match_104")
            if str(saved_m104) == "1": actual["ko_winners"]["Match_104"] = f_h
            elif str(saved_m104) == "2": actual["ko_winners"]["Match_104"] = f_a

            actual["ko_winners"]["Match_104"] = render_match_card(f_h, f_a, "🥇 Grand Final Tournament Champion", "Match_104", disabled=is_m104_saved, score_mode=False, scores_dict=actual["ko_winners"])
            c_f_1, c_f_2 = st.columns(2)
            with c_f_1:
                if not is_m104_saved:
                    if st.button("📢 Lock Grand Champion", key="btn_lock_m104", use_container_width=True):
                        f_v = 1 if actual["ko_winners"]["Match_104"] == f_h else (2 if actual["ko_winners"]["Match_104"] == f_a else 0)
                        if f_v > 0:
                            db_save_league_actual_result(active_league_id, "Match_104", f_v)
                            st.cache_data.clear()
                            st.rerun()
                else: st.markdown("<div style='color: #22c55e; font-weight: bold;'>🏆 Champion Locked</div>", unsafe_allow_html=True)
            with c_f_2:
                if is_m104_saved and st.button("🔓 Unlock Grand Final Champion", key="btn_unl_m104", use_container_width=True):
                    db_delete_league_actual_result(active_league_id, "Match_104")
                    st.cache_data.clear()
                    st.rerun()

        # --- ADMIN WORKSPACE: INDIVIDUAL CANTEEN WALL CHART DOSSIERS (EXPLICIT MATRIX SCHEMA FIX) ---
        with adm_ko_tabs[4]:
            st.title("🖨️ PDF Generator")
            st.write("Select a teammate to compile their complete prediction history (All Match Scores, Group Tables, and the Full Knockout Tree) into an office wall-chart layout.")

            import io
            import pandas as pd
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            # Explicitly reference your dynamic R32 configuration keys for local processing
            LOCAL_R32_CONFIG = {
                "Match_73": {"home": ("Group A", "2nd"), "away": ("Group B", "2nd")},
                "Match_74": {"home": ("Group E", "1st"), "away_lookup": "3-ABCDF"},
                "Match_75": {"home": ("Group F", "1st"), "away": ("Group C", "2nd")},
                "Match_76": {"home": ("Group C", "1st"), "away": ("Group F", "2nd")},
                "Match_77": {"home": ("Group I", "1st"), "away_lookup": "3-CDFGH"},
                "Match_78": {"home": ("Group E", "2nd"), "away": ("Group I", "2nd")},
                "Match_79": {"home": ("Group A", "1st"), "away_lookup": "3-CEFHI"},
                "Match_80": {"home": ("Group L", "1st"), "away_lookup": "3-EHIJK"},
                "Match_81": {"home": ("Group D", "1st"), "away_lookup": "3-BEFIJ"},
                "Match_82": {"home": ("Group G", "1st"), "away_lookup": "3-AEHIJ"},
                "Match_83": {"home": ("Group K", "2nd"), "away": ("Group L", "2nd")},
                "Match_84": {"home": ("Group H", "1st"), "away": ("Group J", "2nd")},
                "Match_85": {"home": ("Group B", "1st"), "away_lookup": "3-EFGIJ"},
                "Match_86": {"home": ("Group J", "1st"), "away": ("Group H", "2nd")},
                "Match_87": {"home": ("Group K", "1st"), "away_lookup": "3-DEIJL"},
                "Match_88": {"home": ("Group D", "2nd"), "away": ("Group G", "2nd")}
            }

            # 1. FETCH ALL REGISTERED USERS NATIVELY FROM THE USERS TABLE
            try:
                db_users = supabase.table("users").select("id, username").execute().data
            except Exception as e:
                st.error(f"Error querying users database: {e}")
                db_users = []

            if db_users:
                user_map = {u["username"]: u["id"] for u in db_users if u.get("username")}
                sorted_names = sorted(list(user_map.keys()))
                
                selected_user_name = st.selectbox("🎯 Select Teammate Profile:", sorted_names, key="canteen_pdf_select_v12")
                target_user_id = user_map[selected_user_name]

                # 2. FETCH ALL RELATIONAL PREDICTION ROWS FOR THIS USER & LEAGUE CONTEXT
                try:
                    raw_rows = supabase.table("predictions").select("match_key, score_value").eq("user_id", target_user_id).eq("league_id", active_league_id).execute().data
                except Exception as e:
                    st.error(f"Error fetching user predictions: {e}")
                    raw_rows = []

                # Reconstruct operational dictionaries matching your engine inputs
                scores_dict = {}
                ko_choices = {}
                for r in raw_rows:
                    m_key = r.get("match_key", "")
                    s_val = r.get("score_value")
                    if m_key:
                        scores_dict[m_key] = s_val
                        if not m_key.endswith("_h") and not m_key.endswith("_a"):
                            ko_choices[m_key] = str(s_val).strip()

                # Fetch user tie-breaker profiles to guarantee 100% bracket logic match consistency
                local_tb_orders = {}
                local_tb_locks = {}
                try:
                    tb_saved_records = supabase.table("tie_breakers").select("group_name, team_order, is_locked").eq("user_id", target_user_id).eq("league_id", active_league_id).execute().data
                    for row in tb_saved_records:
                        local_tb_orders[f"tb_order_{row['group_name']}"] = row["team_order"]
                        local_tb_locks[f"tb_locked_{row['group_name']}"] = row["is_locked"]
                except Exception as tb_err:
                    pass

                # 3. NATIVE EXECUTION OF YOUR COMPUTATION ENGINES
                with st.spinner(f"Simulating complete tournament bracket tree for {selected_user_name}..."):
                    
                    # Exact replica of your run_standings_engine
                    def local_run_standings(s_dict, locks, orders):
                        all_group_results = {}
                        for g_name, teams in GROUPS.items():
                            standings = {t: {"Group": g_name, "Pts": 0, "GD": 0, "GF": 0} for t in teams}
                            for match in CHRONO_MATCHES.get(g_name, []):
                                m_id = match["id"]
                                home, away = match["home"], match["away"]
                                kh, ka = f"Match_{m_id}_h", f"Match_{m_id}_a"
                                h_score = int(s_dict.get(kh, 0) or 0)
                                a_score = int(s_dict.get(ka, 0) or 0)
                                standings[home]["GF"] += h_score
                                standings[away]["GF"] += a_score
                                standings[home]["GD"] += (h_score - a_score)
                                standings[away]["GD"] += (a_score - h_score)
                                if h_score > a_score: standings[home]["Pts"] += 3
                                elif a_score > h_score: standings[away]["Pts"] += 3
                                else:
                                    standings[home]["Pts"] += 1
                                    standings[away]["Pts"] += 1

                            df_g = pd.DataFrame.from_dict(standings, orient='index').reset_index().rename(columns={'index': 'Team'})
                            df_g['h2h_pts'] = 0; df_g['h2h_gd'] = 0; df_g['h2h_gf'] = 0
                            df_g = df_g.sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)

                            tb_lock_val = locks.get(f"tb_locked_{g_name}", False)
                            tb_order_val = orders.get(f"tb_order_{g_name}", [])
                            if tb_lock_val and tb_order_val:
                                if sorted(tb_order_val) == sorted(df_g['Team'].tolist()):
                                    df_g['Team'] = pd.Categorical(df_g['Team'], categories=tb_order_val, ordered=True)
                                    df_g = df_g.sort_values(by='Team', ascending=True).reset_index(drop=True)
                                    df_g['Team'] = df_g['Team'].astype(str)
                            
                            df_g['Position'] = range(1, len(df_g) + 1)
                            all_group_results[g_name] = df_g
                        
                        third_place_pool = [df[df['Position'] == 3].iloc[0].to_dict() for df in all_group_results.values() if not df[df['Position'] == 3].empty]
                        wildcard_df = pd.DataFrame(third_place_pool).sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
                        adv_wildcards = wildcard_df.head(8).to_dict(orient="records")
                        return all_group_results, adv_wildcards

                    # Compute local standing tables
                    g_tables, qualifying_wildcards = local_run_standings(scores_dict, local_tb_locks, local_tb_orders)

                    def get_1st(g): return g_tables[g].iloc[0]["Team"] if g in g_tables and not g_tables[g].empty else "TBD"
                    def get_2nd(g): return g_tables[g].iloc[1]["Team"] if g in g_tables and not g_tables[g].empty else "TBD"
                    
                    # Direct lookup function extracting the 3rd place team name from any calculated Group letter
                    def get_3rd_by_letter(letter_char):
                        g_key = f"Group {letter_char.upper().strip()}"
                        if g_key in g_tables and len(g_tables[g_key]) >= 3:
                            return g_tables[g_key].iloc[2]["Team"]
                        return "TBD"

                    qualifying_group_letters = sorted([row["Group"].replace("Group ", "").strip() for row in qualifying_wildcards])
                    combination_lookup_string = "".join(qualifying_group_letters).upper().strip()

                    # --- EXPLICIT LOOKUP QUERY AGAINST group_combination ---
                    db_mapping_row = None
                    if len(combination_lookup_string) == 8:
                        try:
                            # Direct precise match against the group_combination schema column using case-insensitive ILIKE wildcards
                            res = supabase.table("assign_third").select("*").ilike("group_combination", f"%{combination_lookup_string}%").execute()
                            if res and res.data and len(res.data) > 0:
                                db_mapping_row = {str(k).strip(): str(v).strip().upper() for k, v in res.data[0].items() if v is not None}
                        except Exception as matrix_err:
                            st.error(f"Matrix indexing issue encountered: {matrix_err}")

                    # --- ROUND OF 32 RESOLUTION (Fully Dynamic Across All 495 Combos) ---
                    r32_display = []
                    r32_winners = {}
                    for m_id, structure in LOCAL_R32_CONFIG.items():
                        home_g, home_pos = structure["home"][0], structure["home"][1]
                        h_team = get_1st(home_g) if home_pos == "1st" else get_2nd(home_g)
                        
                        if "away" in structure:
                            away_g, away_pos = structure["away"][0], structure["away"][1]
                            a_team = get_1st(away_g) if away_pos == "1st" else get_2nd(away_g)
                        elif "away_lookup" in structure:
                            lookup_col_header = str(structure["away_lookup"]).strip() # E.g., "3-ABCDF"
                            resolved_target_group_letter = None
                            
                            # Scan row dynamically for exact or underscored layout variations
                            if db_mapping_row:
                                if lookup_col_header in db_mapping_row:
                                    resolved_target_group_letter = db_mapping_row[lookup_col_header]
                                elif lookup_col_header.replace("-", "_") in db_mapping_row:
                                    resolved_target_group_letter = db_mapping_row[lookup_col_header.replace("-", "_")]
                            
                            # Pull the true 3rd place team from that group's standing positions
                            if resolved_target_group_letter:
                                a_team = get_3rd_by_letter(resolved_target_group_letter)
                            else:
                                a_team = f"TBD ({lookup_col_header})"
                        else:
                            a_team = "TBD"
                        
                        choice = ko_choices.get(m_id, "")
                        winner = h_team if choice == "1" else (a_team if choice == "2" else "TBD")
                        r32_winners[m_id] = winner
                        r32_display.append({"match_id": m_id, "home": h_team, "away": a_team, "winner": winner})

                    # Sort display items numerically from Match_73 to Match_88
                    r32_display = sorted(r32_display, key=lambda x: int(x["match_id"].replace("Match_", "")))

                    # --- ROUND OF 16 RESOLUTION (Matches 89 - 96) ---
                    r16_pairings = {
                        "Match_89": ("Match_74", "Match_77"), "Match_90": ("Match_73", "Match_75"),
                        "Match_91": ("Match_76", "Match_78"), "Match_92": ("Match_79", "Match_80"),
                        "Match_93": ("Match_83", "Match_84"), "Match_94": ("Match_81", "Match_82"),
                        "Match_95": ("Match_86", "Match_88"), "Match_96": ("Match_85", "Match_87")
                    }
                    r16_resolved = {}
                    for m_id, (prev1, prev2) in r16_pairings.items():
                        t1 = r32_winners.get(prev1, "TBD")
                        t2 = r32_winners.get(prev2, "TBD")
                        choice = ko_choices.get(m_id, "")
                        winner = t1 if choice == "1" else (t2 if choice == "2" else "TBD")
                        r16_resolved[m_id] = {"home": t1, "away": t2, "winner": winner}

                    # --- QUARTER FINALS RESOLUTION (Matches 97 - 100) ---
                    qf_pairings = {
                        "Match_97": ("Match_89", "Match_90"), "Match_98": ("Match_93", "Match_94"),
                        "Match_99": ("Match_91", "Match_92"), "Match_100": ("Match_95", "Match_96")
                    }
                    qf_resolved = {}
                    for m_id, (prev1, prev2) in qf_pairings.items():
                        t1 = r16_resolved.get(prev1, {}).get("winner", "TBD")
                        t2 = r16_resolved.get(prev2, {}).get("winner", "TBD")
                        choice = ko_choices.get(m_id, "")
                        winner = t1 if choice == "1" else (t2 if choice == "2" else "TBD")
                        qf_resolved[m_id] = {"home": t1, "away": t2, "winner": winner}

                    # --- SEMI FINALS RESOLUTION (Matches 101 - 102) ---
                    sf_pairings = {
                        "Match_101": ("Match_97", "Match_98"),
                        "Match_102": ("Match_99", "Match_100")
                    }
                    sf_resolved = {}
                    for m_id, (prev1, prev2) in sf_pairings.items():
                        t1 = qf_resolved.get(prev1, {}).get("winner", "TBD")
                        t2 = qf_resolved.get(prev2, {}).get("winner", "TBD")
                        choice = ko_choices.get(m_id, "")
                        winner = t1 if choice == "1" else (t2 if choice == "2" else "TBD")
                        sf_resolved[m_id] = {"home": t1, "away": t2, "winner": winner}

                    # --- FINALS & CHAMPIONS RESOLUTION ---
                    f1 = sf_resolved.get("Match_101", {}).get("winner", "TBD")
                    f2 = sf_resolved.get("Match_102", {}).get("winner", "TBD")
                    champ_choice = ko_choices.get("Match_104", "")
                    grand_champion = f1 if champ_choice == "1" else (f2 if champ_choice == "2" else "TBD")

                    # 3rd Place Playoff Losers Lookup
                    sf1_home = sf_resolved.get("Match_101", {}).get("home", "TBD")
                    sf1_away = sf_resolved.get("Match_101", {}).get("away", "TBD")
                    sf1_win = sf_resolved.get("Match_101", {}).get("winner", "TBD")
                    sf1_loser = sf1_away if sf1_win == sf1_home else sf1_home if sf1_win != "TBD" else "TBD"

                    sf2_home = sf_resolved.get("Match_102", {}).get("home", "TBD")
                    sf2_away = sf_resolved.get("Match_102", {}).get("away", "TBD")
                    sf2_win = sf_resolved.get("Match_102", {}).get("winner", "TBD")
                    sf2_loser = sf2_away if sf2_win == sf2_home else sf2_home if sf2_win != "TBD" else "TBD"

                    third_choice = ko_choices.get("Match_103", "")
                    third_place_winner = sf1_loser if third_choice == "1" else (sf2_loser if third_choice == "2" else "TBD")

                # --- PDF GENERATION ENGINE ---
                def generate_master_dossier_pdf(name, scores, r32_data, r16_data, qf_data, sf_data, third_winner, champion):
                    buffer = io.BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
                    story = []
                    
                    styles = getSampleStyleSheet()
                    title_style = ParagraphStyle('TStyle', parent=styles['Heading1'], fontSize=22, leading=26, textColor=colors.HexColor('#4f46e5'), alignment=1)
                    sub_style = ParagraphStyle('SStyle', parent=styles['Normal'], fontSize=12, leading=16, textColor=colors.HexColor('#374151'), alignment=1)
                    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor('#1e1b4b'), spaceBefore=12, spaceAfter=8)
                    body_style = ParagraphStyle('BStyle', parent=styles['Normal'], fontSize=9, leading=12)

                    # Cover Header Banner
                    story.append(Paragraph("🏆 WORLD CUP 2026 TOURNAMENT PREDICTION", title_style))
                    story.append(Spacer(1, 4))
                    story.append(Paragraph(f"<b>Username:</b> {name}", sub_style))
                    story.append(Spacer(1, 10))
                    story.append(Paragraph("<hr color='#4f46e5' width='100%'/>", body_style))
                    
                    # PART 1: MATCH SCORES
                    story.append(Paragraph("📆 Part 1: Group Score Predictions", h2_style))
                    match_rows = []
                    current_pair = []
                    
                    flat_chrono = sorted([{"id": int(m["id"]), "home": m["home"], "away": m["away"], "group": g} for g, matches in CHRONO_MATCHES.items() for m in matches], key=lambda x: x["id"])
                    
                    for m in flat_chrono:
                        kh, ka = f"Match_{m['id']}_h", f"Match_{m['id']}_a"
                        ph, pa = scores.get(kh, "-"), scores.get(ka, "-")
                        m_str = f"<b>#{m['id']}</b> {m['home']} <b>{ph} - {pa}</b> {m['away']} <font color='gray'>({m['group']})</font>"
                        current_pair.append(Paragraph(m_str, body_style))
                        if len(current_pair) == 2:
                            match_rows.append(current_pair)
                            current_pair = []
                    if current_pair:
                        current_pair.append(Paragraph("", body_style))
                        match_rows.append(current_pair)

                    t_matches = Table(match_rows, colWidths=[270, 270])
                    t_matches.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
                    story.append(t_matches)
                    
                    story.append(PageBreak()) # Shift Standings to Page 2
                    
                    # PART 2: FINAL STANDINGS
                    story.append(Paragraph("📊 Part 2: Predicted Final Group Standings (1st - 4th)", h2_style))
                    standings_data = [["Group Table", "1st Position", "2nd Position", "3rd Position", "4th Position"]]
                    for g in sorted(GROUPS.keys()):
                        teams_list = [g_tables[g].iloc[i]["Team"] if g in g_tables and i < len(g_tables[g]) else "—" for i in range(4)]
                        standings_data.append([g, teams_list[0], teams_list[1], teams_list[2], teams_list[3]])
                    
                    t_standings = Table(standings_data, colWidths=[70, 115, 115, 115, 115])
                    t_standings.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4f46e5')),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
                        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')])
                    ]))
                    story.append(t_standings)
                    
                    story.append(PageBreak()) # Shift Knockout Tree to Page 3
                    
                    # PART 3: FULL DYNAMIC KNOCKOUT TREE PROGRESSION
                    story.append(Paragraph("🌳 Part 3: Predicted Knockout Stage Teams to Progress", h2_style))
                    story.append(Paragraph(f"<b>Calculated Wildcard Combination Code:</b> <font color='#4f46e5'><b>{combination_lookup_string or 'N/A'}</b></font>", body_style))
                    story.append(Spacer(1, 8))

                    ko_tree_rows = [["Match Context ID", "Home Generated Slot", "Away Generated Slot", "Predicted Team Advance"]]
                    
                    # Round of 32
                    for r in r32_data:
                        ko_tree_rows.append([f"{r['match_id']} (Round of 32)", r["home"], r["away"], r["winner"]])

                    # Round of 16
                    for m_id, r in sorted(r16_data.items(), key=lambda x: int(x[0].replace("Match_",""))):
                        ko_tree_rows.append([f"{m_id} (Round of 16)", r["home"], r["away"], r["winner"]])

                    # Quarter Finals
                    for m_id, r in sorted(qf_data.items(), key=lambda x: int(x[0].replace("Match_",""))):
                        ko_tree_rows.append([f"{m_id} (Quarter Final)", r["home"], r["away"], r["winner"]])

                    # Semi Finals
                    for m_id, r in sorted(sf_data.items(), key=lambda x: int(x[0].replace("Match_",""))):
                        ko_tree_rows.append([f"{m_id} (Semi Final)", r["home"], r["away"], r["winner"]])

                    # === UPDATED: DYNAMICALLY RESOLVE 3RD PLACE & GRAND FINAL MATCHUPS ===
                    # Extract the actual teams involved in the Semifinals to find out who won and lost
                    sf1 = sf_data.get("Match_101", {"home": "TBD", "away": "TBD", "winner": ""})
                    sf2 = sf_data.get("Match_102", {"home": "TBD", "away": "TBD", "winner": ""})

                    # Identify SF 1 Winner & Loser
                    if sf1["winner"] == sf1["home"]:
                        sf1_w, sf1_l = sf1["home"], sf1["away"]
                    else:
                        sf1_w, sf1_l = sf1["away"], sf1["home"]

                    # Identify SF 2 Winner & Loser
                    if sf2["winner"] == sf2["home"]:
                        sf2_w, sf2_l = sf2["home"], sf2["away"]
                    else:
                        sf2_w, sf2_l = sf2["away"], sf2["home"]

                    # Append Match_103 using the actual computed loser names instead of placeholders
                    ko_tree_rows.append(["Match_103 (3rd Place)", sf1_l, sf2_l, str(third_winner)])

                    # Append Tournament Champion Row using the actual finalist team names
                    ko_tree_rows.append(["CHAMPION", sf1_w, sf2_w, str(champion).upper()])

                    t_ko = Table(ko_tree_rows, colWidths=[130, 135, 135, 140])
                    t_ko.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e1b4b')),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                        ('BACKGROUND', (0,-2), (-1,-2), colors.HexColor('#eff6ff')),
                        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#fef08a')),
                        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#854d0e')),
                        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                    ]))
                    story.append(t_ko)
                    
                    doc.build(story)
                    buffer.seek(0)
                    return buffer.getvalue()

                # 4. EXPORT DOWNLOAD ATTACHMENT NATIVELY
                try:
                    pdf_data = generate_master_dossier_pdf(
                        selected_user_name, 
                        scores_dict, 
                        r32_display, 
                        r16_resolved, 
                        qf_resolved, 
                        sf_resolved,
                        third_place_winner,
                        grand_champion
                    )
                    
                    st.success(f"📋 Verification dossier compiled successfully for **{selected_user_name}**!")
                    st.download_button(
                        label=f"📥 Download {selected_user_name}'s Master Print PDF",
                        data=pdf_data,
                        file_name=f"Tournament_Dossier_{selected_user_name.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    with st.expander("👁️ Quick On-Screen Layout Verification", expanded=True):
                        col_view1, col_view2 = st.columns(2)
                        with col_view1:
                            st.write(f"Total Mapped Scores Found: **{len(scores_dict)} / 144 keys**")
                            st.write(f"Generated Wildcard Code: **{combination_lookup_string}**")
                        with col_view2:
                            st.write(f"Predicted Tournament Champion: **{grand_champion}**")
                            st.write(f"Predicted 3rd Place Winner: **{third_place_winner}**")
                            
                except Exception as pdf_err:
                    st.error(f"Error packaging PDF layout design blueprint: {pdf_err}")
            else:
                st.error("No submission profiles found inside your users infrastructure record.")

    # --- SAFE ADMIN OVERRIDE BUTTON ZONE ---
    # Properly indented within the Admin check block to hide it from all public users
    st.markdown("---")
    st.subheader("🔄 Global Leaderboard Lifecycle Control")
    st.caption("Admin Only: Use this to manually purge the global database cache and force all player leaderboards to recalculate fresh.")
    if st.button("♻️ Force Recalculate Standings & Flush Cache", type="primary", use_container_width=True):
        # 1. Clear all Streamlit memory caches
        st.cache_data.clear()
        st.cache_resource.clear()
        
        # 2. Touch/Rerun the app to force a clean, top-to-bottom re-execution
        st.success("All cache flushed! Recalculating Leaderboard...")
        st.rerun()



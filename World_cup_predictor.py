import streamlit as st
import pandas as pd

# --- 1. CONFIGURATION & FULL COLOUR DARK THEME STYLING ---
st.set_page_config(
    page_title="World Cup 2026 Prediction League",
    page_icon="🏆",
    layout="wide"
)

st.markdown("""
    <style>
    /* Background Image setup - Full colour */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.2), rgba(15, 23, 42, 0.4)),
                    url("https://cdn-media.theathletic.com/cdn-cgi/image/width=1000%2cquality=70%2cformat=auto/https://cdn-media.theathletic.com/vwYC1qZfTwfm_3qmyXkIC5Rja_1440x960.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Global Typography - Crisp white & readable */
    html, body, [class*="st-"] p, label, .stMarkdown, .stText, [data-testid="stWidgetLabel"] p {
        color: #f8fafc !important;
        font-weight: 500 !important;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8);
    }
    
    h1, h2, h3, h4 {
        color: #ffffff !important;
        text-transform: uppercase;
        font-weight: 800 !important;
        letter-spacing: 0.5px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9);
    }

    /* Target explicit functional elements for panels instead of raw floating div rows */
    [data-testid="stExpander"], [data-testid="stTabContent"], .stTabs {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
    }

    /* Input Element Styles */
    div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.95) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }
    
    /* Button Layouts */
    div.stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        width: 100% !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    div.stButton > button:hover {
        background-color: #1d4ed8 !important;
    }
    
    /* Lock Banner Indicator */
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
    </style>
""", unsafe_allow_html=True)

# --- 2. GLOBAL TEAMS & FLAGS MAP ---
FLAGS = {
    "Mexico": "🇲🇽 MEXICO", "South Africa": "🇿🇦 SOUTH AFRICA", "Rep. of Korea": "🇰🇷 REP. OF KOREA", "Czech Rep.": "🇨🇿 CZECH REP.",
    "Canada": "🇨🇦 CANADA", "Bosnia/Herzeg.": "🇧🇦 BOSNIA/HERZEG.", "Qatar": "🇶🇦 QATAR", "Switzerland": "🇨🇭 SWITZERLAND",
    "Brazil": "🇧🇷 BRAZIL", "Morocco": "🇲🇦 MOROCCO", "Haiti": "🇭🇹 HAITI", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 SCOTLAND",
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
    return FLAGS.get(name, name.upper())

# --- 3. DATA STRUCTURES (GROUPS & CHRONOLOGICAL FIXTURES) ---
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

# Real-world chronological mapping with absolute FIFA Match Numbers and home/away designations
CHRONO_MATCHES = {
    "Group A": [
        {"id": 1, "home": "Mexico", "away": "South Africa"},
        {"id": 2, "home": "Rep. of Korea", "away": "Czech Rep."},
        {"id": 25, "home": "Czech Rep.", "away": "South Africa"},
        {"id": 28, "home": "Mexico", "away": "Rep. of Korea"},
        {"id": 49, "home": "Czech Rep.", "away": "Mexico"},
        {"id": 50, "home": "South Africa", "away": "Rep. of Korea"}
    ],
    "Group B": [
        {"id": 3, "home": "Canada", "away": "Bosnia/Herzeg."},
        {"id": 5, "home": "Qatar", "away": "Switzerland"},
        {"id": 26, "home": "Switzerland", "away": "Bosnia/Herzeg."},
        {"id": 27, "home": "Canada", "away": "Qatar"},
        {"id": 51, "home": "Switzerland", "away": "Canada"},
        {"id": 52, "home": "Bosnia/Herzeg.", "away": "Qatar"}
    ],
    "Group C": [
        {"id": 6, "home": "Brazil", "away": "Morocco"},
        {"id": 7, "home": "Haiti", "away": "Scotland"},
        {"id": 30, "home": "Scotland", "away": "Morocco"},
        {"id": 31, "home": "Brazil", "away": "Haiti"},
        {"id": 53, "home": "Scotland", "away": "Brazil"},
        {"id": 54, "home": "Morocco", "away": "Haiti"}
    ],
    "Group D": [
        {"id": 4, "home": "USA", "away": "Paraguay"},
        {"id": 8, "home": "Australia", "away": "Turkey"},
        {"id": 29, "home": "USA", "away": "Australia"},
        {"id": 32, "home": "Turkey", "away": "Paraguay"},
        {"id": 55, "home": "Turkey", "away": "USA"},
        {"id": 56, "home": "Paraguay", "away": "Australia"}
    ],
    "Group E": [
        {"id": 9, "home": "Germany", "away": "Curaçao"},
        {"id": 11, "home": "Ivory Coast", "away": "Ecuador"},
        {"id": 34, "home": "Germany", "away": "Ivory Coast"},
        {"id": 35, "home": "Ecuador", "away": "Curaçao"},
        {"id": 57, "home": "Ecuador", "away": "Germany"},
        {"id": 58, "home": "Curaçao", "away": "Ivory Coast"}
    ],
    "Group F": [
        {"id": 10, "home": "Netherlands", "away": "Japan"},
        {"id": 12, "home": "Sweden", "away": "Tunisia"},
        {"id": 33, "home": "Netherlands", "away": "Sweden"},
        {"id": 36, "home": "Tunisia", "away": "Japan"},
        {"id": 59, "home": "Tunisia", "away": "Netherlands"},
        {"id": 60, "home": "Japan", "away": "Sweden"}
    ],
    "Group G": [
        {"id": 14, "home": "Belgium", "away": "Egypt"},
        {"id": 16, "home": "IR Iran", "away": "New Zealand"},
        {"id": 38, "home": "Belgium", "away": "IR Iran"},
        {"id": 40, "home": "New Zealand", "away": "Egypt"},
        {"id": 61, "home": "New Zealand", "away": "Belgium"},
        {"id": 62, "home": "Egypt", "away": "IR Iran"}
    ],
    "Group H": [
        {"id": 13, "home": "Spain", "away": "Cape Verde"},
        {"id": 15, "home": "Saudi Arabia", "away": "Uruguay"},
        {"id": 37, "home": "Spain", "away": "Saudi Arabia"},
        {"id": 39, "home": "Uruguay", "away": "Cape Verde"},
        {"id": 63, "home": "Uruguay", "away": "Spain"},
        {"id": 64, "home": "Cape Verde", "away": "Saudi Arabia"}
    ],
    "Group I": [
        {"id": 17, "home": "France", "away": "Senegal"},
        {"id": 18, "home": "Iraq", "away": "Norway"},
        {"id": 41, "home": "France", "away": "Iraq"},
        {"id": 42, "home": "Norway", "away": "Senegal"},
        {"id": 65, "home": "Norway", "away": "France"},
        {"id": 66, "home": "Senegal", "away": "Iraq"}
    ],
    "Group J": [
        {"id": 19, "home": "Argentina", "away": "Algeria"},
        {"id": 20, "home": "Austria", "away": "Jordan"},
        {"id": 43, "home": "Argentina", "away": "Austria"},
        {"id": 44, "home": "Jordan", "away": "Algeria"},
        {"id": 67, "home": "Jordan", "away": "Argentina"},
        {"id": 68, "home": "Algeria", "away": "Austria"}
    ],
    "Group K": [
        {"id": 21, "home": "Portugal", "away": "DR Congo"},
        {"id": 24, "home": "Uzbekistan", "away": "Colombia"},
        {"id": 45, "home": "Portugal", "away": "Uzbekistan"},
        {"id": 46, "home": "Colombia", "away": "DR Congo"},
        {"id": 69, "home": "Colombia", "away": "Portugal"},
        {"id": 70, "home": "DR Congo", "away": "Uzbekistan"}
    ],
    "Group L": [
        {"id": 22, "home": "England", "away": "Croatia"},
        {"id": 23, "home": "Ghana", "away": "Panama"},
        {"id": 47, "home": "England", "away": "Ghana"},
        {"id": 48, "home": "Panama", "away": "Croatia"},
        {"id": 71, "home": "Panama", "away": "England"},
        {"id": 72, "home": "Croatia", "away": "Ghana"}
    ]
}

# --- 4. SESSION INITIALIZATION ---
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "admin123", "is_admin": True},
        "Player_1": {"password": "password123", "is_admin": False},
        "Player_2": {"password": "password123", "is_admin": False},
    }
if "predictions" not in st.session_state:
    st.session_state.predictions = {}
if "locked_groups" not in st.session_state:
    st.session_state.locked_groups = {} 
if "actual_results" not in st.session_state:
    st.session_state.actual_results = {"group": {}, "ko_winners": {}, "third_place": "", "finalists": []}
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- 5. UNIFIED INTEGRATED MATCH CARD RENDERER ---
def render_match_card(home, away, label, key_prefix, disabled=False, score_mode=False, scores_dict=None):
    disp1 = fmt_team(home)
    disp2 = fmt_team(away)
    
    st.markdown(f"""
        <div style="border: 1px solid rgba(255,255,255,0.2); border-radius: 10px; background: rgba(15, 23, 42, 0.8); padding: 14px; margin-top: 10px; margin-bottom: 2px;">
            <div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-bottom: 8px; font-weight: bold; text-transform: uppercase;">{label}</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="text-align: left; width: 42%; font-weight: 700; color: white; font-size: 0.95rem;">{disp1}</div>
                <div style="color: #94a3b8; font-weight: 800; font-size: 0.9rem; width: 16%; text-align: center;">VS</div>
                <div style="text-align: right; width: 42%; font-weight: 700; color: white; font-size: 0.95rem;">{disp2}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if score_mode and scores_dict is not None:
        kh, ka = f"{key_prefix}_h", f"{key_prefix}_a"
        c1, c2 = st.columns(2)
        with c1:
            scores_dict[kh] = st.number_input("Home Score", min_value=0, max_value=15, value=scores_dict.get(kh, 0), step=1, key=f"inp_{kh}", disabled=disabled)
        with c2:
            scores_dict[ka] = st.number_input("Away Score", min_value=0, max_value=15, value=scores_dict.get(ka, 0), step=1, key=f"inp_{ka}", disabled=disabled)
        return scores_dict
    else:
        options = ["Select Winner", home, away]
        curr = scores_dict.get(key_prefix, home) if scores_dict else home
        idx_val = options.index(curr) if curr in options else 0
        return st.selectbox("Winner Selection", options, index=idx_val, format_func=fmt_team, key=f"sel_{key_prefix}", label_visibility="collapsed", disabled=disabled)

# --- 6. COMPUTATION ENGINES ---
def run_standings_engine(scores_dict):
    all_group_results = {}
    third_place_pool = []
    for g_name, teams in GROUPS.items():
        standings = {t: {"Group": g_name, "Pts": 0, "GD": 0, "GF": 0} for t in teams}
        for match in CHRONO_MATCHES[g_name]:
            m_id = match["id"]
            home = match["home"]
            away = match["away"]
            kh, ka = f"Match_{m_id}_h", f"Match_{m_id}_a"
            h_score = scores_dict.get(kh, 0)
            a_score = scores_dict.get(ka, 0)
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
        df_g = df_g.sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
        all_group_results[g_name] = df_g
        if len(df_g) >= 3: third_place_pool.append(df_g.iloc[2].to_dict())
    wildcard_df = pd.DataFrame(third_place_pool)
    if not wildcard_df.empty:
        wildcard_df = wildcard_df.sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
        adv_wildcards = list(wildcard_df.head(8)["Team"])
    else: adv_wildcards = []
    while len(adv_wildcards) < 8: adv_wildcards.append(f"Wildcard Slot {len(adv_wildcards)+1}")
    return all_group_results, adv_wildcards

def calculate_user_points(username):
    user_preds = st.session_state.predictions.get(username, {})
    actual = st.session_state.actual_results
    points = 0
    for g_name, matches in CHRONO_MATCHES.items():
        for match in matches:
            m_id = match["id"]
            kh, ka = f"Match_{m_id}_h", f"Match_{m_id}_a"
            p_h, p_a = user_preds.get(kh, None), user_preds.get(ka, None)
            a_h, a_a = actual["group"].get(kh, None), actual["group"].get(ka, None)
            if p_h is not None and p_a is not None and a_h is not None and a_a is not None:
                if p_h == a_h and p_a == a_a: points += 3  
                elif (p_h > p_a and a_h > a_a) or (p_a > p_h and a_a > a_h) or (p_h == p_a and a_h == a_a): points += 1  
    for m in [f"Match {i}" for i in range(73, 89)]:
        if user_preds.get(m) == actual["ko_winners"].get(m): points += 3
    for m in [f"Match {i}" for i in range(89, 97)]:
        if user_preds.get(m) == actual["ko_winners"].get(m): points += 5
    for m in [f"Match {i}" for i in range(97, 101)]:
        if user_preds.get(m) == actual["ko_winners"].get(m): points += 10
    for m in ["Match 101", "Match 102"]:
        if user_preds.get(m) == actual["ko_winners"].get(m): points += 15
    if user_preds.get("Match 103") == actual.get("third_place"): points += 15
    for team in [user_preds.get("Match 101"), user_preds.get("Match 102")]:
        if team in actual["finalists"]: points += 20
    if user_preds.get("Match 104") == actual["ko_winners"].get("Match 104"): points += 25
    return points

# --- 7. SIGN IN GATEWAY ---
if st.session_state.current_user is None:
    with st.container():
        st.title("🔐 Tournament Sign-In")
        t1, t2 = st.tabs(["Login", "Create Account"])
        with t1:
            lin_user = st.text_input("Username")
            lin_pass = st.text_input("Password", type="password")
            if st.button("Log In", use_container_width=True):
                if lin_user in st.session_state.users and st.session_state.users[lin_user]["password"] == lin_pass:
                    st.session_state.current_user = lin_user
                    st.rerun()
                else: st.error("Invalid credentials.")
        with t2:
            reg_user = st.text_input("Choose Username")
            reg_pass = st.text_input("Choose Password", type="password")
            if st.button("Register Account", use_container_width=True):
                if reg_user.strip() == "" or reg_pass.strip() == "": st.error("Fields cannot be empty.")
                elif reg_user in st.session_state.users: st.error("Username already exists.")
                else:
                    st.session_state.users[reg_user] = {"password": reg_pass, "is_admin": False}
                    st.success("Registered! Log in on the left tab.")
    st.stop()

# --- 8. NAVIGATION SETUP ---
c_user = st.session_state.current_user
if c_user not in st.session_state.locked_groups: st.session_state.locked_groups[c_user] = []

col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.markdown(f"👥 Account User: **{c_user}** " + ("<span style='color:#3b82f6;'>(🛠️ Admin)</span>" if st.session_state.users[c_user]["is_admin"] else ""), unsafe_allow_html=True)
with col_nav2:
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.current_user = None
        st.rerun()

main_tabs = ["🏆 Leaderboard", "📝 Submit Predictions"]
if st.session_state.users[c_user]["is_admin"]: main_tabs.append("🛠️ Admin Dashboard")
app_tab = st.sidebar.radio("Main Menu Navigation", main_tabs)

if c_user not in st.session_state.predictions: st.session_state.predictions[c_user] = {}
user_preds = st.session_state.predictions[c_user]

# --- 9. LEADERBOARD WORKSPACE ---
if app_tab == "🏆 Leaderboard":
    with st.container():
        st.header("🏆 Prediction League Leaderboard")
        leaderboard_data = [{"Competitor Name": u, "Current Total Points": calculate_user_points(u)} for u, info in st.session_state.users.items() if not info["is_admin"]]
        df_leaderboard = pd.DataFrame(leaderboard_data)
        if not df_leaderboard.empty:
            df_leaderboard = df_leaderboard.sort_values(by="Current Total Points", ascending=False).reset_index(drop=True)
            df_leaderboard.index += 1
            st.dataframe(df_leaderboard, use_container_width=True)
        else: st.info("No competitor records found.")

# --- 10. USER PREDICTIONS DESK ---
elif app_tab == "📝 Submit Predictions":
    st.header("📝 Match Predictions")
    pred_sub_tabs = st.tabs(["📊 Group Matches Workspace", "🌳 Knockout Brackets"])
    
    with pred_sub_tabs[0]:
        selected_group = st.selectbox("Choose Group Stage Pool", list(GROUPS.keys()))
        
        col_input, col_table = st.columns([1, 1])
        with col_input:
            is_group_locked = selected_group in st.session_state.locked_groups[c_user]
            if is_group_locked:
                st.markdown(f"<div class='lock-badge-banner'>🔒 {selected_group} Locked In</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#34d399; margin-bottom:15px; font-weight:bold; font-size:1.1rem; text-align:center;'>🔓 Unlocked - Edits Allowed</div>", unsafe_allow_html=True)
                
            for match in CHRONO_MATCHES[selected_group]:
                user_preds = render_match_card(
                    home=match["home"], 
                    away=match["away"], 
                    label=f"Match #{match['id']}", 
                    key_prefix=f"Match_{match['id']}", 
                    disabled=is_group_locked,
                    score_mode=True,
                    scores_dict=user_preds
                )
            
            if not is_group_locked:
                if st.button(f"🔒 Lock In {selected_group} Predictions", use_container_width=True):
                    st.session_state.locked_groups[c_user].append(selected_group)
                    st.session_state.predictions[c_user] = user_preds
                    st.success(f"{selected_group} Locked Successfully!")
                    st.rerun()
                
        with col_table:
            st.subheader("Simulated Group Table")
            u_results, _ = run_standings_engine(user_preds)
            df_display = u_results[selected_group][["Team", "Pts", "GD", "GF"]].copy()
            df_display["Team"] = df_display["Team"].apply(fmt_team)
            st.dataframe(df_display, use_container_width=True, hide_index=True)

    with pred_sub_tabs[1]:
        u_results, u_wildcards = run_standings_engine(user_preds)
        def get_confirmed_1st(g): return u_results[g].iloc[0]["Team"] if g in u_results and not u_results[g].empty else f"1st {g}"
        def get_confirmed_2nd(g): return u_results[g].iloc[1]["Team"] if g in u_results and not u_results[g].empty else f"2nd {g}"

        o_r32 = {
            "Match 73": (get_confirmed_1st("Group A"), u_wildcards[4]), "Match 74": (get_confirmed_1st("Group E"), u_wildcards[0]),
            "Match 75": (get_confirmed_1st("Group F"), get_confirmed_2nd("Group C")), "Match 76": (get_confirmed_1st("Group C"), get_confirmed_2nd("Group F")),
            "Match 77": (get_confirmed_1st("Group I"), u_wildcards[1]), "Match 78": (get_confirmed_2nd("Group E"), get_confirmed_2nd("Group I")),
            "Match 79": (get_confirmed_1st("Group B"), u_wildcards[6]), "Match 80": (get_confirmed_1st("Group L"), u_wildcards[5]),
            "Match 81": (get_confirmed_1st("Group D"), u_wildcards[2]), "Match 82": (get_confirmed_1st("Group G"), u_wildcards[3]),
            "Match 83": (get_confirmed_2nd("Group K"), get_confirmed_2nd("Group L")), "Match 84": (get_confirmed_1st("Group H"), get_confirmed_2nd("Group J")),
            "Match 85": (get_confirmed_2nd("Group A"), get_confirmed_2nd("Group B")), "Match 86": (get_confirmed_1st("Group J"), get_confirmed_2nd("Group H")),
            "Match 87": (get_confirmed_1st("Group K"), u_wildcards[7]), "Match 88": (get_confirmed_2nd("Group D"), get_confirmed_2nd("Group G"))
        }
        
        ko_tabs = st.tabs(["Round of 32", "Round of 16", "Quarter-Finals", "Finals"])
        
        with ko_tabs[0]:
            for m_id, (h, a) in o_r32.items():
                user_preds[m_id] = render_match_card(h, a, m_id, m_id, disabled=False, score_mode=False, scores_dict=user_preds)
                        
        with ko_tabs[1]:
            o_r16 = {
                "Match 89": (user_preds.get("Match 74", "W74"), user_preds.get("Match 77", "W77")),
                "Match 90": (user_preds.get("Match 73", "W73"), user_preds.get("Match 75", "W75")),
                "Match 93": (user_preds.get("Match 83", "W83"), user_preds.get("Match 84", "W84")),
                "Match 94": (user_preds.get("Match 81", "W81"), user_preds.get("Match 82", "W82")),
                "Match 91": (user_preds.get("Match 76", "W76"), user_preds.get("Match 78", "W78")),
                "Match 92": (user_preds.get("Match 79", "W79"), user_preds.get("Match 80", "W80")),
                "Match 95": (user_preds.get("Match 86", "W86"), user_preds.get("Match 88", "W88")),
                "Match 96": (user_preds.get("Match 85", "W85"), user_preds.get("Match 87", "W87"))
            }
            for m_id, (h, a) in o_r16.items():
                user_preds[m_id] = render_match_card(h, a, m_id, m_id, disabled=False, score_mode=False, scores_dict=user_preds)
                        
        with ko_tabs[2]:
            o_qf = {
                "Match 97": (user_preds.get("Match 89", "W89"), user_preds.get("Match 90", "W90")),
                "Match 98": (user_preds.get("Match 93", "W93"), user_preds.get("Match 94", "W94")),
                "Match 99": (user_preds.get("Match 91", "W91"), user_preds.get("Match 92", "W92")),
                "Match 100": (user_preds.get("Match 95", "W95"), user_preds.get("Match 100", "W100"))
            }
            for m_id, (h, a) in o_qf.items():
                user_preds[m_id] = render_match_card(h, a, m_id, m_id, disabled=False, score_mode=False, scores_dict=user_preds)
                    
        with ko_tabs[3]:
            sf1_h, sf1_a = user_preds.get("Match 97", "W97"), user_preds.get("Match 98", "W98")
            sf2_h, sf2_a = user_preds.get("Match 99", "W99"), user_preds.get("Match 100", "W100")
            
            st.markdown("### 🌿 Championship Finals Panel")
            
            sf1_opts = [sf1_h, sf1_a]
            user_preds["Match 101"] = st.selectbox("Semi Final 1 Winner", sf1_opts, index=sf1_opts.index(user_preds.get("Match 101", sf1_h)) if user_preds.get("Match 101", sf1_h) in sf1_opts else 0, format_func=fmt_team)
            
            sf2_opts = [sf2_h, sf2_a]
            user_preds["Match 102"] = st.selectbox("Semi Final 2 Winner", sf2_opts, index=sf2_opts.index(user_preds.get("Match 102", sf2_h)) if user_preds.get("Match 102", sf2_h) in sf2_opts else 0, format_func=fmt_team)
            
            sf1_l = sf1_a if user_preds["Match 101"] == sf1_h else sf1_h
            sf2_l = sf2_a if user_preds["Match 102"] == sf2_h else sf2_h
            
            st.markdown("<hr style='border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            p3_opts = [sf1_l, sf2_l]
            user_preds["Match 103"] = st.selectbox("🥉 3rd Place Winner Selection", p3_opts, index=p3_opts.index(user_preds.get("Match 103", sf1_l)) if user_preds.get("Match 103", sf1_l) in p3_opts else 0, format_func=fmt_team)
            
            st.markdown("<hr style='border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            f_opts = [user_preds["Match 101"], user_preds["Match 102"]]
            user_preds["Match 104"] = st.selectbox("🥇 Grand Champion Prediction", f_opts, index=f_opts.index(user_preds.get("Match 104", f_opts[0])) if user_preds.get("Match 104", f_opts[0]) in f_opts else 0, format_func=fmt_team)
                
        if st.button("💾 Archive Complete Bracket Matrix", use_container_width=True):
            st.session_state.predictions[c_user] = user_preds
            st.success("Bracket pathways updated safely!")

# --- 11. ADMINISTRATIVE CONTROL PANEL ---
elif app_tab == "🛠️ Admin Dashboard":
    st.header("🛠️ Admin Scoresheet Panel")
    admin_tabs = st.tabs(["Group Stage Results", "Knockout Progress Matches"])
    actual = st.session_state.actual_results
    
    with admin_tabs[0]:
        selected_adm_group = st.selectbox("Verify Target Group Pool", list(GROUPS.keys()))
        
        for match in CHRONO_MATCHES[selected_adm_group]:
            actual["group"] = render_match_card(
                home=match["home"],
                away=match["away"],
                label=f"Match #{match['id']} Actual Result",
                key_prefix=f"Match_{match['id']}",
                disabled=False,
                score_mode=True,
                scores_dict=actual["group"]
            )
            if st.button("📢 Publish Match Result", key=f"btn_pub_Match_{match['id']}", use_container_width=True):
                st.session_state.actual_results = actual
                st.success("Standings updated instantly!")
            
    with admin_tabs[1]:
        adm_group_res, adm_wildcards = run_standings_engine(actual["group"])
        def get_1st(g): return adm_group_res[g].iloc[0]["Team"] if not adm_group_res[g].empty else f"1st {g}"
        def get_2nd(g): return adm_group_res[g].iloc[1]["Team"] if not adm_group_res[g].empty else f"2nd {g}"
        
        adm_r32_pairings = {
            "Match 73": (get_1st("Group A"), adm_wildcards[4]), "Match 74": (get_1st("Group E"), adm_wildcards[0]),
            "Match 75": (get_1st("Group F"), get_2nd("Group C")), "Match 76": (get_1st("Group C"), get_2nd("Group F")),
            "Match 77": (get_1st("Group I"), adm_wildcards[1]), "Match 78": (get_2nd("Group E"), get_2nd("Group I")),
            "Match 79": (get_1st("Group B"), adm_wildcards[6]), "Match 80": (get_1st("Group L"), adm_wildcards[5]),
            "Match 81": (get_1st("Group D"), adm_wildcards[2]), "Match 82": (get_1st("Group G"), adm_wildcards[3]),
            "Match 83": (get_2nd("Group K"), get_2nd("Group L")), "Match 84": (get_1st("Group H"), get_2nd("Group J")),
            "Match 85": (get_2nd("Group A"), get_2nd("Group B")), "Match 86": (get_1st("Group J"), get_2nd("Group H")),
            "Match 87": (get_1st("Group K"), adm_wildcards[7]), "Match 88": (get_2nd("Group D"), get_2nd("Group G"))
        }
        
        for m_id, (h, a) in adm_r32_pairings.items():
            actual["ko_winners"][m_id] = render_match_card(h, a, f"Winner: {m_id}", m_id, disabled=False, score_mode=False, scores_dict=actual["ko_winners"])
            if st.button("📢 Save Winner", key=f"btn_ko_{m_id}", use_container_width=True):
                st.session_state.actual_results = actual
                st.success(f"{m_id} locked in results tree!")

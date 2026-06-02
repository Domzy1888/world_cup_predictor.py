import streamlit as st
import pandas as pd

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="World Cup 2026 Prediction League",
    page_icon="🏆",
    layout="wide"
)

# Advanced Glassmorphism and Background Image CSS Styling
st.markdown("""
    <style>
    /* Full screen background image styling - Restored to full original vibrant color */
    .stApp {
        background: url("https://cdn-media.theathletic.com/cdn-cgi/image/width=1000%2cquality=70%2cformat=auto/https://cdn-media.theathletic.com/vwYC1qZfTwfm_3qmyXkIC5Rja_1440x960.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Force crisp white typography ONLY in the main app block for maximum readability */
    .stMain, .stMain p, .stMain div, .stMain span, .stMain label, .stMain h1, .stMain h2, .stMain h3, .stMain h4 {
        color: #f1f5f9 !important;
    }
    
    /* Force the sidebar text to remain dark charcoal so it is readable on mobile and desktop layouts */
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #1e293b !important;
        font-weight: 500;
    }
    
    /* Keep selectbox options readable by preventing them from bleeding into the background */
    div[data-baseweb="select"] * {
        color: #0f172a !important;
    }
    
    /* Keep standard dataframe text elements visible and dark inside tables */
    div[data-testid="stDataFrame"] * {
        color: #f1f5f9 !important;
    }
    
    /* Floating Glassmorphic Unified Match Card Container Box */
    .unified-match-card {
        background: rgba(15, 23, 42, 0.82);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        border: 2px solid rgba(255, 255, 255, 0.15);
        padding: 24px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.5);
    }
    
    /* Custom Stylized Center-Aligned Team Title Label */
    .team-header-box {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        color: #ffffff !important;
        letter-spacing: 0.06em;
        text-align: center;
        margin: 12px 0;
        width: 100%;
    }
    
    /* Versus Styling Text Divider */
    .versus-text-middle {
        font-size: 0.95rem;
        text-transform: uppercase;
        color: #cbd5e1 !important;
        font-weight: 900;
        letter-spacing: 0.3em;
        margin: 18px 0;
        text-align: center;
        width: 100%;
    }
    
    /* Input Label Overrides to center them */
    .stMain label div p {
        text-align: center !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        color: #e2e8f0 !important;
    }
    
    /* Custom Badge for Locked States */
    .lock-badge {
        background-color: rgba(239, 68, 68, 0.35);
        color: #fca5a5 !important;
        border: 1px solid rgba(239, 68, 68, 0.5);
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- GLOBAL TEAMS & FLAGS MAP ---
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

# --- CORE DATA STRUCTURE ---
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

MATCH_IDS = {}
for g_name, teams in GROUPS.items():
    MATCH_IDS[g_name] = [
        (teams[0], teams[1]), (teams[2], teams[3]),
        (teams[0], teams[2]), (teams[1], teams[3]),
        (teams[0], teams[3]), (teams[1], teams[2])
    ]

# --- SESSION STATE INITIALIZATION ---
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
    st.session_state.actual_results = {
        "group": {},       
        "ko_winners": {},  
        "third_place": "", 
        "finalists": []    
    }

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- ENGINE LOGIC ---
def run_standings_engine(scores_dict):
    all_group_results = {}
    third_place_pool = []
    
    for g_name, teams in GROUPS.items():
        standings = {t: {"Group": g_name, "Pts": 0, "GD": 0, "GF": 0} for t in teams}
        
        for idx, (home, away) in enumerate(MATCH_IDS[g_name]):
            kh = f"{g_name}_m{idx}_h"
            ka = f"{g_name}_m{idx}_a"
            
            h_score = scores_dict.get(kh, 0)
            a_score = scores_dict.get(ka, 0)
            
            standings[home]["GF"] += h_score
            standings[away]["GF"] += a_score
            standings[home]["GD"] += (h_score - a_score)
            standings[away]["GD"] += (a_score - h_score)
            
            if h_score > a_score:
                standings[home]["Pts"] += 3
            elif a_score > h_score:
                standings[away]["Pts"] += 3
            else:
                standings[home]["Pts"] += 1
                standings[away]["Pts"] += 1
                    
        df_g = pd.DataFrame.from_dict(standings, orient='index').reset_index().rename(columns={'index': 'Team'})
        df_g = df_g.sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
        all_group_results[g_name] = df_g
        if len(df_g) >= 3:
            third_place_pool.append(df_g.iloc[2].to_dict())
            
    wildcard_df = pd.DataFrame(third_place_pool)
    if not wildcard_df.empty:
        wildcard_df = wildcard_df.sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
        adv_wildcards = list(wildcard_df.head(8)["Team"])
    else:
        adv_wildcards = []
    while len(adv_wildcards) < 8:
        adv_wildcards.append(f"Wildcard Slot {len(adv_wildcards)+1}")
        
    return all_group_results, adv_wildcards

def calculate_user_points(username):
    user_preds = st.session_state.predictions.get(username, {})
    actual = st.session_state.actual_results
    points = 0
    
    for g_name, matches in MATCH_IDS.items():
        for idx, (home, away) in enumerate(matches):
            kh = f"{g_name}_m{idx}_h"
            ka = f"{g_name}_m{idx}_a"
            
            p_h = user_preds.get(kh, None)
            p_a = user_preds.get(ka, None)
            a_h = actual["group"].get(kh, None)
            a_a = actual["group"].get(ka, None)
            
            if p_h is not None and p_a is not None and a_h is not None and a_a is not None:
                if p_h == a_h and p_a == a_a:
                    points += 3  
                elif (p_h > p_a and a_h > a_a) or (p_a > p_h and a_a > a_h) or (p_h == p_a and a_h == a_a):
                    points += 1  
                    
    for m in [f"Match {i}" for i in range(73, 89)]:
        if user_preds.get(m) and user_preds.get(m) == actual["ko_winners"].get(m): points += 3
    for m in [f"Match {i}" for i in range(89, 97)]:
        if user_preds.get(m) and user_preds.get(m) == actual["ko_winners"].get(m): points += 5
    for m in [f"Match {i}" for i in range(97, 101)]:
        if user_preds.get(m) and user_preds.get(m) == actual["ko_winners"].get(m): points += 10
    for m in ["Match 101", "Match 102"]:
        if user_preds.get(m) and user_preds.get(m) == actual["ko_winners"].get(m): points += 15
    if user_preds.get("Match 103") and user_preds.get("Match 103") == actual.get("third_place"): points += 15
        
    user_finalists = [user_preds.get("Match 101"), user_preds.get("Match 102")]
    for team in user_finalists:
        if team and team in actual["finalists"]: points += 20
    if user_preds.get("Match 104") and user_preds.get("Match 104") == actual["ko_winners"].get("Match 104"): points += 25
        
    return points

# --- LOGIN SCREEN LAYER ---
if st.session_state.current_user is None:
    st.markdown("<div class='unified-match-card' style='max-width: 500px; margin: 100px auto;'>", unsafe_allow_html=True)
    st.title("🔐 Tournament Sign-In")
    auth_tab1, auth_tab2 = st.tabs(["Login", "Create Account"])
    
    with auth_tab1:
        lin_user = st.text_input("Username", key="lin_user")
        lin_pass = st.text_input("Password", type="password", key="lin_pass")
        if st.button("Log In", use_container_width=True):
            if lin_user in st.session_state.users and st.session_state.users[lin_user]["password"] == lin_pass:
                st.session_state.current_user = lin_user
                st.rerun()
            else: st.error("Invalid credentials.")
                
    with auth_tab2:
        reg_user = st.text_input("Choose Username", key="reg_user")
        reg_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        if st.button("Register Account", use_container_width=True):
            if reg_user.strip() == "" or reg_pass.strip() == "": st.error("Fields cannot be empty.")
            elif reg_user in st.session_state.users: st.error("Username already exists.")
            else:
                st.session_state.users[reg_user] = {"password": reg_pass, "is_admin": False}
                st.success("Registration successful! Proceed to Login tab.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- INTERFACE MENU LAYOUT ---
c_user = st.session_state.current_user
if c_user not in st.session_state.locked_groups:
    st.session_state.locked_groups[c_user] = []

col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.markdown(f"👥 Active Account: **{c_user}** " + ("<span style='color:#60a5fa;'>(🛠️ Admin)</span>" if st.session_state.users[c_user]["is_admin"] else ""), unsafe_allow_html=True)
with col_nav2:
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.current_user = None
        st.rerun()

main_tabs = ["🏆 Leaderboard", "📝 Submit Predictions"]
if st.session_state.users[c_user]["is_admin"]:
    main_tabs.append("🛠️ Admin Dashboard")
    
app_tab = st.sidebar.radio("Main Menu Navigation", main_tabs)

if c_user not in st.session_state.predictions:
    st.session_state.predictions[c_user] = {}
user_preds = st.session_state.predictions[c_user]

# --- LEADERBOARD ---
if app_tab == "🏆 Leaderboard":
    st.header("🏆 Active Standings Leaderboard")
    leaderboard_data = []
    
    for user, info in st.session_state.users.items():
        if not info["is_admin"]:
            score = calculate_user_points(user)
            leaderboard_data.append({"Competitor Name": user, "Current Total Points": score})
            
    df_leaderboard = pd.DataFrame(leaderboard_data)
    if not df_leaderboard.empty:
        df_leaderboard = df_leaderboard.sort_values(by="Current Total Points", ascending=False).reset_index(drop=True)
        df_leaderboard.index += 1
        st.dataframe(df_leaderboard, use_container_width=True)
    else: st.info("No league prediction metrics found yet.")

# --- COMPETITOR SHEETS ---
elif app_tab == "📝 Submit Predictions":
    st.header("📝 Player Prediction Desk")
    pred_sub_tabs = st.tabs(["📊 Group Matches Workspace", "🌳 Knockout Brackets"])
    
    with pred_sub_tabs[0]:
        selected_group = st.selectbox("Choose Group Stage Pool", list(GROUPS.keys()))
        is_group_locked = selected_group in st.session_state.locked_groups[c_user]
        
        col_input, col_table = st.columns([1, 1])
        
        with col_input:
            if is_group_locked:
                st.markdown("<div class='lock-badge'>🔒 This Group is Locked In</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#34d399; margin-bottom:15px; font-weight:bold; font-size:1.1rem;'>🔓 Unlocked - Edits Allowed</div>", unsafe_allow_html=True)
                
            for idx, (home, away) in enumerate(MATCH_IDS[selected_group]):
                kh = f"{selected_group}_m{idx}_h"
                ka = f"{selected_group}_m{idx}_a"
                
                # Structural Fix: Opening container wrapper around all nested entry blocks
                st.markdown("<div class='unified-match-card'>", unsafe_allow_html=True)
                
                st.markdown(f"<div class='team-header-box'>{fmt_team(home)}</div>", unsafe_allow_html=True)
                user_preds[kh] = st.number_input("Home Team Score", min_value=0, max_value=15, 
                                                  value=user_preds.get(kh, 0), step=1, 
                                                  key=f"p_{kh}", disabled=is_group_locked)
                
                st.markdown("<div class='versus-text-middle'>— VERSUS —</div>", unsafe_allow_html=True)
                
                user_preds[ka] = st.number_input("Away Team Score", min_value=0, max_value=15, 
                                                  value=user_preds.get(ka, 0), step=1, 
                                                  key=f"p_{ka}", disabled=is_group_locked)
                st.markdown(f"<div class='team-header-box'>{fmt_team(away)}</div>", unsafe_allow_html=True)
                
                # Closing container wrapper around all nested elements
                st.markdown("</div>", unsafe_allow_html=True)
            
            if not is_group_locked:
                if st.button(f"🔒 Lock In {selected_group} Predictions", use_container_width=True):
                    st.session_state.locked_groups[c_user].append(selected_group)
                    st.session_state.predictions[c_user] = user_preds
                    st.success(f"{selected_group} selections have been locked permanently!")
                    st.rerun()
                
        with col_table:
            st.markdown("<div class='unified-match-card'>", unsafe_allow_html=True)
            st.subheader("Simulated Group Table")
            u_results, _ = run_standings_engine(user_preds)
            
            df_display = u_results[selected_group][["Team", "Pts", "GD", "GF"]].copy()
            df_display["Team"] = df_display["Team"].apply(fmt_team)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with pred_sub_tabs[1]:
        u_results, u_wildcards = run_standings_engine(user_preds)
        def get_confirmed_1st(g): return u_results[g].iloc[0]["Team"] if g in u_results and not u_results[g].empty else f"1st {g}"
        def get_confirmed_2nd(g): return u_results[g].iloc[1]["Team"] if g in u_results and not u_results[g].empty else f"2nd {g}"
        
        def get_1st(g): return get_confirmed_1st(g)
        def get_2nd(g): return get_confirmed_2nd(g)

        o_r32 = {
            "Match 73": (get_confirmed_1st("Group A"), u_wildcards[4]), "Match 74": (get_confirmed_1st("Group E"), u_wildcards[0]),
            "Match 75": (get_confirmed_1st("Group F"), get_confirmed_2nd("Group C")), "Match 76": (get_confirmed_1st("Group C"), get_confirmed_2nd("Group F")),
            "Match 77": (get_confirmed_1st("Group I"), u_wildcards[1]), "Match 78": (get_2nd("Group E"), get_2nd("Group I")),
            "Match 79": (get_1st("Group B"), u_wildcards[6]), "Match 80": (get_confirmed_1st("Group L"), u_wildcards[5]),
            "Match 81": (get_confirmed_1st("Group D"), u_wildcards[2]), "Match 82": (get_confirmed_1st("Group G"), u_wildcards[3]),
            "Match 83": (get_confirmed_2nd("Group K"), get_confirmed_2nd("Group L")), "Match 84": (get_confirmed_1st("Group H"), get_confirmed_2nd("Group J")),
            "Match 85": (get_confirmed_2nd("Group A"), get_confirmed_2nd("Group B")), "Match 86": (get_confirmed_1st("Group J"), get_confirmed_2nd("Group H")),
            "Match 87": (get_confirmed_1st("Group K"), u_wildcards[7]), "Match 88": (get_2nd("Group D"), get_2nd("Group G"))
        }
        
        ko_tabs = st.tabs(["Round of 32", "Round of 16", "Quarter-Finals", "Finals"])
        
        with ko_tabs[0]:
            for idx, (m_id, (h, a)) in enumerate(o_r32.items()):
                st.markdown(f"<div class='unified-match-card'><b>⚽ {m_id}</b><br><small style='opacity:0.8;'>Fixture: {fmt_team(h)} vs {fmt_team(a)}</small>", unsafe_allow_html=True)
                options = [h, a]
                current_pick = user_preds.get(m_id, h)
                default_idx = options.index(current_pick) if current_pick in options else 0
                user_preds[m_id] = st.selectbox("Progresses:", options, index=default_idx, format_func=fmt_team, key=f"up_sel_{m_id}")
                st.markdown("</div>", unsafe_allow_html=True)
                    
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
            for idx, (m_id, (h, a)) in enumerate(o_r16.items()):
                st.markdown(f"<div class='unified-match-card'><b>📋 {m_id}</b><br><small style='opacity:0.8;'>Fixture: {fmt_team(h)} vs {fmt_team(a)}</small>", unsafe_allow_html=True)
                options = [h, a]
                current_pick = user_preds.get(m_id, h)
                default_idx = options.index(current_pick) if current_pick in options else 0
                user_preds[m_id] = st.selectbox("Progresses:", options, index=default_idx, format_func=fmt_team, key=f"up_sel_{m_id}")
                st.markdown("</div>", unsafe_allow_html=True)
                    
        with ko_tabs[2]:
            o_qf = {
                "Match 97": (user_preds.get("Match 89", "W89"), user_preds.get("Match 90", "W90")),
                "Match 98": (user_preds.get("Match 93", "W93"), user_preds.get("Match 94", "W94")),
                "Match 99": (user_preds.get("Match 91", "W91"), user_preds.get("Match 92", "W92")),
                "Match 100": (user_preds.get("Match 95", "W95"), user_preds.get("Match 96", "W96"))
            }
            for m_id, (h, a) in o_qf.items():
                st.markdown(f"<div class='unified-match-card'><b>⭐ {m_id}</b><br><small style='opacity:0.8;'>Fixture: {fmt_team(h)} vs {fmt_team(a)}</small>", unsafe_allow_html=True)
                options = [h, a]
                current_pick = user_preds.get(m_id, h)
                default_idx = options.index(current_pick) if current_pick in options else 0
                user_preds[m_id] = st.selectbox("Progresses:", options, index=default_idx, format_func=fmt_team, key=f"up_sel_{m_id}")
                st.markdown("</div>", unsafe_allow_html=True)
                
        with ko_tabs[3]:
            sf1_h, sf1_a = user_preds.get("Match 97", "W97"), user_preds.get("Match 98", "W98")
            sf2_h, sf2_a = user_preds.get("Match 99", "W99"), user_preds.get("Match 100", "W100")
            
            st.markdown("<div class='unified-match-card'>", unsafe_allow_html=True)
            st.markdown("#### 🌿 Final Four Series")
            
            sf1_opts = [sf1_h, sf1_a]
            sf1_idx = sf1_opts.index(user_preds.get("Match 101", sf1_h)) if user_preds.get("Match 101", sf1_h) in sf1_opts else 0
            user_preds["Match 101"] = st.selectbox(f"Semi Final 1 Winner", sf1_opts, index=sf1_idx, format_func=fmt_team, key="up_sel_M101")
            
            sf2_opts = [sf2_h, sf2_a]
            sf2_idx = sf2_opts.index(user_preds.get("Match 102", sf2_h)) if user_preds.get("Match 102", sf2_h) in sf2_opts else 0
            user_preds["Match 102"] = st.selectbox(f"Semi Final 2 Winner", sf2_opts, index=sf2_idx, format_func=fmt_team, key="up_sel_M102")
            
            sf1_l = sf1_a if user_preds["Match 101"] == sf1_h else sf1_h
            sf2_l = sf2_a if user_preds["Match 102"] == sf2_h else sf2_h
            
            st.markdown("<hr>", unsafe_allow_html=True)
            p3_opts = [sf1_l, sf2_l]
            p3_idx = p3_opts.index(user_preds.get("Match 103", sf1_l)) if user_preds.get("Match 103", sf1_l) in p3_opts else 0
            user_preds["Match 103"] = st.selectbox(f"🥉 3rd Place Playoff Winner", p3_opts, index=p3_idx, format_func=fmt_team, key="up_sel_M103")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            f_opts = [user_preds["Match 101"], user_preds["Match 102"]]
            f_idx = f_opts.index(user_preds.get("Match 104", f_opts[0])) if user_preds.get("Match 104", f_opts[0]) in f_opts else 0
            user_preds["Match 104"] = st.selectbox(f"🥇 Grand Champion Prediction", f_opts, index=f_idx, format_func=fmt_team, key="up_sel_M104")
            st.markdown("</div>", unsafe_allow_html=True)
            
        if st.button("💾 Archive Complete Bracket Matrix", use_container_width=True):
            st.session_state.predictions[c_user] = user_preds
            st.success("Bracket pathways updated safely!")

# --- ADMINISTRATIVE CONTROL PANEL ---
elif app_tab == "🛠️ Admin Dashboard":
    st.header("🛠️ Real-time Admin Scoresheet Panel")
    admin_tabs = st.tabs(["Group Stage Results", "Knockout Progress Matches"])
    actual = st.session_state.actual_results
    
    with admin_tabs[0]:
        adm_group = st.selectbox("Verify Target Group Pool", list(GROUPS.keys()))
        
        for idx, (home, away) in enumerate(MATCH_IDS[adm_group]):
            kh = f"{adm_group}_m{idx}_h"
            ka = f"{adm_group}_m{idx}_a"
            
            st.markdown("<div class='unified-match-card'>", unsafe_allow_html=True)
            val_h = st.number_input(f"{fmt_team(home)} Score", min_value=0, max_value=15, value=actual["group"].get(kh, 0), step=1, key=f"a_{kh}")
            val_a = st.number_input(f"{fmt_team(away)} Score", min_value=0, max_value=15, value=actual["group"].get(ka, 0), step=1, key=f"a_{ka}")
            if st.button("📢 Publish Match", key=f"btn_pub_{kh}", use_container_width=True):
                actual["group"][kh] = val_h
                actual["group"][ka] = val_a
                st.session_state.actual_results = actual
                st.success("Leaderboard points updated instantly!")
            st.markdown("</div>", unsafe_allow_html=True)
            
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
        
        st.subheader("Official Knockout Tree Declarations")
        
        for m_id, (h, a) in adm_r32_pairings.items():
            st.markdown("<div class='unified-match-card'>", unsafe_allow_html=True)
            options = [h, a]
            curr_w = actual["ko_winners"].get(m_id, h)
            sel_w = st.selectbox(f"Winner: {m_id}", options, index=options.index(curr_w) if curr_w in options else 0, format_func=fmt_team, key=f"adm_w_{m_id}")
            if st.button("📢 Save Winner", key=f"btn_ko_{m_id}", use_container_width=True):
                actual["ko_winners"][m_id] = sel_w
                st.session_state.actual_results = actual
                st.success(f"{m_id} updated!")
            st.markdown("</div>", unsafe_allow_html=True)

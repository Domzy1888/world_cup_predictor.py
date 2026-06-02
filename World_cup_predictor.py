import streamlit as st
import pandas as pd

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="World Cup 2026 Prediction League",
    page_icon="🏆",
    layout="wide"
)

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

# Match identification numbers mapped directly to standard scheduling
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

if "actual_results" not in st.session_state:
    st.session_state.actual_results = {
        "group": {},       
        "ko_winners": {},  
        "third_place": "", 
        "finalists": []    
    }

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- HELPER FUNCTIONS ---
def run_standings_engine(scores_dict):
    """Calculates full group-stage positions and extracts wildcard pools."""
    all_group_results = {}
    third_place_pool = []
    
    for g_name, teams in GROUPS.items():
        standings = {t: {"Group": g_name, "Pts": 0, "GD": 0, "GF": 0} for t in teams}
        
        for idx, (home, away) in enumerate(MATCH_IDS[g_name]):
            kh = f"{g_name}_m{idx}_h"
            ka = f"{g_name}_m{idx}_a"
            
            h_score = scores_dict.get(kh, None)
            a_score = scores_dict.get(ka, None)
            
            if h_score is not None and a_score is not None:
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
    """Calculates a user's scoring points against actual verified admin results."""
    user_preds = st.session_state.predictions.get(username, {})
    actual = st.session_state.actual_results
    points = 0
    
    # 1. Group Stage Scoring
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
                    
    # 2. Knockout Stage Scoring
    for m in [f"Match {i}" for i in range(73, 89)]:
        if user_preds.get(m) and user_preds.get(m) == actual["ko_winners"].get(m):
            points += 3
            
    for m in [f"Match {i}" for i in range(89, 97)]:
        if user_preds.get(m) and user_preds.get(m) == actual["ko_winners"].get(m):
            points += 5
            
    for m in [f"Match {i}" for i in range(97, 101)]:
        if user_preds.get(m) and user_preds.get(m) == actual["ko_winners"].get(m):
            points += 10
            
    for m in ["Match 101", "Match 102"]:
        if user_preds.get(m) and user_preds.get(m) == actual["ko_winners"].get(m):
            points += 15
            
    if user_preds.get("Match 103") and user_preds.get("Match 103") == actual.get("third_place"):
        points += 15
        
    user_finalists = [user_preds.get("Match 101"), user_preds.get("Match 102")]
    for team in user_finalists:
        if team and team in actual["finalists"]:
            points += 20
            
    if user_preds.get("Match 104") and user_preds.get("Match 104") == actual["ko_winners"].get("Match 104"):
        points += 25
        
    return points

# --- AUTHENTICATION INTERFACE LAYER ---
if st.session_state.current_user is None:
    st.title("🔐 World Cup 2026 Friends League Sign-In")
    auth_tab1, auth_tab2 = st.tabs(["Login", "Create Account"])
    
    with auth_tab1:
        lin_user = st.text_input("Username", key="lin_user")
        lin_pass = st.text_input("Password", type="password", key="lin_pass")
        if st.button("Log In"):
            if lin_user in st.session_state.users and st.session_state.users[lin_user]["password"] == lin_pass:
                st.session_state.current_user = lin_user
                st.rerun()
            else:
                st.error("Invalid credentials.")
                
    with auth_tab2:
        reg_user = st.text_input("Choose Username", key="reg_user")
        reg_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        if st.button("Register"):
            if reg_user.strip() == "":
                st.error("Username cannot be empty.")
            elif reg_user in st.session_state.users:
                st.error("Username already exists.")
            else:
                st.session_state.users[reg_user] = {"password": reg_pass, "is_admin": False}
                st.success("Registration successful! Proceed to Login.")
    st.stop()

# --- NAVBAR ---
c_user = st.session_state.current_user
col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.write(f"Logged in as: **{c_user}** " + ("(🛠️ Administrator)" if st.session_state.users[c_user]["is_admin"] else "(🏃 Competitor)"))
with col_nav2:
    if st.button("Log Out"):
        st.session_state.current_user = None
        st.rerun()

# --- MAIN APP LAYOUT CONFIG ---
main_tabs = ["🏆 Leaderboard", "📝 Submit Predictions"]
if st.session_state.users[c_user]["is_admin"]:
    main_tabs.append("🛠️ Admin Dashboard")
    
app_tab = st.sidebar.radio("Navigation Menu", main_tabs)

if c_user not in st.session_state.predictions:
    st.session_state.predictions[c_user] = {}

# --- LEADERBOARD TAB ---
if app_tab == "🏆 Leaderboard":
    st.header("🏆 League Standings Leaderboard")
    leaderboard_data = []
    
    for user, info in st.session_state.users.items():
        if not info["is_admin"]:
            score = calculate_user_points(user)
            leaderboard_data.append({"Competitor": user, "Total Points": score})
            
    df_leaderboard = pd.DataFrame(leaderboard_data)
    if not df_leaderboard.empty:
        df_leaderboard = df_leaderboard.sort_values(by="Total Points", ascending=False).reset_index(drop=True)
        df_leaderboard.index += 1
        st.dataframe(df_leaderboard, use_container_width=True)
    else:
        st.info("No prediction data received yet.")

# --- USER PREDICTIONS FILL SHEET ---
elif app_tab == "📝 Submit Predictions":
    st.header("📝 Submit Your Tournament Predictions")
    
    pred_sub_tabs = st.tabs(["📊 Group Stage Matches", "🌳 Knockout Bracket Path"])
    user_preds = st.session_state.predictions[c_user]
    
    with pred_sub_tabs[0]:
        selected_group = st.selectbox("Select Group", list(GROUPS.keys()))
        g_teams = GROUPS[selected_group]
        
        col_input, col_table = st.columns([3, 2])
        
        with col_input:
            st.subheader("Predict Scorelines")
            for idx, (home, away) in enumerate(MATCH_IDS[selected_group]):
                kh = f"{selected_group}_m{idx}_h"
                ka = f"{selected_group}_m{idx}_a"
                
                c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 3])
                with c1: st.write(f"**{home}**")
                with c2: user_preds[kh] = st.number_input("", min_value=0, max_value=15, value=user_preds.get(kh, 0), step=1, key=f"p_{kh}", label_visibility="collapsed")
                with c3: st.markdown("<p style='text-align:center;'>vs</p>", unsafe_allow_html=True)
                with c4: user_preds[ka] = st.number_input("", min_value=0, max_value=15, value=user_preds.get(ka, 0), step=1, key=f"p_{ka}", label_visibility="collapsed")
                with c5: st.write(f"<p style='text-align:right;'><b>{away}</b></p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:0.2em 0px;'>", unsafe_allow_html=True)
                
        with col_table:
            st.subheader("Your Predicted Standings")
            u_results, _ = run_standings_engine(user_preds)
            st.dataframe(u_results[selected_group][["Team", "Pts", "GD", "GF"]], use_container_width=True, hide_index=True)

    with pred_sub_tabs[1]:
        st.subheader("🌳 Knockout Bracket Selections")
        st.write("Review the qualified teams below and use the dropdown to select who advances.")
        
        u_results, u_wildcards = run_standings_engine(user_preds)
        
        def get_confirmed_1st(g):
            if g in u_results and not u_results[g].empty:
                return u_results[g].iloc[0]["Team"]
            return f"1st {g}"

        def get_confirmed_2nd(g):
            if g in u_results and not u_results[g].empty:
                return u_results[g].iloc[1]["Team"]
            return f"2nd {g}"
        
        # Build the accurate Round of 32 Pairing Matrix (Typo Duplicates Fixed Here)
        o_r32 = {
            "Match 73": (get_confirmed_1st("Group A"), u_wildcards[4]), 
            "Match 74": (get_confirmed_1st("Group E"), u_wildcards[0]),
            "Match 75": (get_confirmed_1st("Group F"), get_confirmed_2nd("Group C")), 
            "Match 76": (get_confirmed_1st("Group C"), get_confirmed_2nd("Group F")),
            "Match 77": (get_confirmed_1st("Group I"), u_wildcards[1]), 
            "Match 78": (get_confirmed_2nd("Group E"), get_confirmed_2nd("Group I")),
            "Match 79": (get_confirmed_1st("Group B"), u_wildcards[6]), 
            "Match 80": (get_confirmed_1st("Group L"), u_wildcards[5]),
            "Match 81": (get_confirmed_1st("Group D"), u_wildcards[2]), 
            "Match 82": (get_confirmed_1st("Group G"), u_wildcards[3]),
            "Match 83": (get_confirmed_2nd("Group K"), get_confirmed_2nd("Group L")), 
            "Match 84": (get_confirmed_1st("Group H"), get_confirmed_2nd("Group J")),
            "Match 85": (get_confirmed_2nd("Group A"), get_confirmed_2nd("Group B")), 
            "Match 86": (get_confirmed_1st("Group J"), get_confirmed_2nd("Group H")),
            "Match 87": (get_confirmed_1st("Group K"), u_wildcards[7]), 
            "Match 88": (get_confirmed_2nd("Group D"), get_confirmed_2nd("Group G"))
        }
        
        ko_tabs = st.tabs(["Round of 32", "Round of 16", "Quarter-Finals", "Finals"])
        
        # --- ROUND OF 32 ---
        with ko_tabs[0]:
            cl, cr = st.columns(2)
            for idx, (m_id, (h, a)) in enumerate(o_r32.items()):
                col = cl if idx < 8 else cr
                with col:
                    st.markdown(f"**⚽ {m_id}**")
                    st.caption(f"Fixture: {h} vs {a}")
                    
                    options = [h, a]
                    current_pick = user_preds.get(m_id, h)
                    default_idx = options.index(current_pick) if current_pick in options else 0
                    
                    user_preds[m_id] = st.selectbox(
                        "Predicted Winner to Progress:", 
                        options, 
                        index=default_idx, 
                        key=f"up_sel_{m_id}"
                    )
                    st.markdown("<hr style='margin:0.5em 0px;'>", unsafe_allow_html=True)
                    
        # --- ROUND OF 16 ---
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
            cl, cr = st.columns(2)
            for idx, (m_id, (h, a)) in enumerate(o_r16.items()):
                col = cl if idx < 4 else cr
                with col:
                    st.markdown(f"**📋 {m_id}**")
                    st.caption(f"Fixture: {h} vs {a}")
                    
                    options = [h, a]
                    current_pick = user_preds.get(m_id, h)
                    default_idx = options.index(current_pick) if current_pick in options else 0
                    
                    user_preds[m_id] = st.selectbox("Predicted Winner to Progress:", options, index=default_idx, key=f"up_sel_{m_id}")
                    st.markdown("<hr style='margin:0.5em 0px;'>", unsafe_allow_html=True)
                    
        # --- QUARTER-FINALS ---
        with ko_tabs[2]:
            o_qf = {
                "Match 97": (user_preds.get("Match 89", "W89"), user_preds.get("Match 90", "W90")),
                "Match 98": (user_preds.get("Match 93", "W93"), user_preds.get("Match 94", "W94")),
                "Match 99": (user_preds.get("Match 91", "W91"), user_preds.get("Match 92", "W92")),
                "Match 100": (user_preds.get("Match 95", "W95"), user_preds.get("Match 96", "W96"))
            }
            for m_id, (h, a) in o_qf.items():
                st.markdown(f"**⭐ {m_id}**")
                st.caption(f"Fixture: {h} vs {a}")
                
                options = [h, a]
                current_pick = user_preds.get(m_id, h)
                default_idx = options.index(current_pick) if current_pick in options else 0
                
                user_preds[m_id] = st.selectbox("Predicted Winner to Progress:", options, index=default_idx, key=f"up_sel_{m_id}")
                st.markdown("<hr style='margin:0.5em 0px;'>", unsafe_allow_html=True)
                
        # --- FINALS ---
        with ko_tabs[3]:
            sf1_h = user_preds.get("Match 97", "W97")
            sf1_a = user_preds.get("Match 98", "W98")
            sf2_h = user_preds.get("Match 99", "W99")
            sf2_a = user_preds.get("Match 100", "W100")
            
            st.markdown("#### 🌿 Semi-Finals")
            
            st.caption(f"Semi-Final 1: {sf1_h} vs {sf1_a}")
            sf1_opts = [sf1_h, sf1_a]
            sf1_pick = user_preds.get("Match 101", sf1_h)
            sf1_idx = sf1_opts.index(sf1_pick) if sf1_pick in sf1_opts else 0
            user_preds["Match 101"] = st.selectbox("Progresses to Final:", sf1_opts, index=sf1_idx, key=f"up_sel_M101")
            
            st.caption(f"Semi-Final 2: {sf2_h} vs {sf2_a}")
            sf2_opts = [sf2_h, sf2_a]
            sf2_pick = user_preds.get("Match 102", sf2_h)
            sf2_idx = sf2_opts.index(sf2_pick) if sf2_pick in sf2_opts else 0
            user_preds["Match 102"] = st.selectbox("Progresses to Final:", sf2_opts, index=sf2_idx, key=f"up_sel_M102")
            
            sf1_l = sf1_a if user_preds["Match 101"] == sf1_h else sf1_h
            sf2_l = sf2_a if user_preds["Match 102"] == sf2_h else sf2_h
            
            st.markdown("---")
            st.markdown("#### 🥉 3rd Place Playoff")
            st.caption(f"Match 103: {sf1_l} vs {sf2_l}")
            p3_opts = [sf1_l, sf2_l]
            p3_pick = user_preds.get("Match 103", sf1_l)
            p3_idx = p3_opts.index(p3_pick) if p3_pick in p3_opts else 0
            user_preds["Match 103"] = st.selectbox("3rd Place Winner:", p3_opts, index=p3_idx, key=f"up_sel_M103")
            
            st.markdown("---")
            st.markdown("#### 🥇 Grand Final")
            f_h = user_preds["Match 101"]
            f_a = user_preds["Match 102"]
            st.caption(f"Match 104: {f_h} vs {f_a}")
            f_opts = [f_h, f_a]
            f_pick = user_preds.get("Match 104", f_h)
            f_idx = f_opts.index(f_pick) if f_pick in f_opts else 0
            user_preds["Match 104"] = st.selectbox("World Cup Champion:", f_opts, index=f_idx, key=f"up_sel_M104")
            
        if st.button("💾 Save All Predictions"):
            st.session_state.predictions[c_user] = user_preds
            st.success("Your changes have been safely archived!")

# --- SECURE ADMINISTRATIVE DECK ---
elif app_tab == "🛠️ Admin Dashboard":
    st.header("🛠️ Official Admin Dashboard")
    st.write("Enter the real-life scorelines and match winners to distribute points to players.")
    
    admin_tabs = st.tabs(["Group Results", "Knockout Results"])
    actual = st.session_state.actual_results
    
    with admin_tabs[0]:
        adm_group = st.selectbox("Verify Group", list(GROUPS.keys()), key="adm_grp")
        for idx, (home, away) in enumerate(MATCH_IDS[adm_group]):
            kh = f"{adm_group}_m{idx}_h"
            ka = f"{adm_group}_m{idx}_a"
            
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 3])
            with c1: st.write(home)
            with c2: actual["group"][kh] = st.number_input("", min_value=0, max_value=15, value=actual["group"].get(kh, 0), step=1, key=f"a_{kh}", label_visibility="collapsed")
            with c3: st.markdown("<p style='text-align:center;'>vs</p>", unsafe_allow_html=True)
            with c4: actual["group"][ka] = st.number_input("", min_value=0, max_value=15, value=actual["group"].get(ka, 0), step=1, key=f"a_{ka}", label_visibility="collapsed")
            with c5: st.write(away)
            
    with admin_tabs[1]:
        adm_group_res, adm_wildcards = run_standings_engine(actual["group"])
        
        def get_1st(g): return adm_group_res[g].iloc[0]["Team"] if not adm_group_res[g].empty else f"1st {g}"
        def get_2nd(g): return adm_group_res[g].iloc[1]["Team"] if not adm_group_res[g].empty else f"2nd {g}"
        
        # Parallel administrative matrix matching fixed user structure
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
        
        st.subheader("Verify Knockout Winners")
        
        st.markdown("---")
        for m_id, (h, a) in adm_r32_pairings.items():
            actual["ko_winners"][m_id] = st.selectbox(f"Actual Winner: {m_id} ({h} vs {a})", [h, a], key=f"adm_w_{m_id}")
            
        st.markdown("---")
        adm_r16_pairings = {
            "Match 89": (actual["ko_winners"].get("Match 74"), actual["ko_winners"].get("Match 77")),
            "Match 90": (actual["ko_winners"].get("Match 73"), actual["ko_winners"].get("Match 75")),
            "Match 93": (actual["ko_winners"].get("Match 83"), actual["ko_winners"].get("Match 84")),
            "Match 94": (actual["ko_winners"].get("Match 81"), actual["ko_winners"].get("Match 82")),
            "Match 91": (actual["ko_winners"].get("Match 76"), actual["ko_winners"].get("Match 78")),
            "Match 92": (actual["ko_winners"].get("Match 79"), actual["ko_winners"].get("Match 80")),
            "Match 95": (actual["ko_winners"].get("Match 86"), actual["ko_winners"].get("Match 88")),
            "Match 96": (actual["ko_winners"].get("Match 85"), actual["ko_winners"].get("Match 87"))
        }
        for m_id, (h, a) in adm_r16_pairings.items():
            if h and a:
                actual["ko_winners"][m_id] = st.selectbox(f"Actual Winner: {m_id} ({h} vs {a})", [h, a], key=f"adm_w_{m_id}")
                
        st.markdown("---")
        adm_qf_pairings = {
            "Match 97": (actual["ko_winners"].get("Match 89"), actual["ko_winners"].get("Match 90")),
            "Match 98": (actual["ko_winners"].get("Match 93"), actual["ko_winners"].get("Match 94")),
            "Match 99": (actual["ko_winners"].get("Match 91"), actual["ko_winners"].get("Match 92")),
            "Match 100": (actual["ko_winners"].get("Match 95"), actual["ko_winners"].get("Match 96"))
        }
        for m_id, (h, a) in adm_qf_pairings.items():
            if h and a:
                actual["ko_winners"][m_id] = st.selectbox(f"Actual Winner: {m_id} ({h} vs {a})", [h, a], key=f"adm_w_{m_id}")
                
        st.markdown("---")
        sf1_h, sf1_a = actual["ko_winners"].get("Match 97"), actual["ko_winners"].get("Match 98")
        sf2_h, sf2_a = actual["ko_winners"].get("Match 99"), actual["ko_winners"].get("Match 100")
        
        if sf1_h and sf1_a and sf2_h and sf2_a:
            actual["ko_winners"]["Match 101"] = st.selectbox(f"Actual Semi-Final 1 Winner", [sf1_h, sf1_a], key="adm_w_M101")
            actual["ko_winners"]["Match 102"] = st.selectbox(f"Actual Semi-Final 2 Winner", [sf2_h, sf2_a], key="adm_w_M102")
            
            actual["finalists"] = [actual["ko_winners"]["Match 101"], actual["ko_winners"]["Match 102"]]
            
            sf1_l = sf1_a if actual["ko_winners"]["Match 101"] == sf1_h else sf1_h
            sf2_l = sf2_a if actual["ko_winners"]["Match 102"] == sf2_h else sf2_h
            actual["third_place"] = st.selectbox(f"Actual 3rd Place Match Winner", [sf1_l, sf2_l], key="adm_w_M103")
            actual["ko_winners"]["Match 104"] = st.selectbox(f"Actual Tournament Champion", actual["finalists"], key="adm_w_M104")

    if st.button("📢 Publish Verified Results & Update Scores"):
        st.session_state.actual_results = actual
        st.success("Scores have been updated across all user profiles!")
import streamlit as st
import pandas as pd

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="World Cup 2026 Tournament Engine",
    page_icon="⚽",
    layout="wide"
)

# --- CORE 48-TEAM DATA STRUCTURE ---
GROUPS = {
    "Group A": ["Mexico", "South Africa", "Rep. of Korea", "Czech Rep."],
    "Group B": ["Canada", "Bosnia", "Qatar", "Switzerland"],
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

# --- INITIALIZE SESSION STATE STORAGE ---
if "match_predictions" not in st.session_state:
    st.session_state.match_predictions = {}

st.title("🏆 World Cup 2026 Tournament Predictor")
st.markdown("A completely fresh, user-friendly implementation of the real 48-team tournament bracket logic.")
st.write("---")

tab1, tab2, tab3 = st.tabs(["📊 Group Stage Hub", "🃏 Wildcard Tracker", "🌳 Round of 32 Bracket"])

# --- GLOBAL STANDINGS CALCULATION ENGINE ---
all_group_results = {}
third_place_pool = []

for g_name, teams in GROUPS.items():
    standings = {t: {"Group": g_name, "Pts": 0, "GD": 0, "GF": 0} for t in teams}
    matches = [
        (teams[0], teams[1]), (teams[2], teams[3]),
        (teams[0], teams[2]), (teams[1], teams[3]),
        (teams[0], teams[3]), (teams[1], teams[2])
    ]
    
    for idx, (home, away) in enumerate(matches):
        key_h = f"{g_name}_m{idx}_h"
        key_a = f"{g_name}_m{idx}_a"
        
        # Pull scores from state or default to 0
        h_score = st.session_state.match_predictions.get(key_h, 0)
        a_score = st.session_state.match_predictions.get(key_a, 0)
        
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
            
    # Sort group to find rankings
    df_g = pd.DataFrame.from_dict(standings, orient='index').reset_index().rename(columns={'index': 'Team'})
    df_g = df_g.sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
    
    all_group_results[g_name] = df_g
    # Extract the 3rd place row team to evaluate for wildcards
    third_place_pool.append(df_g.iloc[2].to_dict())

# Sort wildcard matrix globally
wildcard_df = pd.DataFrame(third_place_pool)
wildcard_df = wildcard_df.sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
wildcard_df.index += 1

# Identify the qualifying 8 wildcards and know their original groups
qualified_wildcards_list = wildcard_df.head(8).to_dict(orient="records")
qualified_wildcards_teams = [item["Team"] for item in qualified_wildcards_list]

# --- TAB 1: USER MATCH PREDICTIONS ---
with tab1:
    selected_group = st.selectbox("Select Group Filter", list(GROUPS.keys()))
    col_play, col_view = st.columns([3, 2])
    
    with col_play:
        st.subheader(f"{selected_group} Match Entries")
        g_teams = GROUPS[selected_group]
        g_matches = [
            (g_teams[0], g_teams[1]), (g_teams[2], g_teams[3]),
            (g_teams[0], g_teams[2]), (g_teams[1], g_teams[3]),
            (g_teams[0], g_teams[3]), (g_teams[1], g_teams[2])
        ]
        
        for idx, (home, away) in enumerate(g_matches):
            kh = f"{selected_group}_m{idx}_h"
            ka = f"{selected_group}_m{idx}_a"
            
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 3])
            with c1: st.write(f"**{home}**")
            with c2: 
                v_h = st.number_input("", min_value=0, max_value=15, value=st.session_state.match_predictions.get(kh, 0), step=1, key=kh, label_visibility="collapsed")
                st.session_state.match_predictions[kh] = v_h
            with c3: st.markdown("<p style='text-align:center;'>vs</p>", unsafe_allow_html=True)
            with c4: 
                v_a = st.number_input("", min_value=0, max_value=15, value=st.session_state.match_predictions.get(ka, 0), step=1, key=ka, label_visibility="collapsed")
                st.session_state.match_predictions[ka] = v_a
            with c5: st.write(f"<p style='text-align:right;'><b>{away}</b></p>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:0.4em 0px;'>", unsafe_allow_html=True)

    with col_view:
        st.subheader("Live Standings")
        st.dataframe(all_group_results[selected_group][["Team", "Pts", "GD", "GF"]], use_container_width=True, hide_index=True)

# --- TAB 2: WILDCARD DATA WATCH ---
with tab2:
    st.header("🃏 3rd-Place Wildcard Standings Leaderboard")
    st.write("The top 8 teams highlighted in green successfully qualify for the Round of 32 knockout spots.")
    
    def highlight_qualified(row):
        return ['background-color: #dcfce7' if row.name <= 8 else 'background-color: #fee2e2' for _ in row]
        
    st.dataframe(wildcard_df.style.apply(highlight_qualified, axis=1), use_container_width=True)

# --- TAB 3: DYNAMIC KNOCKOUT BRACKET ---
with tab3:
    st.header("🪵 Round of 32 Dynamic Matching Matrix")
    st.write("These setups update dynamically based on the numbers you input in the Group Stage tab.")
    
    # FIX: Variables renamed safely so they don't start with digits!
    team_1A = all_group_results["Group A"].iloc[0]["Team"]
    team_2B = all_group_results["Group B"].iloc[1]["Team"]
    team_1E = all_group_results["Group E"].iloc[0]["Team"]
    
    col_ko1, col_ko2 = st.columns(2)
    with col_ko1:
        st.info("🔒 Standard Dynamic Matchup (1st Place vs 2nd Place)")
        st.metric(label="Match 73 Pair", value=f"{team_1A} vs {team_2B}")
        
    with col_ko2:
        st.success("🃏 Wildcard Dependent Matchup (1st Place vs Best 3rd Place)")
        # Dynamically allocate the best available matching wildcard team from our sorted list
        allocated_wildcard = qualified_wildcards_teams[0] if len(qualified_wildcards_teams) > 0 else "Pending Wildcard"
        st.metric(label="Match 74 Pair (1E vs Top Ranked Wildcard)", value=f"{team_1E} vs {allocated_wildcard}")

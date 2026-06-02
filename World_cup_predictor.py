import streamlit as st
import pandas as pd

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="World Cup 2026 Tournament Hub",
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

# --- INITIALIZE SESSION STATE ---
if "match_predictions" not in st.session_state:
    st.session_state.match_predictions = {}
if "ko_scores" not in st.session_state:
    st.session_state.ko_scores = {}

st.title("🏆 FIFA World Cup 2026 Comprehensive Predictor")
st.markdown("Enter group predictions, track the 3rd-place wildcards, and simulate the entire knockout bracket.")
st.write("---")

tab1, tab2, tab3 = st.tabs(["📊 Group Stage Hub", "🃏 Wildcard Standings", "🌳 Knockout Brackets"])

# --- GLOBAL STANDINGS ENGINE ---
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
        kh = f"{g_name}_m{idx}_h"
        ka = f"{g_name}_m{idx}_a"
        h_score = st.session_state.match_predictions.get(kh, 0)
        a_score = st.session_state.match_predictions.get(ka, 0)
        
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
    third_place_pool.append(df_g.iloc[2].to_dict())

# Sort wildcard matrix globally
wildcard_df = pd.DataFrame(third_place_pool)
wildcard_df = wildcard_df.sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
wildcard_df.index += 1
qualified_wildcards = list(wildcard_df.head(8)["Team"])

# Fallbacks for missing wildcards
while len(qualified_wildcards) < 8:
    qualified_wildcards.append(f"Wildcard #{len(qualified_wildcards)+1}")

# --- TAB 1: GROUP STAGE INTERFACE ---
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

# --- TAB 2: WILDCARD TABLES ---
with tab2:
    st.header("🃏 Third-Place Wildcard Standings Leaderboard")
    st.write("The top 8 teams highlighted in green successfully qualify for the Round of 32 knockout spots.")
    def highlight_qualified(row):
        return ['background-color: #dcfce7' if row.name <= 8 else 'background-color: #fee2e2' for _ in row]
    st.dataframe(wildcard_df.style.apply(highlight_qualified, axis=1), use_container_width=True)

# --- TAB 3: COMPLETE BRACKETS ENGINE ---
with tab3:
    st.header("🌳 Tournament Knockout Phase")
    
    # Helper to look up rankings safely
    def get_team(group, rank_idx):
        return all_group_results[group].iloc[rank_idx]["Team"]

    # 1. GENERATE DYNAMIC MATCH FIXTURES (ROUND OF 32 Setup)
    # This dictionary maps out standard paths along with sequential wildcard placeholders
    r32_pairings = {
        "Match 1": (get_team("Group A", 0), get_team("Group B", 1)),
        "Match 2": (get_team("Group B", 0), get_team("Group A", 1)),
        "Match 3": (get_team("Group C", 0), qualified_wildcards[0]),
        "Match 4": (get_team("Group D", 0), qualified_wildcards[1]),
        "Match 5": (get_team("Group E", 0), qualified_wildcards[2]),
        "Match 6": (get_team("Group F", 0), qualified_wildcards[3]),
        "Match 7": (get_team("Group G", 0), qualified_wildcards[4]),
        "Match 8": (get_team("Group H", 0), qualified_wildcards[5]),
        "Match 9": (get_team("Group I", 0), qualified_wildcards[6]),
        "Match 10": (get_team("Group J", 0), qualified_wildcards[7]),
        "Match 11": (get_team("Group K", 0), get_team("Group L", 1)),
        "Match 12": (get_team("Group L", 0), get_team("Group K", 1)),
        "Match 13": (get_team("Group C", 1), get_team("Group D", 1)),
        "Match 14": (get_team("Group E", 1), get_team("Group F", 1)),
        "Match 15": (get_team("Group G", 1), get_team("Group H", 1)),
        "Match 16": (get_team("Group I", 1), get_team("Group J", 1)),
    }

    sub_tabs = st.tabs(["Round of 32", "Round of 16", "Quarter-Finals", "Semi-Finals & Final"])
    
    # --- ROUND OF 32 ENTRY LINEUP ---
    r32_winners = {}
    with sub_tabs[0]:
        st.subheader("Simulate Round of 32 Matches")
        
        # Display fixtures split into 2 visual dashboard columns
        k_col1, k_col2 = st.columns(2)
        
        for idx, (m_id, (t_home, t_away)) in enumerate(r32_pairings.items()):
            target_col = k_col1 if idx < 8 else k_col2
            
            with target_col:
                st.markdown(f"##### 📋 {m_id}")
                c_h, c_vs, c_a, c_win = st.columns([3, 1, 3, 3])
                
                with c_h:
                    st.write(t_home)
                    sh = st.number_input("", min_value=0, max_value=10, step=1, key=f"r32_{m_id}_h", label_visibility="collapsed")
                with c_vs:
                    st.markdown("<p style='text-align:center; padding-top:5px;'>-</p>", unsafe_allow_html=True)
                with c_a:
                    st.write(f"<p style='text-align:right;'>{t_away}</p>", unsafe_allow_html=True)
                    sa = st.number_input("", min_value=0, max_value=10, step=1, key=f"r32_{m_id}_a", label_visibility="collapsed")
                
                with c_win:
                    # Choose a winner. Ties handle automatic advancement pick choices
                    options = [t_home, t_away]
                    default_idx = 0 if sh >= sa else 1
                    winner = st.radio("Advances:", options, index=default_idx, key=f"w_{m_id}", horizontal=True)
                    r32_winners[m_id] = winner
                st.markdown("<hr style='margin:0.5em 0px;'>", unsafe_allow_html=True)

    # --- ROUND OF 16 ENTRY LINEUP ---
    r16_winners = {}
    with sub_tabs[1]:
        st.subheader("Simulate Round of 16 Matches")
        
        # Map Round of 32 winners to Round of 16 paths
        r16_pairings = {
            "R16 Match 1": (r32_winners["Match 1"], r32_winners["Match 3"]),
            "R16 Match 2": (r32_winners["Match 2"], r32_winners["Match 4"]),
            "R16 Match 3": (r32_winners["Match 5"], r32_winners["Match 7"]),
            "R16 Match 4": (r32_winners["Match 6"], r32_winners["Match 8"]),
            "R16 Match 5": (r32_winners["Match 9"], r32_winners["Match 11"]),
            "R16 Match 6": (r32_winners["Match 10"], r32_winners["Match 12"]),
            "R16 Match 7": (r32_winners["Match 13"], r32_winners["Match 15"]),
            "R16 Match 8": (r32_winners["Match 14"], r32_winners["Match 16"]),
        }
        
        col_r16_1, col_r16_2 = st.columns(2)
        for idx, (m_id, (t_home, t_away)) in enumerate(r16_pairings.items()):
            target_col = col_r16_1 if idx < 4 else col_r16_2
            with target_col:
                st.markdown(f"##### 📋 {m_id}")
                winner = st.radio(f"Matchup: {t_home} vs {t_away}", [t_home, t_away], key=f"w_{m_id}")
                r16_winners[m_id] = winner
                st.markdown("---")

    # --- QUARTER-FINALS LINEUP ---
    qf_winners = {}
    with sub_tabs[2]:
        st.subheader("Simulate Quarter-Finals")
        
        qf_pairings = {
            "QF Match 1": (r16_winners["R16 Match 1"], r16_winners["R16 Match 3"]),
            "QF Match 2": (r16_winners["R16 Match 2"], r16_winners["R16 Match 4"]),
            "QF Match 3": (r16_winners["R16 Match 5"], r16_winners["R16 Match 7"]),
            "QF Match 4": (r16_winners["R16 Match 6"], r16_winners["R16 Match 8"]),
        }
        
        for m_id, (t_home, t_away) in qf_pairings.items():
            winner = st.radio(f"**{m_id}:** {t_home} vs {t_away}", [t_home, t_away], key=f"w_{m_id}", horizontal=True)
            qf_winners[m_id] = winner

    # --- SEMI-FINALS & FINALS LINEUP ---
    with sub_tabs[3]:
        st.subheader("The Grand Finale Run")
        
        sf1_winner = st.radio(f"Semi-Final 1: {qf_winners['QF Match 1']} vs {qf_winners['QF Match 3']}", [qf_winners['QF Match 1'], qf_winners['QF Match 3']], key="sf1_w")
        sf2_winner = st.radio(f"Semi-Final 2: {qf_winners['QF Match 2']} vs {qf_winners['QF Match 4']}", [qf_winners['QF Match 2'], qf_winners['QF Match 4']], key="sf2_w")
        
        st.markdown("### 🥇 World Cup Final Match")
        champion = st.radio(f"Grand Final: {sf1_winner} vs {sf2_winner}", [sf1_winner, sf2_winner], key="final_w")
        
        if st.button("🏆 Crown the World Champion"):
            st.balloons()
            st.success(f"🎉 Your predicted 2026 FIFA World Cup Champion is **{champion.upper()}**! 🎉")

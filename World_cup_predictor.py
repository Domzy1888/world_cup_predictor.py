import streamlit as st
import pandas as pd
import hashlib
from supabase import create_client, Client

# --- 1. CONFIGURATION & FULL COLOUR DARK THEME STYLING ---
st.set_page_config(
    page_title="World Cup 2026 Prediction League",
    page_icon="🏆",
    layout="wide"
)

st.markdown("""
    <style>
    /* Background Image setup */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.2), rgba(15, 23, 42, 0.4)),
                    url("https://cdn-media.theathletic.com/cdn-cgi/image/width=1000%2cquality=70%2cformat=auto/https://cdn-media.theathletic.com/vwYC1qZfTwfm_3qmyXkIC5Rja_1440x960.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Global Typography */
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

    [data-testid="stExpander"], [data-testid="stTabContent"], .stTabs {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
    }

    div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.95) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }
    
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

# --- 2. SECURITY HELPER ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- 3. GLOBAL SUPABASE CONNECTION INIT ---
try:
    SUPABASE_URL = st.secrets["connections"]["supabase"]["url"]
    SUPABASE_KEY = st.secrets["connections"]["supabase"]["key"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Could not establish a connection to your Supabase database. Please double check your secrets parameters.")
    st.stop()

# --- 4. GLOBAL TEAMS & FLAGS MAP ---
FLAGS = {
    "Mexico": "🇲🇽 MEXICO", "South Africa": "🇿🇦 SOUTH AFRICA", "Rep. of Korea": "🇰🇷 REP. OF KOREA", "Czech Rep.": "🇨🇿 CZECH REP.",
    "Canada": "🇨🇦 CANADA", "Bosnia/Herzeg.": "🇧🇦 BOSNIA/HERZEG.", "Qatar": "🇶🇦 QATAR", "Switzerland": "🇨🇭 SWITZERLAND",
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

# --- 5. DATA STRUCTURES (GROUPS & CHRONOLOGICAL FIXTURES) ---
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

PAIRS_R32_STRUC = {
    "Match_73": ("Group A", "1st", "Wildcard_4"), "Match_74": ("Group E", "1st", "Wildcard_0"),
    "Match_75": ("Group F", "1st", "Group C", "2nd"), "Match_76": ("Group C", "1st", "Group F", "2nd"),
    "Match_77": ("Group I", "1st", "Wildcard_1"), "Match_78": ("Group E", "2nd", "Group I", "2nd"),
    "Match_79": ("Group B", "1st", "Wildcard_6"), "Match_80": ("Group L", "1st", "Wildcard_5"),
    "Match_81": ("Group D", "1st", "Wildcard_2"), "Match_82": ("Group G", "1st", "Wildcard_3"),
    "Match_83": ("Group K", "2nd", "Group L", "2nd"), "Match_84": ("Group H", "1st", "Group J", "2nd"),
    "Match_85": ("Group A", "2nd", "Group B", "2nd"), "Match_86": ("Group J", "1st", "Group H", "2nd"),
    "Match_87": ("Group K", "1st", "Wildcard_7"), "Match_88": ("Group D", "2nd", "Group G", "2nd")
}

# --- 6. DATABASE HELPER WRAPPERS ---
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

def db_fetch_locked_status(user_id, league_id):
    res = supabase.table("predictions").select("match_key, is_locked").eq("user_id", user_id).eq("league_id", league_id).execute()
    locked_keys = set()
    if res.data:
        for row in res.data:
            if row["is_locked"]:
                locked_keys.add(row["match_key"])
    return locked_keys

def db_lock_predictions(user_id, league_id, match_keys_list):
    for key in match_keys_list:
        supabase.table("predictions").update({"is_locked": True}).eq("user_id", user_id).eq("league_id", league_id).eq("match_key", key).execute()

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

# --- 7. SESSION INITIALIZATION ---
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None
if "current_username" not in st.session_state:
    st.session_state.current_username = None

# --- 8. UNIFIED MATCH CARD RENDERER ---
def render_match_card(home, away, label, key_prefix, disabled=False, score_mode=False, scores_dict=None):
    disp1 = fmt_team(name=home)
    disp2 = fmt_team(name=away)
    
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

# --- 9. COMPUTATION ENGINES ---
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
            try:
                h_score = int(h_score)
                a_score = int(a_score)
            except:
                h_score, a_score = 0, 0
                
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

def resolve_bracket_teams(scores_dict, target_is_actual=False, actual_results_obj=None):
    """
    Simulates or extracts the teams that populate each tier of the tournament 
    dynamically based on scores, ensuring flexible cross-referencing per round.
    """
    if target_is_actual and actual_results_obj is not None:
        g_scores = actual_results_obj["group"]
        ko_choices = actual_results_obj["ko_winners"]
    else:
        g_scores = scores_dict
        ko_choices = scores_dict

    g_tables, wildcards = run_standings_engine(g_scores)
    
    def get_1st(g): return g_tables[g].iloc[0]["Team"] if g in g_tables and not g_tables[g].empty else ""
    def get_2nd(g): return g_tables[g].iloc[1]["Team"] if g in g_tables and not g_tables[g].empty else ""

    r32_teams = {}
    for m_id, details in PAIRS_R32_STRUC.items():
        if len(details) == 3:
            h = get_1st(details[0]) if details[1] == "1st" else get_2nd(details[0])
            w_idx = int(details[2].split("_")[1])
            a = wildcards[w_idx] if w_idx < len(wildcards) else ""
        else:
            h = get_1st(details[0]) if details[1] == "1st" else get_2nd(details[0])
            a = get_1st(details[2]) if details[3] == "1st" else get_2nd(details[2])
        r32_teams[m_id] = (h, a)

    # 1. Evaluate Round of 16 Teams
    r16_teams = set()
    for m in range(73, 89):
        m_key = f"Match_{m}"
        teams = r32_teams.get(m_key, ("", ""))
        choice = str(ko_choices.get(m_key, ""))
        if choice == "1" or choice == teams[0]: r16_teams.add(teams[0])
        elif choice == "2" or choice == teams[1]: r16_teams.add(teams[1])

    # 2. Evaluate Quarter-Final Teams
    qf_pairings = {
        "Match_89": ("Match_74", "Match_77"), "Match_90": ("Match_73", "Match_75"),
        "Match_93": ("Match_83", "Match_84"), "Match_94": ("Match_81", "Match_82"),
        "Match_91": ("Match_76", "Match_78"), "Match_92": ("Match_79", "Match_80"),
        "Match_95": ("Match_86", "Match_88"), "Match_96": ("Match_85", "Match_87")
    }
    qf_teams = set()
    for m_id, (prev1, prev2) in qf_pairings.items():
        t1 = str(ko_choices.get(prev1, ""))
        t2 = str(ko_choices.get(prev2, ""))
        if t1 == "1": t1 = r32_teams.get(prev1, ("",""))[0]
        elif t1 == "2": t1 = r32_teams.get(prev1, ("",""))[1]
        if t2 == "1": t2 = r32_teams.get(prev2, ("",""))[0]
        elif t2 == "2": t2 = r32_teams.get(prev2, ("",""))[1]
        
        choice = str(ko_choices.get(m_id, ""))
        if choice == "1" or choice == t1: qf_teams.add(t1)
        elif choice == "2" or choice == t2: qf_teams.add(t2)

    # 3. Evaluate Semi-Final Teams
    sf_pairings = {
        "Match_97": ("Match_89", "Match_90"), "Match_98": ("Match_93", "Match_94"),
        "Match_99": ("Match_91", "Match_92"), "Match_100": ("Match_95", "Match_96")
    }
    sf_teams = set()
    for m_id, (p1, p2) in sf_pairings.items():
        def get_winner_of_r16(r16_id):
            ch = str(ko_choices.get(r16_id, ""))
            if ch == "1": 
                prev = qf_pairings[r16_id][0]
                val = str(ko_choices.get(prev, ""))
                return r32_teams[prev][0] if val == "1" else r32_teams[prev][1]
            elif ch == "2":
                prev = qf_pairings[r16_id][1]
                val = str(ko_choices.get(prev, ""))
                return r32_teams[prev][0] if val == "1" else r32_teams[prev][1]
            return ch
            
        t1 = get_winner_of_r16(p1)
        t2 = get_winner_of_r16(p2)
        choice = str(ko_choices.get(m_id, ""))
        if choice == "1" or choice == t1: sf_teams.add(t1)
        elif choice == "2" or choice == t2: sf_teams.add(t2)

    # 4. Evaluate Finalists
    f1_winner_sel = str(ko_choices.get("Match_101", ""))
    f2_winner_sel = str(ko_choices.get("Match_102", ""))
    
    finalists = set([f1_winner_sel, f2_winner_sel])
    champ = str(ko_choices.get("Match_104", ""))
    third_place = str(ko_choices.get("Match_103" if not target_is_actual else "Match_103_winner", ""))

    return {
        "r32_pairings": r32_teams,
        "r16": r16_teams,
        "qf": qf_teams,
        "sf": sf_teams,
        "finalists": finalists,
        "champ": champ,
        "third": third_place
    }

def calculate_user_points(user_id, league_id):
    user_preds = db_fetch_user_predictions(user_id, league_id)
    actual = db_fetch_league_actual_results(league_id)
    points = 0
    
    # 1. Group Stage Verification
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

    # 2. Team-Based Progression Check (Cross-referencing round qualification groups globally)
    user_bracket = resolve_bracket_teams(user_preds, target_is_actual=False)
    actual_bracket = resolve_bracket_teams(None, target_is_actual=True, actual_results_obj=actual)

    for team in user_bracket["r16"]:
        if team and team in actual_bracket["r16"]: points += 3

    for team in user_bracket["qf"]:
        if team and team in actual_bracket["qf"]: points += 5

    for team in user_bracket["sf"]:
        if team and team in actual_bracket["sf"]: points += 10

    for team in user_bracket["finalists"]:
        if team and team in actual_bracket["finalists"]: points += 15

    if user_bracket["third"] and user_bracket["third"] == actual_bracket["third"]: points += 15
    if user_bracket["champ"] and user_bracket["champ"] == actual_bracket["champ"]: points += 25

    return points

# --- 10. SIGN IN GATEWAY ---
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

# --- 11. STRICT LEAGUE LOCK CHECK ---
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

col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.markdown(f"👥 Active Profile: **{c_user}**")
with col_nav2:
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.current_user_id = None
        st.session_state.current_username = None
        st.rerun()

leagues_dropdown_options = {lg["name"]: lg for lg in user_leagues_list}
selected_league_name = st.sidebar.selectbox("Current League Environment:", list(leagues_dropdown_options.keys()))
active_league_meta = leagues_dropdown_options[selected_league_name]
active_league_id = active_league_meta["id"]
is_league_admin = (active_league_meta["creator_id"] == c_uid)

main_tabs = ["🏆 Leaderboards", "📝 Submit Predictions", "🛡️ Create/Join a League"]
if is_league_admin: 
    main_tabs.append("🛠️ Admin Dashboard")
app_tab = st.sidebar.radio("Main Menu Navigation", main_tabs)

# --- 12. LEADERBOARD WORKSPACE ---
if app_tab == "🏆 Leaderboards":
    st.header(f"🏆 {selected_league_name} Standings")
    members_res = supabase.table("league_members").select("users(id, username)").eq("league_id", active_league_id).execute()
    leaderboard_data = []
    if members_res.data:
        for row in members_res.data:
            if row.get("users"):
                m_id = row["users"]["id"]
                m_name = row["users"]["username"]
                leaderboard_data.append({
                    "Competitor Name": m_name, 
                    "Current Total Points": calculate_user_points(m_id, active_league_id)
                })
    df_leaderboard = pd.DataFrame(leaderboard_data)
    if not df_leaderboard.empty:
        df_leaderboard = df_leaderboard.sort_values(by="Current Total Points", ascending=False).reset_index(drop=True)
        st.dataframe(df_leaderboard, use_container_width=True, hide_index=False)

# --- 13. CREATE / JOIN LEAGUE HUB ---
elif app_tab == "🛡️ Create/Join a League":
    st.header("🛡️ League Management Hub")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Join Another League")
        sec_join_code = st.text_input("Enter Additional Invite Code")
        if st.button("🔑 Join Pool", use_container_width=True):
            if sec_join_code.strip() != "":
                code_query = supabase.table("leagues").select("id, name").eq("invite_code", sec_join_code).execute()
                if code_query.data:
                    t_id = code_query.data[0]["id"]
                    supabase.table("league_members").insert({"user_id": c_uid, "league_id": t_id}).execute()
                    st.success("Successfully registered into new pool context!")
                    st.rerun()

# --- 14. USER PREDICTIONS DESK ---
elif app_tab == "📝 Submit Predictions":
    st.header(f"📝 Match Setup — {selected_league_name}")
    
    user_preds = db_fetch_user_predictions(c_uid, active_league_id)
    locked_keys_set = db_fetch_locked_status(c_uid, active_league_id)
    
    pred_sub_tabs = st.tabs(["📊 Group Matches", "🌳 Knockout Rounds"])
    
    with pred_sub_tabs[0]:
        selected_group = st.selectbox("Choose Group Stage Pool", list(GROUPS.keys()))
        group_match_ids = [m["id"] for m in CHRONO_MATCHES[selected_group]]
        group_keys = [f"Match_{mid}_h" for mid in group_match_ids] + [f"Match_{mid}_a" for mid in group_match_ids]
        is_group_locked = any(k in locked_keys_set for k in group_keys)
        
        col_input, col_table = st.columns([1, 1])
        with col_input:
            if is_group_locked:
                st.markdown(f"<div class='lock-badge-banner'>🔒 {selected_group} Locked In</div>", unsafe_allow_html=True)
                for match in CHRONO_MATCHES[selected_group]:
                    user_preds = render_match_card(
                        home=match["home"], away=match["away"], label=f"Match #{match['id']}", 
                        key_prefix=f"Match_{match['id']}", disabled=is_group_locked, score_mode=True, scores_dict=user_preds
                    )
            else:
                with st.form(key=f"form_{selected_group}", clear_on_submit=False):
                    for match in CHRONO_MATCHES[selected_group]:
                        user_preds = render_match_card(
                            home=match["home"], away=match["away"], label=f"Match #{match['id']}", 
                            key_prefix=f"Match_{match['id']}", disabled=is_group_locked, score_mode=True, scores_dict=user_preds
                        )
                    if st.form_submit_button(f"🔒 Finalize & Lock {selected_group} Predictions", use_container_width=True):
                        for match in CHRONO_MATCHES[selected_group]:
                            db_save_prediction(c_uid, active_league_id, f"Match_{match['id']}_h", user_preds[f"Match_{match['id']}_h"])
                            db_save_prediction(c_uid, active_league_id, f"Match_{match['id']}_a", user_preds[f"Match_{match['id']}_a"])
                        db_lock_predictions(c_uid, active_league_id, group_keys)
                        st.rerun()
                
        with col_table:
            st.subheader("Simulated Group Table")
            u_results, _ = run_standings_engine(user_preds)
            df_display = u_results[selected_group][["Team", "Pts", "GD", "GF"]].copy()
            df_display["Team"] = df_display["Team"].apply(fmt_team)
            st.dataframe(df_display, use_container_width=True, hide_index=True)

    with pred_sub_tabs[1]:
        # Generate the user's dynamic bracket pairings
        user_calc_bracket = resolve_bracket_teams(user_preds, target_is_actual=False)
        o_r32 = user_calc_bracket["r32_pairings"]
        
        ko_tabs = st.tabs(["Round of 32", "Round of 16", "Quarter-Finals", "Finals"])
        
        with ko_tabs[0]:
            r32_keys = list(o_r32.keys())
            is_r32_locked = all(k in locked_keys_set for k in r32_keys)
            
            if is_r32_locked:
                st.markdown("<div class='lock-badge-banner'>🔒 Round of 32 Selections Locked</div>", unsafe_allow_html=True)
            
            for m_id, (h, a) in o_r32.items():
                user_preds[m_id] = render_match_card(h, a, m_id.replace("_", " "), m_id, disabled=is_r32_locked, score_mode=False, scores_dict=user_preds)
                
            if not is_r32_locked:
                if st.button("🔒 Lock Round of 32 Predictions", use_container_width=True):
                    for m_key in r32_keys:
                        val = user_preds.get(m_key)
                        if val and val != "Select Winner" and not str(val).startswith("W"):
                            opts = o_r32[m_key]
                            if val == opts[0]: db_save_prediction(c_uid, active_league_id, m_key, 1)
                            elif val == opts[1]: db_save_prediction(c_uid, active_league_id, m_key, 2)
                    db_lock_predictions(c_uid, active_league_id, r32_keys)
                    st.success("Round of 32 predictions successfully locked!")
                    st.rerun()
                    
        with ko_tabs[1]:
            def get_ko_prev(m_key):
                val = user_preds.get(m_key)
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
            is_r16_locked = all(k in locked_keys_set for k in r16_keys)
            
            if is_r16_locked:
                st.markdown("<div class='lock-badge-banner'>🔒 Round of 16 Selections Locked</div>", unsafe_allow_html=True)
                
            for m_id, (h, a) in o_r16.items():
                user_preds[m_id] = render_match_card(h, a, m_id.replace("_", " "), m_id, disabled=is_r16_locked, score_mode=False, scores_dict=user_preds)
                
            if not is_r16_locked:
                if st.button("🔒 Lock Round of 16 Predictions", use_container_width=True):
                    for m_key in r16_keys:
                        val = user_preds.get(m_key)
                        if val and val != "Select Winner" and not str(val).startswith("W"):
                            opts = o_r16[m_key]
                            if val == opts[0]: db_save_prediction(c_uid, active_league_id, m_key, 1)
                            elif val == opts[1]: db_save_prediction(c_uid, active_league_id, m_key, 2)
                    db_lock_predictions(c_uid, active_league_id, r16_keys)
                    st.success("Round of 16 predictions successfully locked!")
                    st.rerun()
                    
        with ko_tabs[2]:
            def get_ko_prev_r16(m_key):
                val = user_preds.get(m_key)
                if val in o_r16.get(m_key, ("","")): return val
                return f"W{m_key.split('_')[1]}"

            o_qf = {
                "Match_97": (get_ko_prev_r16("Match_89"), get_ko_prev_r16("Match_90")), "Match_98": (get_ko_prev_r16("Match_93"), get_ko_prev_r16("Match_94")),
                "Match_99": (get_ko_prev_r16("Match_91"), get_ko_prev_r16("Match_92")), "Match_100": (get_ko_prev_r16("Match_95"), get_ko_prev_r16("Match_96"))
            }
            qf_keys = list(o_qf.keys())
            is_qf_locked = all(k in locked_keys_set for k in qf_keys)
            
            if is_qf_locked:
                st.markdown("<div class='lock-badge-banner'>🔒 Quarter-Final Selections Locked</div>", unsafe_allow_html=True)
                
            for m_id, (h, a) in o_qf.items():
                user_preds[m_id] = render_match_card(h, a, m_id.replace("_", " "), m_id, disabled=is_qf_locked, score_mode=False, scores_dict=user_preds)
                
            if not is_qf_locked:
                if st.button("🔒 Lock Quarter-Final Predictions", use_container_width=True):
                    for m_key in qf_keys:
                        val = user_preds.get(m_key)
                        if val and val != "Select Winner" and not str(val).startswith("W"):
                            opts = o_qf[m_key]
                            if val == opts[0]: db_save_prediction(c_uid, active_league_id, m_key, 1)
                            elif val == opts[1]: db_save_prediction(c_uid, active_league_id, m_key, 2)
                    db_lock_predictions(c_uid, active_league_id, qf_keys)
                    st.success("Quarter-Final predictions successfully locked!")
                    st.rerun()
                    
        with ko_tabs[3]:
            def get_ko_prev_qf(m_key):
                val = user_preds.get(m_key)
                if val in o_qf.get(m_key, ("","")): return val
                return f"W{m_key.split('_')[1]}"

            sf1_h, sf1_a = get_ko_prev_qf("Match_97"), get_ko_prev_qf("Match_98")
            sf2_h, sf2_a = get_ko_prev_qf("Match_99"), get_ko_prev_qf("Match_100")
            
            finals_keys = ["Match_101", "Match_102", "Match_103", "Match_104"]
            is_finals_locked = all(k in locked_keys_set for k in finals_keys)
            
            if is_finals_locked:
                st.markdown("<div class='lock-badge-banner'>🔒 Finals Selections Locked</div>", unsafe_allow_html=True)
            
            sf1_opts = ["Select Winner", sf1_h, sf1_a]
            curr_sf1 = user_preds.get("Match_101", "Select Winner")
            if str(curr_sf1) == "1": curr_sf1 = sf1_h
            elif str(curr_sf1) == "2": curr_sf1 = sf1_a
            idx_sf1 = sf1_opts.index(curr_sf1) if curr_sf1 in sf1_opts else 0
            user_preds["Match_101"] = st.selectbox("Semi Final 1 Winner", sf1_opts, index=idx_sf1, format_func=fmt_team, key="final_sf1_sel", disabled=is_finals_locked)
            
            sf2_opts = ["Select Winner", sf2_h, sf2_a]
            curr_sf2 = user_preds.get("Match_102", "Select Winner")
            if str(curr_sf2) == "1": curr_sf2 = sf2_h
            elif str(curr_sf2) == "2": curr_sf2 = sf2_a
            idx_sf2 = sf2_opts.index(curr_sf2) if curr_sf2 in sf2_opts else 0
            user_preds["Match_102"] = st.selectbox("Semi Final 2 Winner", sf2_opts, index=idx_sf2, format_func=fmt_team, key="final_sf2_sel", disabled=is_finals_locked)
            
            sf1_l = sf1_a if user_preds["Match_101"] == sf1_h else sf1_h
            sf2_l = sf2_a if user_preds["Match_102"] == sf2_h else sf2_h
            
            p3_opts = ["Select Winner", sf1_l, sf2_l]
            curr_p3 = user_preds.get("Match_103", "Select Winner")
            if str(curr_p3) == "1": curr_p3 = sf1_l
            elif str(curr_p3) == "2": curr_p3 = sf2_l
            idx_p3 = p3_opts.index(curr_p3) if curr_p3 in p3_opts else 0
            user_preds["Match_103"] = st.selectbox("🥉 3rd Place Winner Selection", p3_opts, index=idx_p3, format_func=fmt_team, key="final_p3_sel", disabled=is_finals_locked)
            
            f_opts = ["Select Winner", user_preds["Match_101"], user_preds["Match_102"]]
            curr_f = user_preds.get("Match_104", "Select Winner")
            if str(curr_f) == "1": curr_f = user_preds["Match_101"]
            elif str(curr_f) == "2": curr_f = user_preds["Match_102"]
            idx_f = f_opts.index(curr_f) if curr_f in f_opts else 0
            user_preds["Match_104"] = st.selectbox("🥇 Grand Champion Prediction", f_opts, index=idx_f, format_func=fmt_team, key="final_champ_sel", disabled=is_finals_locked)

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
                    st.rerun()

# --- 15. ADMINISTRATIVE CONTROL PANEL ---
elif app_tab == "🛠️ Admin Dashboard" and is_league_admin:
    st.header(f"🛠️ {selected_league_name} Admin Control Panel")
    actual = db_fetch_league_actual_results(active_league_id)
    admin_tabs = st.tabs(["Group Stage Results", "Knockout Progress Matches"])
    
    with admin_tabs[0]:
        st.subheader("📆 All Group Matches (Match Order)")
        
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
                        st.success(f"Match #{m_id} score locked and live!")
                        st.rerun()
                else:
                    st.markdown("<div style='color: #22c55e; font-weight: bold; padding-top: 10px;'>✅ Confirmed Locked</div>", unsafe_allow_html=True)
            with col_b2:
                if is_score_saved:
                    if st.button("🔓 Reset / Unlock Match Score", key=f"btn_unl_Match_{m_id}", use_container_width=True):
                        db_delete_league_actual_result(active_league_id, kh)
                        db_delete_league_actual_result(active_league_id, ka)
                        st.warning(f"Match #{m_id} score cleared from records.")
                        st.rerun()
            st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);' />", unsafe_allow_html=True)
            
    with admin_tabs[1]:
        # FIXED: Extract dynamic actual pairings from actual real-life group configurations
        actual_calc_bracket = resolve_bracket_teams(None, target_is_actual=True, actual_results_obj=actual)
        adm_r32_pairings = actual_calc_bracket["r32_pairings"]
        
        st.subheader("🌳 Round of 32 Matches (Populated via Real Group Standings)")
        for m_id, (h, a) in adm_r32_pairings.items():
            is_ko_saved = (m_id in actual["ko_winners"])
            
            actual["ko_winners"][m_id] = render_match_card(h, a, f"Winner: {m_id.replace('_', ' ')}", m_id, disabled=is_ko_saved, score_mode=False, scores_dict=actual["ko_winners"])
            
            col_ko1, col_ko2 = st.columns(2)
            with col_ko1:
                if not is_ko_saved:
                    if st.button("📢 Lock Knockout Winner", key=f"btn_ko_{m_id}", use_container_width=True):
                        flag_val = 1 if actual["ko_winners"][m_id] == h else (2 if actual["ko_winners"][m_id] == a else 0)
                        if flag_val > 0:
                            db_save_league_actual_result(active_league_id, m_id, flag_val)
                            st.success(f"{m_id.replace('_', ' ')} progression locked!")
                            st.rerun()
                else:
                    st.markdown("<div style='color: #22c55e; font-weight: bold; padding-top: 10px;'>✅ Confirmed Locked</div>", unsafe_allow_html=True)
            with col_ko2:
                if is_ko_saved:
                    if st.button("🔓 Reset / Unlock Winner", key=f"btn_unl_ko_{m_id}", use_container_width=True):
                        db_delete_league_actual_result(active_league_id, m_id)
                        st.warning(f"{m_id.replace('_', ' ')} status cleared.")
                        st.rerun()
            st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);' />", unsafe_allow_html=True)

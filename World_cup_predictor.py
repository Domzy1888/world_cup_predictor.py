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

    [data-testid="stExpander"], [data-testid="stTabContent"], .stTabs {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
    }

    /* Interactive Guided Tour Box Custom Styling */
    .tour-box {
        background: linear-gradient(135deg, #1e3a8a, #0f172a) !important;
        border: 2px solid #3b82f6 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
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
    # Direct extraction matching your exact secrets structure perfectly
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
    return FLAGS.get(name, name.upper())

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
        {"id": 39, "weight": 2, "home": "Uruguay", "away": "Cape Verde"},
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

# --- 6. DATABASE HELPER WRAPPERS ---
def db_fetch_user_predictions(user_id, league_id):
    res = supabase.table("predictions").select("match_key, score_value").eq("user_id", user_id).eq("league_id", league_id).execute()
    preds = {}
    if res.data:
        for row in res.data:
            preds[row["match_key"]] = row["score_value"]
    return preds

def db_save_prediction(user_id, league_id, match_key, value):
    supabase.table("predictions").upsert({
        "user_id": user_id,
        "league_id": league_id,
        "match_key": match_key,
        "score_value": value
    }, on_conflict="user_id,league_id,match_key").execute()

def db_fetch_locked_status(user_id, league_id):
    res = supabase.table("predictions").select("match_key, is_locked").eq("user_id", user_id).eq("league_id", league_id).execute()
    locked_keys = set()
    if res.data:
        for row in res.data:
            if row["is_locked"]:
                locked_keys.add(row["match_key"])
    return locked_keys

def db_lock_group_predictions(user_id, league_id, match_keys_list):
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
            elif key == "Match_finalists":
                pass
            else:
                results["ko_winners"][key] = val
    return results

def db_save_league_actual_result(league_id, match_key, value):
    supabase.table("actual_results").upsert({
        "league_id": league_id,
        "match_key": match_key,
        "score_value": value
    }, on_conflict="league_id,match_key").execute()

# --- 7. SESSION INITIALIZATION ---
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None
if "current_username" not in st.session_state:
    st.session_state.current_username = None
if "tour_step" not in st.session_state:
    st.session_state.tour_step = 0

# --- 8. UNIFIED INTEGRATED MATCH CARD RENDERER ---
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
        curr = scores_dict.get(key_prefix, home) if scores_dict else home
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

def calculate_user_points(user_id, league_id):
    user_preds = db_fetch_user_predictions(user_id, league_id)
    actual = db_fetch_league_actual_results(league_id)
    points = 0
    for g_name, matches in CHRONO_MATCHES.items():
        for match in matches:
            m_id = match["id"]
            kh, ka = f"Match_{m_id}_h", f"Match_{m_id}_a"
            p_h, p_a = user_preds.get(kh, None), user_preds.get(ka, None)
            a_h, a_a = actual["group"].get(kh, None), actual["group"].get(ka, None)
            if p_h is not None and p_a is not None and a_h is not None and a_a is not None:
                if int(p_h) == int(a_h) and int(p_a) == int(a_a): points += 3  
                elif (int(p_h) > int(p_a) and int(a_h) > int(a_a)) or (int(p_a) > int(p_h) and int(a_a) > int(a_h)) or (int(p_h) == int(p_a) and int(a_h) == int(a_a)): points += 1  
    for m in [f"Match {i}" for i in range(73, 89)]:
        if user_preds.get(m) == actual["ko_winners"].get(m): points += 3
    for m in [f"Match {i}" for i in range(89, 97)]:
        if user_preds.get(m) == actual["ko_winners"].get(m): points += 5
    for m in [f"Match {i}" for i in range(97, 101)]:
        if user_preds.get(m) == actual["ko_winners"].get(m): points += 10
    for m in ["Match 101", "Match 102"]:
        if user_preds.get(m) == actual["ko_winners"].get(m): points += 15
    if user_preds.get("Match 103") == actual.get("third_place"): points += 15
    if user_preds.get("Match 104") == actual["ko_winners"].get("Match 104"): points += 25
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
                    st.session_state.tour_step = 0
                    st.rerun()
                else: st.error("Invalid credentials.")
        with t2:
            reg_user = st.text_input("Choose Username")
            reg_pass = st.text_input("Choose Password", type="password")
            if st.button("Register Account", use_container_width=True):
                if reg_user.strip() == "" or reg_pass.strip() == "": st.error("Fields cannot be empty.")
                else:
                    dup_check = supabase.table("users").select("id").eq("username", reg_user).execute()
                    if dup_check.data:
                        st.error("Username already exists.")
                    else:
                        hashed_p = hash_password(reg_pass)
                        supabase.table("users").insert({"username": reg_user, "password_hash": hashed_p}).execute()
                        st.success("Registered successfully! Proceed to log in via the left tab.")
    st.stop()

c_uid = st.session_state.current_user_id
c_user = st.session_state.current_username

user_meta = supabase.table("users").select("tour_completed").eq("id", c_uid).execute().data[0]

# --- 11. ONE-TIME INTERACTIVE TOUR ENGINE (UPDATED FOR RESTRICTED LEAGUE LOGIC) ---
if not user_meta.get("tour_completed", False):
    tour_content = [
        {
            "title": "🛡️ Welcome! Step 1: Secure League Entry Required",
            "body": "Before you can see match fixtures or enter scores, you must be part of a league environment. Use the **Onboarding Gate** below to enter an admin invite code, or use a master passcode to build your own local station league!"
        },
        {
            "title": "📝 Step 2: Setting Score Selections",
            "body": "Once inside your league, navigate to **📝 Submit Predictions**. Use the interactive arrows to save your scores. The simulated group standings table will instantly adjust live on your screen!"
        },
        {
            "title": "🔒 Step 3: Finalizing & Locking Data",
            "body": "When you are completely happy with a group's scores, click **Finalize & Lock**. This safely saves your figures and prevents accidental edits before the real match kicks off."
        },
        {
            "title": "🏆 Step 4: Standings & Private Admins",
            "body": "Track your position in **🏆 Leaderboards**. If you created the league, you will also see a **🛠️ Admin Dashboard** tab. Saving real match outcomes there calculates scores *exclusively* for your league mates!"
        }
    ]
    current_step = st.session_state.tour_step
    st.markdown(f"""
        <div class="tour-box">
            <h3 style="margin-top:0px; color:#60a5fa !important;">{tour_content[current_step]['title']}</h3>
            <p style="font-size:1.05rem; line-height:1.5;">{tour_content[current_step]['body']}</p>
        </div>
    """, unsafe_allow_html=True)
    btn_col1, btn_col2 = st.columns([8, 2])
    with btn_col1:
        if current_step < len(tour_content) - 1:
            if st.button("👉 Next Tip", use_container_width=True):
                st.session_state.tour_step += 1
                st.rerun()
        else:
            if st.button("🎉 Complete Tour", use_container_width=True):
                supabase.table("users").update({"tour_completed": True}).eq("id", c_uid).execute()
                st.rerun()
    with btn_col2:
        if st.button("❌ Dismiss Guide", use_container_width=True):
            supabase.table("users").update({"tour_completed": True}).eq("id", c_uid).execute()
            st.rerun()
    st.markdown("<hr style='border-color:rgba(255,255,255,0.15); margin-bottom:20px;'>", unsafe_allow_html=True)

# Fetch user's registered leagues maps
user_leagues_list = db_fetch_user_leagues(c_uid)

# --- 12. STRICT LEAGUE LOCK CHECK ---
if not user_leagues_list:
    st.title("🛡️ Secure Onboarding")
    st.warning("Welcome! To proceed into the dashboard, you must first create or join a standalone league environment.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Join an Existing League")
        join_code_input = st.text_input("Enter Invite Code Provided By Your Admin")
        if st.button("🔑 Access League Pool", use_container_width=True):
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
        st.markdown("To prevent spam, league creation requires an authorized Master Passcode. If you don't have one, request it from your regional lead.")
        master_pass = st.text_input("Enter Master Creation Passcode", type="password")
        new_lg_name = st.text_input("Proposed League Name")
        new_lg_code = st.text_input("Create Custom Invite Code For Friends")
        
        if st.button("✨ Initialize Authorized League", use_container_width=True):
            if master_pass != "FIRE_CHIEF_2026":
                st.error("Invalid Master Creation Passcode. Unauthorized setup blocked.")
            elif new_lg_name.strip() == "" or new_lg_code.strip() == "":
                st.error("Fields cannot be left blank.")
            else:
                name_check = supabase.table("leagues").select("id").eq("name", new_lg_name).execute()
                code_check = supabase.table("leagues").select("id").eq("invite_code", new_lg_code).execute()
                if name_check.data or code_check.data:
                    st.error("League name or invite code has already been claimed.")
                else:
                    ins_res = supabase.table("leagues").insert({"name": new_lg_name, "invite_code": new_lg_code, "creator_id": c_uid}).execute()
                    if ins_res.data:
                        new_id = ins_res.data[0]["id"]
                        supabase.table("league_members").insert({"user_id": c_uid, "league_id": new_id}).execute()
                        st.success("Authorized League built smoothly! Refreshing space...")
                        st.rerun()
    st.stop()

# --- 13. APP NAVIGATION PANELS ---
col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.markdown(f"👥 Active Profile: **{c_user}**", unsafe_allow_html=True)
with col_nav2:
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.current_user_id = None
        st.session_state.current_username = None
        st.rerun()

# Clean up league mappings
leagues_dropdown_options = {lg["name"]: lg for lg in user_leagues_list}
selected_league_name = st.sidebar.selectbox("Current League Environment:", list(leagues_dropdown_options.keys()))
active_league_meta = leagues_dropdown_options[selected_league_name]
active_league_id = active_league_meta["id"]
is_league_admin = (active_league_meta["creator_id"] == c_uid)

# Navigation paths
main_tabs = ["🏆 Leaderboards", "📝 Submit Predictions", "🛡️ Create/Join a League"]
if is_league_admin: 
    main_tabs.append("🛠️ Admin Dashboard")
app_tab = st.sidebar.radio("Main Menu Navigation", main_tabs)

# --- 14. LEADERBOARD WORKSPACE ---
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
        df_leaderboard.index += 1
        st.dataframe(df_leaderboard, use_container_width=True)
    else:
        st.info("No competitor records found.")

# --- 15. CREATE / JOIN LEAGUE HUB ---
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
                    member_check = supabase.table("league_members").select("id").eq("user_id", c_uid).eq("league_id", t_id).execute()
                    if member_check.data:
                        st.warning("You are already a registered competitor in this league.")
                    else:
                        supabase.table("league_members").insert({"user_id": c_uid, "league_id": t_id}).execute()
                        st.success("Successfully registered into new pool context!")
                        st.rerun()
                else: st.error("Code not found.")
    with c2:
        st.subheader("Authorized Private League Creation")
        m_pass2 = st.text_input("Master Gatekeeper Passcode", type="password", key="m_pass2")
        l_name2 = st.text_input("League Name", key="l_name2")
        l_code2 = st.text_input("Invite Code Key", key="l_code2")
        if st.button("✨ Establish Additional Standalone League", use_container_width=True):
            if m_pass2 != "FIRE_CHIEF_2026":
                st.error("Unauthorized Master Passcode.")
            elif l_name2.strip() == "" or l_code2.strip() == "":
                st.error("Fields cannot be blank.")
            else:
                ins_res = supabase.table("leagues").insert({"name": l_name2, "invite_code": l_code2, "creator_id": c_uid}).execute()
                if ins_res.data:
                    new_id = ins_res.data[0]["id"]
                    supabase.table("league_members").insert({"user_id": c_uid, "league_id": new_id}).execute()
                    st.success("New standalone league provisioned completely!")
                    st.rerun()

# --- 16. USER PREDICTIONS DESK ---
elif app_tab == "📝 Submit Predictions":
    st.header(f"📝 Match Setup — {selected_league_name}")
    
    user_preds = db_fetch_user_predictions(c_uid, active_league_id)
    locked_keys_set = db_fetch_locked_status(c_uid, active_league_id)
    
    pred_sub_tabs = st.tabs(["📊 Group Matches Workspace", "🌳 Knockout Brackets"])
    
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
                st.markdown("<div style='color:#34d399; margin-bottom:15px; font-weight:bold; font-size:1.1rem; text-align:center;'>🔓 Changes Active</div>", unsafe_allow_html=True)
                
                # Wrap input cards inside an isolated form container to prevent auto-refreshing
                with st.form(key=f"form_{selected_group}", clear_on_submit=False):
                    for match in CHRONO_MATCHES[selected_group]:
                        user_preds = render_match_card(
                            home=match["home"], away=match["away"], label=f"Match #{match['id']}", 
                            key_prefix=f"Match_{match['id']}", disabled=is_group_locked, score_mode=True, scores_dict=user_preds
                        )
                    
                    # The single submission button handles database batching and locking simultaneously
                    if st.form_submit_button(f"🔒 Finalize & Lock {selected_group} Predictions", use_container_width=True):
                        for match in CHRONO_MATCHES[selected_group]:
                            db_save_prediction(c_uid, active_league_id, f"Match_{match['id']}_h", user_preds[f"Match_{match['id']}_h"])
                            db_save_prediction(c_uid, active_league_id, f"Match_{match['id']}_a", user_preds[f"Match_{match['id']}_a"])
                        db_lock_group_predictions(c_uid, active_league_id, group_keys)
                        st.success(f"{selected_group} locked successfully!")
                        st.rerun()
                
        with col_table:
            st.subheader("Simulated Group Table")
            u_results, _ = run_standings_engine(user_preds)
            df_display = u_results[selected_group][["Team", "Pts", "GD", "GF"]].copy()
            df_display["Team"] = df_display["Team"].apply(fmt_team)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
                
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
                db_save_prediction(c_uid, active_league_id, m_id, user_preds[m_id])
        with ko_tabs[1]:
            o_r16 = {
                "Match 89": (user_preds.get("Match 74", "W74"), user_preds.get("Match 77", "W77")), "Match 90": (user_preds.get("Match 73", "W73"), user_preds.get("Match 75", "W75")),
                "Match 93": (user_preds.get("Match 83", "W83"), user_preds.get("Match 84", "W84")), "Match 94": (user_preds.get("Match 81", "W81"), user_preds.get("Match 82", "W82")),
                "Match 91": (user_preds.get("Match 76", "W76"), user_preds.get("Match 78", "W78")), "Match 92": (user_preds.get("Match 79", "W79"), user_preds.get("Match 80", "W80")),
                "Match 95": (user_preds.get("Match 86", "W86"), user_preds.get("Match 88", "W88")), "Match 96": (user_preds.get("Match 85", "W85"), user_preds.get("Match 87", "W87"))
            }
            for m_id, (h, a) in o_r16.items():
                user_preds[m_id] = render_match_card(h, a, m_id, m_id, disabled=False, score_mode=False, scores_dict=user_preds)
                db_save_prediction(c_uid, active_league_id, m_id, user_preds[m_id])
        with ko_tabs[2]:
            o_qf = {
                "Match 97": (user_preds.get("Match 89", "W89"), user_preds.get("Match 90", "W90")), "Match 98": (user_preds.get("Match 93", "W93"), user_preds.get("Match 94", "W94")),
                "Match 99": (user_preds.get("Match 91", "W91"), user_preds.get("Match 92", "W92")), "Match 100": (user_preds.get("Match 95", "W95"), user_preds.get("Match 100", "W100"))
            }
            for m_id, (h, a) in o_qf.items():
                user_preds[m_id] = render_match_card(h, a, m_id, m_id, disabled=False, score_mode=False, scores_dict=user_preds)
                db_save_prediction(c_uid, active_league_id, m_id, user_preds[m_id])
        with ko_tabs[3]:
            sf1_h, sf1_a = user_preds.get("Match 97", "W97"), user_preds.get("Match 98", "W98")
            sf2_h, sf2_a = user_preds.get("Match 99", "W99"), user_preds.get("Match 100", "W100")
            
            sf1_opts = [sf1_h, sf1_a]
            user_preds["Match 101"] = st.selectbox("Semi Final 1 Winner", sf1_opts, index=sf1_opts.index(user_preds.get("Match 101", sf1_h)) if user_preds.get("Match 101", sf1_h) in sf1_opts else 0, format_func=fmt_team)
            db_save_prediction(c_uid, active_league_id, "Match 101", user_preds["Match 101"])
            
            sf2_opts = [sf2_h, sf2_a]
            user_preds["Match 102"] = st.selectbox("Semi Final 2 Winner", sf2_opts, index=sf2_opts.index(user_preds.get("Match 102", sf2_h)) if user_preds.get("Match 102", sf2_h) in sf2_opts else 0, format_func=fmt_team)
            db_save_prediction(c_uid, active_league_id, "Match 102", user_preds["Match 102"])
            
            sf1_l = sf1_a if user_preds["Match 101"] == sf1_h else sf1_h
            sf2_l = sf2_a if user_preds["Match 102"] == sf2_h else sf2_h
            
            p3_opts = [sf1_l, sf2_l]
            user_preds["Match 103"] = st.selectbox("🥉 3rd Place Winner Selection", p3_opts, index=p3_opts.index(user_preds.get("Match 103", sf1_l)) if user_preds.get("Match 103", sf1_l) in p3_opts else 0, format_func=fmt_team)
            db_save_prediction(c_uid, active_league_id, "Match 103", user_preds["Match 103"])
            
            f_opts = [user_preds["Match 101"], user_preds["Match 102"]]
            user_preds["Match 104"] = st.selectbox("🥇 Grand Champion Prediction", f_opts, index=f_opts.index(user_preds.get("Match 104", f_opts[0])) if user_preds.get("Match 104", f_opts[0]) in f_opts else 0, format_func=fmt_team)
            db_save_prediction(c_uid, active_league_id, "Match 104", user_preds["Match 104"])

# --- 17. ADMINISTRATIVE CONTROL PANEL (ISOLATED BY LEAGUE OWNER) ---
elif app_tab == "🛠️ Admin Dashboard" and is_league_admin:
    st.header(f"🛠️ {selected_league_name} Admin Control Panel")
    st.markdown("Scores saved here instantly update points *exclusively* for this league's players.")
    
    actual = db_fetch_league_actual_results(active_league_id)
    admin_tabs = st.tabs(["Group Stage Results", "Knockout Progress Matches"])
    
    with admin_tabs[0]:
        selected_adm_group = st.selectbox("Verify Target Group Pool", list(GROUPS.keys()))
        for match in CHRONO_MATCHES[selected_adm_group]:
            actual["group"] = render_match_card(
                home=match["home"], away=match["away"], label=f"Match #{match['id']} Official Score",
                key_prefix=f"Match_{match['id']}", disabled=False, score_mode=True, scores_dict=actual["group"]
            )
            if st.button("📢 Save Match Score", key=f"btn_pub_Match_{match['id']}", use_container_width=True):
                db_save_league_actual_result(active_league_id, f"Match_{match['id']}_h", actual["group"][f"Match_{match['id']}_h"])
                db_save_league_actual_result(active_league_id, f"Match_{match['id']}_a", actual["group"][f"Match_{match['id']}_a"])
                st.success("Score updated smoothly inside league storage data!")
            
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
            if st.button("📢 Lock Knockout Winner", key=f"btn_ko_{m_id}", use_container_width=True):
                db_save_league_actual_result(active_league_id, m_id, actual["ko_winners"][m_id])
                st.success(f"{m_id} progression locked!")

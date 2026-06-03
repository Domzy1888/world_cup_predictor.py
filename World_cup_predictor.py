import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import uuid
import re
from supabase import create_client, Client

# --- 1. CONFIGURATION AND CONSTANTS ---
st.set_page_config(page_title="🏆 Super League Predictor Dashboard", layout="wide", initial_sidebar_state="expanded")

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

GROUPS = {
    "Group A": ["USA", "Mexico", "Canada", "Guatemala"],
    "Group B": ["England", "France", "Italy", "Wales"],
    "Group C": ["Argentina", "Brazil", "Colombia", "Chile"],
    "Group D": ["Germany", "Spain", "Netherlands", "Poland"],
    "Group E": ["Belgium", "Portugal", "Croatia", "Scotland"],
    "Group F": ["Morocco", "Senegal", "Egypt", "Nigeria"],
    "Group G": ["Japan", "South Korea", "Australia", "Iran"],
    "Group H": ["Uruguay", "Ecuador", "Peru", "Venezuela"],
    "Group I": ["Ghana", "Ivory Coast", "Cameroon", "Algeria"],
    "Group J": ["Saudi Arabia", "UAE", "Qatar", "Oman"],
    "Group K": ["Switzerland", "Austria", "Denmark", "Norway"],
    "Group L": ["Ukraine", "Sweden", "Turkey", "Greece"]
}

TEAM_FLAGS = {
    "USA": "🇺🇸", "Mexico": "🇲🇽", "Canada": "🇨🇦", "Guatemala": "🇬🇹",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "France": "🇫🇷", "Italy": "🇮🇹", "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
    "Argentina": "🇦🇷", "Brazil": "🇧🇷", "Colombia": "🇨🇴", "Chile": "🇨🇱",
    "Germany": "🇩🇪", "Spain": "🇪🇸", "Netherlands": "🇳🇱", "Poland": "🇵🇱",
    "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Croatia": "🇭🇷", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "Morocco": "🇲🇦", "Senegal": "🇸🇳", "Egypt": "🇪🇬", "Nigeria": "🇳🇬",
    "Japan": "🇯🇵", "South Korea": "🇰🇷", "Australia": "🇦🇺", "Iran": "🇮🇷",
    "Uruguay": "🇺🇾", "Ecuador": "🇪🇨", "Peru": "🇵🇪", "Venezuela": "🇻🇪",
    "Ghana": "🇬🇭", "Ivory Coast": "🇨🇮", "Cameroon": "🇨🇲", "Algeria": "🇩🇿",
    "Saudi Arabia": "🇸🇦", "UAE": "🇦🇪", "Qatar": "🇶🇦", "Oman": "🇴🇲",
    "Switzerland": "🇨🇭", "Austria": "🇦🇹", "Denmark": "🇩🇰", "Norway": "🇳🇴",
    "Ukraine": "🇺🇦", "Sweden": "🇸🇪", "Turkey": "🇹🇷", "Greece": "🇬🇷"
}

CHRONO_MATCHES = {}
match_id_counter = 1
for g_name, teams in GROUPS.items():
    g_matches = []
    for i in range(4):
        for j in range(i + 1, 4):
            g_matches.append({"id": match_id_counter, "home": teams[i], "away": teams[j]})
            match_id_counter += 1
    CHRONO_MATCHES[g_name] = g_matches

# --- 2. CORE DATABASE UTILITIES ---
def db_hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def db_verify_user(username, password):
    res = supabase.table("users").select("id, password_hash").eq("username", username.strip()).execute()
    if res.data and len(res.data) > 0:
        stored = res.data[0]["password_hash"]
        if stored == db_hash_password(password):
            return res.data[0]["id"]
    return None

def db_register_user(username, password):
    u_clean = username.strip()
    if not u_clean or len(password) < 4:
        return False, "Invalid validation parameters."
    exist = supabase.table("users").select("id").eq("username", u_clean).execute()
    if exist.data and len(exist.data) > 0:
        return False, "Username matches an active account footprint."
    try:
        supabase.table("users").insert({"username": u_clean, "password_hash": db_hash_password(password)}).execute()
        return True, "Registration successful."
    except Exception as e:
        return False, f"System error writing record: {str(e)}"

def db_create_league(name, passcode, owner_id):
    n_clean = name.strip()
    p_clean = passcode.strip()
    if not n_clean or not p_clean:
        return False, "League parameters cannot be empty entries."
    try:
        res = supabase.table("leagues").insert({"name": n_clean, "passcode": p_clean, "creator_id": owner_id}).execute()
        if res.data and len(res.data) > 0:
            l_id = res.data[0]["id"]
            supabase.table("league_members").insert({"league_id": l_id, "user_id": owner_id}).execute()
            return True, l_id
        return False, "Failed creation instance sequence."
    except Exception as e:
        return False, str(e)

def db_join_league(name, passcode, user_id):
    res = supabase.table("leagues").select("id, passcode").eq("name", name.strip()).execute()
    if not res.data:
        return False, "League definition not uncovered in records."
    rec = res.data[0]
    if rec["passcode"] != passcode.strip():
        return False, "Passcode misalignment caught."
    l_id = rec["id"]
    m_check = supabase.table("league_members").select("id").eq("league_id", l_id).eq("user_id", user_id).execute()
    if m_check.data:
        return True, l_id
    supabase.table("league_members").insert({"league_id": l_id, "user_id": user_id}).execute()
    return True, l_id

def db_get_user_leagues(user_id):
    res = supabase.table("league_members").select("league_id, leagues(name)").eq("user_id", user_id).execute()
    out = []
    if res.data:
        for item in res.data:
            if item.get("leagues"):
                out.append({"id": item["league_id"], "name": item["leagues"]["name"]})
    return out

def db_fetch_user_predictions(user_id, league_id):
    res = supabase.table("predictions").select("match_key, prediction_value").eq("user_id", user_id).eq("league_id", league_id).execute()
    out = {}
    if res.data:
        for r in res.data:
            out[r["match_key"]] = r["prediction_value"]
    return out

def db_save_prediction(user_id, league_id, match_key, val):
    if val is None or val == "":
        return
    supabase.table("predictions").upsert({
        "user_id": user_id,
        "league_id": league_id,
        "match_key": match_key,
        "prediction_value": str(val)
    }, on_conflict="user_id,league_id,match_key").execute()

def db_fetch_locked_status(user_id, league_id):
    res = supabase.table("locked_predictions").select("match_key").eq("user_id", user_id).eq("league_id", league_id).execute()
    if res.data:
        return set(r["match_key"] for r in res.data)
    return set()

def db_lock_group_predictions(user_id, league_id, keys_list):
    arr = [{"user_id": user_id, "league_id": league_id, "match_key": k} for k in keys_list]
    if arr:
        supabase.table("locked_predictions").upsert(arr, on_conflict="user_id,league_id,match_key").execute()

def db_fetch_league_leaderboard(league_id):
    m_res = supabase.table("league_members").select("user_id, users(username)").eq("league_id", league_id).execute()
    if not m_res.data:
        return []
    users_map = {}
    for item in m_res.data:
        if item.get("users"):
            users_map[item["user_id"]] = item["users"]["username"]
            
    p_res = supabase.table("predictions").select("user_id, match_key, prediction_value").eq("league_id", league_id).execute()
    preds_by_user = {uid: {} for uid in users_map.keys()}
    if p_res.data:
        for r in p_res.data:
            uid = r["user_id"]
            if uid in preds_by_user:
                preds_by_user[uid][r["match_key"]] = r["prediction_value"]
                
    actual_res = supabase.table("predictions").select("match_key, prediction_value").eq("user_id", "00000000-0000-0000-0000-000000000000").eq("league_id", "00000000-0000-0000-0000-000000000000").execute()
    master_dict = {}
    if actual_res.data:
        for r in actual_res.data:
            master_dict[r["match_key"]] = r["prediction_value"]
            
    leaderboard = []
    for uid, u_name in users_map.items():
        score = calculate_user_points(preds_by_user[uid], master_dict)
        leaderboard.append({"User": u_name, "Points": score})
        
    df = pd.DataFrame(leaderboard)
    if df.empty:
        return pd.DataFrame(columns=["User", "Points"])
    return df.sort_values(by="Points", ascending=False)

# --- 3. POINTS AND SCORING ENGINE ---
def calculate_user_points(user_preds, master_preds):
    pts = 0
    # Group stage assessment logic
    for g_name, matches in CHRONO_MATCHES.items():
        for m in matches:
            mid = m["id"]
            kh, ka = f"Match_{mid}_h", f"Match_{mid}_a"
            
            u_h, u_a = user_preds.get(kh), user_preds.get(ka)
            m_h, m_a = master_preds.get(kh), master_preds.get(ka)
            
            if u_h is not None and u_a is not None and m_h is not None and m_a is not None:
                try:
                    uh_i, ua_i = int(u_h), int(u_a)
                    mh_i, ma_i = int(m_h), int(m_a)
                    
                    if uh_i == mh_i and ua_i == ma_i:
                        pts += 3
                    else:
                        u_sign = np.sign(uh_i - ua_i)
                        m_sign = np.sign(mh_i - ma_i)
                        if u_sign == m_sign:
                            pts += 1
                except:
                    pass
                    
    # Knockout structures checks
    ko_keys = [f"Match {i}" for i in range(73, 105)]
    for kok in ko_keys:
        u_v = user_preds.get(kok)
        m_v = master_preds.get(kok)
        if u_v and m_v and u_v == m_v and not u_v.startswith("W") and u_v != "Select Winner":
            pts += 5
    return pts

# --- 4. TOURNAMENT SIMULATION ENGINE ---
def run_standings_engine(preds_dict):
    results = {}
    third_places = []
    
    for g_name, teams in GROUPS.items():
        stats = {t: {"Team": t, "Pts": 0, "GD": 0, "GF": 0} for t in teams}
        for m in CHRONO_MATCHES[g_name]:
            mid = m["id"]
            kh = f"Match_{mid}_h"
            ka = f"Match_{mid}_a"
            
            h_val = preds_dict.get(kh, 0)
            a_val = preds_dict.get(ka, 0)
            
            try: h_score = int(h_val)
            except: h_score = 0
            try: a_score = int(a_val)
            except: a_score = 0
            
            stats[m["home"]]["GF"] += h_score
            stats[m["away"]]["GF"] += a_score
            stats[m["home"]]["GD"] += (h_score - a_score)
            stats[m["away"]]["GD"] += (a_score - h_score)
            
            if h_score > a_score:
                stats[m["home"]]["Pts"] += 3
            elif a_score > h_score:
                stats[m["away"]]["Pts"] += 3
            else:
                stats[m["home"]]["Pts"] += 1
                stats[m["away"]]["Pts"] += 1
                
        df = pd.DataFrame(stats.values())
        df = df.sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
        results[g_name] = df
        
        if len(df) >= 3:
            t3 = df.iloc[2].copy()
            t3["Group"] = g_name
            third_places.append(t3)
            
    df_3rd = pd.DataFrame(third_places)
    if not df_3rd.empty:
        df_3rd = df_3rd.sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
        wildcards = list(df_3rd["Team"].head(8))
        while len(wildcards) < 8:
            wildcards.append(f"Wildcard {len(wildcards)+1}")
    else:
        wildcards = [f"Wildcard {i}" for i in range(1, 9)]
        
    return results, wildcards

# --- 5. INTERFACE DESIGN SYSTEM (CSS) ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important;
        color: #f8fafc !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    div.stButton > button {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 22px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.25s ease;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5);
    }
    .lock-badge-banner {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid #ef4444;
        color: #fca5a5;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 6. GLOBAL FORMATTING ROUTINES ---
def fmt_team(name):
    if not name:
        return "TBD"
    return f"{TEAM_FLAGS.get(name, '🏳️')} {name}"

# --- 7. SESSION MANAGEMENT STATE CREATION ---
if "user_id" not in st.session_state: st.session_state.user_id = None
if "username" not in st.session_state: st.session_state.username = None
if "active_league_id" not in st.session_state: st.session_state.active_league_id = None
if "active_league_name" not in st.session_state: st.session_state.active_league_name = None

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
        curr = scores_dict.get(key_prefix, "Select Winner") if scores_dict else "Select Winner"
        
        if curr not in options:
            idx_val = 0
        else:
            idx_val = options.index(curr)
            
        val_select = st.selectbox("Winner Selection", options, index=idx_val, format_func=fmt_team, key=f"sel_{key_prefix}", label_visibility="collapsed", disabled=disabled)
        if scores_dict is not None:
            scores_dict[key_prefix] = val_select
        return val_select

# --- 9. SIDEBAR WORKSPACE AND USER STATES ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#818cf8;'>🏟️ Stadium Control</h2>", unsafe_allow_html=True)
    if st.session_state.user_id:
        st.markdown(f"<div style='text-align:center; margin-bottom:15px;'>Logged in as: <b>{st.session_state.username}</b></div>", unsafe_allow_html=True)
        leagues = db_get_user_leagues(st.session_state.user_id)
        
        if leagues:
            l_names = [lg["name"] for lg in leagues]
            if st.session_state.active_league_name in l_names:
                sel_idx = l_names.index(st.session_state.active_league_name)
            else:
                sel_idx = 0
                st.session_state.active_league_id = leagues[0]["id"]
                st.session_state.active_league_name = leagues[0]["name"]
                
            chosen_l_name = st.selectbox("Active League Workspace", l_names, index=sel_idx)
            for lg in leagues:
                if lg["name"] == chosen_l_name:
                    st.session_state.active_league_id = lg["id"]
                    st.session_state.active_league_name = lg["name"]
        else:
            st.warning("You aren't associated with a league system.")
            
        if st.button("🚪 Leave Session", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.active_league_id = None
            st.session_state.active_league_name = None
            st.grid()
            st.rerun()
    else:
        st.info("Authentication demanded on sidebar matrix layout.")

# --- 10. AUTHENTICATION HUB ROUTINE ---
if not st.session_state.user_id:
    st.title("🏆 Super League Predictor Suite")
    st.subheader("System Secure Matrix Validation")
    
    auth_tabs = st.tabs(["🔐 Secure Login Portal", "🎟️ Account Provisioning"])
    
    with auth_tabs[0]:
        with st.form("login_form"):
            li_user = st.text_input("Username").strip()
            li_pass = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Enter Predictor System")
            if submitted:
                uid = db_verify_user(li_user, li_pass)
                if uid:
                    st.session_state.user_id = uid
                    st.session_state.username = li_user
                    st.success(f"Welcome back, operator {li_user}!")
                    st.rerun()
                else:
                    st.error("Invalid account signatures or keys provided.")
                    
    with auth_tabs[1]:
        with st.form("reg_form"):
            rg_user = st.text_input("Desired Username").strip()
            rg_pass = st.text_input("Secure Passkey Profile", type="password")
            submitted = st.form_submit_button("Deploy Profile Credentials")
            if submitted:
                ok, msg = db_register_user(rg_user, rg_pass)
                if ok: st.success(msg)
                else: st.error(msg)
    st.stop()

# --- 11. LEAGUE MANAGEMENT PANEL ROUTINES ---
if not st.session_state.active_league_id:
    st.title("🛡️ League Generation Framework")
    st.markdown("Your login is confirmed, but an operational room binding is required to proceed.")
    
    l_tabs = st.tabs(["✨ Generate New League", "🔑 Bind Pre-Existing League Key"])
    
    with l_tabs[0]:
        with st.form("create_l_form"):
            nl_name = st.text_input("League Nomenclature Signature")
            nl_pass = st.text_input("Access Security Token", type="password")
            if st.form_submit_button("Instantiate League Ecosystem"):
                ok, res = db_create_league(nl_name, nl_pass, st.session_state.user_id)
                if ok:
                    st.session_state.active_league_id = res
                    st.session_state.active_league_name = nl_name.strip()
                    st.success("Ecosystem bound completely.")
                    st.rerun()
                else:
                    st.error(f"Ecosystem setup fault detected: {res}")
                    
    with l_tabs[1]:
        with st.form("join_l_form"):
            jl_name = st.text_input("Target League Nomenclature Signature")
            jl_pass = st.text_input("Access Token Validation Profile", type="password")
            if st.form_submit_button("Synchronize Binding"):
                ok, res = db_join_league(jl_name, jl_pass, st.session_state.user_id)
                if ok:
                    st.session_state.active_league_id = res
                    st.session_state.active_league_name = jl_name.strip()
                    st.success("Binding verified safely.")
                    st.rerun()
                else:
                    st.error(f"Ecosystem mismatch mapping error: {res}")
    st.stop()

# --- 12. DESKTOP WORKSPACE LAYOUT SECTIONS ---
c_uid = st.session_state.user_id
active_league_id = st.session_state.active_league_id
selected_league_name = st.session_state.active_league_name

app_tab = st.radio(
    "Ecosystem Navigation Array",
    ["📊 League Arena Leaderboard", "📝 Submit Predictions", "⚙️ Admin Controls Engine"],
    horizontal=True, label_visibility="collapsed"
)

# --- 13. MASTER LEAGUE ARENA LEADERS PANEL ---
if app_tab == "📊 League Arena Leaderboard":
    st.header(f"📊 Live Standings Arena — {selected_league_name}")
    ld_df = db_fetch_league_leaderboard(active_league_id)
    if not ld_df.empty:
        st.dataframe(ld_df, use_container_width=True, hide_index=True)
    else:
        st.info("No active matrix metrics compiled for this league group yet.")

# --- 16. USER PREDICTIONS DESK (FORM BATCHING GENERATION) ---
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
                
                # Render cards read-only without form wrapper if group is locked
                for match in CHRONO_MATCHES[selected_group]:
                    user_preds = render_match_card(
                        home=match["home"], away=match["away"], label=f"Match #{match['id']}", 
                        key_prefix=f"Match_{match['id']}", disabled=True, score_mode=True, scores_dict=user_preds
                    )
            else:
                st.markdown("<div style='color:#34d399; margin-bottom:15px; font-weight:bold; font-size:1.1rem; text-align:center;'>🔓 Changes Active (Batch Saving Mode)</div>", unsafe_allow_html=True)
                
                # Isolate input changes within a form to prevent live reruns on every single tap
                with st.form(key=f"form_{selected_group}"):
                    for match in CHRONO_MATCHES[selected_group]:
                        user_preds = render_match_card(
                            home=match["home"], away=match["away"], label=f"Match #{match['id']}", 
                            key_prefix=f"Match_{match['id']}", disabled=False, score_mode=True, scores_dict=user_preds
                        )
                    
                    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                    submit_scores = st.form_submit_button("💾 Save & Sync Group Scores")
                    
                    if submit_scores:
                        # Securely batch save all scores to Supabase at once
                        for match in CHRONO_MATCHES[selected_group]:
                            db_save_prediction(c_uid, active_league_id, f"Match_{match['id']}_h", user_preds[f"Match_{match['id']}_h"])
                            db_save_prediction(c_uid, active_league_id, f"Match_{match['id']}_a", user_preds[f"Match_{match['id']}_a"])
                        st.success("Group scores securely synchronized into league cloud data!")
                        st.rerun()
            
            # Lock button is outside the form container to avoid mixing state submissions
            if not is_group_locked:
                st.markdown("<hr style='border-color:rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)
                if st.button(f"🔒 Finalize & Permanently Lock {selected_group}", use_container_width=True):
                    db_lock_group_predictions(c_uid, active_league_id, group_keys)
                    st.success(f"{selected_group} predictions locked securely!")
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
            st.subheader("Round of 32 Predictions")
            for m_id, (h, a) in o_r32.items():
                chosen = render_match_card(h, a, m_id, m_id, disabled=False, score_mode=False, scores_dict=user_preds)
                # Ensure placeholder strings are ignored so they don't hit the database
                if chosen and chosen != "Select Winner" and not chosen.startswith("1st ") and not chosen.startswith("2nd ") and not chosen.startswith("Wildcard "):
                    db_save_prediction(c_uid, active_league_id, m_id, chosen)

        with ko_tabs[1]:
            st.subheader("Round of 16 Predictions")
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
                chosen = render_match_card(h, a, m_id, m_id, disabled=False, score_mode=False, scores_dict=user_preds)
                if chosen and chosen != "Select Winner" and not chosen.startswith("W"):
                    db_save_prediction(c_uid, active_league_id, m_id, chosen)

        with ko_tabs[2]:
            st.subheader("Quarter-Finals Predictions")
            o_qf = {
                "Match 97": (user_preds.get("Match 89", "W89"), user_preds.get("Match 90", "W90")), 
                "Match 98": (user_preds.get("Match 93", "W93"), user_preds.get("Match 94", "W94")),
                "Match 99": (user_preds.get("Match 91", "W91"), user_preds.get("Match 92", "W92")), 
                "Match 100": (user_preds.get("Match 95", "W95"), user_preds.get("Match 96", "W96"))
            }
            for m_id, (h, a) in o_qf.items():
                chosen = render_match_card(h, a, m_id, m_id, disabled=False, score_mode=False, scores_dict=user_preds)
                if chosen and chosen != "Select Winner" and not chosen.startswith("W"):
                    db_save_prediction(c_uid, active_league_id, m_id, chosen)

        with ko_tabs[3]:
            st.subheader("Finals Predictions")
            sf1_h, sf1_a = user_preds.get("Match 97", "W97"), user_preds.get("Match 98", "W98")
            sf2_h, sf2_a = user_preds.get("Match 99", "W99"), user_preds.get("Match 100", "W100")
            
            sf1_opts = ["Select Winner", sf1_h, sf1_a]
            curr_sf1 = user_preds.get("Match 101", "Select Winner")
            idx_sf1 = sf1_opts.index(curr_sf1) if curr_sf1 in sf1_opts else 0
            sf1_winner = st.selectbox("Semi Final 1 Winner", sf1_opts, index=idx_sf1, format_func=fmt_team, key="sel_m101")
            if sf1_winner != "Select Winner" and not sf1_winner.startswith("W"):
                db_save_prediction(c_uid, active_league_id, "Match 101", sf1_winner)
                user_preds["Match 101"] = sf1_winner
            
            sf2_opts = ["Select Winner", sf2_h, sf2_a]
            curr_sf2 = user_preds.get("Match 102", "Select Winner")
            idx_sf2 = sf2_opts.index(curr_sf2) if curr_sf2 in sf2_opts else 0
            sf2_winner = st.selectbox("Semi Final 2 Winner", sf2_opts, index=idx_sf2, format_func=fmt_team, key="sel_m102")
            if sf2_winner != "Select Winner" and not sf2_winner.startswith("W"):
                db_save_prediction(c_uid, active_league_id, "Match 102", sf2_winner)
                user_preds["Match 102"] = sf2_winner
            
            sf1_l = sf1_a if user_preds.get("Match 101") == sf1_h else sf1_h
            sf2_l = sf2_a if user_preds.get("Match 102") == sf2_h else sf2_h
            
            p3_opts = ["Select Winner", sf1_l, sf2_l]
            curr_p3 = user_preds.get("Match 103", "Select Winner")
            idx_p3 = p3_opts.index(curr_p3) if curr_p3 in p3_opts else 0
            p3_winner = st.selectbox("🥉 3rd Place Winner Selection", p3_opts, index=idx_p3, format_func=fmt_team, key="sel_m103")
            if p3_winner != "Select Winner" and not p3_winner.startswith("W"):
                db_save_prediction(c_uid, active_league_id, "Match 103", p3_winner)
                user_preds["Match 103"] = p3_winner
            
            f_opts = ["Select Winner", user_preds.get("Match 101", "W101"), user_preds.get("Match 102", "W102")]
            curr_f = user_preds.get("Match 104", "Select Winner")
            idx_f = f_opts.index(curr_f) if curr_f in f_opts else 0
            f_winner = st.selectbox("🥇 Grand Champion Prediction", f_opts, index=idx_f, format_func=fmt_team, key="sel_m104")
            if f_winner != "Select Winner" and not f_winner.startswith("W"):
                db_save_prediction(c_uid, active_league_id, "Match 104", f_winner)
                user_preds["Match 104"] = f_winner

# --- 17. ADMIN ENGINE HUB SYSTEM PANEL ---
elif app_tab == "⚙️ Admin Controls Engine":
    st.header("⚙️ System Administration Hub")
    
    is_admin = False
    chk = supabase.table("leagues").select("creator_id").eq("id", active_league_id).execute()
    if chk.data and chk.data[0]["creator_id"] == c_uid:
        is_admin = True
        
    if not is_admin:
        st.error("Access restriction. Admin keys not assigned to current terminal context.")
    else:
        st.markdown(f"Authorized deployment session active for <b>{st.session_state.username}</b>.", unsafe_allow_html=True)
        
        adm_user_preds = db_fetch_user_predictions("00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000")
        
        ad_tabs = st.tabs(["📊 Group Results Board", "🌳 Knockout Matches Sync"])
        
        with ad_tabs[0]:
            ad_group = st.selectbox("Select Target Admin Pool", list(GROUPS.keys()), key="adm_g_sel")
            
            with st.form(key=f"adm_form_{ad_group}"):
                for match in CHRONO_MATCHES[ad_group]:
                    adm_user_preds = render_match_card(
                        home=match["home"], away=match["away"], label=f"Official Match #{match['id']}", 
                        key_prefix=f"Match_{match['id']}", disabled=False, score_mode=True, scores_dict=adm_user_preds
                    )
                
                if st.form_submit_button("📢 Publish Official Group Results"):
                    for match in CHRONO_MATCHES[ad_group]:
                        db_save_prediction("00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", f"Match_{match['id']}_h", adm_user_preds[f"Match_{match['id']}_h"])
                        db_save_prediction("00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", f"Match_{match['id']}_a", adm_user_preds[f"Match_{match['id']}_a"])
                    st.success("Official Master scores saved safely!")
                    st.rerun()
                    
        with ad_tabs[1]:
            st.subheader("Official Master Knockout Progression Assignment")
            a_results, a_wildcards = run_standings_engine(adm_user_preds)
            
            def get_adm_1st(g): return a_results[g].iloc[0]["Team"] if g in a_results and not a_results[g].empty else f"1st {g}"
            def get_adm_2nd(g): return a_results[g].iloc[1]["Team"] if g in a_results and not a_results[g].empty else f"2nd {g}"

            adm_o_r32 = {
                "Match 73": (get_adm_1st("Group A"), a_wildcards[4]), "Match 74": (get_adm_1st("Group E"), a_wildcards[0]),
                "Match 75": (get_adm_1st("Group F"), get_adm_2nd("Group C")), "Match 76": (get_adm_1st("Group C"), get_adm_2nd("Group F")),
                "Match 77": (get_adm_1st("Group I"), a_wildcards[1]), "Match 78": (get_adm_2nd("Group E"), get_adm_2nd("Group I")),
                "Match 79": (get_adm_1st("Group B"), a_wildcards[6]), "Match 80": (get_adm_1st("Group L"), a_wildcards[5]),
                "Match 81": (get_adm_1st("Group D"), a_wildcards[2]), "Match 82": (get_adm_1st("Group G"), a_wildcards[3]),
                "Match 83": (get_adm_2nd("Group K"), get_adm_2nd("Group L")), "Match 84": (get_adm_1st("Group H"), get_adm_2nd("Group J")),
                "Match 85": (get_adm_2nd("Group A"), get_adm_2nd("Group B")), "Match 86": (get_adm_1st("Group J"), get_adm_2nd("Group H")),
                "Match 87": (get_adm_1st("Group K"), a_wildcards[7]), "Match 88": (get_adm_2nd("Group D"), get_adm_2nd("Group G"))
            }
            
            adm_ko_tabs = st.tabs(["R32", "R16", "QF", "Finals"])
            
            with adm_ko_tabs[0]:
                for m_id, (h, a) in adm_o_r32.items():
                    chosen = render_match_card(h, a, m_id, m_id, disabled=False, score_mode=False, scores_dict=adm_user_preds)
                    if chosen and chosen != "Select Winner" and not chosen.startswith("1st ") and not chosen.startswith("2nd ") and not chosen.startswith("Wildcard "):
                        db_save_prediction("00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", m_id, chosen)

            with adm_ko_tabs[1]:
                adm_o_r16 = {
                    "Match 89": (adm_user_preds.get("Match 74", "W74"), adm_user_preds.get("Match 77", "W77")), 
                    "Match 90": (adm_user_preds.get("Match 73", "W73"), adm_user_preds.get("Match 75", "W75")),
                    "Match 93": (adm_user_preds.get("Match 83", "W83"), adm_user_preds.get("Match 84", "W84")), 
                    "Match 94": (adm_user_preds.get("Match 81", "W81"), adm_user_preds.get("Match 82", "W82")),
                    "Match 91": (adm_user_preds.get("Match 76", "W76"), adm_user_preds.get("Match 78", "W78")), 
                    "Match 92": (adm_user_preds.get("Match 79", "W79"), adm_user_preds.get("Match 80", "W80")),
                    "Match 95": (adm_user_preds.get("Match 86", "W86"), adm_user_preds.get("Match 88", "W88")), 
                    "Match 96": (adm_user_preds.get("Match 85", "W85"), adm_user_preds.get("Match 87", "W87"))
                }
                for m_id, (h, a) in adm_o_r16.items():
                    chosen = render_match_card(h, a, m_id, m_id, disabled=False, score_mode=False, scores_dict=adm_user_preds)
                    if chosen and chosen != "Select Winner" and not chosen.startswith("W"):
                        db_save_prediction("00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", m_id, chosen)

            with adm_ko_tabs[2]:
                adm_o_qf = {
                    "Match 97": (adm_user_preds.get("Match 89", "W89"), adm_user_preds.get("Match 90", "W90")), 
                    "Match 98": (adm_user_preds.get("Match 93", "W93"), adm_user_preds.get("Match 94", "W94")),
                    "Match 99": (adm_user_preds.get("Match 91", "W91"), adm_user_preds.get("Match 92", "W92")), 
                    "Match 100": (adm_user_preds.get("Match 95", "W95"), adm_user_preds.get("Match 96", "W96"))
                }
                for m_id, (h, a) in adm_o_qf.items():
                    chosen = render_match_card(h, a, m_id, m_id, disabled=False, score_mode=False, scores_dict=adm_user_preds)
                    if chosen and chosen != "Select Winner" and not chosen.startswith("W"):
                        db_save_prediction("00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", m_id, chosen)

            with adm_ko_tabs[3]:
                asf1_h, asf1_a = adm_user_preds.get("Match 97", "W97"), adm_user_preds.get("Match 98", "W98")
                asf2_h, asf2_a = adm_user_preds.get("Match 99", "W99"), adm_user_preds.get("Match 100", "W100")
                
                asf1_opts = ["Select Winner", asf1_h, asf1_a]
                acurr_sf1 = adm_user_preds.get("Match 101", "Select Winner")
                aidx_sf1 = asf1_opts.index(acurr_sf1) if acurr_sf1 in asf1_opts else 0
                asf1_winner = st.selectbox("Official Semi Final 1 Winner", asf1_opts, index=aidx_sf1, format_func=fmt_team, key="adm_sel_m101")
                if asf1_winner != "Select Winner" and not asf1_winner.startswith("W"):
                    db_save_prediction("00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", "Match 101", asf1_winner)
                    adm_user_preds["Match 101"] = asf1_winner
                
                asf2_opts = ["Select Winner", asf2_h, asf2_a]
                acurr_sf2 = adm_user_preds.get("Match 102", "Select Winner")
                aidx_sf2 = asf2_opts.index(acurr_sf2) if acurr_sf2 in asf2_opts else 0
                asf2_winner = st.selectbox("Official Semi Final 2 Winner", asf2_opts, index=aidx_sf2, format_func=fmt_team, key="adm_sel_m102")
                if asf2_winner != "Select Winner" and not asf2_winner.startswith("W"):
                    db_save_prediction("00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", "Match 102", asf2_winner)
                    adm_user_preds["Match 102"] = asf2_winner
                
                asf1_l = asf1_a if adm_user_preds.get("Match 101") == asf1_h else asf1_h
                asf2_l = asf2_a if adm_user_preds.get("Match 102") == asf2_h else asf2_h
                
                ap3_opts = ["Select Winner", asf1_l, asf2_l]
                acurr_p3 = adm_user_preds.get("Match 103", "Select Winner")
                aidx_p3 = ap3_opts.index(acurr_p3) if acurr_p3 in ap3_opts else 0
                ap3_winner = st.selectbox("Official 3rd Place Winner Selection", ap3_opts, index=aidx_p3, format_func=fmt_team, key="adm_sel_m103")
                if ap3_winner != "Select Winner" and not ap3_winner.startswith("W"):
                    db_save_prediction("00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", "Match 103", ap3_winner)
                    adm_user_preds["Match 103"] = ap3_winner
                
                af_opts = ["Select Winner", adm_user_preds.get("Match 101", "W101"), adm_user_preds.get("Match 102", "W102")]
                acurr_f = adm_user_preds.get("Match 104", "Select Winner")
                aidx_f = af_opts.index(acurr_f) if acurr_f in af_opts else 0
                af_winner = st.selectbox("Official Grand Champion Prediction", af_opts, index=aidx_f, format_func=fmt_team, key="adm_sel_m104")
                if af_winner != "Select Winner" and not af_winner.startswith("W"):
                    db_save_prediction("00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", "Match 104", af_winner)
                    adm_user_preds["Match 104"] = af_winner

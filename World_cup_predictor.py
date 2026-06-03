def render_world_cup_card(home_team, away_team, match_label, key_prefix, disabled=False):
    """
    Renders an encapsulated visual match card inspired by the Premier League Darts App,
    with a perfectly aligned selection or score input system right below it.
    """
    # 1. Fetch flag emojis or placeholder flags if your app uses them
    # (If you use local flag assets or links, you can pass them in or use text/emojis)
    home_disp = home_team
    away_disp = away_team
    
    # 2. Visual Container Card (HTML matching your Darts App format)
    st.markdown(f"""
        <div style="border: 1px solid #C4B454; border-radius: 12px; background: rgba(20, 20, 20, 0.95); padding: 15px; margin-top: 15px; margin-bottom: 5px;">
            <div style="text-align: center; font-size: 0.85rem; color: #888; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 1px;">
                {match_label}
            </div>
            <div style="display: flex; justify-content: space-around; align-items: center;">
                <div style="text-align: center; width: 42%;">
                    <div style="font-size: 1.8rem; margin-bottom: 4px;">🏳️</div>
                    <div style="font-weight: 900; color: white;">{home_disp}</div>
                </div>
                <div style="color: #C4B454; font-weight: 900; font-size: 1.2rem; letter-spacing: 2px;">VS</div>
                <div style="text-align: center; width: 42%;">
                    <div style="font-size: 1.8rem; margin-bottom: 4px;">🏳️</div>
                    <div style="font-weight: 900; color: white;">{away_disp}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 3. Form Selection / Entry Fields (Placed cleanly OUTSIDE the raw HTML block)
    # This prevents layout breakages, clipping, or duplicate key selector rendering.
    options = ["Select Winner", home_team, away_team]
    
    # Using a structured columns layout to hold the selectbox elegantly right below the card
    col_left, col_mid, col_right = st.columns([1, 4, 1])
    with col_mid:
        winner_selection = st.selectbox(
            label=f"Winner Selection for {match_label}",
            options=options,
            key=f"{key_prefix}_select",
            label_visibility="collapsed",
            disabled=disabled
        )
        
    return winner_selection

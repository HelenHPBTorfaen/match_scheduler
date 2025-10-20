import streamlit as st
import pandas as pd
import itertools
import os

st.set_page_config(page_title="Weekly Doubles Match Scheduler", layout="wide")

DATA_FILE = "players.csv"


# ---------- Utility Functions ----------

def load_players():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Name", "Value", "Selected"])


def save_players(df):
    df.to_csv(DATA_FILE, index=False)


def doubles_round_robin(players):
    """Generate doubles matches for 4 or 5 players."""
    matches = []

    n = len(players)
    if n == 4:
        # Fixed 3 matches to rotate partners
        a, b, c, d = players
        matches = [
            {"Match": f"{a}+{b} vs {c}+{d}"},
            {"Match": f"{a}+{c} vs {b}+{d}"},
            {"Match": f"{a}+{d} vs {b}+{c}"}
        ]
    elif n == 5:
        # Rotate 5th player sitting out
        a, b, c, d, e = players
        matches = [
            {"Match": f"{a}+{b} vs {c}+{d} (E sits out)"},
            {"Match": f"{a}+{c} vs {b}+{e} (D sits out)"},
            {"Match": f"{a}+{d} vs {c}+{e} (B sits out)"},
            {"Match": f"{b}+{d} vs {c}+{e} (A sits out)"},
            {"Match": f"{a}+{e} vs {b}+{c} (D sits out)"},
        ]
    else:
        # For 6+ players, just pick first 4-5 players and generate matches
        subset = players[:5] if n >=5 else players[:4]
        return doubles_round_robin(subset)

    return matches


def group_players(selected_players):
    """Group players into courts of 4 or 5 by numeric value."""
    selected_players = selected_players.sort_values(by="Value", ascending=False).reset_index(drop=True)
    num_players = len(selected_players)
    groups = []

    i = 0
    while i < num_players:
        remaining = num_players - i
        if remaining % 5 == 0 or remaining > 5:
            group_size = 5
        else:
            group_size = 4
        group = selected_players.iloc[i:i+group_size]
        groups.append(group)
        i += group_size
    return groups


# ---------- Main App ----------

st.title("🎾 Weekly Doubles Match Scheduler")

players_df = load_players()

st.sidebar.header("Manage Players")

# Add new player
with st.sidebar.form("add_player"):
    name = st.text_input("Player Name")
    value = st.number_input("Player Value (rating)", min_value=0.0, step=0.1)
    add = st.form_submit_button("Add Player")

    if add and name:
        new_row = pd.DataFrame({"Name": [name], "Value": [value], "Selected": [False]})
        players_df = pd.concat([players_df, new_row], ignore_index=True)
        save_players(players_df)
        st.sidebar.success(f"Added {name}")

# Select players for this week
st.subheader("Select Players for This Week")

for i, row in players_df.iterrows():
    players_df.at[i, "Selected"] = st.checkbox(
        f"{row['Name']} (Value: {row['Value']})", value=row["Selected"]
    )

save_players(players_df)

selected = players_df[players_df["Selected"] == True]

st.write(f"✅ {len(selected)} players selected")

if len(selected) >= 4:
    groups = group_players(selected)

    st.subheader("Court Assignments & Doubles Matches")

    for idx, group in enumerate(groups, start=1):
        st.markdown(f"### 🏟️ Court {idx}")
        st.dataframe(group[["Name", "Value"]].reset_index(drop=True))

        # Generate doubles matches
        player_names = group["Name"].tolist()
        doubles_matches = doubles_round_robin(player_names)
        matches_df = pd.DataFrame(doubles_matches)
        st.table(matches_df)

else:
    st.warning("Please select at least 4 players to create doubles matches.")

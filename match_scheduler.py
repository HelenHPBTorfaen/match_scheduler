import streamlit as st
import pandas as pd
import itertools
import os

st.set_page_config(page_title="Weekly Match Scheduler", layout="wide")

DATA_FILE = "players.csv"


# ---------- Utility Functions ----------

def load_players():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Name", "Value", "Selected"])


def save_players(df):
    df.to_csv(DATA_FILE, index=False)


def round_robin(players, double=False):
    """Generate round robin fixtures for given players."""
    matches = []
    if double:
        all_pairs = list(itertools.permutations(players, 2))
        matches = [{"Match": f"{p1} vs {p2}"} for (p1, p2) in all_pairs]
    else:
        all_pairs = list(itertools.combinations(players, 2))
        matches = [{"Match": f"{p1} vs {p2}"} for (p1, p2) in all_pairs]
    return matches


def group_players(selected_players):
    """Group players into courts of 4 or 5 by their numeric value."""
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

st.title("🎾 Weekly Match Scheduler")

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

# Edit player selection
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

    st.subheader("Court Assignments & Round Robin Matches")

    for idx, group in enumerate(groups, start=1):
        st.markdown(f"### 🏟️ Court {idx}")
        st.dataframe(group[["Name", "Value"]].reset_index(drop=True))

        if len(group) == 5:
            rr = round_robin(group["Name"].tolist(), double=False)
        else:
            rr = round_robin(group["Name"].tolist(), double=True)

        rr_df = pd.DataFrame(rr)
        st.table(rr_df)

else:
    st.warning("Please select at least 4 players to create matches.")

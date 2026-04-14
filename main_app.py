"""


A beautiful Streamlit-based interface for managing the Greek mythology database.
Converted from MySQL to SQLite.
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import os
import sys

# Database file path (same directory as this script)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'olympian_codex.db')

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="The Olympian Codex",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS FOR AESTHETIC STYLING
# =====================================================

def load_custom_css():
    """Apply custom CSS for a beautiful Greek mythology theme."""
    st.markdown("""
        <style>
        :root {
            --primary-color: #DAA520;
            --secondary-color: #4B0082;
            --background-color: #0E1117;
        }
        .main-header {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .main-header h1 {
            color: #FFD700;
            font-size: 3rem;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        .main-header p {
            color: #FFFFFF;
            font-size: 1.2rem;
            margin-top: 0.5rem;
        }
        .css-1d391kg {
            background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
        }
        .success-message {
            padding: 1rem;
            background-color: #28a745;
            color: white;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .error-message {
            padding: 1rem;
            background-color: #dc3545;
            color: white;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .info-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: white;
        }
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.5rem 2rem;
            border-radius: 5px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        }
        .dataframe {
            border-radius: 10px;
            overflow: hidden;
        }
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            color: #667eea;
        }
        </style>
    """, unsafe_allow_html=True)

# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    Returns a connection with row_factory set to sqlite3.Row for dict-like access.
    """
    try:
        if not os.path.exists(DB_PATH):
            st.error(f"❌ Database file not found at: {DB_PATH}\n\nPlease run `python init_db.py` first to create and populate the database.")
            return None
        connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
    except sqlite3.Error as e:
        st.error(f"❌ Error connecting to SQLite Database: {e}")
        return None

def check_connection():
    """Check if database connection exists in session state."""
    return 'db_connection' in st.session_state and st.session_state.db_connection is not None

def dict_from_row(row):
    """Convert sqlite3.Row to dict."""
    if row is None:
        return None
    return dict(row)

def dicts_from_rows(rows):
    """Convert list of sqlite3.Row to list of dicts."""
    return [dict(row) for row in rows]

# =====================================================
# QUERY FUNCTIONS (READ OPERATIONS)
# =====================================================

def query_demigods_by_parent(connection, god_name):
    try:
        cursor = connection.cursor()
        sql_query = """
            SELECT 
                d.Hero_ID,
                d.First_Name,
                d.Last_Name,
                g.Name as Divine_Parent,
                d.Date_of_Birth,
                d.Fatal_Flaw,
                d.Status
            FROM Demigod d
            JOIN God g ON d.Divine_Parent_ID = g.Divine_ID
            WHERE g.Name = ?
            ORDER BY d.First_Name
        """
        cursor.execute(sql_query, (god_name,))
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return []

def query_quests_with_details(connection, status=None):
    try:
        cursor = connection.cursor()
        if status:
            sql_query = """
                SELECT 
                    q.Quest_ID, q.Objective, q.Start_Date, q.End_Date, q.Outcome,
                    p.Full_Text as Prophecy, p.Status as Prophecy_Status
                FROM Quest q
                LEFT JOIN Prophecy p ON q.Prophecy_ID = p.Prophecy_ID
                WHERE q.Outcome = ?
                ORDER BY q.Start_Date DESC
            """
            cursor.execute(sql_query, (status,))
        else:
            sql_query = """
                SELECT 
                    q.Quest_ID, q.Objective, q.Start_Date, q.End_Date, q.Outcome,
                    p.Full_Text as Prophecy, p.Status as Prophecy_Status
                FROM Quest q
                LEFT JOIN Prophecy p ON q.Prophecy_ID = p.Prophecy_ID
                ORDER BY q.Start_Date DESC
            """
            cursor.execute(sql_query)
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return []

def query_artifacts_and_wielders(connection):
    try:
        cursor = connection.cursor()
        sql_query = """
            SELECT 
                a.Artifact_ID,
                a.Name as Artifact_Name,
                a.Description,
                (d.First_Name || ' ' || d.Last_Name) as Current_Wielder,
                GROUP_CONCAT(mp.Property, ', ') as Magical_Properties
            FROM Divine_Artifact a
            LEFT JOIN Demigod d ON a.Current_Wielder = d.Hero_ID
            LEFT JOIN Magical_Properties mp ON a.Artifact_ID = mp.Artifact_ID
            GROUP BY a.Artifact_ID, a.Name, a.Description, d.First_Name, d.Last_Name
            ORDER BY a.Name
        """
        cursor.execute(sql_query)
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return []

def query_most_dangerous_monsters(connection, min_threat_level):
    try:
        cursor = connection.cursor()
        sql_query = """
            SELECT 
                m.Monster_ID, m.Species, m.Threat_Level,
                GROUP_CONCAT(DISTINCT kw.Weakness) as Weaknesses,
                GROUP_CONCAT(DISTINCT ch.Habitat) as Habitats,
                COUNT(DISTINCT e.Hero_ID) as Times_Encountered
            FROM Monster m
            LEFT JOIN Known_Weaknesses kw ON m.Monster_ID = kw.Monster_ID
            LEFT JOIN Common_Habitats ch ON m.Monster_ID = ch.Monster_ID
            LEFT JOIN Encounters e ON m.Monster_ID = e.Monster_ID
            WHERE m.Threat_Level >= ?
            GROUP BY m.Monster_ID, m.Species, m.Threat_Level
            ORDER BY m.Threat_Level DESC, Times_Encountered DESC
        """
        cursor.execute(sql_query, (min_threat_level,))
        results = dicts_from_rows(cursor.fetchall())
        for result in results:
            result['Times_Encountered'] = int(result['Times_Encountered']) if result['Times_Encountered'] else 0
        return results
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return []

def query_quest_participants(connection, quest_id):
    try:
        cursor = connection.cursor()
        sql_query = """
            SELECT 
                (d.First_Name || ' ' || d.Last_Name) as Hero_Name,
                g.Name as Divine_Parent,
                ql.Role, ql.Outcome,
                GROUP_CONCAT(ka.Ability, ', ') as Abilities
            FROM Quest_Log ql
            JOIN Demigod d ON ql.Hero_ID = d.Hero_ID
            LEFT JOIN God g ON d.Divine_Parent_ID = g.Divine_ID
            LEFT JOIN Known_Abilities ka ON d.Hero_ID = ka.Hero_ID
            WHERE ql.Quest_ID = ?
            GROUP BY d.Hero_ID, d.First_Name, d.Last_Name, g.Name, ql.Role, ql.Outcome
            ORDER BY ql.Role
        """
        cursor.execute(sql_query, (quest_id,))
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return []

def query_olympian_council(connection):
    try:
        cursor = connection.cursor()
        sql_query = """
            SELECT 
                o.Council_Seat_Number, g.Name, g.Domain, g.Symbol_of_Power,
                o.Palace_Location,
                COUNT(DISTINCT d.Hero_ID) as Number_of_Children
            FROM Olympian o
            JOIN God g ON o.Divine_ID = g.Divine_ID
            LEFT JOIN Demigod d ON g.Divine_ID = d.Divine_Parent_ID
            WHERE o.Council_Seat_Number IS NOT NULL
            GROUP BY o.Council_Seat_Number, g.Name, g.Domain, g.Symbol_of_Power, o.Palace_Location
            ORDER BY o.Council_Seat_Number
        """
        cursor.execute(sql_query)
        results = dicts_from_rows(cursor.fetchall())
        for result in results:
            result['Number_of_Children'] = int(result['Number_of_Children']) if result['Number_of_Children'] else 0
        return results
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return []

def query_active_prophecies_no_quest(connection):
    try:
        cursor = connection.cursor()
        sql_query = """
            SELECT p.Prophecy_ID, p.Full_Text, p.Date_Issued, p.Status
            FROM Prophecy p
            LEFT JOIN Quest q ON p.Prophecy_ID = q.Prophecy_ID
            WHERE q.Quest_ID IS NULL
              AND p.Status != 'Fulfilled'
              AND p.Status != 'Failed'
            ORDER BY p.Date_Issued DESC
        """
        cursor.execute(sql_query)
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return []

def query_demigods_projection(connection):
    try:
        cursor = connection.cursor()
        sql_query = """
            SELECT 
                d.First_Name, d.Last_Name,
                (d.First_Name || ' ' || d.Last_Name) as Full_Name,
                g.Name as Divine_Parent
            FROM Demigod d
            LEFT JOIN God g ON d.Divine_Parent_ID = g.Divine_ID
            ORDER BY d.Last_Name, d.First_Name
        """
        cursor.execute(sql_query)
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return []

def query_titan_avg_threat(connection):
    try:
        cursor = connection.cursor()
        sql_query = """
            SELECT 
                AVG(m.Threat_Level) as Average_Threat_Level,
                COUNT(t.Monster_ID) as Total_Titans,
                MIN(m.Threat_Level) as Min_Threat,
                MAX(m.Threat_Level) as Max_Threat
            FROM Monster m
            JOIN Titan t ON m.Monster_ID = t.Monster_ID
        """
        cursor.execute(sql_query)
        result = dict_from_row(cursor.fetchone())
        if result:
            result['Average_Threat_Level'] = float(result['Average_Threat_Level']) if result['Average_Threat_Level'] else None
            result['Total_Titans'] = int(result['Total_Titans']) if result['Total_Titans'] else 0
            result['Min_Threat'] = int(result['Min_Threat']) if result['Min_Threat'] else 0
            result['Max_Threat'] = int(result['Max_Threat']) if result['Max_Threat'] else 0
        return result
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return None

def query_artifacts_search_blade(connection, search_term='Blade'):
    try:
        cursor = connection.cursor()
        sql_query = """
            SELECT 
                a.Artifact_ID, a.Name, a.Description,
                (d.First_Name || ' ' || d.Last_Name) as Current_Wielder,
                GROUP_CONCAT(mp.Property, ', ') as Magical_Properties
            FROM Divine_Artifact a
            LEFT JOIN Demigod d ON a.Current_Wielder = d.Hero_ID
            LEFT JOIN Magical_Properties mp ON a.Artifact_ID = mp.Artifact_ID
            WHERE a.Name LIKE ? OR a.Description LIKE ?
            GROUP BY a.Artifact_ID, a.Name, a.Description, d.First_Name, d.Last_Name
            ORDER BY a.Name
        """
        search_pattern = f"%{search_term}%"
        cursor.execute(sql_query, (search_pattern, search_pattern))
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return []

def report_quests_by_divine_parent(connection):
    try:
        cursor = connection.cursor()
        sql_query = """
            SELECT 
                g.Name as Divine_Parent, g.Domain,
                COUNT(DISTINCT q.Quest_ID) as Total_Quests,
                COUNT(DISTINCT d.Hero_ID) as Children_Participated,
                SUM(CASE WHEN q.Outcome = 'Success' THEN 1 ELSE 0 END) as Successful_Quests,
                GROUP_CONCAT(DISTINCT q.Objective, ' | ') as Quest_Objectives
            FROM God g
            JOIN Demigod d ON g.Divine_ID = d.Divine_Parent_ID
            JOIN Quest_Log ql ON d.Hero_ID = ql.Hero_ID
            JOIN Quest q ON ql.Quest_ID = q.Quest_ID
            GROUP BY g.Divine_ID, g.Name, g.Domain
            ORDER BY Total_Quests DESC, Successful_Quests DESC
        """
        cursor.execute(sql_query)
        results = dicts_from_rows(cursor.fetchall())
        for result in results:
            result['Total_Quests'] = int(result['Total_Quests']) if result['Total_Quests'] else 0
            result['Children_Participated'] = int(result['Children_Participated']) if result['Children_Participated'] else 0
            result['Successful_Quests'] = int(result['Successful_Quests']) if result['Successful_Quests'] else 0
        return results
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return []

def report_prophecy_monster_correlation(connection):
    try:
        cursor = connection.cursor()
        sql_query = """
            SELECT 
                p.Prophecy_ID,
                SUBSTR(p.Full_Text, 1, 100) as Prophecy_Text,
                p.Status as Prophecy_Status,
                q.Objective as Quest_Objective,
                m.Species as Monster_Species,
                m.Threat_Level,
                COUNT(*) as Encounter_Count
            FROM Prophecy p
            JOIN Quest q ON p.Prophecy_ID = q.Prophecy_ID
            JOIN Combat_Encounter ce ON q.Quest_ID = ce.Quest_ID
            JOIN Monster m ON ce.Monster_ID = m.Monster_ID
            GROUP BY p.Prophecy_ID, p.Full_Text, p.Status, q.Objective, m.Species, m.Threat_Level
            ORDER BY p.Prophecy_ID, Encounter_Count DESC
        """
        cursor.execute(sql_query)
        results = dicts_from_rows(cursor.fetchall())
        for result in results:
            result['Encounter_Count'] = int(result['Encounter_Count']) if result['Encounter_Count'] else 0
        return results
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return []

def query_database_statistics(connection):
    try:
        cursor = connection.cursor()
        stats = {}
        cursor.execute("SELECT COUNT(*) as count FROM God")
        stats['total_gods'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM Demigod")
        stats['total_demigods'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM Demigod WHERE Status = 'Active'")
        stats['active_demigods'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM Monster")
        stats['total_monsters'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM Quest")
        stats['total_quests'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM Quest WHERE Outcome = 'Success'")
        stats['completed_quests'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM Divine_Artifact")
        stats['total_artifacts'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM Encounters")
        stats['total_encounters'] = cursor.fetchone()['count']
        return stats
    except sqlite3.Error as e:
        st.error(f"Error during query: {e}")
        return {}

# =====================================================
# UPDATE FUNCTIONS (WRITE OPERATIONS)
# =====================================================

def insert_new_demigod(connection, first_name, last_name, divine_parent_id, date_of_birth,
                       fatal_flaw, date_of_arrival, status, abilities=None):
    try:
        cursor = connection.cursor()
        if divine_parent_id:
            cursor.execute("SELECT Divine_ID FROM God WHERE Divine_ID = ?", (divine_parent_id,))
            if not cursor.fetchone():
                return False, f"Divine Parent with ID {divine_parent_id} does not exist."
        sql_insert = """
            INSERT INTO Demigod 
            (First_Name, Last_Name, Divine_Parent_ID, Date_of_Birth, Fatal_Flaw, Date_of_Arrival, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql_insert, (first_name, last_name, divine_parent_id,
                                     str(date_of_birth) if date_of_birth else None,
                                     fatal_flaw,
                                     str(date_of_arrival) if date_of_arrival else None,
                                     status))
        hero_id = cursor.lastrowid
        if abilities:
            for ability in abilities:
                if ability.strip():
                    cursor.execute("INSERT INTO Known_Abilities (Hero_ID, Ability) VALUES (?, ?)",
                                   (hero_id, ability.strip()))
        connection.commit()
        return True, hero_id
    except sqlite3.Error as e:
        connection.rollback()
        return False, str(e)

def insert_new_quest(connection, objective, start_date, outcome='Ongoing', prophecy_id=None):
    try:
        cursor = connection.cursor()
        if prophecy_id:
            cursor.execute("SELECT Quest_ID FROM Quest WHERE Prophecy_ID = ?", (prophecy_id,))
            if cursor.fetchone():
                return False, "This prophecy is already linked to another quest."
        sql_insert = "INSERT INTO Quest (Objective, Start_Date, Outcome, Prophecy_ID) VALUES (?, ?, ?, ?)"
        cursor.execute(sql_insert, (objective, str(start_date), outcome, prophecy_id))
        connection.commit()
        return True, cursor.lastrowid
    except sqlite3.Error as e:
        connection.rollback()
        return False, str(e)

def insert_monster_sighting(connection, monster_id, location, reported_by):
    try:
        cursor = connection.cursor()
        sighting_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql_insert = "INSERT INTO Sighting_Log (Monster_ID, Sighting_Timestamp, Location, Reported_By) VALUES (?, ?, ?, ?)"
        cursor.execute(sql_insert, (monster_id, sighting_timestamp, location, reported_by))
        connection.commit()
        return True, "Sighting recorded successfully"
    except sqlite3.Error as e:
        connection.rollback()
        return False, str(e)

def update_demigod_status(connection, hero_id, new_status):
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE Demigod SET Status = ? WHERE Hero_ID = ?", (new_status, hero_id))
        rows_affected = cursor.rowcount
        if new_status == 'Deceased':
            cursor.execute("UPDATE Quest_Log SET Outcome = 'Deceased' WHERE Hero_ID = ? AND Outcome = 'Ongoing'", (hero_id,))
        connection.commit()
        if rows_affected > 0:
            return True, "Status updated successfully"
        else:
            return False, "No demigod found with that ID"
    except sqlite3.Error as e:
        connection.rollback()
        return False, str(e)

def update_quest_outcome(connection, quest_id, outcome, end_date=None):
    try:
        cursor = connection.cursor()
        if end_date:
            cursor.execute("UPDATE Quest SET Outcome = ?, End_Date = ? WHERE Quest_ID = ?",
                           (outcome, str(end_date), quest_id))
        else:
            cursor.execute("UPDATE Quest SET Outcome = ? WHERE Quest_ID = ?", (outcome, quest_id))
        connection.commit()
        if cursor.rowcount > 0:
            return True, "Quest updated successfully"
        else:
            return False, "No quest found with that ID"
    except sqlite3.Error as e:
        connection.rollback()
        return False, str(e)

def update_artifact_wielder(connection, artifact_id, new_wielder_id):
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE Divine_Artifact SET Current_Wielder = ? WHERE Artifact_ID = ?",
                       (new_wielder_id, artifact_id))
        connection.commit()
        if cursor.rowcount > 0:
            return True, "Artifact wielder updated successfully"
        else:
            return False, "No artifact found with that ID"
    except sqlite3.Error as e:
        connection.rollback()
        return False, str(e)

def delete_monster_sighting(connection, monster_id, sighting_timestamp):
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Sighting_Log WHERE Monster_ID = ? AND Sighting_Timestamp = ?",
                       (monster_id, sighting_timestamp))
        connection.commit()
        if cursor.rowcount > 0:
            return True, "Sighting deleted successfully"
        else:
            return False, "No sighting found with those parameters"
    except sqlite3.Error as e:
        connection.rollback()
        return False, str(e)

def delete_quest(connection, quest_id):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM Quest_Log WHERE Quest_ID = ?", (quest_id,))
        affected_logs = cursor.fetchone()['count']
        cursor.execute("DELETE FROM Quest WHERE Quest_ID = ?", (quest_id,))
        connection.commit()
        if cursor.rowcount > 0:
            return True, f"Quest deleted successfully. {affected_logs} quest log entries also removed due to CASCADE."
        else:
            return False, "No quest found with that ID"
    except sqlite3.Error as e:
        connection.rollback()
        return False, str(e)

def delete_demigod_ability(connection, hero_id, ability):
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Known_Abilities WHERE Hero_ID = ? AND Ability = ?", (hero_id, ability))
        connection.commit()
        if cursor.rowcount > 0:
            return True, "Ability deleted successfully"
        else:
            return False, "No such ability found for this hero"
    except sqlite3.Error as e:
        connection.rollback()
        return False, str(e)

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_all_gods(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT Divine_ID, Name FROM God ORDER BY Name")
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error fetching gods: {e}")
        return []

def get_all_demigods(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT Hero_ID, (First_Name || ' ' || Last_Name) as Full_Name FROM Demigod ORDER BY First_Name")
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error fetching demigods: {e}")
        return []

def get_all_monsters(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT Monster_ID, Species FROM Monster ORDER BY Species")
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error fetching monsters: {e}")
        return []

def get_all_artifacts(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT Artifact_ID, Name FROM Divine_Artifact ORDER BY Name")
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error fetching artifacts: {e}")
        return []

def get_all_quests(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT Quest_ID, Objective FROM Quest ORDER BY Quest_ID DESC")
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error fetching quests: {e}")
        return []

def get_available_prophecies(connection):
    try:
        cursor = connection.cursor()
        sql_query = """
            SELECT p.Prophecy_ID, p.Full_Text, p.Date_Issued, p.Status
            FROM Prophecy p
            LEFT JOIN Quest q ON p.Prophecy_ID = q.Prophecy_ID
            WHERE q.Quest_ID IS NULL
            ORDER BY p.Date_Issued DESC
        """
        cursor.execute(sql_query)
        return dicts_from_rows(cursor.fetchall())
    except sqlite3.Error as e:
        st.error(f"Error fetching available prophecies: {e}")
        return []

# =====================================================
# UI PAGES
# =====================================================

def show_dashboard(connection):
    st.markdown("""
        <div class="main-header">
            <h1>⚡ The Olympian Codex ⚡</h1>
            <p>A Comprehensive Database of Greek Mythology</p>
        </div>
    """, unsafe_allow_html=True)
    stats = query_database_statistics(connection)
    if stats:
        st.header("📊 Database Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏛️ Total Gods", stats['total_gods'])
            st.metric("⚔️ Total Demigods", stats['total_demigods'])
        with col2:
            st.metric("✅ Active Demigods", stats['active_demigods'])
            st.metric("👹 Total Monsters", stats['total_monsters'])
        with col3:
            st.metric("🗺️ Total Quests", stats['total_quests'])
            st.metric("🏆 Completed Quests", stats['completed_quests'])
        with col4:
            st.metric("⚔️ Divine Artifacts", stats['total_artifacts'])
            st.metric("⚡ Total Encounters", stats['total_encounters'])
        st.header("🏛️ The Olympian Council")
        council_results = query_olympian_council(connection)
        if council_results:
            df = pd.DataFrame(council_results)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No council members found.")
    else:
        st.error("Unable to fetch database statistics.")

def show_query_page(connection):
    st.header("🔍 Query Operations")
    query_option = st.selectbox(
        "Select a query to execute:",
        [
            "Find Demigods by Divine Parent",
            "View Quest Details",
            "Active Prophecies (No Quest Assigned)",
            "All Demigods with Divine Parents",
            "Average Threat Level of Titans",
            "Search Artifacts (Contains Text)",
            "Report: Quests by Divine Parent",
        ]
    )
    st.divider()

    if query_option == "Find Demigods by Divine Parent":
        st.subheader("⚡ Find Demigods by Divine Parent")
        gods = get_all_gods(connection)
        if gods:
            god_names = [god['Name'] for god in gods]
            selected_god = st.selectbox("Select a god:", god_names)
            if st.button("🔍 Search", key="query1"):
                results = query_demigods_by_parent(connection, selected_god)
                if results:
                    st.success(f"Found {len(results)} demigod(s) with {selected_god} as their divine parent:")
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"No demigods found for {selected_god}.")

    elif query_option == "View Quest Details":
        st.subheader("🗺️ View Quest Details")
        status_filter = st.selectbox("Filter by outcome:", ["All", "Success", "Failure", "Ongoing", "Abandoned"])
        if st.button("🔍 Search", key="query2"):
            status = None if status_filter == "All" else status_filter
            results = query_quests_with_details(connection, status)
            if results:
                st.success(f"Found {len(results)} quest(s):")
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("No quests found.")

    elif query_option == "Active Prophecies (No Quest Assigned)":
        st.subheader("📜 Active Prophecies with No Quest Assigned")
        st.info("**REQUIRED Query - Selection**: Retrieves all active prophecies that have no quest assigned.")
        if st.button("🔍 Execute Query", key="req_query1"):
            results = query_active_prophecies_no_quest(connection)
            if results:
                st.success(f"Found {len(results)} active prophecy/prophecies without assigned quests:")
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("All active prophecies have quests assigned, or no active prophecies exist.")

    elif query_option == "All Demigods with Divine Parents":
        st.subheader("👤 All Demigods with Their Divine Parents")
        st.info("**REQUIRED Query - Projection**: Displays the names and divine parents of all registered demigods.")
        if st.button("🔍 Execute Query", key="req_query2"):
            results = query_demigods_projection(connection)
            if results:
                st.success(f"Found {len(results)} registered demigod(s):")
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("No demigods found in the database.")

    elif query_option == "Average Threat Level of Titans":
        st.subheader("⚡ Average Threat Level of Titans")
        st.info("**REQUIRED Query - Aggregate**: Calculates the average threat level of monsters in the Titan subclass.")
        if st.button("🔍 Execute Query", key="req_query3"):
            result = query_titan_avg_threat(connection)
            if result and result['Average_Threat_Level']:
                st.success("Titan Threat Level Statistics:")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Average Threat", f"{result['Average_Threat_Level']:.2f}")
                with col2:
                    st.metric("Total Titans", result['Total_Titans'])
                with col3:
                    st.metric("Minimum Threat", result['Min_Threat'])
                with col4:
                    st.metric("Maximum Threat", result['Max_Threat'])
            else:
                st.warning("No Titan data found in the database.")

    elif query_option == "Search Artifacts (Contains Text)":
        st.subheader("🔍 Search Divine Artifacts")
        st.info("**REQUIRED Query - Search**: Find all divine artifacts with specific text in their name or description.")
        search_term = st.text_input("Enter search term (e.g., 'Blade', 'Sword', 'Shield'):", value="Blade")
        if st.button("🔍 Execute Search", key="req_query4"):
            if search_term:
                results = query_artifacts_search_blade(connection, search_term)
                if results:
                    st.success(f"Found {len(results)} artifact(s) matching '{search_term}':")
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"No artifacts found matching '{search_term}'.")
            else:
                st.warning("Please enter a search term.")

    elif query_option == "Report: Quests by Divine Parent":
        st.subheader("📊 Analysis Report: Quests by Divine Parent")
        st.info("**REQUIRED Report 1**: Generates a report of quests grouped by the divine parent of participating demigods.")
        if st.button("📊 Generate Report", key="report1"):
            results = report_quests_by_divine_parent(connection)
            if results:
                st.success(f"Report generated for {len(results)} divine parent(s):")
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.subheader("Summary Statistics")
                total_quests = sum(r['Total_Quests'] for r in results)
                total_successful = sum(r['Successful_Quests'] for r in results)
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Quests Across All Parents", total_quests)
                with col2:
                    st.metric("Total Successful Quests", total_successful)
            else:
                st.warning("No quest data found.")

def show_insert_page(connection):
    st.header("➕ Insert Operations")
    insert_option = st.selectbox("Select an insert operation:",
                                  ["Add New Demigod", "Create New Quest", "Report Monster Sighting"])
    st.divider()

    if insert_option == "Add New Demigod":
        st.subheader("⚔️ Register a New Demigod")
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name:")
            last_name = st.text_input("Last Name:")
            gods = get_all_gods(connection)
            if gods:
                god_dict = {g['Name']: g['Divine_ID'] for g in gods}
                selected_god = st.selectbox("Divine Parent:", ["None"] + list(god_dict.keys()))
                divine_parent_id = None if selected_god == "None" else god_dict[selected_god]
        with col2:
            date_of_birth = st.date_input("Date of Birth:", value=date(2000, 1, 1))
            date_of_arrival = st.date_input("Date of Arrival at Camp:", value=date.today())
            fatal_flaw = st.text_input("Fatal Flaw:")
            status = st.selectbox("Status:", ["Active", "Deceased", "Missing", "Retired"])
        st.subheader("Known Abilities (Optional)")
        abilities_text = st.text_area("Enter abilities (one per line):",
                                       placeholder="Water Manipulation\nUnderwater Breathing\nSwordsmanship", height=100)
        if st.button("✅ Register Demigod", key="insert1"):
            if first_name and last_name and fatal_flaw:
                abilities = [a.strip() for a in abilities_text.split('\n') if a.strip()]
                success, result = insert_new_demigod(connection, first_name, last_name, divine_parent_id,
                                                      date_of_birth, fatal_flaw, date_of_arrival, status, abilities)
                if success:
                    st.success(f"✅ Demigod registered successfully! Hero ID: {result}")
                    if abilities:
                        st.info(f"📋 Added {len(abilities)} ability/abilities.")
                else:
                    st.error(f"❌ Error: {result}")
            else:
                st.warning("Please fill in all required fields.")

    elif insert_option == "Create New Quest":
        st.subheader("🗺️ Create a New Quest")
        objective = st.text_area("Quest Objective:", height=100)
        start_date = st.date_input("Start Date:", value=date.today())
        outcome = st.selectbox("Initial Outcome:", ["Ongoing", "Success", "Failure", "Abandoned"])
        st.subheader("Link to Prophecy (Optional)")
        available_prophecies = get_available_prophecies(connection)
        prophecy_id = None
        if available_prophecies:
            prophecy_options = ["None - No Prophecy"] + [
                f"Prophecy {p['Prophecy_ID']}: {p['Full_Text'][:80]}..." for p in available_prophecies
            ]
            selected_prophecy = st.selectbox("Select a Prophecy:", prophecy_options)
            if selected_prophecy != "None - No Prophecy":
                prophecy_id = available_prophecies[prophecy_options.index(selected_prophecy) - 1]['Prophecy_ID']
                selected_prophecy_data = available_prophecies[prophecy_options.index(selected_prophecy) - 1]
                st.info(f"**Full Prophecy Text:**\n{selected_prophecy_data['Full_Text']}")
        else:
            st.warning("⚠️ No available prophecies. All prophecies are already linked to quests.")
        if st.button("✅ Create Quest", key="insert2"):
            if objective:
                success, result = insert_new_quest(connection, objective, start_date, outcome, prophecy_id)
                if success:
                    st.success(f"✅ Quest created successfully! Quest ID: {result}")
                    if prophecy_id:
                        st.info(f"🔗 Quest linked to Prophecy ID: {prophecy_id}")
                else:
                    st.error(f"❌ Error: {result}")
            else:
                st.warning("Please provide a quest objective.")

    elif insert_option == "Report Monster Sighting":
        st.subheader("👁️ Report a Monster Sighting")
        col1, col2 = st.columns(2)
        with col1:
            monsters = get_all_monsters(connection)
            if monsters:
                monster_dict = {m['Species']: m['Monster_ID'] for m in monsters}
                selected_monster = st.selectbox("Monster Species:", list(monster_dict.keys()))
                monster_id = monster_dict[selected_monster]
        with col2:
            demigods = get_all_demigods(connection)
            if demigods:
                demigod_dict = {d['Full_Name']: d['Hero_ID'] for d in demigods}
                selected_reporter = st.selectbox("Reported By:", list(demigod_dict.keys()))
                reporter_id = demigod_dict[selected_reporter]
        location = st.text_input("Location:")
        if st.button("✅ Report Sighting", key="insert3"):
            if location:
                success, result = insert_monster_sighting(connection, monster_id, location, reporter_id)
                if success:
                    st.success("✅ Sighting reported successfully!")
                else:
                    st.error(f"❌ Error: {result}")
            else:
                st.warning("Please provide a location.")

def show_update_page(connection):
    st.header("✏️ Update Operations")
    update_option = st.selectbox("Select an update operation:",
                                  ["Update Demigod Status", "Update Quest Outcome", "Change Artifact Wielder"])
    st.divider()

    if update_option == "Update Demigod Status":
        st.subheader("✏️ Update Demigod Status")
        st.info("**REQUIRED Update**: When updating to 'Deceased', this triggers an update on associated 'Quest_Log' records.")
        demigods = get_all_demigods(connection)
        if demigods:
            demigod_dict = {d['Full_Name']: d['Hero_ID'] for d in demigods}
            selected_demigod = st.selectbox("Select Demigod:", list(demigod_dict.keys()))
            hero_id = demigod_dict[selected_demigod]
            new_status = st.selectbox("New Status:", ["Active", "Deceased", "Missing", "Retired"])
            if new_status == "Deceased":
                st.warning("⚠️ Updating to 'Deceased' will also update all ongoing Quest_Log entries for this hero.")
            if st.button("✅ Update Status", key="update1"):
                success, result = update_demigod_status(connection, hero_id, new_status)
                if success:
                    st.success(f"✅ {result}")
                else:
                    st.error(f"❌ Error: {result}")

    elif update_option == "Update Quest Outcome":
        st.subheader("✏️ Update Quest Outcome")
        quests = get_all_quests(connection)
        if quests:
            quest_dict = {f"Quest {q['Quest_ID']}: {q['Objective'][:50]}...": q['Quest_ID'] for q in quests}
            selected_quest = st.selectbox("Select Quest:", list(quest_dict.keys()))
            quest_id = quest_dict[selected_quest]
            outcome = st.selectbox("New Outcome:", ["Success", "Failure", "Ongoing", "Abandoned"])
            set_end_date = st.checkbox("Set End Date")
            end_date = None
            if set_end_date:
                end_date = st.date_input("End Date:", value=date.today())
            if st.button("✅ Update Quest", key="update2"):
                success, result = update_quest_outcome(connection, quest_id, outcome, end_date)
                if success:
                    st.success(f"✅ {result}")
                else:
                    st.error(f"❌ Error: {result}")

    elif update_option == "Change Artifact Wielder":
        st.subheader("⚔️ Change Artifact Wielder")
        artifacts = get_all_artifacts(connection)
        demigods = get_all_demigods(connection)
        if artifacts and demigods:
            artifact_dict = {a['Name']: a['Artifact_ID'] for a in artifacts}
            selected_artifact = st.selectbox("Select Artifact:", list(artifact_dict.keys()))
            artifact_id = artifact_dict[selected_artifact]
            demigod_dict = {d['Full_Name']: d['Hero_ID'] for d in demigods}
            selected_wielder = st.selectbox("New Wielder:", ["None"] + list(demigod_dict.keys()))
            new_wielder_id = None if selected_wielder == "None" else demigod_dict[selected_wielder]
            if st.button("✅ Change Wielder", key="update3"):
                success, result = update_artifact_wielder(connection, artifact_id, new_wielder_id)
                if success:
                    st.success(f"✅ {result}")
                else:
                    st.error(f"❌ Error: {result}")

def show_delete_page(connection):
    st.header("🗑️ Delete Operations")
    st.warning("⚠️ Warning: Delete operations are permanent and cannot be undone!")
    delete_option = st.selectbox("Select a delete operation:",
                                  ["Delete Monster Sighting", "Delete Quest", "Remove Demigod Ability"])
    st.divider()

    if delete_option == "Delete Monster Sighting":
        st.subheader("🗑️ Delete a Monster Sighting")
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT sl.Monster_ID, m.Species, sl.Sighting_Timestamp, sl.Location,
                       (d.First_Name || ' ' || d.Last_Name) as Reporter
                FROM Sighting_Log sl
                JOIN Monster m ON sl.Monster_ID = m.Monster_ID
                LEFT JOIN Demigod d ON sl.Reported_By = d.Hero_ID
                ORDER BY sl.Sighting_Timestamp DESC
                LIMIT 20
            """)
            sightings = dicts_from_rows(cursor.fetchall())
            if sightings:
                df = pd.DataFrame(sightings)
                st.dataframe(df, use_container_width=True, hide_index=True)
                sighting_dict = {
                    f"{s['Species']} at {s['Location']} ({s['Sighting_Timestamp']})":
                    (s['Monster_ID'], s['Sighting_Timestamp']) for s in sightings
                }
                selected_sighting = st.selectbox("Select Sighting to Delete:", list(sighting_dict.keys()))
                if st.button("🗑️ Delete Sighting", key="delete1"):
                    monster_id, timestamp = sighting_dict[selected_sighting]
                    success, result = delete_monster_sighting(connection, monster_id, timestamp)
                    if success:
                        st.success(f"✅ {result}")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result}")
            else:
                st.info("No sightings found.")
        except sqlite3.Error as e:
            st.error(f"Error fetching sightings: {e}")

    elif delete_option == "Delete Quest":
        st.subheader("🗑️ Delete a Quest")
        st.info("**REQUIRED Delete**: All associated 'Quest_Log' entries will also be deleted due to CASCADE constraint.")
        quests = get_all_quests(connection)
        if quests:
            quest_dict = {f"Quest {q['Quest_ID']}: {q['Objective'][:50]}...": q['Quest_ID'] for q in quests}
            selected_quest = st.selectbox("Select Quest to Delete:", list(quest_dict.keys()))
            quest_id = quest_dict[selected_quest]
            st.warning("⚠️ This will CASCADE delete all quest logs associated with this quest!")
            confirm = st.checkbox("I understand this action is permanent")
            if st.button("🗑️ Delete Quest", key="delete2", disabled=not confirm):
                success, result = delete_quest(connection, quest_id)
                if success:
                    st.success(f"✅ {result}")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result}")

    elif delete_option == "Remove Demigod Ability":
        st.subheader("🗑️ Remove a Demigod Ability")
        demigods = get_all_demigods(connection)
        if demigods:
            demigod_dict = {d['Full_Name']: d['Hero_ID'] for d in demigods}
            selected_demigod = st.selectbox("Select Demigod:", list(demigod_dict.keys()))
            hero_id = demigod_dict[selected_demigod]
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT Ability FROM Known_Abilities WHERE Hero_ID = ? ORDER BY Ability", (hero_id,))
                abilities = dicts_from_rows(cursor.fetchall())
                if abilities:
                    ability_list = [a['Ability'] for a in abilities]
                    selected_ability = st.selectbox("Select Ability to Remove:", ability_list)
                    if st.button("🗑️ Remove Ability", key="delete3"):
                        success, result = delete_demigod_ability(connection, hero_id, selected_ability)
                        if success:
                            st.success(f"✅ {result}")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result}")
                else:
                    st.info(f"No abilities found for {selected_demigod}.")
            except sqlite3.Error as e:
                st.error(f"Error fetching abilities: {e}")

def show_about_page():
    st.header("ℹ️ About The Olympian Codex")
    st.markdown("""
    ### 🏛️ Welcome to The Olympian Codex

    This is a comprehensive database management system for Greek mythology, featuring:

    - **Gods & Goddesses**: The mighty Olympians, chthonic deities, and primordials
    - **Demigods**: Heroic half-bloods with divine parentage
    - **Monsters**: Fearsome creatures and threats from mythology
    - **Quests**: Epic adventures guided by prophecies
    - **Divine Artifacts**: Powerful weapons and magical items

    ### 🛠️ Technical Stack

    - **Database**: SQLite (local, no server required)
    - **Backend**: Python with sqlite3 (built-in)
    - **Frontend**: Streamlit
    - **Design**: Entity-Relationship Model with proper normalization

    ---

    *May the gods be with you on your database journey!* ⚡
    """)

# =====================================================
# MAIN APPLICATION
# =====================================================

def main():
    load_custom_css()

    if 'db_connection' not in st.session_state:
        st.session_state.db_connection = None

    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/lightning-bolt.png", width=100)
        st.title("⚡ The Olympian Codex")
        st.divider()

        if not check_connection():
            st.header("🔐 Database Connection")
            st.info(f"📁 Database: `olympian_codex.db`")

            if st.button("🔌 Connect to Database", use_container_width=True):
                connection = get_db_connection()
                if connection:
                    st.session_state.db_connection = connection
                    st.success("✅ Connected successfully!")
                    st.rerun()
                else:
                    st.error("❌ Connection failed! Run `python init_db.py` first.")
        else:
            st.success("✅ Database Connected")

            if st.button("🔌 Disconnect", use_container_width=True):
                if st.session_state.db_connection:
                    st.session_state.db_connection.close()
                st.session_state.db_connection = None
                st.rerun()

            st.divider()

            st.header("📑 Navigation")
            page = st.radio(
                "Select a page:",
                [
                    "🏠 Dashboard",
                    "🔍 Query Operations",
                    "➕ Insert Operations",
                    "✏️ Update Operations",
                    "🗑️ Delete Operations",
                    "ℹ️ About"
                ],
                label_visibility="collapsed"
            )

            st.divider()
        

    if not check_connection():
        st.markdown("""
            <div class="main-header">
                <h1>⚡ The Olympian Codex ⚡</h1>
                <p>A Comprehensive Database of Greek Mythology</p>
            </div>
        """, unsafe_allow_html=True)

        st.info("👈 Please connect to the database using the sidebar to begin.")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div class="info-card">
                    <h3>🏛️ Gods & Demigods</h3>
                    <p>Explore the divine pantheon and their heroic children</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <div class="info-card">
                    <h3>👹 Monsters & Quests</h3>
                    <p>Track legendary creatures and epic adventures</p>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
                <div class="info-card">
                    <h3>⚔️ Divine Artifacts</h3>
                    <p>Manage powerful weapons and magical items</p>
                </div>
            """, unsafe_allow_html=True)

    else:
        connection = st.session_state.db_connection
        if page == "🏠 Dashboard":
            show_dashboard(connection)
        elif page == "🔍 Query Operations":
            show_query_page(connection)
        elif page == "➕ Insert Operations":
            show_insert_page(connection)
        elif page == "✏️ Update Operations":
            show_update_page(connection)
        elif page == "🗑️ Delete Operations":
            show_delete_page(connection)
        elif page == "ℹ️ About":
            show_about_page()

if __name__ == "__main__":
    main()

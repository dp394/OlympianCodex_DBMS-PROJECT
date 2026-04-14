-- =====================================================
-- The Olympian Codex Database Schema (SQLite)
-- =====================================================

-- Enable foreign key support in SQLite
PRAGMA foreign_keys = ON;

-- =====================================================
-- STRONG ENTITY TABLES
-- =====================================================

-- Table: God
-- Represents the divine entities in the Greek pantheon
CREATE TABLE IF NOT EXISTS God (
    Divine_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL UNIQUE,
    Domain TEXT,
    Symbol_of_Power TEXT,
    Roman_Counterpart TEXT
);

-- Table: Demigod
-- Represents the half-blood children of gods
CREATE TABLE IF NOT EXISTS Demigod (
    Hero_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    First_Name TEXT NOT NULL,
    Last_Name TEXT NOT NULL,
    Divine_Parent_ID INTEGER NULL,  -- NULLABLE to resolve insertion anomaly
    Date_of_Birth TEXT,
    Fatal_Flaw TEXT,
    Date_of_Arrival TEXT,
    Status TEXT NOT NULL DEFAULT 'Active' CHECK (Status IN ('Active', 'Deceased', 'Missing', 'Retired')),
    FOREIGN KEY (Divine_Parent_ID) REFERENCES God(Divine_ID) 
        ON DELETE SET NULL  -- Resolves deletion anomaly
        ON UPDATE CASCADE
);

-- Table: Monster
-- Represents the mythological creatures and threats
CREATE TABLE IF NOT EXISTS Monster (
    Monster_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Species TEXT NOT NULL,
    Threat_Level INTEGER NOT NULL CHECK (Threat_Level BETWEEN 1 AND 10)
);

-- Table: Prophecy
-- Represents prophecies issued by the Oracle of Delphi
CREATE TABLE IF NOT EXISTS Prophecy (
    Prophecy_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Full_Text TEXT NOT NULL,
    Date_Issued TEXT NOT NULL,
    Status TEXT NOT NULL DEFAULT 'Pending' CHECK (Status IN ('Pending', 'In Progress', 'Fulfilled', 'Failed'))
);

-- Table: Quest
-- Represents heroic quests undertaken by demigods
CREATE TABLE IF NOT EXISTS Quest (
    Quest_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Objective TEXT NOT NULL,
    Prophecy_ID INTEGER UNIQUE,  -- 1:1 relationship with Prophecy
    Start_Date TEXT,
    End_Date TEXT,
    Outcome TEXT DEFAULT 'Ongoing' CHECK (Outcome IN ('Success', 'Failure', 'Ongoing', 'Abandoned')),
    FOREIGN KEY (Prophecy_ID) REFERENCES Prophecy(Prophecy_ID)
        ON DELETE RESTRICT  -- Cannot delete a prophecy if quest exists
        ON UPDATE CASCADE,
    CHECK (End_Date IS NULL OR End_Date >= Start_Date)
);

-- Table: Divine_Artifact
-- Represents magical items and weapons of power
CREATE TABLE IF NOT EXISTS Divine_Artifact (
    Artifact_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL UNIQUE,
    Description TEXT,
    Current_Wielder INTEGER NULL,  -- Can be unwielded
    FOREIGN KEY (Current_Wielder) REFERENCES Demigod(Hero_ID)
        ON DELETE SET NULL  -- Artifact becomes unwielded if hero dies/deleted
        ON UPDATE CASCADE
);

-- =====================================================
-- SUBCLASS TABLES (God Hierarchy)
-- =====================================================

-- Table: Olympian
-- Represents the twelve major Olympian gods
CREATE TABLE IF NOT EXISTS Olympian (
    Divine_ID INTEGER PRIMARY KEY,
    Council_Seat_Number INTEGER UNIQUE CHECK (Council_Seat_Number BETWEEN 1 AND 12),
    Palace_Location TEXT,
    FOREIGN KEY (Divine_ID) REFERENCES God(Divine_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: Chthonic_God
-- Represents underworld and earth deities
CREATE TABLE IF NOT EXISTS Chthonic_God (
    Divine_ID INTEGER PRIMARY KEY,
    Underworld_Domain TEXT,
    Associated_River TEXT,
    FOREIGN KEY (Divine_ID) REFERENCES God(Divine_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: Primordial
-- Represents the ancient primordial deities
CREATE TABLE IF NOT EXISTS Primordial (
    Divine_ID INTEGER PRIMARY KEY,
    Creation_Aspect TEXT,
    Era_of_Power TEXT,
    FOREIGN KEY (Divine_ID) REFERENCES God(Divine_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================
-- SUBCLASS TABLES (Monster Hierarchy)
-- =====================================================

-- Table: Beast
-- Represents physical monster creatures
CREATE TABLE IF NOT EXISTS Beast (
    Monster_ID INTEGER PRIMARY KEY,
    Physical_Description TEXT,
    Natural_Habitat TEXT,
    FOREIGN KEY (Monster_ID) REFERENCES Monster(Monster_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: Titan
-- Represents the powerful Titan entities
CREATE TABLE IF NOT EXISTS Titan (
    Monster_ID INTEGER PRIMARY KEY,
    Titan_Name TEXT NOT NULL,
    Domain_of_Rule TEXT,
    Imprisonment_Location TEXT,
    FOREIGN KEY (Monster_ID) REFERENCES Monster(Monster_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: Spirit
-- Represents ethereal and spiritual entities
CREATE TABLE IF NOT EXISTS Spirit (
    Monster_ID INTEGER PRIMARY KEY,
    Ethereal_Form INTEGER DEFAULT 1,
    Binding_Object TEXT,
    FOREIGN KEY (Monster_ID) REFERENCES Monster(Monster_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================
-- WEAK ENTITY TABLES
-- =====================================================

-- Table: Quest_Log
-- Weak entity: Links demigods to quests with their roles
CREATE TABLE IF NOT EXISTS Quest_Log (
    Hero_ID INTEGER,
    Quest_ID INTEGER,
    Role TEXT,
    Outcome TEXT DEFAULT 'Ongoing' CHECK (Outcome IN ('Survived', 'Deceased', 'Abandoned', 'Ongoing')),
    PRIMARY KEY (Hero_ID, Quest_ID),
    FOREIGN KEY (Hero_ID) REFERENCES Demigod(Hero_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Quest_ID) REFERENCES Quest(Quest_ID)
        ON DELETE CASCADE  -- If quest deleted, remove all participant logs
        ON UPDATE CASCADE
);

-- Table: Sighting_Log
-- Weak entity: Tracks specific monster sightings
CREATE TABLE IF NOT EXISTS Sighting_Log (
    Monster_ID INTEGER,
    Sighting_Timestamp TEXT,
    Location TEXT NOT NULL,
    Reported_By INTEGER,
    PRIMARY KEY (Monster_ID, Sighting_Timestamp),
    FOREIGN KEY (Monster_ID) REFERENCES Monster(Monster_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Reported_By) REFERENCES Demigod(Hero_ID)
        ON DELETE SET NULL  -- Preserve sighting even if reporter deleted
        ON UPDATE CASCADE
);

-- =====================================================
-- MULTI-VALUED ATTRIBUTE TABLES
-- =====================================================

-- Table: Known_Abilities
-- Stores the multi-valued abilities of demigods
CREATE TABLE IF NOT EXISTS Known_Abilities (
    Hero_ID INTEGER,
    Ability TEXT,
    PRIMARY KEY (Hero_ID, Ability),
    FOREIGN KEY (Hero_ID) REFERENCES Demigod(Hero_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: Known_Weaknesses
-- Stores the multi-valued weaknesses of monsters
CREATE TABLE IF NOT EXISTS Known_Weaknesses (
    Monster_ID INTEGER,
    Weakness TEXT,
    PRIMARY KEY (Monster_ID, Weakness),
    FOREIGN KEY (Monster_ID) REFERENCES Monster(Monster_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: Common_Habitats
-- Stores the multi-valued habitats where monsters are found
CREATE TABLE IF NOT EXISTS Common_Habitats (
    Monster_ID INTEGER,
    Habitat TEXT,
    PRIMARY KEY (Monster_ID, Habitat),
    FOREIGN KEY (Monster_ID) REFERENCES Monster(Monster_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: Magical_Properties
-- Stores the multi-valued magical properties of divine artifacts
CREATE TABLE IF NOT EXISTS Magical_Properties (
    Artifact_ID INTEGER,
    Property TEXT,
    PRIMARY KEY (Artifact_ID, Property),
    FOREIGN KEY (Artifact_ID) REFERENCES Divine_Artifact(Artifact_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================
-- RELATIONSHIP TABLES (M:N Relationships)
-- =====================================================

-- Table: Encounters
-- M:N relationship: Tracks which demigods have encountered which monsters
CREATE TABLE IF NOT EXISTS Encounters (
    Hero_ID INTEGER,
    Monster_ID INTEGER,
    Encounter_Date TEXT,
    Location TEXT,
    Outcome TEXT CHECK (Outcome IN ('Victory', 'Defeat', 'Escape', 'Stalemate')),
    PRIMARY KEY (Hero_ID, Monster_ID, Encounter_Date),
    FOREIGN KEY (Hero_ID) REFERENCES Demigod(Hero_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Monster_ID) REFERENCES Monster(Monster_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: Combat_Encounter
-- Complex M:N relationship: Specific combat events involving demigod, artifact, monster, and quest
CREATE TABLE IF NOT EXISTS Combat_Encounter (
    Encounter_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Hero_ID INTEGER NOT NULL,
    Artifact_ID INTEGER,
    Monster_ID INTEGER NOT NULL,
    Quest_ID INTEGER,
    Combat_Date TEXT NOT NULL,
    Combat_Location TEXT,
    Result TEXT CHECK (Result IN ('Hero Victory', 'Monster Victory', 'Draw', 'Interrupted')),
    Notes TEXT,
    FOREIGN KEY (Hero_ID) REFERENCES Demigod(Hero_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Artifact_ID) REFERENCES Divine_Artifact(Artifact_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (Monster_ID) REFERENCES Monster(Monster_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Quest_ID) REFERENCES Quest(Quest_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Table: Rescue_Mission
-- Complex M:N relationship: Captures rescue missions involving demigods, quests, gods, and monsters
CREATE TABLE IF NOT EXISTS Rescue_Mission (
    Mission_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Hero_ID INTEGER NOT NULL,
    Quest_ID INTEGER NOT NULL,
    God_Being_Rescued INTEGER,
    Captor_Monster_ID INTEGER,
    Mission_Date TEXT NOT NULL,
    Mission_Location TEXT,
    Mission_Success INTEGER,
    FOREIGN KEY (Hero_ID) REFERENCES Demigod(Hero_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Quest_ID) REFERENCES Quest(Quest_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (God_Being_Rescued) REFERENCES God(Divine_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (Captor_Monster_ID) REFERENCES Monster(Monster_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- =====================================================
-- CREATE INDEXES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_demigod_divine_parent ON Demigod(Divine_Parent_ID);
CREATE INDEX IF NOT EXISTS idx_demigod_status ON Demigod(Status);
CREATE INDEX IF NOT EXISTS idx_monster_threat_level ON Monster(Threat_Level);
CREATE INDEX IF NOT EXISTS idx_prophecy_status ON Prophecy(Status);
CREATE INDEX IF NOT EXISTS idx_prophecy_date_issued ON Prophecy(Date_Issued);
CREATE INDEX IF NOT EXISTS idx_quest_prophecy ON Quest(Prophecy_ID);
CREATE INDEX IF NOT EXISTS idx_quest_outcome ON Quest(Outcome);
CREATE INDEX IF NOT EXISTS idx_artifact_wielder ON Divine_Artifact(Current_Wielder);
CREATE INDEX IF NOT EXISTS idx_sighting_location ON Sighting_Log(Location);
CREATE INDEX IF NOT EXISTS idx_sighting_timestamp ON Sighting_Log(Sighting_Timestamp);
CREATE INDEX IF NOT EXISTS idx_encounter_date ON Encounters(Encounter_Date);
CREATE INDEX IF NOT EXISTS idx_combat_date ON Combat_Encounter(Combat_Date);
CREATE INDEX IF NOT EXISTS idx_combat_hero ON Combat_Encounter(Hero_ID);
CREATE INDEX IF NOT EXISTS idx_combat_monster ON Combat_Encounter(Monster_ID);
CREATE INDEX IF NOT EXISTS idx_mission_date ON Rescue_Mission(Mission_Date);
CREATE INDEX IF NOT EXISTS idx_mission_quest ON Rescue_Mission(Quest_ID);

-- =====================================================
-- END OF SCHEMA
-- =====================================================
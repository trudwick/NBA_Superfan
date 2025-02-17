import mysql.connector
from mysql.connector import errorcode

# MySQL connection parameters
host = "localhost"
user = "root"
password = ""  # Use your actual MySQL password here
database = "NBA_Superfan"  # Replace with your database name

# SQL queries to create the tables
create_nba_good_games_table = """
CREATE TABLE IF NOT EXISTS NBA_Good_Games (
    date DATE,
    game_id INT PRIMARY KEY,
    team1 VARCHAR(255),
    team2 VARCHAR(255),
    game_score INT
);
"""

create_saved_dates_table = """
CREATE TABLE IF NOT EXISTS Saved_Dates (
    date DATE PRIMARY KEY,
    last_saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    finished BOOLEAN DEFAULT FALSE
);
"""

def create_tables():
    try:
        # Establish a connection to the MySQL server
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
        cursor = conn.cursor()

        # Execute the table creation queries
        print("Creating tables...")
        cursor.execute(create_nba_good_games_table)
        cursor.execute(create_saved_dates_table)

        # Commit the changes
        conn.commit()

        print("Tables created successfully.")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied: Check your username or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist.")
        else:
            print(f"Error: {err}")
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()

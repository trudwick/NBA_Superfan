import mysql.connector
import json

# Replace these values with your database information
"""
    On pythonanywhere:
        host = "trudwick.mysql.pythonanywhere-services.com"
        user = "trudwick"
        password = "tmr_sql_pw"
        database = "trudwick$default"
"""
host = "localhost"
user = ""
password = ""
database = "NBA_Superfan"
# host = "trudwick.mysql.pythonanywhere-services.com"
# user = "trudwick"
# password = "tmr_sql_pw"
# database = "trudwick$default"

def add_games():
    # Establish a connection to the MySQL server
    conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    f = open('output.txt')
    data = json.load(f)
    for matchup_str in data:
        insert_game_into_table(conn, cursor, matchup_str)

    if conn.is_connected():
        cursor.close()
        conn.close()
    # return good


def insert_game_into_table(conn, cursor, matchup):
    try:
        query = "INSERT INTO NBA_Good_Games (date, game_id, team1, team2) VALUES (%s, %s, %s, %s)"
        values = (matchup['date'], matchup['game_id'], matchup['team1'], matchup['team2'])
        cursor.execute(query, values)
        conn.commit()
        print("Game inserted into the table successfully:",matchup)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        print("game was:",matchup)


if __name__ == "__main__":
    add_games()
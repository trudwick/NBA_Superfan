import mysql.connector
import json


# Replace these values with your database information

# On pythonanywhere:
# host = "trudwick.mysql.pythonanywhere-services.com"
# user = "trudwick"
# password = "tmr_sql_pw"
# database = "trudwick$default"
# # local:
host = "localhost"
user = "root"
password = ""
database = "NBA_Superfan"


def query_date(date_in):
    # Establish a connection to the MySQL server
    conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    # Example query: Select all rows from the NBA_Good_Games table
    query = "SELECT * FROM NBA_Good_Games WHERE date = '{0}'".format(date_in)
    print(query)
    # Execute the query
    cursor.execute(query)
    # Fetch all the rows
    rows = cursor.fetchall()
    # Iterate over the rows and print the results
    result_list = []
    for row in rows:
        result_dict = {
            "date": str(row[1]),  # Convert date to string if needed
            "game_id": row[2],
            "team1": row[3],
            "team2": row[4],
            "game_score": row[5]  # Add more columns as needed
        }
        result_list.append(result_dict)
    result_json = json.dumps(result_list, indent=2)
    print(result_json)

    # Close the cursor and connection
    cursor.close()
    conn.close()

def remove_date(date_in):
    # Establish a connection to the MySQL server
    conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    # query = "DELETE FROM NBA_Good_Games WHERE date = '{0}'".format(date_in)
    # print(query)
    # cursor.execute(query)
    print("DELETE FROM %s WHERE date = '%s'" % ('NBA_Good_Games', date_in))
    print("DELETE FROM %s WHERE date = '%s'" % ('Saved_Dates', date_in))
    cursor.execute("DELETE FROM %s WHERE date = '%s'" % ('NBA_Good_Games', date_in))
    conn.commit()
    cursor.execute("DELETE FROM %s WHERE date = '%s'" % ('Saved_Dates', date_in))
    conn.commit()
    # print(query2)
    # cursor.execute(query2)
    # Fetch all the rows
    # Close the cursor and connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    action = int(input("1 for delete date\n2 for query date\n"))
    print(action)
    date_in = input("Enter date in format YYYY-MM-DD:")
    print(date_in)
    if action == 1:
        remove_date(date_in)
    else:
        query_date(date_in)
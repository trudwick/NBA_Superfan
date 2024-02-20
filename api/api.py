#guide: https://blog.miguelgrinberg.com/post/how-to-create-a-react--flask-project
#if I have problems: chrome://net-internals/#sockets -> flush
from flask import Flask, request
import flask
from nba_api.stats.static import teams
from nba_api.stats.static import players
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import playbyplay
from nba_api.live.nba.endpoints import scoreboard
from datetime import date,datetime,timedelta
import mysql.connector
import time
import json

"""
    activate virtual environment
        python3 -m venv venv
        source venv/bin/activate
    install important things:
        pip install flask python-dotenv
        pip install nba_api
        pip install pandas
    set flask env variables:
        export FLASK_APP=api.py
        FLASK_ENV=development
    run flask:
        flask run
    example url to test with:
        http://127.0.0.1:5000/getgames?date=2023-01-17
"""

app = Flask(__name__)
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

@app.route('/api/getgames', methods=['GET'])
def get_games_getgames():
    """
        handle arguments:
            start_date: "YYYY-MM-DD"    (default: yesterday)
            end_date:   "YYYY-MM-DD"    (default: yesterday)
            num_games:  int             (default:12)
            teams:      PHX,WAS,...     (default:"")
            sort_by:    date,game_score (default:"date")
    """
    default_date = str(date.today()-timedelta(days = 1)) #use yesterday
    start_date = request.args.get('start_date',default= default_date)
    print('start_date',start_date)
    end_date = request.args.get('end_date',default=default_date)
    print('end_date',end_date)
    num_games = request.args.get('num_games',default= 20, type=int)
    # if num_games>15:
    #     num_games=15
    print('num_games',num_games)
    teams=request.args.get('teams',default="", type=str)
    print('teams',teams)
    teams_long = convertTeamsShortToLong(teams)
    sort_by=request.args.get('sort_by',default="date", type=str)
    print('sort_by',sort_by)
    print("INPUTS:",start_date,end_date,num_games,teams,sort_by)


    # Establish a connection to the MySQL server
    conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    fill_dates(conn, cursor, start_date,end_date)
    
    # Example query: Select all rows from the NBA_Good_Games table
    query_p1 = ("SELECT * FROM NBA_Good_Games WHERE \n"
            "date BETWEEN '{0}' AND '{1}'  \n")
    query_p2 = "AND ( (team1 in ({2})) OR (team2 in ({2}))) \n"
    query_p3 = "ORDER BY game_score DESC limit {3}"
    query = query_p1
    if teams_long != "":
        query+=query_p2
    query+=query_p3
    query_with_args = query.format(start_date,end_date,str(teams_long)[1:-1],num_games)
    print(query_with_args)
    # Execute the query
    cursor.execute(query_with_args)
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
    # response = json.dumps(result_list, indent=2)
    response = response = flask.jsonify(result_list)
    # print(response)

    # Close the cursor and connection
    cursor.close()
    conn.close()
    response.headers.add('Access-Control-Allow-Origin', '*')
    print(response)
    return response

def fill_dates(conn, cursor, start_date,end_date):
    print("fill_dates")
    query = "SELECT date FROM Saved_Dates WHERE date BETWEEN '{0}' AND '{1}' ORDER BY date".format(start_date,end_date)
    # Execute the query
    cursor.execute(query)
    # Fetch all the rows
    saved_dates_rows = cursor.fetchall()
    saved_dates_rows = [i[0] for i in saved_dates_rows]
    end_date=datetime.strptime(end_date,'%Y-%m-%d').date()
    start_date=datetime.strptime(start_date,'%Y-%m-%d').date()
    day_count = (end_date - start_date).days + 1
    for single_date in [d for d in (start_date + timedelta(n) for n in range(day_count)) if d <= end_date]:
        # single_date = single_datetime.date()
        cur_date = single_date.strftime('%Y-%m-%d')
        
        if single_date not in saved_dates_rows:
            print('single_date')
            print(single_date)
            add_date(conn, cursor, cur_date)

def add_date(conn,cursor,game_date):
    gamefinder = leaguegamefinder.LeagueGameFinder()
    games = gamefinder.get_data_frames()[0]

    games_filtered = games
    #this next line matches the game date
    games_filtered = games.loc[(games['GAME_DATE']==game_date) & (games['GAME_ID'].astype(str).str[0]=='0')]
    games_filtered = games_filtered.drop_duplicates(subset=['GAME_ID'])
    games_filtered = games_filtered.sort_values('GAME_ID')

    for game_id in zip(games_filtered['GAME_ID']):  #loop over games
        game_id_no = game_id[0]
        print('our game')
        
        game_score = getGameScore(game_id_no)
        if game_score>0:
            teams = games[games["GAME_ID"]==game_id_no]['TEAM_NAME'].tolist()
            matchup_str={
                "team1":teams[0],
                "team2":teams[1],
                "date":games[games["GAME_ID"]==game_id_no].iloc[0]['GAME_DATE'],
                "game_id":game_id_no,
                "game_score":game_score
            }
            print(matchup_str)
            insert_game_into_table(conn, cursor, matchup_str)
    insert_date_into_table(conn,cursor,game_date)

def getGameScore(game_id):
    time.sleep(0.5)
    print('getting game score for:',game_id)
    pbp = playbyplay.PlayByPlay(game_id).get_data_frames()[0]
    pbp_q4_and_beyond = pbp.loc[(pbp['PERIOD']>=4) &
                     (pbp['PCTIMESTRING'].astype(str).str[0]<'5')&
                     (pbp['PCTIMESTRING'].astype(str).str[1]==':')]
    pbp_q4_and_beyond=pbp_q4_and_beyond[['PERIOD','PCTIMESTRING','SCOREMARGIN']].dropna().replace("TIE",0)
    pbp_q4_and_beyond['SCOREMARGIN']=pbp_q4_and_beyond['SCOREMARGIN'].astype(int)
    
    scores_as_list = pbp_q4_and_beyond.values.tolist()
    if len(scores_as_list) == 0:    #weird games that don't have fourth quarters or any scoring in last 5 minutes
        return 0
    game_score = 0
    if scores_as_list[0][2] > 0:
        up=1
    elif scores_as_list[0][2] < 0:
        up=-1
    else:
        up=0
    by_minute={}
    for pd in range(4,pbp['PERIOD'].max()+1):
        by_minute[pd]=[5,5,5,5,5]
    print(by_minute)
    for x in scores_as_list:
        print(x)
    for x in range(1,len(scores_as_list)):  #format: period, PCTIMESTRING, margin
        x_pd = scores_as_list[x][0]
        x_minute = int(scores_as_list[x][1][0])
        if scores_as_list[x][1][0]!=scores_as_list[x-1][1][0]:
            by_minute[x_pd][x_minute]=abs(scores_as_list[x-1][2])
        by_minute[x_pd][x_minute]=min(by_minute[x_pd][x_minute],abs(scores_as_list[x][2]))
    for x in by_minute:
        for closest in by_minute[x]:
            game_score+=max(0,5-closest)
    for row in scores_as_list:  #format: period, PCTIMESTRING, margin
        value = row[2]
        if value==0:
            if up!=0:
                game_score+=1
            up=0
        elif value>0:
            if up<=0:
                game_score+=1
            up=1
        else:
            if up>=0:
                game_score+=1
            up=-1
    return game_score

def insert_game_into_table(conn, cursor, matchup):
    query = "INSERT IGNORE INTO NBA_Good_Games (date, game_id, team1, team2,game_score) VALUES (%s, %s, %s, %s, %s)"
    values = (matchup['date'], matchup['game_id'], matchup['team1'], matchup['team2'], matchup['game_score'])
    cursor.execute(query, values)
    conn.commit()

def insert_date_into_table(conn, cursor, date):
    query = "INSERT IGNORE INTO Saved_Dates (date) VALUES (%s)"
    values = (date,)
    cursor.execute(query, values)
    conn.commit()

def main():
    game_date = input("Input date in the format YYYY-MM-DD. (leave blank for yesterday):")
    if game_date=='':
        game_date=str(date.today()-timedelta(days = 1)) #use yesterday

def insert_game_into_good_games_table(conn,cursor,matchup):
    try:

        # Insert the game into the MySQL table
        query = "INSERT INTO NBA_Good_Games (date, game_id, team1, team2, game_score) VALUES (%s, %s, %s, %s, %s)"
        values = (matchup["date"], matchup["game_id"], matchup["team1"], matchup["team2"], 0)  # Assuming initial game_score is 0
        cursor.execute(query, values)

        conn.commit()
        # print("Game inserted into the table successfully")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

def convertTeamsShortToLong(teams_short):
    teams_short=teams_short.split(",")
    print(teams_short)
    if "" in teams_short:
        return ""
    teams_long = []
    teams_map = {}
    teams_map["ATL"] = "Atlanta Hawks"
    teams_map["BOS"] = "Boston Celtics"
    teams_map["BKN"] = "Brooklyn Nets"
    teams_map["CHA"] = "Charlotte Hornets"
    teams_map["CHI"] = "Chicago Bulls"
    teams_map["CLE"] = "Cleveland Cavaliers"
    teams_map["DAL"] = "Dallas Mavericks"
    teams_map["DEN"] = "Denver Nuggets"
    teams_map["DET"] = "Detroit Pistons"
    teams_map["GSW"] = "Golden State Warriors"
    teams_map["HOU"] = "Houston Rockets"
    teams_map["IND"] = "Indiana Pacers"
    teams_map["LAC"] = "Los Angelas Clippers"
    teams_map["LAL"] = "Los Angeles Lakers"
    teams_map["MEM"] = "Memphis Grizzlies"
    teams_map["MIA"] = "Miami Heat"
    teams_map["MIL"] = "Milwaukee Bucks"
    teams_map["MIN"] = "Minnesota Timberwolves"
    teams_map["NOP"] = "New Orleans Pelicans"
    teams_map["NYK"] = "New York Knicks"
    teams_map["OKC"] = "Oklahoma City Thunder"
    teams_map["ORL"] = "Orlando Magic"
    teams_map["PHI"] = "Philadelphia 76ers"
    teams_map["PHX"] = "Phoenix Suns"
    teams_map["POR"] = "Portland Trail Blazers"
    teams_map["SAC"] = "Sacramento Kings"
    teams_map["SAS"] = "San Antonio Spurs"
    teams_map["TOR"] = "Toronto Raptors"
    teams_map["UTA"] = "Utah Jazz"
    teams_map["WAS"] = "Washington Wizards"
    for team in teams_short:
        teams_long.append(teams_map[team])
    return teams_long

if __name__ == "__main__":
    main()
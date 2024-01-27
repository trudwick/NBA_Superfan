#guide: https://blog.miguelgrinberg.com/post/how-to-create-a-react--flask-project
#if I have problems: chrome://net-internals/#sockets -> flush
from flask import Flask, request
import flask
from nba_api.stats.static import teams
from nba_api.stats.static import players
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import playbyplay
from nba_api.live.nba.endpoints import scoreboard
from datetime import date
from datetime import timedelta
import time

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

@app.route('/api/getgames', methods=['GET'])
def get_games_getgames():
    default_date = str(date.today()-timedelta(days = 1)) #use yesterday
    start_date = request.args.get('start_date',default= default_date)
    print('start_date',start_date)
    end_date = request.args.get('end_date',default=default_date)
    print('end_date',end_date)
    num_games = request.args.get('num_games',default= 5, type=int)
    if num_games>15:
        num_games=15
    print('num_games',num_games)
    teams=request.args.get('teams',default="", type=str)
    print('teams',teams)
    response = flask.jsonify(goodGamesFromDate(start_date,end_date,num_games,teams))
    response.headers.add('Access-Control-Allow-Origin', '*')
    print(response)
    return response

def goodGamesFromDate(start_date,end_date,num_games=5,teams=""):
    gamefinder = leaguegamefinder.LeagueGameFinder()
    games = gamefinder.get_data_frames()[0]

    # games_2023 = games[] 
    games_filtered = games.loc[(games['GAME_DATE']>=start_date) & (games['GAME_DATE']<=end_date)  & (games['GAME_ID'].astype(str).str[0]=='0')]
    if teams!="":
        teamcode_list = teams.split(",")
        teamcode_list.remove("")
        games_filtered=games_filtered.loc[(games_filtered["TEAM_ABBREVIATION"].isin(teamcode_list))]
    # print(games_filtered['GAME_DATE'])
    games_filtered = games_filtered.drop_duplicates(subset=['GAME_ID'])
    games_filtered = games_filtered.sort_values('GAME_ID')
    print("\n\nTotal games on this date:",len(games_filtered))
    if len(games_filtered)==0:
        print ("No games found on this date :(. Try again!")
        return
    game_id = games_filtered.sort_values('GAME_ID').iloc[0]['GAME_ID']

    # print(games_filtered.columns)
    good=[]
    for game_id, team_name in zip(games_filtered['GAME_ID'], games_filtered['TEAM_NAME']):
        teams = games[games["GAME_ID"]==game_id]['TEAM_NAME'].tolist()
        matchup_str={
                        "team1":teams[0],
                        "team2":teams[1],
                        "date":games['GAME_DATE'],
                        "game_id":game_id
                    }
        if gameIsGood(game_id):
            good.append(matchup_str)
    return good

def gameIsGood(game_id):
    pbp = playbyplay.PlayByPlay(game_id).get_data_frames()[0]
    pbp_q4 = pbp.loc[ (pbp['PERIOD']==4) &(pbp['PCTIMESTRING'].astype(str).str[0]<'4')&(pbp['PCTIMESTRING'].astype(str).str[1]==':')]     # 
    
    for play in pbp_q4['SCOREMARGIN']:
        if play is not None and (play == "TIE" or abs(int(play))<5):
            return True
    return False

def main():
    query_type = input("Enter a number 1 through 3:\n1 for by date\n2 for by team\n3 for by huge performance\n")
    if query_type=='1':
        game_date = input("Input date in the format YYYY-MM-DD. (leave blank for yesterday):")
        if game_date=='':
            game_date=str(date.today()-timedelta(days = 1)) #use yesterday
        print('Games for date:',game_date)
        print(goodGamesFromDate(game_date))
    elif query_type=='2':
        teamcodes = input("Enter team(s) by 3 letter code, comma seperated. (leave blank for DEN):")
        if teamcodes=="":
            teamcodes="DEN"
        numgames = input("Enter the number of games. (leave blank for 5 by default)")
        try:
            numgames=int(numgames)
        except:
            numgames=5
        print(goodGamesByTeamCode(teamcodes,numgames))

if __name__ == "__main__":
    main()
    # print(scoreboard.ScoreBoard().get_json())
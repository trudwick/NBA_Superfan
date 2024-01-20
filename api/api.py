#guide: https://blog.miguelgrinberg.com/post/how-to-create-a-react--flask-project
#if I have problems: chrome://net-internals/#sockets -> flush
from flask import Flask, request
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
        http://127.0.0.1:5000/from_date?date=2023-01-17
"""

app = Flask(__name__)

@app.route('/from_date')
def get_games_from_date():
    return goodGamesFromDate(request.args.get('date'))
@app.route('/by_team')
def get_games_by_team():
    teamcode=request.args.get('team')
    numgames=request.args.get('numGames')
    try:
        numgames=int(numgames)
    except:
        numgames=5
    return goodGamesByTeamCode(request.args.get('team'),numgames)

def goodGamesFromDate(gameDate):
    gamefinder = leaguegamefinder.LeagueGameFinder()
    games = gamefinder.get_data_frames()[0]

    # games_2023 = games[] 
    games_on_date = games.loc[(games['GAME_DATE']==gameDate)  & (games['GAME_ID'].astype(str).str[0]=='0')]
    # print(games_on_date['GAME_DATE'])
    games_on_date = games_on_date.drop_duplicates(subset=['GAME_ID'])
    games_on_date = games_on_date.sort_values('GAME_ID')
    print("\n\nTotal games on this date:",len(games_on_date))
    if len(games_on_date)==0:
        print ("No games found on this date :(. Try again!")
        return
    game_id = games_on_date.sort_values('GAME_ID').iloc[0]['GAME_ID']

    # print(games_on_date.columns)
    good=[]
    for game_id, team_name in zip(games_on_date['GAME_ID'], games_on_date['TEAM_NAME']):
        teams = games[games["GAME_ID"]==game_id]['TEAM_NAME'].tolist()
        matchup_str={
                        "team1":teams[0],
                        "team2":teams[1],
                        "date":gameDate,
                        "game_id":game_id
                    }
        if gameIsGood(game_id):
            good.append(matchup_str)
    return good

def goodGamesByTeamCode(teamcode,num_games):
    gamefinder = leaguegamefinder.LeagueGameFinder()
    # gamefinder = leaguegamefinder.LeagueGameFinder(date_from_nullable='2023-01-14')
    # The first DataFrame of those returned is what we want.
    teamcode_list = teamcode.split(",")
    games = gamefinder.get_data_frames()[0]
    nba_games = games.loc[(games['GAME_ID'].astype(str).str[0]=='0') & games["TEAM_ABBREVIATION"].isin(teamcode_list)]
    filtered_games = nba_games.drop_duplicates(subset=['GAME_ID'])
    good=[]
    for game_id, team_name in zip(filtered_games['GAME_ID'], filtered_games['TEAM_NAME']):
        teams = games[games["GAME_ID"]==game_id]['TEAM_NAME'].tolist()
        matchup_str={   
                        "team1":teams[0],
                        "team2":teams[1],
                        "date":games[games["GAME_ID"]==game_id].iloc[0]['GAME_DATE'],
                        "game_id":game_id
                     }
        if gameIsGood(game_id):
            good.append(matchup_str)
            if len(good)>=num_games:
                break
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
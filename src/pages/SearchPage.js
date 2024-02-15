import React, { useState } from 'react'
import $ from 'jquery'



function SearchPage() {
  const [gameData,setGameData] = useState([])
  const [showGameScore, setShowGameScore] = useState(false);
  const handleChange = () => {
    setShowGameScore(!showGameScore);
  };
  

  function handleSubmit(e) {
    e.preventDefault();
    console.log("start:"+$("#start_date").val())
    let end_date = $("#end_date").val()
    console.log("end_date:"+end_date)
    console.log("teams:"+$("#teams").val())
    // fetch(`/from_date?date=${encodeURIComponent(end_date)}`)

    fetch(`/api/getgames?start_date=${encodeURIComponent($("#start_date").val())}&end_date=${encodeURIComponent(end_date)}&teams=${encodeURIComponent($("#teams").val())}`)
    .then(res => res.json())  // Corrected handling of the response
    .then(data => {
      console.log(data);
      setGameData(data);
    })
    .catch(error => console.error('Error fetching data:', error));

    // fetch(`/from_date?date=2024-01-16`)
    //     .then(res => {res.json()})
    //     .then(data => { 
    //       console.log(data)
    //       setGameData(data)
    //     })
  }
  var curr = new Date();
  curr.setDate(curr.getDate() - 1);
  var date = curr.toISOString().substring(0,10);
  
  return (
    <div>
      <form className="search" onSubmit={handleSubmit}>
        
        <p className="search-date">
          <label>Start Date:</label><input type="date" id="start_date" defaultValue={date} />
          <label>End Date:</label><input type="date" id="end_date" defaultValue={date} />
        </p>
        <TeamSelect />
        <div className='buttonHolder'>
          <button type="submit">Search</button>
        </div>
        
      </form>
      <div className='buttonHolder'>
        <label>
          <input type="checkbox" showGameScore={showGameScore} onChange={handleChange}/>
          Show Game Score
        </label>
      </div>
      <div className="search-output">
        {gameData.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Team 1</th>
                <th>Team 2</th>
                <th>NBA.com league pass link</th>
                {showGameScore?<th>Game Score</th>:""}
              </tr>
            </thead>
            <tbody>
              {gameData.map((game, index) => (
                <tr key={index}>
                  <td>{game.date}</td>
                  <td>{game.team1}</td>
                  <td>{game.team2}</td>
                  <td><a href={`https://www.nba.com/game/${game.game_id}?watch`} target="_blank" rel="noopener noreferrer">Click to watch game</a></td>
                  {showGameScore?<td>{game.game_score}</td>:""}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );

}
function TeamSelect(){
  return (
    <select className="search-teams" id="teams" name="teams" multiple>
      <option value="">Select Teams</option>
      <option value="ATL">Atlanta Hawks</option>
      <option value="BOS">Boston Celtics</option>
      <option value="BKN">Brooklyn Nets</option>
      <option value="CHA">Charlotte Hornets</option>
      <option value="CHI">Chicago Bulls</option>
      <option value="CLE">Cleveland Cavaliers</option>
      <option value="DAL">Dallas Mavericks</option>
      <option value="DEN">Denver Nuggets</option>
      <option value="DET">Detroit Pistons</option>
      <option value="GSW">Golden State Warriors</option>
      <option value="HOU">Houston Rockets</option>
      <option value="IND">Indiana Pacers</option>
      <option value="LAC">Los Angelas Clippers</option>
      <option value="LAL">Los Angeles Lakers</option>
      <option value="MEM">Memphis Grizzlies</option>
      <option value="MIA">Miami Heat</option>
      <option value="MIL">Milwaukee Bucks</option>
      <option value="MIN">Minnesota Timberwolves</option>
      <option value="NOP">New Orleans Pelicans</option>
      <option value="NYK">New York Knicks</option>
      <option value="OKC">Oklahoma City Thunder</option>
      <option value="ORL">Orlando Magic</option>
      <option value="PHI">Philadelphia 76ers</option>
      <option value="PHX">Phoenix Suns</option>
      <option value="POR">Portland Trail Blazers</option>
      <option value="SAC">Sacramento Kings</option>
      <option value="SAS">San Antonio Spurs</option>
      <option value="TOR">Toronto Raptors</option>
      <option value="UTA">Utah Jazz</option>
      <option value="WAS">Washington Wizards</option>
    </select>
  )
}

export default SearchPage
import React, { useState } from 'react'
import $ from 'jquery'



function SearchPage() {
  const [gameData,setGameData] = useState([])
  

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
      <div className="search-output">
        {gameData.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Team 1</th>
                <th>Team 2</th>
                <th>NBA.com league pass link</th>
              </tr>
            </thead>
            <tbody>
              {gameData.map((game, index) => (
                <tr key={index}>
                  <td>{game.date}</td>
                  <td>{game.team1}</td>
                  <td>{game.team2}</td>
                  <td><a href={`https://www.nba.com/game/${game.game_id}?watch`} target="_blank" rel="noopener noreferrer">Click to watch game</a></td>
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
      <option value="ATL">Boston Celtics</option>
      <option value="BOS">Brooklyn Nets</option>
      <option value="BKN">New York Knicks</option>
      <option value="CHA">Philadelphia 76ers</option>
      <option value="CHI">Toronto Raptors</option>
      <option value="CLE">Chicago Bulls</option>
      <option value="DAL">Cleveland Cavaliers</option>
      <option value="DEN">Detroit Pistons</option>
      <option value="DET">Indiana Pacers</option>
      <option value="GSW">Milwaukee Bucks</option>
      <option value="HOU">Atlanta Hawks</option>
      <option value="IND">Charlotte Hornets</option>
      <option value="LAC">Miami Heat</option>
      <option value="LAL">Orlando Magic</option>
      <option value="MEM">Washington Wizards</option>
      <option value="MIA">Denver Nuggets</option>
      <option value="MIL">Minnesota Timberwolves</option>
      <option value="MIN">Oklahoma City Thunder</option>
      <option value="NOP">Portland Trail Blazers</option>
      <option value="NYK">Utah Jazz</option>
      <option value="OKC">Golden State Warriors</option>
      <option value="ORL">LA Clippers</option>
      <option value="PHI">Los Angeles Lakers</option>
      <option value="PHX">Phoenix Suns</option>
      <option value="POR">Sacramento Kings</option>
      <option value="SAC">Dallas Mavericks</option>
      <option value="SAS">Houston Rockets</option>
      <option value="TOR">Memphis Grizzlies</option>
      <option value="UTA">New Orleans Pelicans</option>
      <option value="WAS">San Antonio Spurs</option>
    </select>
  )
}

export default SearchPage
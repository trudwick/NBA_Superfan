import React from 'react'
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <div className="navbar">
        <div className="logo">
            NBA Superfan
        </div>
        <ul className="navbar-menu">
            <li><Link to="/">Home</Link></li>
            <li><Link to="/Search">Game Search</Link></li>
        </ul>
    </div>
  )
}

export default Navbar
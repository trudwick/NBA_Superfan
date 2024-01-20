import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import Navbar from './components/Navbar';
import SearchPage from './pages/SearchPage';
import reportWebVitals from './reportWebVitals';
import Home from './pages/Home';
import {
  BrowserRouter,
  createBrowserRouter,
  RouterProvider,
  Route,
  Routes
} from "react-router-dom";

// const router = createBrowserRouter([
//   {
//     path: "/",
//     element: <App/>,
//   },
//   {
//     path:"Search",
//     element: <SearchPage/>
//   }
// ]);


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <BrowserRouter>
    <Navbar/>
    {/* <RouterProvider router={router}/> */}
    <Routes>
      <Route path="/" element={<Home/>}/>
      <Route path="/Search" element={<SearchPage/>}/>
    </Routes>
  </BrowserRouter>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();

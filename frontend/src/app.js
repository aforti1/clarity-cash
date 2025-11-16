// src/App.js
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import LoginPage from "../loginPage";
import Dashboard from "./Dashboard";  // Your dashboard component

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;

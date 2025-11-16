import React from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import LoginPage from "./LoginPage";

// Define the types for route components (optional, TypeScript can infer these in most cases)
const App: React.FC = () => {
  return (
    <Router>
      <Switch>
        <Route path="/" exact component={LoginPage} />
        {/* Add more routes here for your other pages */}
      </Switch>
    </Router>
  );
};

export default App;

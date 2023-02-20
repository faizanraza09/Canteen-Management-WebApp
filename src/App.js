import React,{useContext} from 'react'
import './App.css';
import {LoginProvider} from './Contexts/LoginContext'
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useParams,
  Redirect
  
} from "react-router-dom"
import { Home } from './Pages/Home';
import {LoginContext} from './Contexts/LoginContext'
import {Login} from './Pages/Login'
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const {loggedUser} = useContext(LoginContext)

  const [user,domain] = loggedUser.split('@')

  return (
      <div className="App"> 
        <Router>
          <Switch>
            <Route exact path='/login'>
              <Login/>            
            </Route> 
            {!loggedUser&&<Redirect to="/login" />}      
            <Route path='/:domain/:user/home/:activity?'>
              <Home/>
            </Route>
            
          </Switch>
        </Router>    
      </div>
  );
}
/*export default App*/

export default function AppWrapper() {
  return (
    <LoginProvider>
      <App />
    </LoginProvider>
  );
}


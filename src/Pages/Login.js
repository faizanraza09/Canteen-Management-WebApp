import React,{useContext} from 'react'
import {LoginForm} from '../Components/LoginForm'
import {LoginContext} from '../Contexts/LoginContext'


export const Login = () => {
    const {setLoggedUser}=useContext(LoginContext)
    return (
        <div>
            {/*<h1 style={{paddingTop:'3vh'}}>Canteen App</h1>*/}
            <LoginForm/>
        </div>
    )
}

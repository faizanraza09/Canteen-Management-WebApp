import React,{useState,useEffect,createContext} from 'react'
import App from '../App'

export const LoginContext=createContext()

export const LoginProvider = (props) => {
    const [loggedUser, setLoggedUser]=useState('')

    return (
        <LoginContext.Provider value={{loggedUser, setLoggedUser}}>
            {props.children}
        </LoginContext.Provider>

    )
}



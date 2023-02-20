import React,{useContext} from 'react'
import { Redirect, useParams } from 'react-router-dom'
import { CreateCanteenOwner } from '../Components/CreateCanteenOwner'
import { CreateStudentAccount } from '../Components/CreateStudentAccount'
import { ManageStudents } from '../Components/ManageStudents'
import {PrincipalNavbar} from '../Components/PrincipalNavbar'


export const Principal = () => {

    const {domain,activity} = useParams()

    const handleNavigation = () => {
        
        if (activity==='createcanteenowner') {
            return <CreateCanteenOwner/>
        }

        else if (activity==='createstudentaccount') {
            return <CreateStudentAccount/>
        }

        else if (activity==='managestudents') {
            return <ManageStudents/>
        }
    }

    return (      
        <div>
            <PrincipalNavbar/>
            <Redirect from={`/${domain}/principal/home`} to={`/${domain}/principal/home/createcanteenowner`}/>
            {handleNavigation()}
        </div>
    )
}

import React from 'react'
import { CreatePrincipal } from '../Components/CreatePrincipal'
import { AdminNavbar } from '../Components/AdminNavbar'

export const Admin = () => {
    return (
        <div>
            <AdminNavbar/>
            <CreatePrincipal/>     
        </div>
    )
}

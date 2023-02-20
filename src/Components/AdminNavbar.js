import React,{useContext} from 'react'
import {Navbar,Button} from 'react-bootstrap'
import {LoginContext} from '../Contexts/LoginContext'

export const AdminNavbar = () => {
    const {loggedUser,setLoggedUser} = useContext(LoginContext)

    const handleClick =() => {
        setLoggedUser('')
    }

    return (
        <div>
            <Navbar bg="light" expand="lg">
            <Navbar.Brand>{`admin@test`}</Navbar.Brand>
            <Button className='ml-auto' style={{marginRight:'5px'}} onClick={handleClick} variant="outline-success">Log out</Button>
            </Navbar>
        </div>
    )
}

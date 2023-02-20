import React,{useContext} from 'react'
import { Button,Navbar,Nav } from 'react-bootstrap'
import {NavLink,useParams} from 'react-router-dom'
import {LoginContext} from '../Contexts/LoginContext'



export const PrincipalNavbar = () => {
    
    const {domain} = useParams()
    const {setLoggedUser} = useContext(LoginContext)
    
    const handleClick =() => {
        setLoggedUser('')
    }

    return (
        <div>
            <Navbar bg="light" expand="lg">
            <Navbar.Brand>{`principal@${domain}`}</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="mr-auto">
                <Nav.Link style={{marginLeft:'5px', marginRight:'5px'}} as={NavLink} to={`/${domain}/principal/home/createcanteenowner`}>Create Canteen Owner</Nav.Link>
                <Nav.Link style={{marginLeft:'5px', marginRight:'5px'}} as={NavLink} to={`/${domain}/principal/home/createstudentaccount`}>Create Student Account</Nav.Link>
                <Nav.Link style={{marginLeft:'5px', marginRight:'5px'}} as={NavLink} to={`/${domain}/principal/home/managestudents`}>Manage Students</Nav.Link>
                </Nav>
                <Button style={{marginRight:'5px'}} onClick={handleClick} variant="outline-success">Log out</Button>
            </Navbar.Collapse>
            </Navbar>
        </div>
    )
}


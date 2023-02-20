import React, {useState, useContext} from 'react'
import {LoginContext} from '../Contexts/LoginContext'
import {useHistory} from 'react-router-dom'
import {Grid,Paper, Avatar, TextField, Button, CircularProgress} from '@material-ui/core'
import {Alert} from '@material-ui/lab'
import LockOutlinedIcon from '@material-ui/icons/LockOutlined';
import {makeStyles} from '@material-ui/core/styles'
import useMediaQuery from '@material-ui/core/useMediaQuery'



const useStyles=makeStyles({
    paperStyle: {
        padding:20,height:'auto',width:props=>props.width, margin:"auto"
    },
    avatarStyle:{
        backgroundColor:'green'
    }


})



export const LoginForm = () => {
    const matches = useMediaQuery('(min-width:600px)');
    const width = matches?400:280
    const classes =useStyles({'width':width})

    const [username,setUsername] = useState('')
    const [password,setPassword] = useState('')
    const [loading,setLoading] = useState(false)
    const [error,setError]= useState('')
    const [clicked,setClicked]=useState(false)


    const {loggedUser, setLoggedUser} = useContext(LoginContext)

    const [user,domain] = username.split('@')


    let history = useHistory()

    const handleSubmit = (event) =>{
        event.preventDefault()
        setError('')
        setClicked(true)
        setLoading(true)
        fetch('/api/login',{
            method:'POST',
            body: JSON.stringify({
                username:username,
                password:password
            }),
            headers:{
                "Content-type":"application/json; charset=UTF-8"
            }
        }).then(response => response.json())
        .then((message)=>{
            setLoading(false)
            if (message.hasOwnProperty(201)){
                setLoggedUser(message[201])
                history.push(`/${domain}/${user}/home`)
            }
            else {   
                setError(message[403])
                setClicked(false)            
            }
        })
    }



    return (
        /*<div>
            <form onSubmit={handleSubmit}>
                <input type='text' value={username} onChange={(x)=>setUsername(x.target.value)} placeholder='Username'/>
                <br/>
                <input style={{marginTop:10}}type='password' value={password} onChange={(x)=>setPassword(x.target.value)} placeholder='Password'/>
                <br/>
                <h4>{error}</h4>
                {!clicked&&<input type='submit' value='Log In'/>}             
            </form>
            <ClipLoader loading={loading}/>
            
            
        </div>*/

        <Grid style={{paddingTop:30}}>
            <Paper className={classes.paperStyle}elevation={10} >
                <Grid align='center'>
                    <Avatar className={classes.avatarStyle}><LockOutlinedIcon/></Avatar>
                    <h2>Sign In</h2>
                </Grid>
                <form onSubmit={handleSubmit}>
                    <TextField style={{marginTop:'20px'}} label='Username' placeholder='Enter username' value={username} onChange={(x)=>setUsername(x.target.value)} fullWidth required/>
                    <TextField style={{marginTop:'20px'}} label='Password' placeholder='Enter password' value={password} type='password' onChange={(x)=>setPassword(x.target.value)} fullWidth required/>
                    {loading&&<CircularProgress style={{marginTop:10}}/>}
                    {error&&<Alert style={{marginTop:'10px'}} severity='warning' onClose={()=>setError('')}>{error}</Alert>}
                    {!clicked&&<Button style={{margin:'20px 0'}} type='submit' color='primary' variant='contained' fullWidth>Log in</Button>}
                </form>
            </Paper>
        </Grid>
    )
}

import React, {useState} from 'react'
import {Grid,Paper, Avatar, TextField, Button, CircularProgress, InputAdornment} from '@material-ui/core'
import {Alert} from '@material-ui/lab'
import {makeStyles} from '@material-ui/core/styles'
import useMediaQuery from '@material-ui/core/useMediaQuery'
import {useParams} from 'react-router-dom'



const useStyles=makeStyles({
    paperStyle: {
        padding:20,height:'auto',width:props=>props.width, margin:"auto"
    },
    avatarStyle:{
        backgroundColor:'green'
    }


})


export const CreateCanteenOwner = () => {
    const matches = useMediaQuery('(min-width:600px)');
    const width = matches?400:280
    const classes =useStyles({'width':width})

    const {domain} = useParams()
    const [password,setPassword] = useState('')
    const [loading,setLoading] = useState(false)
    const [output,setOutput]= useState('')
    const [clicked,setClicked]=useState(false)
    const [variant,setVariant] = useState('')



    const handleSubmit =(event) => {
        event.preventDefault()
        setOutput('')
        setClicked(true)
        setLoading(true)
        fetch(`/api/${domain}/principal/home/createcanteenowner`,{
            method:'POST',
            body: JSON.stringify({
                password:password
            }),
            headers:{
                "Content-type":"application/json; charset=UTF-8"
            }
        }).then(response => response.json())
        .then((message)=>{
            setLoading(false)
            if (message.hasOwnProperty(201)){
                setVariant('success')
                setOutput(message[201])
                }
            else {
                setVariant('warning')
                setOutput(message[409])
            }
            setClicked(false)

        })
    }



    return (
        <Grid style={{paddingTop:30}}>
            <Paper className={classes.paperStyle}elevation={10} >
                <Grid align='center'>
                    <h2>Create Canteen Owner</h2>
                </Grid>
                <form onSubmit={handleSubmit}>
                    <TextField disabled style={{marginTop:'20px'}} label='Username' placeholder='Enter username' value={`canteen_owner@${domain}`} fullWidth required/>
                    <TextField style={{marginTop:'20px'}} label='Password' placeholder='Enter password' type='password' value={password} onChange={(x)=>setPassword(x.target.value)} fullWidth required/>
                    {loading&&<CircularProgress style={{marginTop:10}}/>}
                    {output&&<Alert style={{marginTop:'10px'}} severity={variant} onClose={()=>setOutput('')}>{output}</Alert>}
                    {!clicked&&<Button style={{margin:'20px 0'}} type='submit' color='primary' variant='contained' fullWidth>Create Account</Button>}
                </form>
            </Paper>
        </Grid>
    )
}

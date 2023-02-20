import React,{useContext, useState} from 'react'
import ClipLoader from "react-spinners/ClipLoader"
import {Form,Button,Alert} from 'react-bootstrap'


export const CreatePrincipal = () => {
    const [domain,setDomain] = useState('')
    const [password,setPassword] = useState('')
    const [output,setOutput] = useState('')
    const [clicked,setClicked]=useState(false)
    const [loading,setLoading] = useState(false)
    const [variant,setVariant] = useState('')

    const handleSubmit =(event) => {
        event.preventDefault()
        setOutput('')
        setClicked(true)
        setLoading(true)
        fetch('/api/test/admin/home',{
            method:'POST',
            body: JSON.stringify({
                domain:domain,
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
        <div>
            <h1 style={{paddingTop:'30px'}}> Create Principal Account</h1>
            <Form style={{paddingTop:'5vh', paddingLeft:'10vh', paddingRight:'10vh', fontSize:'20px', fontWeight:'bold'}} onSubmit={handleSubmit}>
                <Form.Group controlId='formBasicDomain'>
                    <Form.Control required type="text" value={domain} onChange={(x)=>setDomain(x.target.value)} placeholder="Domain" />
                </Form.Group>

                <Form.Group controlId="formBasicPassword">
                    <Form.Control required type="password" value={password} onChange={(x)=>setPassword(x.target.value)} placeholder="Password" />
                </Form.Group>
                {output&&<Alert variant={variant}>{output}</Alert>}
                {!clicked&&<Button variant="outline-primary" type="submit">
                    Submit
                </Button>}
            </Form>
            <ClipLoader loading={loading}/>
        </div>
    )
}

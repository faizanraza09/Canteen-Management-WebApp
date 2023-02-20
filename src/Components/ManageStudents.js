import React,{useState, useEffect} from 'react'
import {Grid,Paper, Avatar, TextField, Button, CircularProgress} from '@material-ui/core'
import {Alert} from '@material-ui/lab'
import {useParams} from 'react-router-dom'
import {makeStyles} from '@material-ui/core/styles'
import useMediaQuery from '@material-ui/core/useMediaQuery'
import { DataGrid } from '@material-ui/data-grid';
import { FormatColorReset, Message, TramOutlined } from '@material-ui/icons'


const useStyles=makeStyles({
    paperStyle: {
        padding:20,width:props=>props.width, margin:"auto"
    },
    gridStyle:{
        marginTop:10,
        backgroundColor:'white',
        height:props=>props.height
    },
    headerStyle:{
        fontSize:props=>props.fontSize
    },
    cellStyle: {
        marginLeft:5
    },

    alertStyle : {
        marginTop:10,
        textAlign:'center'
    }



})




export const ManageStudents = () => {

    const matches = useMediaQuery('(min-width:700px)');
    const width = matches?700:350
    const columnWidth = matches?200:150
    const fontSize = matches?18:14
    const classes =useStyles({width:width,fontSize:fontSize})

    const columns = [{field:'id',headerClassName:classes.headerStyle,cellClassName:classes.cellStyle, headerName:'Username' , width:columnWidth},
                    {field:'password', headerName:'Password', headerClassName:classes.headerStyle,cellClassName:classes.cellStyle, width:columnWidth}
                    ,{field:'balance', headerName:'Balance', headerClassName:classes.headerStyle,cellClassName:classes.cellStyle, width:columnWidth}]

    const {domain} = useParams()
    const [transactionCompleted,setTransactionCompleted] = useState(false)
    const [page, setPage] = useState(0)
    const [rows,setRows]= useState([])
    const [loading,setLoading] = useState(false)
    const [loading2,setLoading2]= useState(false)
    const [output,setOutput] = useState('')
    const [clicked,setClicked]=useState(false)
    const [selectedIds,setSelectedIds]=useState(new Set())
    const [pageSize, setPageSize] = useState(5)
    const [amount,setAmount]=useState(0)

    
    const [variant,setVariant] = useState('')


    /*const addBalance = (rows,message) => {
        let newrows=rows.slice()
        let c=0
        for (var i=0;i<rows.length;i++){
            if ((i+1)<=page*pageSize){
                continue
            }
            else if ((i+1)<=(page+1)*pageSize){
                newrows[i]['balance']=message[c]
                c+=1
            }
            else{
                continue
            }
            
        }
        console.log(newrows)
        return newrows
    }*/
    
    const handlePageChange = (params) => {
        setPage(params.page)             
    }
        

    useEffect( () => {
        setLoading(true)
        fetch(`/api/${domain}/principal/home/managestudents`,{
            method:'POST',
            body: JSON.stringify({
                requirement:'credentials'
            }),
            headers:{
                "Content-type":"application/json; charset=UTF-8"
            }
        }).then(response => response.json())
        .then((message)=>{
            setRows(message.rows)         
            setLoading(false)       
        })
    },[transactionCompleted])

    /*useEffect( () => {
        setLoading(true)
        fetch(`/api/${domain}/principal/home/givestudentmoney`,{
            method:'POST',
            body: JSON.stringify({
                page:page,
                pagesize: pageSize,
                required:'balances'
            }),
            headers:{
                "Content-type":"application/json; charset=UTF-8"
            }
        }).then(response => response.json())
        .then((message)=>{
            setRows(rows=>{addBalance(rows,message)})
            



            setLoading(false)
        })
      },[page]
    )*/

    const handleSelection = (e) => {
        setSelectedIds(e.selectionModel)
        /*const selectedRowData = rows.filter((row) =>
        selectedIDs.has(row.id.toString()))*/
        
        }

    const handleClick = (param,event) => {
        /*console.log(param)*/
    }
    
    const handlePageSizeChange = (params) => {
        setPageSize(params.pageSize)
      };

    const handleSubmit = (event) => {
        event.preventDefault()
        console.log(selectedIds)
        setOutput('')
        setClicked(true)
        setLoading2(true)
        fetch(`/api/${domain}/principal/home/managestudents`,{
            method:'POST',
            body: JSON.stringify({
                requirement:'balance',
                usernames:selectedIds,
                amount:amount
            }),
            headers:{
                "Content-type":"application/json; charset=UTF-8"
            }
        }).then(response => response.json())
        .then((message)=>{
            setLoading2(false)
            if (message.hasOwnProperty(201)){
                setTransactionCompleted(true)
                setVariant('success')
                setOutput(message[201])
                }
            else {
                setVariant('warning')
                setOutput(message[409])
            }
            setClicked(false)     
            setTransactionCompleted(false)    
                   
        })
    }


    return (
        <Grid style={{paddingTop:30, paddingBottom:10}}>
            <Paper className={classes.paperStyle} elevation={10}>
                <h2>Manage Students</h2>
                <DataGrid className={classes.gridStyle} rows={rows} columns={columns} autoHeight page={page} onPageChange={handlePageChange}
                          loading={loading} checkboxSelection onSelectionModelChange={handleSelection} disableSelectionOnClick
                          rowsPerPageOptions={[5, 10, 20]} onCellClick={handleClick} pageSize={pageSize}
                          onPageSizeChange={handlePageSizeChange}/>
                <form onSubmit={handleSubmit}>
                    <TextField style={{marginTop:'10px'}} label='Amount' type='number' value={amount} onChange={(x)=>setAmount(x.target.value)} helperText='Money will only be deposited into selected students accounts' FormHelperTextProps={{focused:true}} fullWidth required/>
                    {loading2&&<CircularProgress style={{marginTop:10}}/>}
                    {output&&<Alert className={classes.alertStyle} severity={variant} onClose={()=>setOutput('')}>{output}</Alert>}
                    {!clicked&&<Button style={{marginTop:10}} color='primary' variant='contained' type='submit' fullWidth >Deposit Money</Button>}
                </form>
            </Paper>
        </Grid>
    )
}


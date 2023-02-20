import React from 'react'
import {Admin} from './Admin'
import { Principal } from './Principal'
import { CanteenOwner } from './CanteenOwner'
import {Student} from './Student'
import {useParams} from 'react-router-dom'

export const Home = () => {
    const {user} = useParams()

    if (user==='admin') {
        return <Admin/>
    }

    else if (user==='principal') {
        return <Principal/>
    }

    else if (user==='canteen_owner') {
        return <CanteenOwner/>
    }

    else {
        return <Student/>
    }
    
    
}

import streamlit as st
import helper as c
import pandas as pd
import SessionState
from google.cloud import firestore
import re
from password_generator import PasswordGenerator
import random
from datetime import datetime

session_state=SessionState.get(username=None)


db = firestore.Client.from_service_account_json("firestore-key.json")


def login(username,password):
    dom_list=re.findall('\S@(\S+)', username)
    if len(dom_list)>0:
        dom=dom_list[0]
        if username=='admin@test' and password=='1234':
            session_state.username=username
            st.success(f'You are logged in as {username}. Please Proceed to the Home Page to access your portal')
        elif db.collection('domains').document(dom).collection('staff').document(username).get().exists:
            if password==db.collection('domains').document(dom).collection('staff').document(username).get().get('password'):
                session_state.username=username
                st.success(f'You are logged in as {username}.Please Proceed to the Home Page to access your portal')
            else:
                session_state.username=None
                st.warning('Enter the correct credentials')
        elif db.collection('domains').document(dom).collection('students').document(username).get().exists:
            if password==db.collection('domains').document(dom).collection('students').document(username).get().get('password'):
                session_state.username=username
                st.success(f'You are logged in as {username}.Please Proceed to the Home Page to access your portal')
            else:
                session_state.username=None
                st.warning('Enter the correct credentials')
        else:
            st.warning('Enter the correct credentials')
    else:
        st.warning('Enter the correct credentials')

pg=st.sidebar.radio('',['Login','Home'])
if pg=='Login':
    st.title('Canteen Login Page')
    username=st.text_input('Username')
    pas=st.text_input('Password',type='password',key='a')
    if st.button('Login'):
        login(username,pas)

elif pg=='Home':
    if session_state.username==None:
        st.title('Go Back and Login to access your portal')
    else:
        lst=session_state.username.split('@')
        user=lst[0]
        user_domain=lst[1]
        if user=='admin':
            st.title('Welcome Admin')
            st.header('Create a Principal Account')
            domain=st.text_input('Domain Name')
            password=st.text_input('Select the password for the principal account',type='password',key='b')
            if st.button('Create Account',key='a'):
                c.domain(domain)
                c.principal(f'principal@{domain}',password,domain)
                st.success(f'The Account of the Principal with username principal@{domain} has been created')

        elif user=='principal':
            st.title('Welcome Principal')
            st.subheader('Select the Activity that you want to perform')
            option=st.selectbox('',['Create Canteen Owner Account','Create Student Accounts', 'Give Students Money'])
            st.markdown("***")
            if option=='Create Canteen Owner Account':        
                st.subheader('Select the password for the canteen owner account')
                password=st.text_input('',type='password')
                if st.button('Create Account',key='b'):
                    c.canteen_owner(f'canteen_owner@{user_domain}',password,user_domain)
                    st.success(f'The Account of the Canteen Owner with username canteen_owner@{user_domain} has been created')
            elif option=='Create Student Accounts':
                st.subheader('Select the number of accounts that you want to make')
                count=int(st.number_input('',min_value=1,max_value=100))
                if st.button('Create Accounts'):
                    id_list=db.collection('domains').document(user_domain).get().get('id_numbers')
                    for i in range(count):
                        pwo=PasswordGenerator()
                        pwo.minlen=6
                        pwo.maxlen=6
                        pas=pwo.generate()
                        student_id=id_list.pop()
                        c.student(f'{student_id}@{user_domain}',pas,user_domain)
                    st.success(f'{count} student accounts have been created')
                    db.collection('domains').document(user_domain).update({'id_numbers':id_list})
            elif option=='Give Students Money':
                st.subheader('Enter how much money do you want to give to the students')
                money=int(st.number_input(''))
                if st.button('Send Money'):
                    students=db.collection('domains').document(user_domain).collection('students').list_documents()
                    for s in students:
                        username=s.get().get('username')
                        c.student.receive_money(username,user_domain,money)
                    st.success(f"A deposit of {money} has been done in the students accounts")
        
        elif user=='canteen_owner':
            st.title('Welcome Canteen Owner')
            st.header('Price List')
            doc_ref=db.collection('domains').document(user_domain).collection('staff').document(f'canteen_owner@{user_domain}')
            price_list=doc_ref.get().get('price_list')
            price_table=st.table(pd.DataFrame.from_dict(price_list))
            item=st.text_input('Enter the name of your item').upper()
            price=int(st.number_input('Enter the price of the item',value=0))
            if st.button('Add Item'):
                price_list['Item'].append(item)
                price_list['Price'].append(price)
                price_table.add_rows(pd.DataFrame.from_dict({'Item':[item],'Price':[price]}))
                doc_ref.update({'price_list':price_list})
            st.header('Balance')
            st.subheader(c.canteen_owner.get_account_assets(f'canteen_owner@{user_domain}',user_domain))

        else:
            st.title('Welcome Student')
            option=st.selectbox('',['Canteen','Transaction History'])           
            if option=='Canteen':
                st.markdown("***")
                st.header('Price List')
                doc_ref=db.collection('domains').document(user_domain).collection('staff').document(f'canteen_owner@{user_domain}')
                price_list=doc_ref.get().get('price_list')
                print(price_list)
                st.table(pd.DataFrame.from_dict(price_list))
                st.write('Select the item that you want to buy:')
                item=st.selectbox('',price_list['Item'])
                st.write(f'Select how many {item} do you want:')       
                quantity=int(st.selectbox('',[1,2,3,4,5]))
                price=price_list['Price'][price_list['Item'].index(item)]
                if st.button('Buy'):
                    c.student.buy_items(f'{user}@{user_domain}',user_domain,item,price,quantity)
                    st.success(f'Your purchase of {quantity} {item} was sucessful')
                st.markdown("<h2 style='text-align: center; color: black;'>Balance</h1>", unsafe_allow_html=True)
                bal=c.student.get_account_assets(f'{user}@{user_domain}',user_domain)
                st.markdown(f"<h2 style='text-align: center; color: black;'>{bal}</h1>", unsafe_allow_html=True)
            else:
                trail=c.student.get_trail(f'{user}@{user_domain}',user_domain)
                df=pd.DataFrame(trail,columns=['Date','Description','Amount'])
                df['Date']=(df['Date'].astype('int'))/1000
                df2=df.sort_values(by=['Date'],ascending=False)
                df2.reset_index(drop=True,inplace=True)
                df2['Date']=df2['Date'].apply(lambda x:c.convert_timestamp(x))
                st.table(df2)





    
            



from flask import Flask,request,json,redirect,url_for,jsonify
#from werkzeug.utils import redirect
import re
import sys

sys.path.append('.')

import helper as h

app=Flask(__name__)

'''@app.route('/api',methods=['GET'])
def index():
    return {'name':'Hello World'}'''


@app.route('/api/login', methods=['POST'])
def login():
    request_data=json.loads(request.data)
    username=request_data['username']
    password=request_data['password']

    return h.login(username,password)

@app.route('/api/<domain>/admin/home', methods=['POST'])
def admin_home(domain):
    request_data=json.loads(request.data)
    print(request_data)
    new_domain=request_data['domain']
    password=request_data['password']
    h.domain(new_domain)
    return h.principal(f'principal@{new_domain}',password,new_domain).message

@app.route('/api/<domain>/principal/home/<action>', methods=['POST'])
def principal_home(domain,action):
    request_data=json.loads(request.data)
    if action=='createcanteenowner':
        password=request_data['password']
        return h.canteen_owner(f'canteen_owner@{domain}',password,domain).message
    elif action=='createstudentaccount':
        quantity=int(request_data['quantity'])
        return h.student.create_students(domain,quantity)
    else:
        requirement=request_data['requirement']
        if requirement=='credentials':
            return jsonify(h.principal.get_details(domain))
        else:
            usernames=request_data['usernames']
            amount=int(request_data['amount'])
            return h.student.receive_money(usernames,domain,amount)

            
        







if __name__=='__main__':
    app.run(debug=True)


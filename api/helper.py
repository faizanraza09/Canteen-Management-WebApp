import os
import pandas as pd
import binascii
from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
import random
from iroha.primitive_pb2 import can_transfer_my_assets
from google.protobuf.json_format import MessageToDict
import sys
from google.cloud import firestore
from password_generator import PasswordGenerator
import re
from datetime import datetime
import re
import psycopg2

db = firestore.Client.from_service_account_json("firestore-key.json")




if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'admin@test')

ADMIN_PRIVATE_KEY = os.getenv(
    'ADMIN_PRIVATE_KEY', 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')

ADMIN_PUBLIC_KEY= IrohaCrypto.derive_public_key(ADMIN_PRIVATE_KEY)

iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))

def trace(func):
    """
    A decorator for tracing methods' begin/end execution points
    """

    def tracer(*args, **kwargs):
        name = func.__name__
        print('\tEntering "{}"'.format(name))
        result = func(*args, **kwargs)
        print('\tLeaving "{}"'.format(name))
        return result

    return tracer

def login(username,password):
    dom_list=re.findall('\S@(\S+)', username)
    if len(dom_list)>0:
        dom=dom_list[0]
        if username=='admin@test' and password=='1234':
            return {'201': username}
        elif db.collection('domains').document(dom).collection('staff').document(username).get().exists:
            if password==db.collection('domains').document(dom).collection('staff').document(username).get().get('password'):
                return {'201': username}
            else:
                return {'403':'Enter the Correct Credentials'}
        elif db.collection('domains').document(dom).collection('students').document(username).get().exists:
            if password==db.collection('domains').document(dom).collection('students').document(username).get().get('password'):
                return {'201': username}
            else:
                return {'403':'Enter the Correct Credentials'}
        else:
            return {'403':'Enter the Correct Credentials'}
    else:
        return {'403':'Enter the Correct Credentials'}

@trace
def send_transaction_and_print_status(transaction):
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net.send_tx(transaction)
    directory=[]
    for status in net.tx_status_stream(transaction):
        directory.append(status)
        print(status)
    return directory[-1][0]

class domain:
    def __init__(self,domain):
        self.create_domain_and_asset(domain)
    
    @trace
    def add_to_database(self,domain):
        doc_ref=db.collection('domains').document(domain)
        doc=doc_ref.get()
        if doc.exists:
            return
        else:
            doc_ref.set({"domain_name":domain, "id_numbers":list(range(1999,1000,-1))})
    
    @trace
    def create_domain_and_asset(self,domain):
        commands = [iroha.command('CreateDomain', domain_id=domain, default_role='user'),iroha.command('CreateAsset', asset_name='coin', domain_id=domain, precision=0)]
        tx = IrohaCrypto.sign_transaction(iroha.transaction(commands), ADMIN_PRIVATE_KEY)
        self.add_to_database(domain)
        send_transaction_and_print_status(tx)
    
class principal:
    def __init__(self,username,password,domain):
        self.statuses=[]
        self.statuses.append(self.create_principal(username,password,domain))
        self.statuses.append(self.attach_role(username))
        self.statuses.append(self.add_coin_to_principal(username,domain))
        if self.statuses[0]=='COMMITTED' and self.statuses.count(self.statuses[0]) == len(self.statuses):
            self.message = {'201':f'The Account of the Principal with username, principal@{domain}, has been created'}
        else:
            self.message = {'409':'Account could not be created'}

    @trace
    def add_to_database(self,username,password,domain,private_key,public_key):
        doc_ref=db.collection('domains').document(domain).collection('staff').document(username)
        doc=doc_ref.get()
        if doc.exists:
            return
        else:
            doc_ref.set({"username":username,"password":password,"private_key":private_key,"public_key":public_key})
    
    @trace
    def create_principal(self,username,password,domain):
        private_key=IrohaCrypto.private_key().decode('utf-8')
        public_key=IrohaCrypto.derive_public_key(private_key).decode('utf-8')
        tx=iroha.transaction([iroha.command('CreateAccount',account_name='principal',domain_id=domain,public_key=public_key)])
        IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
        self.add_to_database(username,password,domain,private_key,public_key)
        return send_transaction_and_print_status(tx)

    @trace
    def attach_role(self,username):
        tx=iroha.transaction([iroha.command('AppendRole',account_id=username,role_name='admin'),iroha.command('AppendRole',account_id=username,role_name='money_creator')])
        IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
        return send_transaction_and_print_status(tx)
    
    @trace
    def add_coin_to_principal(self,username,domain):
        tx = iroha.transaction([
            iroha.command('AddAssetQuantity',
                        asset_id=f'coin#{domain}', amount='100000000')
        ],creator_account=username)
        key=principal.output_key(domain)
        IrohaCrypto.sign_transaction(tx, key)
        return send_transaction_and_print_status(tx)

    @staticmethod
    def output_key(domain):
        doc_ref=db.collection('domains').document(domain).collection('staff').document(f'principal@{domain}')
        doc=doc_ref.get()
        return doc.get('private_key')

    @staticmethod
    @trace
    def get_details(domain):
        rows=[]
        rowcount=0
        #cur.execute(f'''SELECT account_id,amount FROM account_has_asset WHERE account_id IN (SELECT account_id FROM account WHERE "domain_id"='{domain}')''')
        #balances=dict(cur.fetchall())
        for x in db.collection('domains').document(domain).collection('students').stream():
            rowcount+=1
            username=x.get('username')
            password=x.get('password')
            balance=x.get('balance')
            #balance=student.get_account_assets(username,domain)
            rows.append({'id':username,'password':password,'balance':balance})
        return {'rows':rows}

    @staticmethod
    @trace
    def get_balances(domain,page,pagesize):
        rows=[]
        rowcount=0
        for x in db.collection('domains').document(domain).collection('students').stream():
            rowcount+=1
            if rowcount<=page*pagesize:
                continue
            elif rowcount<=(page+1)*pagesize:
                username=x.get('username')
                balance=student.get_account_assets(username,domain)
                rows.append(balance)
            else:
                continue
        return rows
        
        


class canteen_owner:
    def __init__(self,username,password,domain):
        self.statuses=[]
        self.statuses.append(self.create_canteen_owner(username,password,domain))
        self.create_price_list(username,domain)
        self.statuses.append(self.receive_money(username,domain,100))
        if self.statuses[0]=='COMMITTED' and self.statuses.count(self.statuses[0]) == len(self.statuses):
            self.message = {'201':f'The Account of the Canteen Owner with username, canteen_owner@{domain}, has been created'}
        else:
            self.message = {'409':'Account could not be created'}

    
    @trace
    def add_to_database(self,username,password,domain,private_key,public_key):
        doc_ref=db.collection('domains').document(domain).collection('staff').document(username)
        doc=doc_ref.get()
        if doc.exists:
            return
        else:
            doc_ref.set({"username":username,"password":password,"private_key":private_key,"public_key":public_key})

    @trace
    def create_canteen_owner(self,username,password,domain):
        private_key=IrohaCrypto.private_key().decode('utf-8')
        public_key=IrohaCrypto.derive_public_key(private_key).decode('utf-8')
        tx=iroha.transaction([iroha.command('CreateAccount',account_name='canteen_owner',domain_id=domain,public_key=public_key)],creator_account=f'principal@{domain}')
        key=principal.output_key(domain)
        IrohaCrypto.sign_transaction(tx, key)
        self.add_to_database(username,password,domain,private_key,public_key)
        return send_transaction_and_print_status(tx)

    @trace
    def create_price_list(self,username,domain):
        doc_ref=db.collection('domains').document(domain).collection('staff').document(username)
        doc_ref.update({'price_list':{'Item':[],'Price':[]}})
    
    @staticmethod
    def output_key(domain):
        doc_ref=db.collection('domains').document(domain).collection('staff').document(f'canteen_owner@{domain}')
        doc=doc_ref.get()
        return doc.get('private_key')

    @trace
    def receive_money(self,username,domain,amount):
        tx = iroha.transaction([
            iroha.command('TransferAsset', src_account_id=f'principal@{domain}', dest_account_id=username,
                      asset_id=f'coin#{domain}', description='init top up', amount=str(amount))
        ],creator_account=f'principal@{domain}')
        key=principal.output_key(domain)
        IrohaCrypto.sign_transaction(tx, key)
        return send_transaction_and_print_status(tx)
        
    @staticmethod
    def get_account_assets(username,domain):
        query = iroha.query('GetAccountAssets', account_id=username, creator_account=username)
        key=canteen_owner.output_key(domain)
        IrohaCrypto.sign_query(query, key)
        response = net.send_query(query)
        data = response.account_assets_response.account_assets
        balance=0
        for asset in data:
            balance=asset.balance

        return int(balance)

class student:

    
    @staticmethod
    def add_to_database(username,password,domain,private_key,public_key):
        doc_ref=db.collection('domains').document(domain).collection('students').document(username)
        doc=doc_ref.get()
        if doc.exists:
            return
        else:
            doc_ref.set({"username":username,"password":password,'balance':0,"private_key":private_key,"public_key":public_key})

    
    @staticmethod
    @trace
    def create_students(domain,number):
        id_list=db.collection('domains').document(domain).get().get('id_numbers')
        pwo=PasswordGenerator()
        pwo.minlen=6
        pwo.maxlen=6
        commands=[]
        for i in range(number):        
            password=pwo.generate()
            student_id=id_list.pop()
            private_key=IrohaCrypto.private_key().decode('utf-8')
            public_key=IrohaCrypto.derive_public_key(private_key).decode('utf-8')
            commands.append(iroha.command('CreateAccount',account_name=str(student_id),domain_id=domain,public_key=public_key))
            student.add_to_database(f'{student_id}@{domain}',password,domain,private_key,public_key)
        db.collection('domains').document(domain).update({'id_numbers':id_list})
        tx=iroha.transaction(commands,creator_account=f'principal@{domain}')
        key=principal.output_key(domain)
        IrohaCrypto.sign_transaction(tx, key)
        
        
        status= send_transaction_and_print_status(tx)

        if status=='COMMITTED':
            return {'201':f'{number} student accounts have been created'}
        else:
            return {'409':'Creation of student accounts was not successful'}

    
    @staticmethod
    @trace
    def receive_money(usernames,domain,amount):
        if usernames=={}:
            return {'409':'Deposit was not successful'}
        commands=[]
        usernames_tpl=(tuple(usernames),)
        
        for username in usernames:
            commands.append(iroha.command('TransferAsset', src_account_id=f'principal@{domain}', dest_account_id=username,
                      asset_id=f'coin#{domain}', description='init top up', amount=str(amount)))
        tx = iroha.transaction(commands,creator_account=f'principal@{domain}')
        key=principal.output_key(domain)
        IrohaCrypto.sign_transaction(tx, key)
        status=send_transaction_and_print_status(tx)
        if status=='COMMITTED':
            conn = psycopg2.connect(
            host="172.19.0.2",
            database="iroha_data",
            user="postgres",
            password="mysecretpassword")

            cur = conn.cursor()

            cur.execute(f'''SELECT account_id,amount FROM account_has_asset WHERE account_id IN %s ''',usernames_tpl)
            balances=dict(cur.fetchall())
            cur.close()
            conn.close()
            for x in db.collection('domains').document(domain).collection('students').list_documents():
                username=x.get().get('username')
                try:
                    x.update({'balance':int(balances[username])})
                except:
                    continue

            return {'201':f'The amount {amount} was deposited in the student accounts'}
        else:
            return {'409':'Deposit was not successful'}

    @staticmethod
    def output_key(username,domain):
        doc_ref=db.collection('domains').document(domain).collection('students').document(username)
        doc=doc_ref.get()
        return doc.get('private_key')

    
    @staticmethod
    @trace
    def buy_items(username,domain,item,price,qty):
        bill=price*qty
        tx = iroha.transaction([
            iroha.command('TransferAsset', src_account_id=username, dest_account_id=f'canteen_owner@{domain}',
                      asset_id=f'coin#{domain}', description=f'Bill for {qty} {item}', amount=str(bill))
        ], creator_account=username)
        key=student.output_key(username,domain)
        IrohaCrypto.sign_transaction(tx, key)
        send_transaction_and_print_status(tx)

    
    @staticmethod
    @trace
    def get_account_assets(username,domain):
        query = iroha.query('GetAccountAssets', account_id=username, creator_account=username)
        key=student.output_key(username,domain)
        IrohaCrypto.sign_query(query, key)
        response = net.send_query(query)
        data = response.account_assets_response.account_assets
        balance=0
        for asset in data:
            balance=asset.balance
        return int(balance)




    
    @staticmethod
    @trace
    def get_trail(username,domain):
        query = iroha.query('GetAccountTransactions', account_id=username, creator_account=username ,page_size=30)
        key=student.output_key(username,domain)
        IrohaCrypto.sign_query(query, key)
        response = net.send_query(query)
        data=response.transactions_page_response.transactions
        lst=[]
        i=0
        for t in data:
            dct_t=MessageToDict(t,preserving_proto_field_name=True)
            lst.append([dct_t['payload']['reduced_payload']['created_time'],dct_t['payload']['reduced_payload']['commands'][0]['transfer_asset']['description'], dct_t['payload']['reduced_payload']['commands'][0]['transfer_asset']['amount']])
            i+=1
        return lst


def convert_timestamp(x):
    x=datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
    return x


    
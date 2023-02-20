import psycopg2

conn = psycopg2.connect(
    host="172.19.0.2",
    database="iroha_data",
    user="postgres",
    password="mysecretpassword")

cur = conn.cursor()



cur.execute(f'''SELECT account_id,amount FROM account_has_asset WHERE account_id IN %s''',(tuple(['principal@alnoor21','principal@alnoor23']),))
 
balances = cur.fetchall()
print(balances)
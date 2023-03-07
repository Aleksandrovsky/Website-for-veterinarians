from flask import Flask
from contact_form.contact_form import bp_contact
from contact_form.reply import bp_reply
from index.index import bp_index
from login.login import bp_login

from db.db import create_new_db, create_table_in_db, clear_table

import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'dndsk!fngbdjksbj543fk2b..74dsnfds'

app.register_blueprint(bp_contact)
app.register_blueprint(bp_index)
app.register_blueprint(bp_login)
app.register_blueprint(bp_reply)

db_path = os.getcwd() + '/db_folder/database.db'



@app.before_first_request
def bfr():

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    table_messages_name = 'messages'
    table_users_name = 'users'

    #clear_table(db_path,table_messages_name)
    #clear_table(db_path, table_users_name)
    check_folder()
    check_db()

    table_messages_columns = {
        'email': 'TEXT',
        'message': 'TEXT',
        'did_accepted': 'INTEGER'
    }

    table_users_columns = {
        'name': 'TEXT',
        'email': 'TEXT',
        'password': 'TEXT',
        'hash_passwrd': 'TEXT',
        'admin': 'INTEGER'
    }

    if os.path.exists(db_path):

        create_table_in_db(db_path, table_messages_name, table_messages_columns)
        create_table_in_db(db_path, table_users_name, table_users_columns)



def check_folder():

    current_path = os.getcwd()

    if os.path.exists(current_path + '/db_folder'):
        print('Database folder exists.')

    else:
        os.system('mkdir db_folder')
        print('Database folder has been created.')



def check_db():

    current_path = os.getcwd()

    if os.path.exists(current_path + '/db_folder/database.db'):
        print('Database exists.')

    else:
        create_new_db(current_path + '/db_folder/database.db')
        


if __name__ == '__main__':

    app.run(debug=True)
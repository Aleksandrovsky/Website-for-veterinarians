from flask import Flask, render_template
from contact_form.contact_form import bp_contact
from contact_form.reply import bp_reply
from index.index import bp_index
from auth.auth import bp_auth
from login.login import bp_login

from db.db import create_new_db, create_table_in_db, clear_table

import os
import sqlite3

from dotenv import load_dotenv



#INITIALIZATION
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.register_blueprint(bp_contact)
app.register_blueprint(bp_index)
app.register_blueprint(bp_auth)
app.register_blueprint(bp_reply)
app.register_blueprint(bp_login)

db_path = (os.getcwd() + '/db_folder/' + str(os.getenv('DB_NAME')))




#BEFORE FIRST REQUEST- CHECK DATABASE
@app.before_first_request
def before_first_request():

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    table_messages_name = 'messages'
    table_users_name = 'users'

    check_folder()
    check_db()

    table_messages_columns = {
        'email': 'TEXT',
        'message': 'TEXT',
        'did_accepted': 'INTEGER'
    }

    table_users_columns = {
        'email': 'TEXT',
        'username': 'TEXT',
        'hash_password': 'TEXT',
        'admin': 'INTEGER'
    }

    if os.path.exists(db_path):

        create_table_in_db(db_path, table_messages_name, table_messages_columns)
        create_table_in_db(db_path, table_users_name, table_users_columns)




#ERRORS
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



@app.errorhandler(500)
def intrenal_server_error(e):
    return render_template('500.html'), 500




#INITIALIZING FUNCTIONS
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
        
        


#MAIN
if __name__ == '__main__':

    app.run(debug=True)
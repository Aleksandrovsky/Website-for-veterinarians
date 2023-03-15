from flask import Flask, render_template, Blueprint, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, InputRequired

from db.db import add_data, get_data

import os
import sqlite3

bp_contact = Blueprint('bp_contact_form', __name__, template_folder='templates')

info_from_site = {}

db_path = (os.getcwd() + '/db_folder/' + str(os.getenv('DB_NAME')))
table_messages_name = 'messages'


'''
        ZROBIĆ ERRORY
'''


@bp_contact.route('/contact', methods=["GET", "POST"])
def contact():

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    form = Contact()

    if form.validate_on_submit():

        email = form.email.data
        message = form.message.data
        accept = form.accept.data

        info_from_site[f'email'] = email
        info_from_site[f'message'] = message
        
        if accept:
            
            info_from_site[f'did_accepted'] = 'Yes'

        else:

            info_from_site[f'did_accepted'] = 'No'


        add_data(info_from_site, table_messages_name, db_path)

        return redirect(url_for('bp_contact_form.messages'))


    return render_template('contact_form.html', form = form)



@bp_contact.route('/messages', methods=['GET', 'POST'])
def messages():

    button = Button()
    
    list_of_datas = list(info_from_site.keys())
    messages_site = get_data(list_of_datas, db_path, table_messages_name)
    
    if button.validate_on_submit():
        
        return redirect(url_for('bp_reply_form.reply'))

    return render_template('messages.html', messages_site = messages_site, button = button)



class Contact(FlaskForm):

    email = StringField('Your e-mail:', validators = [DataRequired()])
    message = StringField('Message:', validators = [DataRequired()])
    accept = BooleanField('I accept all terms.', validators = [InputRequired()])
    submit = SubmitField('Send message')

class Button(FlaskForm):

    button = SubmitField('Write message')
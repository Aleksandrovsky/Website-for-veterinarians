from flask import Flask, Blueprint, render_template

bp_login = Blueprint('bp_login_form', __name__, template_folder='templates')

@bp_login.route('/login')
def login():

    return render_template('login.html')
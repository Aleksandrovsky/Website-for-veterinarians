from flask import Flask, Blueprint, render_template

bp_index = Blueprint('bp_index_form', __name__, template_folder='templates')

@bp_index.route('/')
def index():
    
    return render_template('index.html')
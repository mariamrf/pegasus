from pegasus import app
from flask import render_template

# error handling
@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401
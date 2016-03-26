from pegasus import app
from flask import render_template

def render_error(code, msg, det='Oops..'):
	return render_template('error.html', error_code=code, error_message=msg, error_details=det), code

# error handling
@app.errorhandler(400)
def bad_request(e):
	return render_error(400, 'Bad Request')

@app.errorhandler(401)
def unauthorized(e):
    return render_error(401, 'Unauthorized', det="The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required.")

@app.errorhandler(403)
def forbidden(e):
	return render_error(403, 'Forbidden')

@app.errorhandler(404)
def not_found(e):
	return render_error(404, 'Page Not Found', det="These aren't the droids you're looking for.")

@app.errorhandler(410)
def gone(e):
	return render_error(410, 'Page Gone')

@app.errorhandler(500)
def internal_error(e):
	return render_error(500, 'Internal Server Error')


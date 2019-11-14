from flask import Flask, render_template, request, redirect, url_for, flash
from utils import *
app = Flask(__name__)


@app.route('/upload')
def upload_file():
	return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def uploaded_file():
	if request.method == 'POST':
		f = request.files['file']
		f.save("empire.json")

		return redirect(url_for('answer'))

@app.route('/answer')
def answer():
	rebel_file = "millenium-falcon.json"
	empire_file = "empire.json"

	route_description, captured_proba, total_day = odds(rebel_file, empire_file)
	success_proba = int((1-captured_proba)*100)

	return render_template('answer.html', success=success_proba, route=route_description, days=total_day)


if __name__ == '__main__':
	app.run(debug = True)

import sys
import json
sys.path.append('../class/')

import Ilwar
from flask import render_template
from flask import request
from flask import Flask
from flask import jsonify

from spamaze_db import DbControl

app = Flask(__name__)
dbcon = DbControl("spamaze")

def load_model():
	predict_model.load_model(save_path = "../predict_model/")

@app.route('/')
def test_():
	return render_template("test.html")

@app.route('/test')
def home():
	return render_template("index.html")


@app.route('/request', methods = ['POST'])
def send_request():
	data = request.data.decode('utf-8')
	data = json.loads(data)

	print(data)
	
	email = data["email"]
	text = data["message"]

	target_data = ["\"%s\"" % (email), "\"%s\"" % (text)]
	columns = ['email', 'text']
	
	dbcon.insert_data('requests', columns, target_data)

	response = {'status' : 'ok'}
	return jsonify(response)


@app.route('/api/enroll', methods = ['POST', 'GET'])
def send_enroll():
	if request.method == 'POST':
		data = request.data.decode('utf-8')
		data = json.loads(data)
	api_key = request.args.get("api_key")
	
	for item in data:
		content_id = item["id"]
		text = item["text"]
		is_spam = item["is_spam"]

		target_data = ["\"%s\"" % (content_id), "\"%s\"" % (text), \
						"\"%s\"" % (is_spam), "\"%s\"" % (api_key)]

		columns = ['content_id', 'text', 'is_spam', 'api_key']
	
		dbcon.insert_data('enrolls', columns, target_data)

	response = {'status' : 'ok'}
	return jsonify(response)


@app.route('/api/recognize', methods = ['POST', 'GET'])
def test():
	if request.method == 'POST':
		data = request.data.decode('utf-8')
		input_data = json.loads(data)
	
	api_key = request.args.get("api_key")
	print(api_key)

	modify_data = []
	for item in input_data:
		temp_item = item
		temp_item["pk"] = item["id"]
		del temp_item["id"]
		modify_data.append(temp_item)

	result = predict_model.predict(modify_data)
	
	response = {}
	for i in range(0, len(modify_data)):
		response[str(modify_data[i]["pk"])] = bool(result[i])

	print(response)
	
	return jsonify(response)

if __name__ == '__main__':
	predict_model = Ilwar.TrollClassifier()
	load_model()
	app.run(debug=True)

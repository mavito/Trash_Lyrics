import numpy as np
import pandas as pd
import sys
import os 
import json
from tensorflow.python.keras.models import load_model
from flask import Flask, request,render_template

artists = os.listdir('Artists_Songs')
model={key: None for key in artists}
char_to_int=json.load(open("jsons/cti.json","r"))
int_to_char=json.load(open("jsons/itc.json","r"))
n_vocab=json.load(open("jsons/nvocab.json","r"))
dataX=json.load(open("jsons/datax.json","r"))

app = Flask(__name__)

def create_model(artist):
	model=load_model('Weights/%s.hdf5'%artist)
	return model

def output_func(cti,itc,nvocab,datax,modl,numchar):
	start = np.random.randint(0, len(dataX)-1)
	pattern = datax[start]
	seed = ''.join([itc["%s"%value] for value in pattern])

	output = ""
	for i in range(int(numchar)):
		x = np.reshape(pattern, (1, len(pattern), 1))
		x = x / float(nvocab)
		prediction = modl.predict(x, verbose=0)
		index = np.argmax(prediction)
		result = itc["%s"%index]
		output += result
		pattern.append(index)
		pattern = pattern[1:len(pattern)]
	return output

for i in artists:
	model[i] = create_model(i)

@app.route("/")
def home():
	return render_template('index.html')

@app.route("/generate",methods=["POST"])
def generate():
	numchar = request.form['numchar']
	artist_name = request.form['artistname']
	i = artist_name.lower()
	if artist_name.lower() not in artists:
		output_text = "SORRY Model not trained to understand {}'s style :/".format(artist_name)
	else:
		output = output_func(char_to_int[i],int_to_char[i],n_vocab[i],dataX[i],model[i],numchar)
		output_text = 'Verse generated in the style of {} is:...> {}'.format(artist_name,output)
	
	return render_template('index.html', output = output_text)

if __name__ == "__main__":
	app.run("0.0.0.0",port=8080)
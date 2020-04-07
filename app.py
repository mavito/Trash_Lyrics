import numpy as np
import pandas as pd
import sys
import os 
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import LSTM, Activation, Flatten, Dropout, Dense
from tensorflow.python.keras.callbacks import ModelCheckpoint
from tensorflow.python.keras.utils import np_utils
from flask import Flask, request,jsonify,render_template

app = Flask(__name__)

def preprocess_test_load_model(artist):
	textFileName = 'Merged/%s.txt'%artist
	raw_text = open(textFileName,'r',encoding='UTF-8').read()
	raw_text = raw_text.lower()

	chars = sorted(list(set(raw_text)))
	char_to_int = dict((c, i) for i, c in enumerate(chars))
	int_to_char = dict((i, c) for i, c in enumerate(chars))

	n_chars = len(raw_text)
	n_vocab = len(chars)

	seq_length = 100
	dataX =[]
	dataY= []
	for i in range(0, n_chars - seq_length, 1):
		seq_in = raw_text[i:i + seq_length]
		seq_out = raw_text[i + seq_length]
		dataX.append([char_to_int[char] for char in seq_in])
		dataY.append(char_to_int[seq_out])
	n_patterns = len(dataX)
	X = np.reshape(dataX, (n_patterns, seq_length, 1))
	X = X / float(n_vocab)
	y = np_utils.to_categorical(dataY)

	model = Sequential()
	model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2]), return_sequences=True))
	model.add(Dropout(0.2))
	model.add(LSTM(256))
	model.add(Dropout(0.4))
	model.add(Dense(y.shape[1], activation='softmax'))
	model.compile(loss='categorical_crossentropy', optimizer='adam')

	filename = "Weights/%s.hdf5"%artist
	model.load_weights(filename)
	return char_to_int,int_to_char,n_vocab,dataX,model

def output_func(char_to_int,int_to_char,n_vocab,dataX,model,numchar):
	start = np.random.randint(0, len(dataX)-1)
	pattern = dataX[start]
	seed = ''.join([int_to_char[value] for value in pattern])

	output = ""
	for i in range(int(numchar)):
		x = np.reshape(pattern, (1, len(pattern), 1))
		x = x / float(n_vocab)
		prediction = model.predict(x, verbose=0)
		index = np.argmax(prediction)
		result = int_to_char[index]
		output += result
		pattern.append(index)
		pattern = pattern[1:len(pattern)]

	return output
artists = os.listdir('Artists_Songs')
char_to_int={key: None for key in artists}
int_to_char={key: None for key in artists}
n_vocab={key: None for key in artists}
dataX={key: None for key in artists}
model={key: None for key in artists}

for i in artists:
	char_to_int[i],int_to_char[i],n_vocab[i],dataX[i],model[i] = preprocess_test_load_model(i)
	

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
	app.run(debug=True)

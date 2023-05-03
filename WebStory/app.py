from flask import Flask, request, render_template,jsonify
import nltk
from autocorrect import spell
from gensim.summarization import summarize as g_sumn
import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
from requests.auth import HTTPBasicAuth
from pathlib import Path
import openai
import os
from IPython.display import Markdown
import pythonFiles.jinxin as jinxinFunction
import pythonFiles.tmpceazar as ceazarFunction

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('/index.html')

#####################################################################################
###############################Begin Jinxin Ai#######################################
#####################################################################################
# render giveInfo part
@app.route('/giveInfo_jinxin', methods=["GET"])
def jinxinHtml():
    return render_template('giveInfo_jinxin.html')

#render web story part
@app.route('/webstory_jinxin', methods=["GET"])
def installation():
    return render_template('webstory_jinxin.html')

# receive topic and try to generate 6 sections
@app.route('/topic', methods=["GET", "POST"])
def topic2story():
    text = request.form['text']
    jinxinFunction.generate6sections(text)
    return 'Already generated text'
# receive the second button singal to generate images
@app.route('/generate4imgs', methods=["GET", "POST"])
def generate4imgs():
    jinxinFunction.deliverImages()
    return "Already generated Images"

# give sections for render frontend text part
@app.route('/showSections', methods=["GET", "POST"])
def showSections():
    return jinxinFunction.postSections()

# give title for render frontend title part
@app.route('/showTitle', methods=["GET", "POST"])
def showTitle():
    return jinxinFunction.postTitle()
#####################################################################################
#################################End Jinxin Ai#######################################
#####################################################################################

if __name__ == '__main__':
    app.run(debug=True)
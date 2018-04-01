from flask import Flask, render_template
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os
import socket
import json
import argparse


app = Flask(__name__)
CORS(app)

parser = argparse.ArgumentParser()
parser.add_argument('--logdir', type=str,
    help='path to log directories', default='.')
args = parser.parse_args()

def interpolate_path(path):
    return os.path.join(args.logdir, path)

def get_dirs():
    paths = map(interpolate_path, os.listdir(args.logdir))
    dirs = filter(os.path.isdir, paths)
    names = map(os.path.basename, dirs)
    return list(names)

def get_files(dir_name):
    file_names = os.listdir(interpolate_path(dir_name))
    paths = map(lambda p: interpolate_path(os.path.join(dir_name, p)), file_names)
    files = filter(os.path.isfile, paths)
    names = map(os.path.basename, files)
    return list(names)

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/dirs", methods=['GET'])
def dirs():
    dir_names = get_dirs()
    data = []
    for dir_name in dir_names:
        data.append({
            'directory': dir_name,
            'files': get_files(dir_name)
        })
    res = {'dirs': data}
    return jsonify(res)

@app.route("/dirs/<dir_name>/<file_name>", methods=['GET'])
def get_content(dir_name, file_name):
    path = interpolate_path(os.path.join(dir_name, file_name))
    with open(path, 'r') as f:
        content = f.read()
    data = {'content': content}
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=8000, host='0.0.0.0', debug=True)

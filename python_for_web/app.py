# let's import the flask
from flask import Flask, render_template, request, redirect, url_for,Response
from flask_cors import CORS
import os # importing operating system module
from mongo_crud import mongo_api
from bson.json_util import dumps

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
# to stop caching static file
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.register_blueprint(mongo_api,url_prefix='/mongo_crud')

@app.route('/login',methods= ['POST'])
def login():
    username =  request.json.get('username')
    password =  request.json.get('password')
    if username == 'admin' and password == '123456':
        return Response(dumps({"code":200,"msg":"login success","data":"token"}), mimetype='application/json')
    else:
        return Response(dumps({"code":500,"msg":"login failed"}), mimetype='application/json')

@app.route('/') # this decorator create the home route
def home ():
    techs = ['HTML', 'CSS', 'Flask', 'Python']
    name = '30 Days Of Python Programming'
    return render_template('home.html', techs=techs, name = name, title = 'Home')

@app.route('/about')
def about():
    name = '30 Days Of Python Programming'
    return render_template('about.html', name = name, title = 'About Us')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/post', methods= ['GET','POST'])
def post():
    name = 'Text Analyzer'
    if request.method == 'GET':
         return render_template('post.html', name = name, title = name)
    if request.method =='POST':
        content = request.form['content']
        print(content)
        return redirect(url_for('result'))

if __name__ == '__main__':
    # for deployment
    # to make it work for both production and development
    port = int(os.environ.get("PORT", 35000))
    app.run(debug=True, host='0.0.0.0', port=port)
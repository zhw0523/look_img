# coding=utf-8
from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
#设置连接数据库的URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:weige521@127.0.0.1:3306/look_img'

#设置每次请求结束后会自动提交数据库中的改动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#查询时会显示原始SQL语句
#app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
manager = Manager(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    pswd = db.Column(db.String(64))

    def __repr__(self):
        return 'User:%s'%self.name

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        uname = request.form['uname']
        upswd = request.form['upswd']
        user_ = User.query.filter_by(name=uname).first()
        if user_:
            session['user_'] = uname
        else:
            user = User(name=uname,pswd=upswd)
            print(user,upswd)
            db.session.add(user)
            db.session.commit()
            session['user_'] = uname
        return redirect('/load_img_html')

#加载图片html
@app.route('/load_img_html')
def load_img_html():
    list_dir = os.listdir('static/img/')
    return render_template('img.html',list_dir=list_dir)

def my_key(x):
    x1 = x.split('张')
    x2 = x1[0].split('第')[-1]
    return int(x2)

@app.route('/img/<string:url>')
def img_url(url):
    list_img = os.listdir('static/img/'+url+'/')
    list_img.sort(key=my_key)
    return render_template('img_detail.html',list_img=list_img,url=url)

@app.route('/files')
def files():
    file_list = os.listdir(os.getcwd())
    return render_template('upload_file.html',file_list=file_list)

@app.route('/upload/<string:file_name>',methods=['GET'])
def upload_file(file_name):
    resp = make_response(send_from_directory(os.getcwd(),file_name,as_attachment=True))
    resp.headers['Content-Disposition'] = 'attachment; filename={}'.format(file_name.encode().decode('latin-1'))
    return resp


if __name__ == '__main__':
    manager.run()

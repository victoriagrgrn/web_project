import os

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from werkzeug.utils import secure_filename

import datetime as dt


from forms.user_forms import RegisterForm, LoginForm
from forms.news_forms import PublishForm
from data.users import User
from data.news import News
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/foto'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/eng.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
@app.route('/index')
def index():
    return render_template('title.html', title='EngEdu')


@app.route('/main/')
def site_main():
    db_session.global_init('db/dataB.db')
    db_sess = db_session.create_session()
    news = []
    for new in db_sess.query(News).all():
        publisher_name = db_sess.query(User).filter(User.id == new.publisher).first()
        publisher_name = publisher_name.surname + ' ' + publisher_name.name
        news.append([new.publisher, new.author, new.file, new.name, new.content, publisher_name])
    return render_template('main.html', news=news)


def latest_news(channel_name):
    telegram_url = 'https://t.me/s/'
    url = telegram_url+channel_name
    r = requests.get(url)
    print(r.text)
    soup = BeautifulSoup(r.text, 'lxml')
    link = soup.find_all('a')
    url = link[-1]['href']
    url = url.replace('https://t.me/', '')
    print(url)
    channel_name, news1_id = url.split('/')
    urls = []
    for i in range(5):
        urls.append(f'{channel_name}/{int(news1_id) - i}')
    return urls


@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template("about.html")


@app.route("/articles", methods=['GET', 'POST'])
def articles():
    return render_template("articles.html")


@app.route("/introduction", methods=['GET', 'POST'])
def introduction():
    url = 'english4allofyou1/4'
    if request.method == 'GET':
        return render_template("introduction.html", url=url)
    else:
        channel_name = request.form['adress']
        urls = latest_news(channel_name)
        return render_template("introduction.html", urls=urls)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают!")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже зарегистрирован!")
        user = User(
            email=form.email.data,
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/main")
        return render_template('login.html',
                               message="Ошибка! Логин или пароль введены неверно",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/publish',  methods=['GET', 'POST'])
@login_required
def publish():
    form = PublishForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        file = form.file.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        news = News(
            publisher=current_user.id,
            author=form.author.data,
            name=form.name.data,
            content=form.content.data,
            file=f'static/foto/{filename}',
            publish_date=dt.datetime.now(),
        )
        db_sess.add(news)
        db_sess.commit()
        return redirect('/main')
    return render_template('news.html', title='Добавление поста',
                           form=form)


@app.route('/audio_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    main()

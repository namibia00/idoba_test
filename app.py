from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'jbiurxtsecdvjbunkmlijmlknub'
app.debug = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return '{}さん、こんにちは！'.format(name)


@app.route('/dbtest')
def dbtest():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('select name, age, address from users where id = 1')
    user = c.fetchone()
    c.close()
    user = {
        'name': user[0],
        'age': user[1],
        'address': user[2]
    }
    return render_template('dbtest.html', user=user)


@app.route('/add', methods=['GET'])
def add_get():
    if 'user_id' in session:
        return render_template('add.html')
    else:
        return redirect('/login')


@app.route('/add', methods=['POST'])
def add_post():
    if 'user_id' in session:
        task = request.form.get('task')
        user_id = session['user_id']
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("INSERT INTO task(task,user_id) VALUES(?,?)",
                  (task, user_id))
        conn.commit()
        c.close()
        return redirect('/list')
    else:
        return redirect('/login')

    # cur.execute("INSERT INTO `users` (`id`, `name`, `age`, `gender`) VALUES (0, {name}, {age}, {gender});".format(name=name, age=age, gender=gender))


@app.route('/list')
def task_list():
    if 'user_id' in session:
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        user_id = session['user_id']
        c.execute('select id, task from task where user_id=?', (user_id,))
        task_list = [dict(id=i, task=t) for i, t in c.fetchall()]
        c.close()
        return render_template('task_list.html', task_list=task_list)
    else:
        return redirect('/login')


@app.route('/edit/<int:id>')
def edit(id):
    if 'user_id' in session:
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute('select id, task from task where id = ?', (id,))
        item = c.fetchone()
        if item is None:
            return app.errorhandler['404.html']
        item = dict(id=item[0], task=item[1])
        c.close()
        return render_template('edit.html', item=item)
    else:
        return redirect('/login')


@app.route('/edit', methods=['POST'])
def update_task():
    if 'user_id' in session:
        id = request.form.get('id')
        task = request.form.get('task')
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("UPDATE task SET task=? where id=?", (task, id))
        conn.commit()
        c.close()
        return redirect('/list')
    else:
        return redirect('/login')


@app.route('/del/<int:id>')
def del_get(id):
    if 'user_id' in session:
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute('select id, task from task where id = ?', (id,))
        item = c.fetchone()
        if item is None:
            return app.errorhandler['404.html']
        item = dict(id=item[0], task=item[1])
        c.close()
        return render_template('del.html', item=item)
    else:
        return redirect('/login')


@app.route('/del', methods=['POST'])
def del_post():
    if 'user_id' in session:
        id = request.form.get('id')
        task = request.form.get('task')
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("delete from task where id = ?", (id,))
        conn.commit()
        c.close()
        return redirect('/list')
    else:
        return redirect('/login')


@app.route('/regist')
def regist_get():
    if 'user_id' in session:
        return redirect('/list')
    else:
        return render_template('regist.html')


@app.route('/regist', methods=['POST'])
def regist_post():
    if 'user_id' in session:
        return redirect('/list')
    else:
        name = request.form.get('name')
        password = request.form.get('password')

        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("insert into users(name, password) values(?,?)",
                  (name, password))
        conn.commit()
        c.close()
        return redirect('/login')


@app.route('/login')
def login_get():
    if 'user_id' in session:
        return redirect('/list')
    else:
        return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    if 'user_id' in session:
        return redirect('/list')
    else:
        name = request.form.get('name')
        password = request.form.get('password')
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute(
            'select id from users where name = ? and password = ?', (name, password))
        user_id = c.fetchone()
        c.close()

        if user_id is None:
            return render_template('login.html')
        else:
            session['user_id'] = user_id[0]
            return redirect('/list')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')


@app.errorhandler(404)
def notfound(code):
    return render_template('404.html')


if __name__ == '__main__':
    app.run()

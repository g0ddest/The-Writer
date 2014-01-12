from app import app

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['username'] and request.form['name'] and request.form['password']:
            mdfive = hashlib.md5()
            mdfive.update(request.form['password'])
            #TODO: Potential injection. Parse data, please
            user = users.find_one({'login': request.form['username']})
            if user:
                return 'Not a unique username'
            else:
                users.insert({
                    'login': request.form['username'],
                    'password': mdfive.hexdigest(),
                    'name': request.form['name']
                })
                return "User added!"
        else:
            return 'Please, fill all fields'
    return '''
        <form action="" method="post">
            <p><input placeholder="Name" type=text name=name>
            <p><input placeholder="Login" type=text name=username>
            <p><input placeholder="Password" type=text name=password>
            <p><input type=submit value=Register>
        </form>
    '''

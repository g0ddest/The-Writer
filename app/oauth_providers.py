from app import app, connection
from flask_oauth import OAuth
from flask import redirect, url_for, request, session, flash

oauth = OAuth()

bitbucket = oauth.remote_app('bitbucket',
    base_url='https://bitbucket.org/!api/1.0/',
    request_token_url='https://bitbucket.org/!api/1.0/oauth/request_token',
    access_token_url='https://bitbucket.org/!api/1.0/oauth/access_token',
    authorize_url='https://bitbucket.org/!api/1.0/oauth/authenticate',
    consumer_key=app.config['BITBUCKET_KEY'],
    consumer_secret=app.config['BITBUCKET_SECRET']
)

@app.route('/login/bitbucket')
def login_bitbucket():
    if session.has_key('bitbucket_token'):
        token = session['bitbucket_token']
        user = connection.User.find_one({
            'bitbucket.oauth_token': token[0],
            'bitbucket.oauth_token_secret': token[1]
        })
        session['user_id'] = str(user._id)
        return redirect('/') # FIXME
    return bitbucket.authorize(callback=url_for('authorized_bitbucket',
        next=request.args.get('next') or request.referrer or None))

@app.route('/authorized/bitbucket')
@bitbucket.authorized_handler
def authorized_bitbucket(resp):
    next_url = request.args.get('next') or '/'
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['bitbucket_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )

    req_user = bitbucket.get('user').data['user']
    req_user['oauth_token'] = resp['oauth_token']
    req_user['oauth_token_secret'] = resp['oauth_token_secret']
    user = connection.User.get_or_create_from_bitbucket( req_user )
    session['user_id'] = str(user._id)

    flash('You were signed in with Bitbucket')
    return redirect(next_url)

@bitbucket.tokengetter
def get_bitbucket_token(token=None):
    return session.get('bitbucket_token')

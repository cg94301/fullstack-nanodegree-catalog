from flask import Flask, render_template, url_for, request, redirect, flash

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbinit import Base, Varietal, Wine

# imports for authentication
from flask import session as login_session
import random, string

# more imports for authentication
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']

app = Flask(__name__)

engine = create_engine('sqlite:///redwines.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    print "login_session: "
    print login_session
    # prevent cross-site reference forgery attack
    print "request state:"
    print request
    print request.args.get('state')
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    print "code: " + code

    try:
        # Upgrade the authorization code into a credentials object
        print "oauth_flow start"
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        print "oauth_flow:"
        print oauth_flow
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print "credentials: "
        print credentials
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    print "access_token: "
    print access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    print "result: "
    print result
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    #login_session['credentials'] = credentials
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print "data: "
    print data

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    #user_id = getUserID(login_session['email'])
    #if not user_id:
    #    user_id = createUser(login_session)
    #login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "login_session: "
    print login_session
    print "done!"
    return output

@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    print "The current session state is %s" % login_session['state']
    return render_template('login.html', state=state)

# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    varietals = session.query(Varietal).all()
    varietalcount = session.query(Varietal).count()
    wines = session.query(Wine).order_by(Wine.id.desc()).limit(varietalcount)
    return render_template('catalog.html', varietals=varietals, wines=wines)

@app.route('/catalog/<int:varietal_id>/')
@app.route('/catalog/<int:varietal_id>/wines/')
def showWines(varietal_id):
    #varietals = session.query(Varietal).filter(Varietal.id != varietal_id).all()
    varietals = session.query(Varietal).all()
    varietal = session.query(Varietal).filter_by(id = varietal_id).one()
    wines = session.query(Wine).filter_by(varietal_id=varietal_id).all()
    count = session.query(Wine).filter_by(varietal_id=varietal_id).count()
    return render_template('wines.html', varietals=varietals, varietal=varietal, wines=wines, count=count)

@app.route('/catalog/wine/<int:wine_id>/')
def showWine(wine_id):
    wine = session.query(Wine).filter_by(id=wine_id).one()
    return render_template('description.html', wine=wine)

@app.route('/catalog/add/', methods=['GET', 'POST'])
def addWine():
    if request.method == 'POST':
        print "POST"
        print request.form
        varietal = session.query(Varietal).filter_by(name=request.form['varietal']).one()
        newWine = Wine(name=request.form['name'], year=request.form['year'], description=request.form['description'],
                       label=request.form['label'],varietal_id=varietal.id)
        session.add(newWine)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        varietals = session.query(Varietal).all()
        return render_template('addwine.html', varietals=varietals)

@app.route('/catalog/wine/<int:wine_id>/edit/', methods=['GET', 'POST'])
def editWine(wine_id):
    varietals = session.query(Varietal).all()
    wine = session.query(Wine).filter_by(id = wine_id).one()
    if request.method == 'POST':
        if request.form['name']:
            wine.name = request.form['name']
        if request.form['year']:
            wine.year = request.form['year']
        if request.form['label']:
            wine.label = request.form['label']
        if request.form['description']:
            wine.description = request.form['description']
        session.add(wine)
        session.commit()
        return redirect(url_for('showWine', wine_id=wine_id))
    else:
        return render_template('editwine.html', varietals=varietals, wine=wine)

@app.route('/catalog/wine/<int:wine_id>/delete/', methods=['GET', 'POST'])
def deleteWine(wine_id):
    wine = session.query(Wine).filter_by(id = wine_id).one()
    print request.form
    if request.method == 'POST':
        session.delete(wine)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deletewine.html', wine=wine)

if __name__ == '__main__':
    app.secret_key = 'catalog_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

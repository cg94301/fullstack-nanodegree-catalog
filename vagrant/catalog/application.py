from flask import Flask, render_template, url_for, request, redirect, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbinit import Base, Varietal, Wine, User

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

# imports for XML manipulation
import xml.etree.ElementTree as ET

CLIENT_ID = json.loads(open('/var/www/catalog/client_secrets.json','r').read())['web']['client_id']

app = Flask(__name__)

engine = create_engine('postgresql://catalog:caTal0g@localhost:5432/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Helper functions to check login status
def checkLogin():
    if 'username' in login_session:
        return True
    else:
        return False

def checkLoginUser(wine):
    creator = getUserInfo(wine.user_id)
    if 'username' in login_session and creator.id == login_session['user_id']:
        return True
    else:
        return False

# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id
    
def getUserInfo(user_id):
    users = session.query(User).all()
    names = [(u.name, u.id) for u in users]
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Helper function to build XML tree
def buildXML(data,subname):
    root = ET.Element('catalog')
    for d in data:
        wine = ET.SubElement(root, 'wine')
        for k,v in d.iteritems():
            subelem = ET.SubElement(wine, k)
            subelem.text = str(v)
    return (ET, root)
    

# Route section

# Google+ OAuth API will post to this route
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    # prevent cross-site reference forgery attack
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
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
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    return output

# Route to log out of the app
@app.route('/gdisconnect/')
def gdisconnect():
    access_token = login_session['credentials']
    if access_token is None:
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['credentials']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
	del login_session['credentials'] 
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return redirect(url_for('showCatalog'))
    else:
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

# Route to log into the app
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
    return render_template('catalog.html', varietals=varietals, wines=wines, loginOK=checkLogin())

# JSON endpoint for varietals
@app.route('/catalog/JSON/')
def catalogJSON():
    varietalsobj = session.query(Varietal).all()
    varietals=[i.serialize for i in varietalsobj]
    output = jsonify(varietals=[i.serialize for i in varietalsobj])
    return output

# XML endpoint for varietals
@app.route('/catalog/XML/')
def catalogXML():
    varietalsobj = session.query(Varietal).all()
    varietals=[i.serialize for i in varietalsobj]
    (ET, root) = buildXML(varietals,'varietal')
    x = ET.tostring(root)
    output = app.response_class(ET.tostring(root), mimetype='application/xml')
    return output

# Show wines by varietal
@app.route('/catalog/<int:varietal_id>/')
@app.route('/catalog/<int:varietal_id>/wines/')
def showWines(varietal_id):
    varietals = session.query(Varietal).all()
    varietal = session.query(Varietal).filter_by(id = varietal_id).one()
    wines = session.query(Wine).filter_by(varietal_id=varietal_id).all()
    count = session.query(Wine).filter_by(varietal_id=varietal_id).count()
    return render_template('wines.html', varietals=varietals, varietal=varietal, wines=wines, count=count, loginOK=checkLogin())

# JSON endpoint for wines by varietal
@app.route('/catalog/<int:varietal_id>/wines/JSON/')
def winesJSON(varietal_id):
    winesobj = session.query(Wine).filter_by(varietal_id=varietal_id).all()
    return jsonify(wines=[i.serialize for i in winesobj])

# XML endpoint for wines by varietal
@app.route('/catalog/<int:varietal_id>/wines/XML/')
def winesXML(varietal_id):
    winesobj = session.query(Wine).filter_by(varietal_id=varietal_id).all()
    wines = [i.serialize for i in winesobj]
    (ET, root) = buildXML(wines,'wine')
    output = app.response_class(ET.tostring(root), mimetype='application/xml')
    return output

# Show wine description
@app.route('/catalog/wine/<int:wine_id>/')
def showWine(wine_id):
    wine = session.query(Wine).filter_by(id=wine_id).one()
    return render_template('description.html', wine=wine, loginOK=checkLogin(), loginUserOK=checkLoginUser(wine))

# Wine description JSON endpoint
@app.route('/catalog/wine/<int:wine_id>/JSON/')
def wineJSON(wine_id):
    wineobj = session.query(Wine).filter_by(id=wine_id).one()
    return jsonify(wine=wineobj.serialize)

# Wine description XML endpoint
@app.route('/catalog/wine/<int:wine_id>/XML/')
def wineXML(wine_id):
    wineobj = session.query(Wine).filter_by(id=wine_id).one()
    wine = wineobj.serialize
    (ET, root) = buildXML([wine], 'wine')
    output = app.response_class(ET.tostring(root), mimetype='application/xml')
    return output

# Add wine when logged in
@app.route('/catalog/add/', methods=['GET', 'POST'])
def addWine():
    if not checkLogin():
        return redirect('/login/')
    if request.method == 'POST':
        varietal = session.query(Varietal).filter_by(name=request.form['varietal']).one()
        newWine = Wine(name=request.form['name'], year=request.form['year'], description=request.form['description'],
                       label=request.form['label'],varietal_id=varietal.id, user_id=login_session['user_id'])
        session.add(newWine)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        varietals = session.query(Varietal).all()
        return render_template('addwine.html', varietals=varietals, loginOK=checkLogin())

# Edit wine when logged in
@app.route('/catalog/wine/<int:wine_id>/edit/', methods=['GET', 'POST'])
def editWine(wine_id):
    wine = session.query(Wine).filter_by(id = wine_id).one()
    if not checkLoginUser(wine):
        return redirect('/login/')
    varietals = session.query(Varietal).all()
    if request.method == 'POST':
        if request.form['varietal']:
            varietal = session.query(Varietal).filter_by(name=request.form['varietal']).one()
            wine.varietal_id=varietal.id
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
        return render_template('editwine.html', varietals=varietals, wine=wine, loginOK=checkLoginUser(wine))

# Delete wine
@app.route('/catalog/wine/<int:wine_id>/delete/', methods=['GET', 'POST'])
def deleteWine(wine_id):
    wine = session.query(Wine).filter_by(id = wine_id).one()
    if not checkLoginUser(wine):
        return redirect('/login/')
    if request.method == 'POST':
        session.delete(wine)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deletewine.html', wine=wine, loginOK=checkLoginUser(wine))

if __name__ == '__main__':
    app.secret_key = 'catalog_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

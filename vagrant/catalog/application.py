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

CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']

app = Flask(__name__)

engine = create_engine('sqlite:///redwines.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

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
    print names
    print user_id
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

def buildXML(data,subname):
    print data
    root = ET.Element('catalog')
    item = ET.SubElement(root, subname)
    for d in data:
        print d
        item2 = ET.SubElement(item, 'item')
        for k,v in d.iteritems():
            print k
            print v
            subelem = ET.SubElement(item2, k)
            subelem.text = str(v)
        #name = ET.SubElement(item, 'name')
        #name.text = "Pinot"
    return (ET, root)
    

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
    print "login_session: "
    print login_session
    print "done!"
    return output

@app.route('/gdisconnect/')
def gdisconnect():
    print "disconnect"
    print "login_session: "
    print login_session
    #access_token = login_session['access_token']
    access_token = login_session['credentials']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    #url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    print "access token:"
    print login_session['credentials']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['credentials']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	#del login_session['access_token'] 
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

@app.route('/catalog/JSON/')
def catalogJSON():
    varietalsobj = session.query(Varietal).all()
    #print varietalsobj
    varietals=[i.serialize for i in varietalsobj]
    #print varietals
    output = jsonify(varietals=[i.serialize for i in varietalsobj])
    print output
    return output

@app.route('/catalog/XML/')
def catalogXML():
    varietalsobj = session.query(Varietal).all()
    varietals=[i.serialize for i in varietalsobj]
    #print varietals
    (ET, root) = buildXML(varietals,'varietal')
    x = ET.tostring(root)
    print "x: " + x
    output = app.response_class(ET.tostring(root), mimetype='application/xml')
    print output
    return output

@app.route('/catalog/<int:varietal_id>/')
@app.route('/catalog/<int:varietal_id>/wines/')
def showWines(varietal_id):
    #varietals = session.query(Varietal).filter(Varietal.id != varietal_id).all()
    varietals = session.query(Varietal).all()
    varietal = session.query(Varietal).filter_by(id = varietal_id).one()
    wines = session.query(Wine).filter_by(varietal_id=varietal_id).all()
    count = session.query(Wine).filter_by(varietal_id=varietal_id).count()
    return render_template('wines.html', varietals=varietals, varietal=varietal, wines=wines, count=count, loginOK=checkLogin())

@app.route('/catalog/<int:varietal_id>/wines/JSON/')
def winesJSON(varietal_id):
    winesobj = session.query(Wine).filter_by(varietal_id=varietal_id).all()
    return jsonify(wines=[i.serialize for i in winesobj])

@app.route('/catalog/<int:varietal_id>/wines/XML/')
def winesXML(varietal_id):
    winesobj = session.query(Wine).filter_by(varietal_id=varietal_id).all()
    wines = [i.serialize for i in winesobj]
    (ET, root) = buildXML(wines,'wine')
    output = app.response_class(ET.tostring(root), mimetype='application/xml')
    print output
    return output

@app.route('/catalog/wine/<int:wine_id>/')
def showWine(wine_id):
    wine = session.query(Wine).filter_by(id=wine_id).one()
    return render_template('description.html', wine=wine, loginOK=checkLogin(), loginUserOK=checkLoginUser(wine))

@app.route('/catalog/wine/<int:wine_id>/JSON/')
def wineJSON(wine_id):
    wineobj = session.query(Wine).filter_by(id=wine_id).one()
    return jsonify(wine=wineobj.serialize)

@app.route('/catalog/wine/<int:wine_id>/XML/')
def wineXML(wine_id):
    wineobj = session.query(Wine).filter_by(id=wine_id).one()
    wine = wineobj.serialize
    print wine
    (ET, root) = buildXML([wine], 'wine')
    output = app.response_class(ET.tostring(root), mimetype='application/xml')
    print output
    return output

@app.route('/catalog/add/', methods=['GET', 'POST'])
def addWine():
    if not checkLogin():
        return redirect('/login/')
    if request.method == 'POST':
        print "POST"
        print request.form
        varietal = session.query(Varietal).filter_by(name=request.form['varietal']).one()
        newWine = Wine(name=request.form['name'], year=request.form['year'], description=request.form['description'],
                       label=request.form['label'],varietal_id=varietal.id, user_id=login_session['user_id'])
        session.add(newWine)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        varietals = session.query(Varietal).all()
        return render_template('addwine.html', varietals=varietals, loginOK=checkLogin())

@app.route('/catalog/wine/<int:wine_id>/edit/', methods=['GET', 'POST'])
def editWine(wine_id):
    wine = session.query(Wine).filter_by(id = wine_id).one()
    if not checkLoginUser(wine):
        return redirect('/login/')
    varietals = session.query(Varietal).all()
    if request.method == 'POST':
        if request.form['varietal']:
            varietal = session.query(Varietal).filter_by(name=request.form['varietal']).one()
            print varietal.name
            print varietal.id
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

@app.route('/catalog/wine/<int:wine_id>/delete/', methods=['GET', 'POST'])
def deleteWine(wine_id):
    wine = session.query(Wine).filter_by(id = wine_id).one()
    if not checkLoginUser(wine):
        return redirect('/login/')
    print request.form
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

from flask import Flask, render_template, url_for, request, redirect

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbinit import Base, Varietal, Wine

app = Flask(__name__)

engine = create_engine('sqlite:///redwines.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

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
        newWine = Wine(name=request.form['name'], year=request.form['year'], varietal_id=varietal.id)
        return redirect(url_for('addWine'))
    else:
        varietals = session.query(Varietal).all()
        return render_template('addwine.html', varietals=varietals)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, render_template, url_for

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
    return render_template('wines.html', varietals=varietals, varietal=varietal, wines=wines)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# Table to track log in user and wine ownership
class User(Base):
    __tablename__= 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(250))

# Table for available varietals
class Varietal(Base):
    __tablename__='varietal'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id' : self.id,
           'name' : self.name,
       }

# Table for wine
class Wine(Base):
    __tablename__='wine'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    year = Column(Integer)
    label = Column(String(250))
    description = Column(String)
    varietal_id = Column(Integer, ForeignKey('varietal.id'))
    varietal = relationship(Varietal)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id' : self.id,
           'name' : self.name,
           'year' : self.year,
           'description' : self.description,
           'label' : self.label,
           'varietal_id' : self.varietal_id,
       }


engine = create_engine('sqlite:///redwines.db')
Base.metadata.create_all(engine)

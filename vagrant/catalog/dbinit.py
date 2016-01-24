from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__= 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(250))

class Varietal(Base):
    __tablename__='varietal'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

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

engine = create_engine('sqlite:///redwines.db')
Base.metadata.create_all(engine)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import *
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy.pool import NullPool


## Creacion del engine
#engine=create_engine("mysql+pymysql://cris1:magma3@localhost/biolac",pool_recycle=3600)
engine=create_engine("mysql+pymysql://cris1:magma3@localhost/biolac",poolclass=NullPool)

## Creacion de un session factory
session_factory=sessionmaker()
dbSession=scoped_session(session_factory)
dbSession.remove()
session_factory.configure(bind=engine)

## Definicion de la base declarativa dinamica de sql alchemy
Base=declarative_base()
Base.metadata.bind=engine

@contextmanager
def session_manager():

    """ Puedo crear un scope safe thread para las sesiones de las base de
    datos ademas  dbSession crea objetos session por lo que puedo crearlos
    cada vez que necesite  """

    session=dbSession()

    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        raise(e)

    finally:
        session.close()

def init_db():

	Base.metadata.create_all(bind=engine)

def delete_schema():

	Base.metadata.clear_mappers()

def drop_db():

	Base.metadata.drop_all(bind=engine)



if __name__=="__main__":

    drop_db()
    init_db()

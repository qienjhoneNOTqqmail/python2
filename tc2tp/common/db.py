from contextlib import contextmanager

from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import config

# mongodb
mongo_db = MongoClient(config.MONGO_URI, maxPoolSize=None)[config.DATABASE]

# mysql
engine = create_engine(config.MYSQL_URI,
                       echo=config.DEBUG,
                       pool_size=config.POOL_SIZE,
                       pool_recycle=config.POOL_RECYCLE)
Session = sessionmaker(bind=engine)


@contextmanager
def getSession(session=Session()):
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

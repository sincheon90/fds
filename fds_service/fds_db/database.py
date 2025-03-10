from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base

engine = create_engine("sqlite:///fds.db", echo=True)
metadata = MetaData()
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)
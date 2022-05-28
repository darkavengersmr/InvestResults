import databases
from sqlalchemy import create_engine, MetaData

from config import SQLALCHEMY_DATABASE_URL

database = databases.Database(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

metadata = MetaData()

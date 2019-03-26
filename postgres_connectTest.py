from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_string = "postgres://dbmaster:dbpa$$w0rd!@w210postgres01.c8siy60gz3hg.us-east-1.rds.amazonaws.com:5432/w210results"
engine = create_engine(db_string, echo=True)
Base = declarative_base(engine)

class Results(Base):
    __tablename__ = 'test_upload'
    # __tablename__ = 'dummy_table'
    # __tablename__ = str(current_user.username + '_results')
    __table_args__ = {'autoload':True}

metadata = Base.metadata
Session = sessionmaker(bind=engine)
session = Session()

qry = session.query(Results)

header = Results.__table__.columns.keys()

for record in qry.all():
    print([getattr(record, c) for c in header ])

session.close()
engine.dispose()

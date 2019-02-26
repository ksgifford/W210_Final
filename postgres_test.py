from sqlalchemy import create_engine, Column, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_string = "postgres://dbmaster:dbpa$$w0rd!@w210postgres01.c8siy60gz3hg.us-east-1.rds.amazonaws.com:5432/w210results"

db = create_engine(db_string)
base = declarative_base()

class AnimalEvents(base):
    __tablename__ =  'dummy_table'

    eventID = Column(String, primary_key=True)
    species = Column(String)
    cameraID = Column(String)
    timestamp = Column(String)

Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)

#Create dummy table
event = AnimalEvents(eventID="1", species="black bear", cameraID="001", timestamp="2019-02-22 14:38:00")
session.add(event)
session.commit()

#Read
events = session.query(AnimalEvents)
for event in events:
    print(event)


def export():
    q = session.query(AnimalEvents)
    file = './results.csv'

    with open(file, 'w') as csvfile:
        outcsv = csv.writer(csvfile, delimiter=',',quotechar='"', quoting = csv.QUOTE_MINIMAL)
        header = AnimalEvents.__table__.columns.keys()

        outcsv.writerow(header)

        for record in q.all():
            outcsv.writerow([getattr(record, c) for c in header ])

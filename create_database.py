# Import dependencies.
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import Session

# Create the Listing class.
class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True)
    address = Column(String(255))
    price = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    square_feet = Column(Float)
    acres = Column(Float)
    built = Column(Integer)
    county = Column(String(255))
    city = Column(String(255))
    zipcode = Column(Integer)
    HS = Column(String(255))
    MS = Column(String(255))
    ES = Column(String(255))

# Create a list to hold off of the listing objects.
listing_list = []

# Create an instance of the Listing class for every row in the dataframe of the scraped data.
for index, row in scraped_data.itterrows():
    listing = Listing(
        address = row["address"],
        price = row["price"],
        bedrooms = row["bedrooms"],
        bathrooms = row["bathrooms"],
        square_feet = row["square_feet"],
        acres = row["acres"],
        built = row["built"],
        county = row["county"],
        city = row["city"],
        zipcode = row["zipcode"],
        HS = row["HS"],
        MS = row["MS"],
        ES = row["ES"]
    )
    listing_list.append(listing)

# Create the database connection.
database_path = "assets/housing"
engine = create_engine(f"sqlite:///{database_path}")
conn = engine.connect()

# Create a metadata layer that abstracts the SQL database.
Base.metadata.create_all(engine)

# Clear out the database if necessary.
# Base.metadata.drop_all(engine)

# Create a session to connec to the database.
session = Session(bind=engine)

# Commit records to the session.
for listing in listing_list:
    session.add(listing)
session.commit()

# Close the session.
session.close()
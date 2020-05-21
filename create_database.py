# Import dependencies.
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Float
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Create the Listings class.
class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True)
    address = Column(String(255))
    price = Column(Integer)
    home_type = Column(String(255))
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    square_feet = Column(Integer)
    built = Column(Integer)
    lot_size = Column(Float)
    neighborhood = Column(String(255))
    county = Column(String(255))
    city = Column(String(255))
    zipcode = Column(Integer)
    high_school = Column(String(255))
    middle_school = Column(String(255))
    elementary_school = Column(String(255))

# Create the database connection.
database_path = "Resources/housing.sqlite"
engine = create_engine(f"sqlite:///{database_path}")
conn = engine.connect()
session = Session(bind=engine)

# Clear out current data in the database.
Base.metadata.drop_all(engine)

# Drop all current data.
meta.drop_all()

# Create the listings table.
listings = Table(
    "listings", meta,
    Column("id", Integer, primary_key=True),
    Column("address", String(255)),
    Column("price", Integer),
    Column("home_type", String(255)),
    Column("bedrooms", Integer),
    Column("bathrooms", Float),
    Column("square_feet", Integer),
    Column("built", Integer),
    Column("lot_size", Float),
    Column("neighborhood", String(255)),
    Column("county", String(255)),
    Column("city", String(255)),
    Column("zipcode", Integer),
    Column("high_school", String(255)),
    Column("middle_school", String(255)),
    Column("elementary_school", String(255))
)
meta.create_all()

# Create a metadata layer that abstracts the database.
Base.metadata.create_all(engine)

# Store the scraped data as a data frame.
scraped_data = pd.read_csv("Resources/housingData.csv")

# Insert data into the database.
for _, row in scraped_data.iterrows():
    listing = Listing(
      address = row["address"],
      price = row["price"],
      home_type = row["home_type"],
      bedrooms = row["bedrooms"],
      bathrooms = row["bathrooms"],
      square_feet = row["square_feet"],
      built = row["built"],
      lot_size = row["lot_size"],
      neighborhood = row["neighborhood"],
      county = row["county"],
      city = row["city"],
      zipcode = row["zipcode"],
      high_school = row["high_school"],
      middle_school = row["middle_school"],
      elementary_school = row["elementary_school"]
      )
    session.add(listing)

# Commit all listings
session.commit()

# Close the session.
session.close()

# Close the connection.
conn.close()

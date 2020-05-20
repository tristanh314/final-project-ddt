# Import dependencies.
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, Float

# Create the database connection.
database_path = "Resources/housing.sqlite"
engine = create_engine(f"sqlite:///{database_path}")
meta = MetaData(engine)
conn = engine.connect()

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
    Column("neighborhood", String(255)),
    Column("county", String(255)),
    Column("city", String(255)),
    Column("zipcode", Integer),
    Column("high_school", String(255)),
    Column("middle_school", String(255)),
    Column("elementary_school", String(255))
)
meta.create_all()

# Store the scraped data as a data frame.
scraped_data = pd.read_csv("Resources/housingData.csv")

# Insert data into the database.
for _, row in scraped_data.iterrows():
    ins = listings.insert().values(
      address = row["address"],
      price = row["price"],
      home_type = row["home_type"],
      bedrooms = row["bedrooms"],
      bathrooms = row["bathrooms"],
      square_feet = row["square_feet"],
      built = row["built"],
      neighborhood = row["neighborhood"],
      county = row["county"],
      city = row["city"],
      zipcode = row["zipcode"],
      high_school = row["high_school"],
      middle_school = row["middle_school"],
      elementary_school = row["elementary_school"]
      )
    conn.execute(ins)

# Close the connection.
conn.close()
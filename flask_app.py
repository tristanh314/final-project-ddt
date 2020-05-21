import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from flask import Flask, jsonify
from flask_cors import CORS
from flask import request
from flask import render_template

from flask_cors import CORS


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/housing.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

# Create a database session object.
session = Session(engine)

# Get the table names of the database.
inspector = inspect(engine)
inspector.get_table_names()

# Save a reference to the listings table as "Listings".
Listings = Base.classes.listings

# Save reference to the table
# housing_listings = Base.classes.listings

# Flask Setup
#################################################
app = Flask(__name__)
CORS(app)

# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available aqi routes."""
    return (
        f"Welcome to Portland Housing API!<br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/listings'>Housing Data from past listings in Portland, OR</a><br/>"
    )

@app.route("/api/v1.0/listings")   
def boise():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query Boise's data
    housing_data = session.query(
        Listings.address,
        Listings.price,
        Listings.home_type,
        Listings.bedrooms,
        Listings.bathrooms,
        Listings.square_feet,
        Listings.built,
        Listings.lot_size,
        Listings.neighborhood,
        Listings.county,
        Listings.city,
        Listings.zipcode,
        Listings.high_school,
        Listings.middle_school,
        Listings.elementary_school,
        ).all()
    
    session.close()

    # Create a dictionary to hold boise data
    listing_data = []
    for (address, price, home_type, bedrooms, bathrooms, square_feet, built, lot_size, neighborhood, 
    county, city, zipcode, high_school, middle_school, elementary_school) in housing_data:
        structure_dict = {}
        structure_dict["address"] = address
        structure_dict["price"] = price
        structure_dict["home_type"] = home_type
        structure_dict["bedrooms"] = bedrooms
        structure_dict["bathrooms"] = bathrooms
        structure_dict["square_feet"] = square_feet
        structure_dict["built"] = built
        structure_dict["lot_size"] = lot_size
        structure_dict["neighborhood"] = neighborhood
        structure_dict["county"] = county
        structure_dict["city"] = city
        structure_dict["zipcode"] = zipcode
        structure_dict["high_school"] = high_school
        structure_dict["middle_school"] = middle_school
        structure_dict["elementary_school"] = elementary_school
        listing_data.append(structure_dict)

    return jsonify(listing_data)

# # Route to render index.html
# @app.route("/")
# def home():
#     # Return template and data
#     return render_template("index.html")


# @app.route("/<city_name>")
# def city(city_name):
#     return render_template("dashboard.html", urlOne= city_name)

if __name__ == '__main__':
    app.run(debug=True)
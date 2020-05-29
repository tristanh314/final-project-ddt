import numpy as np
import requests
from flask_pymongo import PyMongo
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify
from flask_cors import CORS
from flask import request
from flask import render_template, redirect
from flask import url_for
from tensorflow.keras.models import load_model
from joblib import load

#################################################
# Database Setup - Housing Data
#################################################
engine = create_engine("sqlite:///Resources/housingUpdated.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

# Create a database session object.
session = Session(engine)

# # Get the table names of the database.
# inspector = inspect(engine)
# inspector.get_table_names()

# Save a reference to the listings table as "Listings".
Listings = Base.classes.listings

# Flask Setup
#################################################
app = Flask(__name__)
CORS(app)

# Database Setup - Model Prediction
#################################################

# # Use PyMongo to establish Mongo connection
# mongo = PyMongo(app, uri="mongodb://localhost:27017/housing_model_predictions")

# Flask Routes
#################################################

# Route to render index.html
@app.route("/")
def home():

    models_range = "Input values to find your price range."

    # Return template and data
    return render_template("index.html", prediction = models_range)

@app.route("/machineLearning", methods=['POST'])
def machineLearning():
    # Load the model, scaler and label encoder.
    model = load_model("ML Models/housing_model_trained.h5")
    scaler = load("ML Models/minmax_scaler.bin")
    label_encoder = load("ML Models/label_encoder.bin")
    
    # Grabs the entire request dictionary
    user_input = request.values

    if user_input["bathrooms"]:
        bath = float(user_input["bathrooms"])
    else:
        bath = 0
    if user_input["bedrooms"]:
        bed = int(user_input["bedrooms"])
    else:
        bed = 0
    if user_input["yearBuilt"]:
        built = int(user_input["yearBuilt"])
    else:
        built = 0
    if user_input["lotSize"]:
        lot = float(user_input["lotSize"])
    else:
        lot = 0
    if user_input["sqFoot"]:
        sq = int(user_input["sqFoot"])
    else:
        sq = 0

    # Input data as bathrooms, bedrooms, built, lot_size, square_feet
    input_data = np.array([[bath,bed,built,lot,sq]])
    print(input_data)
    
    encoded_predictions = model.predict_classes(scaler.transform(input_data))
    prediction_labels = label_encoder.inverse_transform(encoded_predictions)

    high = prediction_labels[0].right
    low = prediction_labels[0].left
    models_range = f'${low:,.0f} - ${high:,.0f}'

    # Return template and data
    return render_template("index.html", prediction = models_range)
    # return jsonify(initial_request)

@app.route("/housingDataAPI")
def welcome():
    """List all available aqi routes."""
    return (
        f"Welcome to Portland Housing API!<br/><br/>"
        f"Available Routes:<br/>"
        f"<a href='/housingDataAPI/v1.0/listings'>Housing Data from past listings in Portland, OR</a><br/>"
    )


@app.route("/housingDataAPI/v1.0/listings")   
def housing_data():
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

if __name__ == '__main__':
    app.run(debug=True)

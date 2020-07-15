import numpy as np
import pandas as pd
import requests
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify
from flask_cors import CORS
from flask import request
from flask import render_template, redirect
from flask import url_for
from sklearn.model_selection import GridSearchCV
from joblib import load

#################################################
# Database Setup - Housing Data
#################################################
engine = create_engine("sqlite:///Resources/housing.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

# Create a database session object.
session = Session(engine)

# Save a reference to the listings table as "Listings".
Listings = Base.classes.listings

# Flask Setup
#################################################
app = Flask(__name__)
CORS(app)

# Flask Routes
#################################################

# Route to render index.html
@app.route("/")
def home():
    # Load the model, scaler and label encoder.
    district_df = pd.read_csv("Resources/district.csv")
    zipcode_df = pd.read_csv("Resources/zipcode.csv")	
    generic_search = [2, 1, 700, 1950, 0, "Portland Public", 97266]
    # Zipcodes and Districts accepted by model
    # listD = district_df.district.tolist()
    # listZ = zipcode_df.zipcode.tolist()
    listDisZip = [district_df.district.tolist(),zipcode_df.zipcode.tolist(), 
            generic_search]
    models_range = "Input values to see your results."

    # Return template and data
    return render_template("index.html", prediction = models_range, list = listDisZip)

@app.route("/machineLearning", methods=['POST'])
def machineLearning():
    # Load the model, scaler and label encoder.
    model = load("mlp_classifier.pkl")
    scaler = load("standard_scaler.pkl")
    label_encoder = load("label_encoder.pkl")
    district_df = pd.read_csv("Resources/district.csv")
    zipcode_df = pd.read_csv("Resources/zipcode.csv")	

    # Zipcodes and Districts accepted by model
    listD = district_df.district.tolist()
    listZ = zipcode_df.zipcode.tolist()
    
    # Grabs the entire request dictionary
    user_input = request.values

    # Grab user data (bath, bed, built, lot, sqfoot)
    try:
        bath = float(user_input["bathrooms"])
        warning1 = ""
    except:
        bath = 1
        warning1 = "Bathrooms requires an integer."
    try:
        bed = int(user_input["bedrooms"])
        warning2 = ""
    except:
        bed = 2
        warning2 = "Bedrooms requires an integer."
    try:
        built = int(user_input["yearBuilt"])
        warning3 = ""
    except:
        built = 1950
        warning3 = "Year built requires an integer."
    try:
        lot = float(user_input["lotSize"])
        warning4 = ""
    except:
        lot = 0
        warning4 = "Lot size requires a decimal."
    try:
        sq = int(user_input["sqFoot"])
        warning5 = ""
    except:
        sq = 900
        warning5 = "Square Feet requires an integer."

    # Print user input
    # print(user_input["zipcode"])
    # print(user_input["schoolDistrict"])

    # User input
    if (user_input["schoolDistrict"]) in district_df["district"] :
        sd = user_input["schoolDistrict"]
        warning6 = ""
    else:
        sd = "Portland Public"
        warning6 = "District was not found."
    if (user_input["zipcode"]) in zipcode_df["zipcode"]:
        zcode = (user_input["zipcode"])
        warning7 = ""
    else:
        zcode = 97266
        warning7 = "Zipcode was not found."
    
    data_input = [bed, bath, sq, built, lot, sd, zcode]
    warning_messages = ["Bathrooms requires an integer.",
        "Bedrooms requires an integer.",
        "Year built requires an integer.",
        "Lot size requires a decimal.",
        "Square Feet requires an integer.",
        "District was not found.",
        "Zipcode was not found."
    ]
    warning_list = [warning1, warning2, warning3, warning4, warning5, warning6, warning7]

    for warning in warning_list:
        if warning in warning_messages:
            warning8 = "Replaced with value(s) listed above."
            break
        else:
            warning8 = ""
    # print(warning_list) 

    # Items to display on website
    listDisZip = [listD,
        listZ,
        data_input,
        warning1,
        warning2,
        warning3,
        warning4,
        warning5,
        warning6,
        warning7,
        warning8
    ]

    # Input data as bathrooms, bedrooms, built, lot_size, square_feet
    # district, and zip code.
    input_data = np.array([[bath,
        bed,
        2020-built,
        lot,
        sq, 
    ] + ([0] * 45 )])

    # Place the value for district in the appropriate dummy column.
    i = 5
    for district in listD:
        if sd == district:
            input_data[0][i] = 1
            break
        else:
            i += 1
    
    # Place the value for zipcode in the appropriate dummy column.
    j = 17
    for zipcode in listZ:
        if zcode == zipcode:
            input_data[0][j] = 1
            break
        else:
            j += 1
    # print(input_data)

    encoded_predictions = model.predict(scaler.transform(input_data))
    prediction_labels = label_encoder.inverse_transform(encoded_predictions)

    high = prediction_labels[0].right
    low = prediction_labels[0].left
    models_range = f'${low:,.0f} - ${high:,.0f}'

    # Return template and data
    return render_template("index.html", prediction = models_range, list = listDisZip)

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

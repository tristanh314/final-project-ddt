#!/usr/bin/env python
# coding: utf-8

# Setup

# Import Dependencies.
import numpy as np
import pandas as pd

import json

from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from joblib import dump, load

# Prepare engine for database connection.
engine = create_engine("sqlite:///Resources/housing.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

# Create a database session object.
session = Session(engine)

# Save a reference to the listings table as "Listings".
Listings = Base.classes.listings

# Query listing data
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

# Create a dictionary to hold listing data
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

# Create a dataframe to use for our model.
data_df = pd.DataFrame(listing_data)

# Data Preprocessing

# Simplify home types 
for i in data_df.index:
    if "Floating" in data_df.at[i, "home_type"]:
        data_df.at[i, "home_type"] = "Floating"
    if "Condo" in data_df.at[i, "home_type"]:
        data_df.at[i, "home_type"] = "Condo"
    if "Single Family" in data_df.at[i, "home_type"]:
        data_df.at[i, "home_type"] = "Single Family"
    if "Manufactured" in data_df.at[i, "home_type"]:
        data_df.at[i, "home_type"] = "Manufactured"

# Change lot size to 0 for floating homes and condos
for i in data_df.index:
    if data_df.at[i, "home_type"] == "Floating":
        data_df.at[i, "lot_size"] = 0
    if data_df.at[i, "home_type"] == "Condo":
        data_df.at[i, "lot_size"] = 0

# Drop listing with null lot_size
data_df.drop(data_df[data_df["lot_size"].isnull()].index, inplace=True)
      
# Drop rows where high school cannot be compared.
data_df.drop(data_df[data_df.high_school == "Other"].index, inplace = True)

# Create district df
school_dict = ({"high_school" : ['Reynolds', 'Parkrose', 'David Douglas', 'Centennial', 'Cleveland',
        'Lincoln', 'Madison', 'Jefferson', 'Roosevelt', 'Sunset','Westview', 'Liberty', 'Beaverton', 
        'Grant', 'Southridge', 'Tigard', 'Wilson', 'Riverdale', 'Lake Oswego', 'Franklin',
        'Tualatin', 'Milwaukie', 'Scappoose'], "district" : ['Reynolds', 'Parkrose','David Douglas',
        'Centennial', 'Portland Public', 'Portland Public', 'Portland Public', 'Portland Public',
        'Portland Public', 'Beaverton', 'Beaverton', 'Hillsboro', 'Beaverton', 'Portland Public',
        'Beaverton', 'Tigard-Tualatin', 'Portland Public', 'Riverdale', 'Lake Oswego', 'Portland Public',
        'Tigard-Tualatin', 'North Clackamas', 'Scappose']})
district_df = pd.DataFrame(school_dict)

# Merge into OG df
data_df = pd.merge(data_df, district_df, on="high_school")

# Add age of home column
data_df["house_age"] = 2020 - data_df["built"]

# Prepare Data for Model

# Include only those columns that will be used in the deep learning model.
model_df = data_df.loc[:, ["bathrooms",
                            "bedrooms",
                            "house_age",
                            "lot_size",
                            "square_feet",
                            "district",
                            "zipcode",
                            "price"]
                       ]

# Drop rows with NaN entries.
model_df.dropna(inplace=True)

# Analysis of price data.
housing_prices = model_df["price"]

quartiles = housing_prices.quantile([.25,.5,.75])
lowerq = quartiles[0.25]
upperq = quartiles[0.75]
iqr = upperq-lowerq

lower_bound = lowerq - (1.5*iqr)
upper_bound = upperq + (1.5*iqr)

outlier_model_df = model_df.loc[(model_df['price'] < lower_bound) 
                                        | (model_df['price'] > upper_bound)]

# Define a function to place each listing into an interval up to the upper bound of prices.
def bin_price(price):
    """
    Input: Integer price of a home.
    Output: Pandas interval into which the price falls, outliers are put in the max bin up to the upper bound.
    """
    if price <= 375000:
        return pd.Interval(250000, 375000, closed="right")
    elif price <= 480000:
        return pd.Interval(375000, 480000, closed="right")
    elif price <= 650000:
        return pd.Interval(480000, 650000, closed="right")
    elif price <= 879900:
        return pd.Interval(650000, 879900, closed="right")
    else:
        return pd.Interval(879900, 1400125, closed="right")
    
# Add the price range column to the data frame.
model_df["price_range"] = model_df["price"].map(bin_price)
# Drop the original price data.
model_df.drop("price", axis=1, inplace=True)

# Get dummies for the values in home_type to use in the model.
model_df = pd.get_dummies(model_df, columns=["district", "zipcode"])

# Assign X (input) and y (target).
X = model_df.drop("price_range", axis=1)
y = model_df.loc[:,"price_range"].values.reshape(-1, 1)

# Split the data into training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
X_train.loc[48]

# Create a StandardScaler model and fit it to the training data
X_scaler = StandardScaler().fit(X_train)

# Save the scalar.
dump(X_scaler, 'standard_scaler.bin', compress=True)

# Transform the training and testing data using the X_scaler.
X_train_scaled = X_scaler.transform(X_train)
X_test_scaled = X_scaler.transform(X_test)

# Label encode the target data.
label_encoder = LabelEncoder()
label_encoder.fit(np.ravel(y_train))
encoded_y_train = label_encoder.transform(np.ravel(y_train))
encoded_y_test = label_encoder.transform(np.ravel(y_test))

# Save the label encoder
dump(label_encoder, 'label_encoder.bin', compress=True)

# Model Creation, Training, and Testing

# Create an mlp model.
model = MLPClassifier(hidden_layer_sizes=(100,100), random_state=42)

# Use grid search to tune the model.
grid = GridSearchCV(model,
                    {
                        "alpha":10.0 ** -np.arange(1, 7),
                        "learning_rate_init":10.0 ** -np.arange(1, 7),
                        "max_iter":[100, 200, 300],    
                    },
                    verbose=2)
grid.fit(X_train_scaled, encoded_y_train)

# Quantify the trained model
model_accuracy = grid.score(X=X_test_scaled, y=encoded_y_test)
print(f"Accuracy: {model_accuracy}")

# Save the Trained Model

# Save the model
dump(grid, 'mlp_classifier.bin', compress=True)
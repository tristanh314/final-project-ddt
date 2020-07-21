# Load dependencies
from sklearn.model_selection import GridSearchCV
from joblib import load
import numpy as np

# Test the Saved Model, Scaler, and Label Encoder

# Load the model, scaler and label encoder.
model = load("mlp_classifier.bin")
scaler = load("standard_scaler.bin")
label_encoder = load("label_encoder.bin")

# Input data for testing.
input_data = np.array([[  1.,   1.,  55.,   0., 744.,   0.,   0.,   0.,   0.,   0.,   0.,
          0.,   1.,   0.,   0.,   0.,   0.,   0.,   1.,   0.,   0.,   0.,
          0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
          0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
          0.,   0.,   0.,   0.,   0.,   0.]])

encoded_predictions = model.predict(scaler.transform(input_data))
prediction_labels = label_encoder.inverse_transform(encoded_predictions)

print(f"{prediction_labels[0].left}, {prediction_labels[0].right}")
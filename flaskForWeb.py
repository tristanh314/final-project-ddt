# Dependencies
from flask import Flask, jsonify
from flask_cors import CORS
from flask import request
from flask import render_template, redirect
from flask import url_for
from flask_cors import CORS

# Flask Setup
#################################################
app = Flask(__name__)
CORS(app)


# # Route to render index.html
@app.route("/")
def home():
    # Return template and data
    return render_template("index.html")


@app.route("/test/dev/", methods=['POST'])
def testingDev():
    # Grabs the entire request dictionary
    initial_request = request.values
        
    # Printing the method
    print(f"The method was {request.method}")
    print("Are you sure you are working?")
        
    # Debugging the entire dictionary
    print(float(initial_request["sqFoot"]) + float(initial_request["lotSize"]))
    return jsonify(initial_request['bathrooms'])
    

if __name__ == '__main__':
    app.run(debug=True)
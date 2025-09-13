from flask import Flask, render_template, request
import pandas as pd
import joblib

app = Flask(__name__)
pipeline = joblib.load("budgetbee_pipeline.joblib")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if request.method == "POST":
        desc = request.form["description"]
        amt = request.form["amount"]
        category = pipeline.predict([desc])[0]
        return render_template("result.html",
                               description=desc,
                               amount=amt,
                               category=category)

if __name__ == "__main__":
    app.run(debug=True)

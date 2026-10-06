from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymongo
from bson.objectid import ObjectId
from datetime import datetime
import os
import re
import urllib.parse

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

try:
    import certifi
    ca = certifi.where()
except ImportError:
    ca = None

def clean_mongo_uri(uri):
    """Encodes special characters in URI password like # or @ if unencoded."""
    if not uri or uri.startswith("mongodb://localhost") or uri.startswith("mongodb://127.0.0.1"):
        return uri
    match = re.match(r'^(mongodb(?:\+srv)?://)([^:]+):([^@]+)@(.+)$', uri)
    if match:
        prefix, user, password, rest = match.groups()
        unquoted = urllib.parse.unquote(password)
        encoded_password = urllib.parse.quote_plus(unquoted)
        return f"{prefix}{user}:{encoded_password}@{rest}"
    return uri

# Database connection
raw_uri = os.environ.get("MONGO_URI", "mongodb+srv://vidhyuth:vidhyuth008@cluster0.vqsqxdf.mongodb.net/?appName=Cluster0")
MONGO_URI = clean_mongo_uri(raw_uri)

db = None
collection = None

try:
    kwargs = {"serverSelectionTimeoutMS": 5000}
    if ca:
        kwargs["tlsCAFile"] = ca
    client = pymongo.MongoClient(MONGO_URI, **kwargs)
    client.server_info() # Verify connection
    db = client["expense_tracker_db"]
    collection = db["expenses"]
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    if collection is None:
        return jsonify({
            "error": "Could not connect to MongoDB. Please check your MongoDB Atlas IP Whitelist (Network Access)."
        }), 500
    try:
        expenses = list(collection.find().sort("date", pymongo.DESCENDING))
        for exp in expenses:
            exp['_id'] = str(exp['_id'])
        return jsonify(expenses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    if collection is None:
        return jsonify({"error": "Could not connect to MongoDB. Please check MongoDB Atlas IP Whitelist."}), 500
    data = request.json
    if not data or 'date' not in data or 'description' not in data or 'amount' not in data or 'category' not in data:
        return jsonify({"error": "Missing data"}), 400
    
    try:
        amount = float(data['amount'])
    except ValueError:
        return jsonify({"error": "Invalid amount"}), 400

    expense = {
        "date": data['date'],
        "description": data['description'],
        "amount": amount,
        "category": data['category']
    }
    
    try:
        result = collection.insert_one(expense)
        expense['_id'] = str(result.inserted_id)
        return jsonify(expense), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expenses/<expense_id>', methods=['PUT'])
def update_expense(expense_id):
    if collection is None:
        return jsonify({"error": "Could not connect to MongoDB. Please check MongoDB Atlas IP Whitelist."}), 500
    data = request.json
    try:
        amount = float(data['amount'])
    except ValueError:
        return jsonify({"error": "Invalid amount"}), 400

    update_data = {
        "date": data['date'],
        "description": data['description'],
        "amount": amount,
        "category": data['category']
    }
    
    try:
        result = collection.update_one({"_id": ObjectId(expense_id)}, {"$set": update_data})
        if result.matched_count:
            return jsonify({"message": "Updated successfully"})
        return jsonify({"error": "Expense not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    if collection is None:
        return jsonify({"error": "Could not connect to MongoDB. Please check MongoDB Atlas IP Whitelist."}), 500
    try:
        result = collection.delete_one({"_id": ObjectId(expense_id)})
        if result.deleted_count:
            return jsonify({"message": "Deleted successfully"})
        return jsonify({"error": "Expense not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.plaid_client import PlaidClient
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize Plaid client 
plaid_client = PlaidClient()

@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    try:
        token = plaid_client.create_link_token(user_id='user-1')
        return jsonify({'link_token': token})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exchange_token', methods=['POST'])
def exchange_public_token():
    try:
        public_token = request.json.get('public_token')
        accounts = request.json.get('accounts', [])

        if not public_token:
            return jsonify({'error': 'Missing public_token'}), 400

        # Exchange public token for access token
        access_token = plaid_client.exchange_public_token(public_token)

        return jsonify({'success': True, 'message': 'Account connected successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.plaid_client import PlaidClient
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize Plaid client 
plaid_client = PlaidClient()

@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    try:
        logger.info("Attempting to create link token")
        token = plaid_client.create_link_token(user_id='user-1')
        logger.info("Link token created successfully")
        return jsonify({'link_token': token})
    except Exception as e:
        logger.error(f"Error creating link token: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/exchange_token', methods=['POST'])
def exchange_public_token():
    try:
        logger.info("Received token exchange request")
        public_token = request.json.get('public_token')
        accounts = request.json.get('accounts', [])

        if not public_token:
            logger.error("Missing public_token in request")
            return jsonify({'error': 'Missing public_token'}), 400

        # Exchange public token for access token
        logger.info("Exchanging public token for access token")
        access_token = plaid_client.exchange_public_token(public_token)

        return jsonify({'success': True, 'message': 'Account connected successfully'})
    except Exception as e:
        logger.error(f"Error exchanging token: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask server on port 5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
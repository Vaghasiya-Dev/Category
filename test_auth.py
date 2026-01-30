from auth.auth_handler import AuthHandler
from auth.models import User, UserRepository
from config import Config
import json

# Test user data
test_user = {
    'user_id': 'user_5cf6a33d',
    'username': 'Vaghasiya Dev',
    'email': 'vaghasiyadev84@gmail.com',
    'password_hash': '098664894329a0ef178ae5cd0fba479b29918b52abb3ebc600bab3054d994f65',
    'role': 'super_admin',
    'created_by': None,
    'status': 'active',
    'created_at': '2026-01-23T14:21:43.812514',
    'updated_at': '2026-01-23T14:21:43.812514',
    'last_login': '2026-01-28T17:03:32.935134'
}

# Test token generation
from flask import Flask
app = Flask(__name__)
app.config.from_object(Config)

with app.app_context():
    # Generate token
    token = AuthHandler.generate_token(test_user)
    print("Token generated:", token[:50] + "...")
    
    # Try to decode it
    payload, error = AuthHandler.decode_token(token)
    if error:
        print("Error decoding:", error)
    else:
        print("Token decoded successfully")
        print("User ID from token:", payload.get('user_id'))
        
        # Try to get current user
        repo = UserRepository(Config.USERS_DB_PATH)
        user_from_db = repo.find_by_id(payload['user_id'])
        if user_from_db:
            print("User found in database:", user_from_db['username'])
        else:
            print("User NOT found in database")

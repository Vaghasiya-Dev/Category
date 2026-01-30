import jwt
from datetime import datetime, timedelta
from flask import current_app, request
from functools import wraps
from auth.models import UserRepository
 
 
class AuthHandler:
    """JWT authentication handler"""
    
    @staticmethod
    def generate_token(user):
        """
        Generate JWT access token
        
        Args:
            user: User dictionary
        
        Returns:
            str: JWT token
        """
        payload = {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def generate_refresh_token(user):
        """
        Generate JWT refresh token
        
        Args:
            user: User dictionary
        
        Returns:
            str: JWT refresh token
        """
        payload = {
            'user_id': user['user_id'],
            'type': 'refresh',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def decode_token(token):
        """
        Decode JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            tuple: (payload, error_message)
        """
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
    
    @staticmethod
    def get_current_user(token):
        """
        Get current user from token
        
        Args:
            token: JWT token string
        
        Returns:
            tuple: (user_dict, error_message)
        """
        payload, error = AuthHandler.decode_token(token)
        if error:
            return None, error
        
        repo = UserRepository()
        user = repo.find_by_id(payload['user_id'])
        
        if not user:
            return None, "User not found"
        
        if user['status'] != 'active':
            return None, "User account is disabled"
        
        return user, None

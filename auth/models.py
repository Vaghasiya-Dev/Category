import json
from datetime import datetime
from pathlib import Path
import hashlib
import uuid
 
 
class User:
    """User model representing a system user"""
    
    def __init__(self, user_id, username, email, password_hash, role, 
                 created_by=None, status='active'):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_by = created_by
        self.status = status
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.last_login = None
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password):
        """Verify password against hash"""
        return self.password_hash == self.hash_password(password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_by': self.created_by,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login
        }
    
    def to_safe_dict(self):
        """Convert user to dictionary without sensitive data"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_by': self.created_by,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login
        }
 
 
class UserRepository:
    """User data repository handling all user data operations"""
    
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_data()
    
    def _load_data(self):
        """Load users from database file, tolerating empty/invalid JSON"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    content = f.read().strip()
                    self.users = json.loads(content) if content else {}
            except (json.JSONDecodeError, OSError):
                self.users = {}
        else:
            self.users = {}
    
    def _save_data(self):
        """Save users to database file"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def create_user(self, username, email, password, role, created_by):
        """
        Create a new user
        
        Args:
            username: Username (must be unique)
            email: Email address (must be unique)
            password: Plain text password
            role: User role (emp, admin, super_admin)
            created_by: User ID of creator
        
        Returns:
            tuple: (user_dict, message)
        """
        # Check if username or email already exists
        for user in self.users.values():
            if user['username'] == username:
                return None, "Username already exists"
            if user['email'] == email:
                return None, "Email already exists"
        
        # Validate role
        valid_roles = ['emp', 'admin', 'super_admin']
        if role not in valid_roles:
            return None, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        password_hash = User.hash_password(password)
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            created_by=created_by
        )
        
        self.users[user_id] = user.to_dict()
        self._save_data()
        
        return user.to_safe_dict(), "User created successfully"
    
    def find_by_username(self, username):
        """Find user by username"""
        for user in self.users.values():
            if user['username'] == username:
                return user
        return None
    
    def find_by_email(self, email):
        """Find user by email"""
        for user in self.users.values():
            if user['email'] == email:
                return user
        return None
    
    def find_by_id(self, user_id):
        """Find user by user ID"""
        return self.users.get(user_id)
    
    def verify_password(self, user, password):
        """Verify user password"""
        return user['password_hash'] == User.hash_password(password)
    
    def update_last_login(self, user_id):
        """Update user's last login time"""
        if user_id in self.users:
            self.users[user_id]['last_login'] = datetime.now().isoformat()
            self._save_data()
    
    def get_all_users(self, requester_role):
        """
        Get all users based on requester's role
        
        Args:
            requester_role: Role of the user requesting the list
        
        Returns:
            list: List of users based on role permissions
        """
        if requester_role == 'super_admin':
            return list(self.users.values())
        elif requester_role == 'admin':
            # Admin can only see emp users
            return [u for u in self.users.values() if u['role'] == 'emp']
        else:
            return []
    
    def update_user_status(self, user_id, status, requester_role, requester_id):
        """
        Update user status
        
        Args:
            user_id: ID of user to update
            status: New status (active/inactive)
            requester_role: Role of user making the request
            requester_id: ID of user making the request
        
        Returns:
            tuple: (success, message)
        """
        if user_id not in self.users:
            return False, "User not found"
        
        target_user = self.users[user_id]
        
        # Permission checks
        if requester_role == 'emp':
            return False, "Insufficient permissions"
        
        if requester_role == 'admin':
            # Admin can only manage emp users
            if target_user['role'] != 'emp':
                return False, "Cannot manage users of this role"
        
        if requester_role == 'super_admin':
            # Super admin cannot manage other super admins
            if target_user['role'] == 'super_admin' and user_id != requester_id:
                return False, "Cannot manage other super admins"
        
        self.users[user_id]['status'] = status
        self.users[user_id]['updated_at'] = datetime.now().isoformat()
        self._save_data()
        
        return True, "Status updated successfully"
    
    def get_user_count_by_role(self):
        """Get count of users by role"""
        counts = {'emp': 0, 'admin': 0, 'super_admin': 0}
        for user in self.users.values():
            role = user['role']
            if role in counts:
                counts[role] += 1
        return counts
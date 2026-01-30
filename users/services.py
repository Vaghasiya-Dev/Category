from auth.models import UserRepository
from flask import current_app
 
 
class UserService:
    """User service handling user business logic"""
    
    def __init__(self):
        self.repo = UserRepository()
    
    def create_employee(self, username, email, password, created_by):
        """
        Create an employee user
        
        Args:
            username: Employee username
            email: Employee email
            password: Employee password
            created_by: User ID of the creator
        
        Returns:
            tuple: (user_dict, message)
        """
        return self.repo.create_user(username, email, password, 'emp', created_by)
    
    def create_admin(self, username, email, password, created_by):
        """
        Create an admin user
        
        Args:
            username: Admin username
            email: Admin email
            password: Admin password
            created_by: User ID of the creator
        
        Returns:
            tuple: (user_dict, message)
        """
        return self.repo.create_user(username, email, password, 'admin', created_by)
    
    def get_users_list(self, requester_role):
        """
        Get list of users based on requester role with RBAC filtering
        
        Args:
            requester_role: Role of the user requesting the list
        
        Returns:
            list: List of safe user dictionaries (filtered by RBAC)
        """
        all_users = self.repo.get_all_users(requester_role)
        
        # Apply RBAC filtering
        rbac_matrix = current_app.config.get('RBAC_MATRIX', {})
        allowed_roles_dict = rbac_matrix.get(requester_role, {})
        
        # Get roles that requester can view
        viewable_roles = []
        for role, actions in allowed_roles_dict.items():
            if 'view' in actions:
                viewable_roles.append(role)
        
        # Filter users by viewable roles
        filtered_users = [user for user in all_users if user['role'] in viewable_roles]
        
        return [self._remove_sensitive_data(user) for user in filtered_users]
    
    def _remove_sensitive_data(self, user):
        """Remove sensitive data from user dictionary"""
        safe_user = {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'created_by': user['created_by'],
            'status': user['status'],
            'created_at': user['created_at'],
            'last_login': user['last_login']
        }
        return safe_user
    
    def get_user_by_id(self, user_id, requester_role, requester_id):
        """
        Get user by ID with RBAC permission checks
        
        Args:
            user_id: User ID to retrieve
            requester_role: Role of the requester
            requester_id: User ID of the requester
        
        Returns:
            tuple: (user_dict, error_message)
        """
        user = self.repo.find_by_id(user_id)
        
        if not user:
            return None, "User not found"
        
        # Self access always allowed
        if user_id == requester_id:
            return self._remove_sensitive_data(user), None
        
        # Check RBAC permissions
        rbac_matrix = current_app.config.get('RBAC_MATRIX', {})
        allowed_actions = rbac_matrix.get(requester_role, {}).get(user['role'], [])
        
        if 'view' not in allowed_actions:
            return None, "Access denied"
        
        return self._remove_sensitive_data(user), None
    
    def update_user_status(self, user_id, status, requester_role, requester_id):
        """
        Update user status with RBAC permission checks
        
        Args:
            user_id: User ID to update
            status: New status (active/inactive)
            requester_role: Role of the requester
            requester_id: User ID of the requester
        
        Returns:
            tuple: (success, message)
        """
        user = self.repo.find_by_id(user_id)
        
        if not user:
            return False, "User not found"
        
        # Cannot change own status
        if user_id == requester_id:
            return False, "Cannot change your own status"
        
        # Check RBAC permissions
        rbac_matrix = current_app.config.get('RBAC_MATRIX', {})
        allowed_actions = rbac_matrix.get(requester_role, {}).get(user['role'], [])
        
        if 'update' not in allowed_actions:
            return False, f"You do not have permission to update {user['role']} users"
        
        # Update status
        return self.repo.update_user_status(user_id, status, requester_role, requester_id)
    
    def get_user_statistics(self):
        """
        Get user statistics
        
        Returns:
            dict: User count by role and status
        """
        return {
            'total': len(self.repo.users),
            'by_role': self.repo.get_user_count_by_role(),
            'active': sum(1 for u in self.repo.users.values() if u['status'] == 'active'),
            'inactive': sum(1 for u in self.repo.users.values() if u['status'] == 'inactive')
        }
    
    def update_user_profile(self, user_id, updates, requester_role, requester_id):
        """
        Update user profile information with RBAC checks
        
        Args:
            user_id: User ID to update
            updates: Dictionary of fields to update (username, email)
            requester_role: Role of the requester
            requester_id: User ID of the requester
        
        Returns:
            tuple: (updated_user, error_message)
        """
        user = self.repo.find_by_id(user_id)
        
        if not user:
            return None, "User not found"
        
        # Self access always allowed
        if user_id == requester_id:
            pass  # Allow self update
        else:
            # Check RBAC permissions
            rbac_matrix = current_app.config.get('RBAC_MATRIX', {})
            allowed_actions = rbac_matrix.get(requester_role, {}).get(user['role'], [])
            
            if 'update' not in allowed_actions:
                return None, f"You do not have permission to update {user['role']} users"
        
        # Validate and apply updates
        allowed_fields = ['username', 'email']
        for field in updates:
            if field not in allowed_fields:
                return None, f"Cannot update field: {field}"
        
        # Check username uniqueness
        if 'username' in updates and updates['username'] != user['username']:
            existing = self.repo.find_by_username(updates['username'])
            if existing and existing['user_id'] != user_id:
                return None, "Username already exists"
        
        # Check email uniqueness
        if 'email' in updates and updates['email'] != user['email']:
            existing = self.repo.find_by_email(updates['email'])
            if existing and existing['user_id'] != user_id:
                return None, "Email already exists"
        
        # Update user
        from datetime import datetime
        for field, value in updates.items():
            self.repo.users[user_id][field] = value
        
        self.repo.users[user_id]['updated_at'] = datetime.now().isoformat()
        self.repo._save_data()
        
        return self._remove_sensitive_data(self.repo.users[user_id]), None
    
    def update_password(self, user_id, old_password, new_password, requester_role, requester_id):
        """
        Update user password with RBAC checks
        
        Args:
            user_id: User ID to update
            old_password: Current password (for verification)
            new_password: New password
            requester_role: Role of the requester
            requester_id: User ID of the requester
        
        Returns:
            tuple: (success, message)
        """
        user = self.repo.find_by_id(user_id)
        
        if not user:
            return False, "User not found"
        
        # For own password, verify old password
        if user_id == requester_id:
            if not self.repo.verify_password(user, old_password):
                return False, "Current password is incorrect"
        else:
            # Check RBAC permissions for changing other users' passwords
            rbac_matrix = current_app.config.get('RBAC_MATRIX', {})
            allowed_actions = rbac_matrix.get(requester_role, {}).get(user['role'], [])
            
            if 'change_password' not in allowed_actions:
                return False, f"You do not have permission to change passwords for {user['role']} users"
        
        # Validate new password
        if len(new_password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Update password
        from auth.models import User
        from datetime import datetime
        
        self.repo.users[user_id]['password_hash'] = User.hash_password(new_password)
        self.repo.users[user_id]['updated_at'] = datetime.now().isoformat()
        self.repo._save_data()
        
        return True, "Password updated successfully"
    
    def delete_user(self, user_id, requester_role, requester_id):
        """
        Delete user (soft delete by setting status to inactive) with RBAC checks
        
        Args:
            user_id: User ID to delete
            requester_role: Role of the requester
            requester_id: User ID of the requester
        
        Returns:
            tuple: (success, message)
        """
        user = self.repo.find_by_id(user_id)
        
        if not user:
            return False, "User not found"
        
        # Cannot delete yourself
        if user_id == requester_id:
            return False, "Cannot delete your own account"
        
        # Check RBAC permissions
        rbac_matrix = current_app.config.get('RBAC_MATRIX', {})
        allowed_actions = rbac_matrix.get(requester_role, {}).get(user['role'], [])
        
        if 'delete' not in allowed_actions:
            return False, f"You do not have permission to delete {user['role']} users"
        
        # Perform soft delete
        self.repo.users[user_id]['status'] = 'inactive'
        from datetime import datetime
        self.repo.users[user_id]['updated_at'] = datetime.now().isoformat()
        self.repo._save_data()
        
        return True, "User deleted successfully"
    
    def validate_role_permission(self, requester_role, target_role, action):
        """
        Validate if requester role has permission to perform action on target role using RBAC matrix
        
        Args:
            requester_role: Role of the requester
            target_role: Role of the target user
            action: Action to perform (create, update, delete, view, change_password)
        
        Returns:
            tuple: (allowed, message)
        """
        rbac_matrix = current_app.config.get('RBAC_MATRIX', {})
        
        # Get allowed actions for this role combination
        allowed_actions = rbac_matrix.get(requester_role, {}).get(target_role, [])
        
        if action in allowed_actions:
            return True, f"Action '{action}' allowed on {target_role} users"
        else:
            return False, f"You do not have permission to {action} {target_role} users"

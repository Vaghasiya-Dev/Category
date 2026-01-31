import json
from datetime import datetime
from pathlib import Path
from database.kv_store import JSONStore
 
 
class Audience:
    """Audience model representing an audience record"""
    
    def __init__(self, audience_id, category_path, audience_info=None, created_by=None):
        self.audience_id = audience_id
        self.category_path = category_path
        self.audience_info = audience_info or {}
        self.created_by = created_by
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        """Convert audience to dictionary"""
        return {
            'audience_id': self.audience_id,
            'category_path': self.category_path,
            'category_path_str': ' -> '.join(self.category_path),
            'audience_info': self.audience_info,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
 
 
class AudienceRepository:
    """Audience data repository using KV storage"""
    
    def __init__(self, db_path=None):
        # db_path kept for backward compatibility but not used with KV
        self.kv_key = 'audiences'
        self.data = None
    
    def _load_data(self):
        """Load audiences from Vercel KV storage (always fresh read for serverless)"""
        try:
            self.data = JSONStore.read(self.kv_key)
            # Ensure data is a dict, not None
            if self.data is None:
                self.data = {}
            # Ensure it's actually a dict
            if not isinstance(self.data, dict):
                print(f"Warning: audiences data is not a dict: {type(self.data)}")
                self.data = {}
        except Exception as e:
            print(f"Error loading audiences data: {e}")
            import traceback
            traceback.print_exc()
            self.data = {}
    
    def _save_data(self):
        """Save audiences to Vercel KV storage"""
        JSONStore.write(self.kv_key, self.data)
    
    def add_audience_to_category(self, audience_id, category_path, audience_info=None, created_by=None):
        """
        Add audience to specific category path
        
        Args:
            audience_id: Unique audience identifier
            category_path: Category path list
            audience_info: Additional audience information
            created_by: User ID of creator
        
        Returns:
            tuple: (audience_dict, message)
        """
        # Fresh load for serverless
        self._load_data()
        
        # Create audience record if not exists
        if audience_id not in self.data:
            self.data[audience_id] = {
                'audience_id': audience_id,
                'audience_info': audience_info or {},
                'categories': [],
                'created_by': created_by,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        
        # Check if category path already exists
        category_str = ' -> '.join(category_path)
        for existing in self.data[audience_id]['categories']:
            if existing['category_path_str'] == category_str:
                return self.data[audience_id], "Audience already assigned to this category"
        
        # Add category path
        self.data[audience_id]['categories'].append({
            'category_path': category_path,
            'category_path_str': category_str,
            'assigned_at': datetime.now().isoformat()
        })
        self.data[audience_id]['updated_at'] = datetime.now().isoformat()
        
        self._save_data()
        return self.data[audience_id], "Audience added to category successfully"
    
    def get_audience_categories(self, audience_id):
        """
        Get all categories assigned to an audience
        
        Args:
            audience_id: Audience identifier
        
        Returns:
            list: List of category paths
        """
        # Fresh load for serverless
        self._load_data()
        
        if audience_id not in self.data:
            return []
        
        return self.data[audience_id].get('categories', [])
    
    def get_audiences_by_category(self, category_path):
        """
        Get all audiences assigned to a specific category
        
        Args:
            category_path: Category path list
        
        Returns:
            list: List of audiences
        """
        try:
            # Fresh load for serverless
            self._load_data()
            
            # Defensive check
            if not self.data or not isinstance(self.data, dict):
                return []
            
            category_str = ' -> '.join(category_path)
            audiences = []
            
            for audience_id, data in self.data.items():
                try:
                    if not isinstance(data, dict):
                        continue
                    for cat in data.get('categories', []):
                        if cat.get('category_path_str') == category_str:
                            audiences.append({
                                'audience_id': audience_id,
                                'audience_info': data.get('audience_info', {}),
                                'assigned_at': cat.get('assigned_at', '')
                            })
                            break
                except Exception as item_error:
                    print(f"Error processing audience {audience_id}: {item_error}")
                    continue
            
            return audiences
        except Exception as e:
            print(f"Error in get_audiences_by_category: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def remove_audience_from_category(self, audience_id, category_path):
        """
        Remove audience from specific category
        
        Args:
            audience_id: Audience identifier
            category_path: Category path list
        
        Returns:
            tuple: (success, message)
        """
        # Fresh load for serverless
        self._load_data()
        
        if audience_id not in self.data:
            return False, "Audience not found"
        
        category_str = ' -> '.join(category_path)
        categories = self.data[audience_id]['categories']
        
        for i, cat in enumerate(categories):
            if cat['category_path_str'] == category_str:
                del categories[i]
                self.data[audience_id]['updated_at'] = datetime.now().isoformat()
                self._save_data()
                return True, "Audience removed from category successfully"
        
        return False, "Audience not assigned to this category"
    
    def get_all_audiences(self):
        """Get all audiences"""
        try:
            self._load_data()
            if not self.data or not isinstance(self.data, dict):
                return []
            return list(self.data.values())
        except Exception as e:
            print(f"Error in get_all_audiences: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_audience_by_id(self, audience_id):
        """Get audience by ID"""
        try:
            self._load_data()
            if not self.data or not isinstance(self.data, dict):
                return None
            return self.data.get(audience_id)
        except Exception as e:
            print(f"Error in get_audience_by_id: {e}")
            return None
    
    def update_audience_info(self, audience_id, audience_info):
        """
        Update audience information - only modifies existing fields
        Does not create new nested objects or child nodes
        
        Args:
            audience_id: Audience identifier
            audience_info: Dictionary with fields to update
        
        Returns:
            tuple: (success, message)
        """
        try:
            # Fresh load for serverless
            self._load_data()
            
            if not self.data or audience_id not in self.data:
                return False, "Audience not found"
        
            # Get existing audience_info
            existing_info = self.data[audience_id].get('audience_info', {})
            
            # Only update fields that already exist in the structure
            # This prevents creating new nested objects
            allowed_fields = ['names', 'min_age', 'max_age', 'description', 'target_criteria']
            
            for field in allowed_fields:
                if field in audience_info:
                    existing_info[field] = audience_info[field]
            
            # Update the audience_info with modified fields only
            self.data[audience_id]['audience_info'] = existing_info
            self.data[audience_id]['updated_at'] = datetime.now().isoformat()
            
            self._save_data()
            return True, "Audience information updated successfully"
        except Exception as e:
            print(f"Error in update_audience_info: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error updating audience: {str(e)}"
    
    def get_statistics(self):
        """Get audience statistics"""
        try:
            self._load_data()
            if not self.data or not isinstance(self.data, dict):
                return {'total_audiences': 0, 'total_assignments': 0}
            
            total_audiences = len(self.data)
            total_assignments = sum(len(a.get('categories', [])) for a in self.data.values())
            
            return {
                'total_audiences': total_audiences,
                'total_assignments': total_assignments
            }
        except Exception as e:
            print(f"Error in get_statistics: {e}")
            return {'total_audiences': 0, 'total_assignments': 0}

import json
from pathlib import Path
from flask import current_app
 
 
class CategoryService:
    """Category service handling category business logic"""
    
    def __init__(self):
        self.db_path = Path(current_app.config['CATEGORIES_DB_PATH'])
    
    def _load_categories(self):
        """Load categories from file"""
        with open(self.db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_categories(self, categories):
        """Save categories to file"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=2, ensure_ascii=False)
    
    def get_all_categories(self):
        """Get all categories"""
        return self._load_categories()
    
    def find_category(self, category_path):
        """
        Find a category by path
        
        Args:
            category_path: List of category names forming the path
        
        Returns:
            The category node if found, None otherwise
        """
        categories = self._load_categories()
        current = categories
        
        for level in category_path:
            if isinstance(current, dict) and level in current:
                current = current[level]
            else:
                return None
        
        return current
    
    def add_category(self, parent_path, new_category_name):
        """
        Add a new category
        
        Args:
            parent_path: Path to parent category (empty list for root level)
            new_category_name: Name of new category
        
        Returns:
            tuple: (success, message)
        """
        categories = self._load_categories()
        
        if parent_path:
            parent = self.find_category(parent_path)
            if not parent:
                return False, "Parent category not found"
            
            # Find parent node reference
            current = categories
            for level in parent_path[:-1]:
                current = current[level]
            
            # Add new category
            current[parent_path[-1]][new_category_name] = {}
        else:
            # Add to root level
            if new_category_name in categories:
                return False, "Category already exists at root level"
            categories[new_category_name] = {}
        
        self._save_categories(categories)
        return True, "Category added successfully"
    
    def update_category(self, old_path, new_name):
        """
        Update category name
        
        Args:
            old_path: Path to category to rename
            new_name: New category name
        
        Returns:
            tuple: (success, message)
        """
        categories = self._load_categories()
        
        if len(old_path) < 1:
            return False, "Cannot update root"
        
        # Find parent of the category to update
        current = categories
        for level in old_path[:-1]:
            if isinstance(current, dict) and level in current:
                current = current[level]
            else:
                return False, "Category path not found"
        
        old_name = old_path[-1]
        if old_name not in current:
            return False, "Category not found"
        
        # Check if new name already exists at same level
        if new_name in current and new_name != old_name:
            return False, "Category with this name already exists"
        
        # Update category name
        current[new_name] = current.pop(old_name)
        self._save_categories(categories)
        
        return True, "Category updated successfully"
    
    def delete_category(self, category_path):
        """
        Delete a category
        
        Args:
            category_path: Path to category to delete
        
        Returns:
            tuple: (success, message)
        """
        if len(category_path) < 1:
            return False, "Cannot delete root"
        
        categories = self._load_categories()
        
        # Find parent of the category to delete
        current = categories
        for level in category_path[:-1]:
            if isinstance(current, dict) and level in current:
                current = current[level]
            else:
                return False, "Category path not found"
        
        category_name = category_path[-1]
        if category_name not in current:
            return False, "Category not found"
        
        # Check if category has children
        if current[category_name]:
            return False, "Cannot delete category with children. Delete children first."
        
        # Delete category
        del current[category_name]
        self._save_categories(categories)
        
        return True, "Category deleted successfully"
    
    def get_category_tree(self):
        """
        Get category tree with metadata
        
        Returns:
            Category tree with count information
        """
        categories = self._load_categories()
        
        def enrich_tree(node, path):
            if not isinstance(node, dict):
                return node
            
            result = {}
            for key, value in node.items():
                current_path = path + [key]
                result[key] = enrich_tree(value, current_path)
            
            return result
        
        return enrich_tree(categories, [])
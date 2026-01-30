from audiences.models import AudienceRepository
from flask import current_app
 
 
class AudienceService:
    """Audience service handling audience business logic"""
    
    def __init__(self):
        self.repo = AudienceRepository()
    
    def add_audience_to_leaf_node(self, audience_id, category_path, audience_info=None, created_by=None):
        """
        Add audience to leaf node category
        
        Args:
            audience_id: Audience ID
            category_path: Complete category path list
            audience_info: Audience information
            created_by: User ID of creator
        
        Returns:
            dict: Operation result
        """
        try:
            audience, message = self.repo.add_audience_to_category(
                audience_id=audience_id,
                category_path=category_path,
                audience_info=audience_info,
                created_by=created_by
            )
            
            return {
                'success': True,
                'data': audience,
                'message': message
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to add audience to category'
            }
    
    def batch_add_audience_to_category(self, audience_ids, category_path, created_by=None):
        """
        Batch add multiple audiences to same category
        
        Args:
            audience_ids: List of audience IDs
            category_path: Category path list
            created_by: User ID of creator
        
        Returns:
            dict: Batch operation result
        """
        results = []
        for audience_id in audience_ids:
            result = self.add_audience_to_leaf_node(
                audience_id=audience_id,
                category_path=category_path,
                created_by=created_by
            )
            results.append(result)
        
        success_count = sum(1 for r in results if r['success'])
        
        return {
            'success': True,
            'total': len(results),
            'successful': success_count,
            'failed': len(results) - success_count,
            'details': results
        }
    
    def get_audience_categories(self, audience_id):
        """
        Get all categories assigned to an audience
        
        Args:
            audience_id: Audience ID
        
        Returns:
            list: List of category paths
        """
        return self.repo.get_audience_categories(audience_id)
    
    def get_category_audiences(self, category_path):
        """
        Get all audiences assigned to a specific category
        
        Args:
            category_path: Category path list
        
        Returns:
            list: List of audiences
        """
        return self.repo.get_audiences_by_category(category_path)
    
    def remove_audience_from_category(self, audience_id, category_path):
        """
        Remove audience from specific category
        
        Args:
            audience_id: Audience ID
            category_path: Category path list
        
        Returns:
            dict: Operation result
        """
        success, message = self.repo.remove_audience_from_category(
            audience_id=audience_id,
            category_path=category_path
        )
        
        return {
            'success': success,
            'message': message
        }
    
    def get_all_audiences(self):
        """Get all audiences"""
        return self.repo.get_all_audiences()
    
    def get_audience_by_id(self, audience_id):
        """Get audience by ID"""
        return self.repo.get_audience_by_id(audience_id)
    
    def update_audience_info(self, audience_id, audience_info):
        """
        Update audience information (only existing fields)
        
        Args:
            audience_id: Audience ID
            audience_info: Dictionary with fields to update
        
        Returns:
            dict: Operation result
        """
        success, message = self.repo.update_audience_info(
            audience_id=audience_id,
            audience_info=audience_info
        )
        
        return {
            'success': success,
            'message': message
        }
    
    def get_statistics(self):
        """Get audience statistics"""
        return self.repo.get_statistics()

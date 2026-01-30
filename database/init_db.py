import sys
import os
 
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
from auth.models import UserRepository, User
from database.db import ensure_database_directory
from config import Config
 
 
def initialize_database():
    """Initialize database and create default super admin"""
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)
    
    # Ensure database directory exists
    ensure_database_directory(Config.USERS_DB_PATH)
    
    # Check if users already exist
    repo = UserRepository(Config.USERS_DB_PATH)
    
    if repo.users:
        print(f"\n✅ Database already initialized with {len(repo.users)} user(s).")
        print("Skipping initialization.")
        return
    
    print("\n📝 Creating default super admin...")
    
    # Create default super admin
    default_super_admin = User(
        user_id='user_super001',
        username='superadmin',
        email='superadmin@example.com',
        password_hash=User.hash_password('admin123'),
        role='super_admin',
        created_by='system'
    )
    
    repo.users[default_super_admin.user_id] = default_super_admin.to_dict()
    repo._save_data()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE INITIALIZED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📋 Default Super Admin Credentials:")
    print("   Username: superadmin")
    print("   Password: admin123")
    print("   Role: super_admin")
    print("   User ID: user_super001")
    print("\n⚠️  IMPORTANT: Change the default password in production!")
    print("=" * 60)
 
 
def reset_database():
    """Reset database - WARNING: This will delete all data"""
    print("\n⚠️  WARNING: This will delete all existing data!")
    confirm = input("Are you sure you want to reset the database? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("Database reset cancelled.")
        return
    
    # Delete existing database
    import os
    if os.path.exists(Config.USERS_DB_PATH):
        os.remove(Config.USERS_DB_PATH)
        print("🗑️  Existing database deleted.")
    
    # Initialize new database
    initialize_database()
 
 
def create_test_users():
    """Create test users for development"""
    print("\n📝 Creating test users...")
    
    repo = UserRepository(Config.USERS_DB_PATH)
    
    # Create test admin
    admin, msg = repo.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123',
        role='admin',
        created_by='system'
    )
    print(f"   ✅ Admin created: {msg}" if admin else f"   ❌ Admin: {msg}")
    
    # Create test employee
    emp, msg = repo.create_user(
        username='employee',
        email='employee@example.com',
        password='emp123',
        role='emp',
        created_by='system'
    )
    print(f"   ✅ Employee created: {msg}" if emp else f"   ❌ Employee: {msg}")
    
    print("\n📋 Test Users:")
    print("   Admin - Username: admin, Password: admin123")
    print("   Employee - Username: employee, Password: emp123")
 
 
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database initialization utility')
    parser.add_argument('--reset', action='store_true', help='Reset database (deletes all data)')
    parser.add_argument('--test-users', action='store_true', help='Create test users')
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    else:
        initialize_database()
    
    if args.test_users:
        create_test_users()
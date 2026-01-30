from flask import Flask, jsonify, render_template
from flask_cors import CORS
from config import Config
from database.kv_store import JSONStore
from auth.routes import auth_bp
from users.routes import users_bp
from categories.routes import categories_bp
from audiences.routes import audiences_bp
from blog.routes import blog_bp
from settings.routes import settings_bp
from pages.login import login_bp
from pages.dashboard import dashboard_bp
from pages.blog_page import blog_page_bp
from pages.settings_page import settings_page_bp
from pages.categories_page import categories_page_bp
from pages.admin_page import admin_page_bp
from pages.home_page import home_page_bp

# ...existing code...
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize default data in KV if empty
def initialize_kv_data():
    """Initialize default data in KV storage (only for Vercel KV, not local files)"""
    import os
    import json
    from pathlib import Path
    
    # Only initialize if using Vercel KV (not local files)
    if not os.environ.get('KV_URL'):
        print("Using local JSON files for storage")
        return
    
    print("Initializing Vercel KV storage...")
    
    # Load categories from local file if KV is empty
    if not JSONStore.read('categories'):
        categories_path = Path(__file__).parent / 'categories.json'
        if categories_path.exists():
            with open(categories_path, 'r', encoding='utf-8') as f:
                categories = json.load(f)
                JSONStore.write('categories', categories)
                print("✓ Categories loaded to KV")
    
    # Load users from local file if KV is empty
    if not JSONStore.read('users'):
        users_path = Path(__file__).parent / 'database' / 'users.json'
        if users_path.exists():
            with open(users_path, 'r', encoding='utf-8') as f:
                users = json.load(f)
                JSONStore.write('users', users)
                print("✓ Users loaded to KV")
    
    # Load blog from local file if KV is empty
    if not JSONStore.read('blog'):
        blog_path = Path(__file__).parent / 'database' / 'blog.json'
        if blog_path.exists():
            with open(blog_path, 'r', encoding='utf-8') as f:
                blog = json.load(f)
                JSONStore.write('blog', blog)
        else:
            JSONStore.write('blog', {"title": "Welcome, to Category Content", "content": "Admin can Access all Emp. SuperAdmin can CRUD in audience, etc."})
        print("✓ Blog loaded to KV")
    
    # Load settings from local file if KV is empty
    if not JSONStore.read('settings'):
        settings_path = Path(__file__).parent / 'database' / 'settings.json'
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                JSONStore.write('settings', settings)
        else:
            JSONStore.write('settings', {"theme": "minimal", "allow_signups": False})
        print("✓ Settings loaded to KV")
    
    # Load audiences from local file if KV is empty
    if not JSONStore.read('audiences'):
        audiences_path = Path(__file__).parent / 'database' / 'audiences.json'
        if audiences_path.exists():
            with open(audiences_path, 'r', encoding='utf-8') as f:
                audiences = json.load(f)
                JSONStore.write('audiences', audiences)
        else:
            JSONStore.write('audiences', {})
        print("✓ Audiences loaded to KV")

initialize_kv_data()
 
# Register API blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(audiences_bp)
app.register_blueprint(blog_bp)
app.register_blueprint(settings_bp)

# Register page handler blueprints
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(blog_page_bp)
app.register_blueprint(settings_page_bp)
app.register_blueprint(categories_page_bp)
app.register_blueprint(admin_page_bp)
app.register_blueprint(home_page_bp)
 
# Public routes
@app.route('/categories')
def public_categories():
    """Public category endpoint - no authentication required"""
    categories = JSONStore.read('categories')
    return jsonify(categories)
 
@app.route('/children/<parent_id>')
def get_children(parent_id):
    """Public endpoint to get child categories"""
    categories = JSONStore.read('categories')
    
    def find_node(node, target_id):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == target_id:
                    return value
                result = find_node(value, target_id)
                if result:
                    return result
        return None
    
    node = find_node(categories, parent_id)
    if not node:
        return jsonify([])
    
    children = []
    if isinstance(node, dict):
        for key, value in node.items():
            children.append({'id': key, 'name': key})
    
    return jsonify(children)
 
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')


@app.route('/signup')
def signup_page():
    """Signup page"""
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard_page():
    """Dashboard page"""
    return render_template('dashboard.html')

@app.route('/admin')
def admin_dashboard():
    """Admin panel page"""
    return render_template('admin_panel.html')

@app.route('/settings-page')
def settings_page():
    """Settings page"""
    return render_template('settings.html')

@app.route('/blog-page')
def blog_page():
    """Blog page"""
    return render_template('blog.html')

@app.route('/category-page')
def category_page():
    """Category page"""
    return render_template('categories.html')

@app.route('/audiences-page')
def audiences_page():
    """Audiences page"""
    return render_template('audiences.html')

@app.route('/super-admin')
def super_admin_page():
    """Super Admin panel - same as admin but with elevated permissions"""
    return render_template('admin_panel.html')
 
@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({'success': False, 'message': 'Resource not found'}), 404
 
@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({'success': False, 'message': 'Internal server error'}), 500
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

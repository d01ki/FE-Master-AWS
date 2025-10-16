"""
管理者ルート
"""
from flask import Blueprint, render_template, session
from auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def admin():
    """管理者ダッシュボード"""
    from flask import current_app
    db_manager = current_app.db_manager
    question_manager = current_app.question_manager
    
    total_questions = question_manager.get_total_questions()
    genres = question_manager.get_available_genres()
    
    # ユーザー数
    try:
        users = db_manager.execute_query('SELECT COUNT(*) as count FROM users')
        user_count = users[0]['count'] if users else 0
    except:
        user_count = 0
    
    return render_template('admin.html', 
                         total_questions=total_questions,
                         genres=genres,
                         user_count=user_count)

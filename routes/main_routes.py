"""
メインルート - ダッシュボードとホームページ
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
from auth import login_required
from datetime import datetime
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """トップページ"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """ダッシュボード"""
    from flask import current_app
    
    db_manager = current_app.db_manager
    question_manager = current_app.question_manager
    
    # 統計情報の取得
    total_questions = question_manager.get_total_questions()
    
    # ユーザーの解答履歴
    user_id = session.get('user_id')
    
    try:
        if db_manager.db_type == 'postgresql':
            answered_count = db_manager.execute_query(
                'SELECT COUNT(DISTINCT question_id) as count FROM user_answers WHERE user_id = %s',
                (user_id,)
            )
            correct_count = db_manager.execute_query(
                'SELECT COUNT(*) as count FROM user_answers WHERE user_id = %s AND is_correct = true',
                (user_id,)
            )
        else:
            answered_count = db_manager.execute_query(
                'SELECT COUNT(DISTINCT question_id) as count FROM user_answers WHERE user_id = ?',
                (user_id,)
            )
            correct_count = db_manager.execute_query(
                'SELECT COUNT(*) as count FROM user_answers WHERE user_id = ? AND is_correct = 1',
                (user_id,)
            )
        
        answered = answered_count[0]['count'] if answered_count else 0
        correct = correct_count[0]['count'] if correct_count else 0
        accuracy = round((correct / answered * 100), 1) if answered > 0 else 0
        
    except Exception as e:
        print(f"Error getting user stats: {e}")
        answered = 0
        correct = 0
        accuracy = 0
    
    # ジャンル一覧
    genres = question_manager.get_available_genres()
    
    return render_template('dashboard.html',
                         username=session.get('username'),
                         total_questions=total_questions,
                         answered_count=answered,
                         correct_count=correct,
                         accuracy=accuracy,
                         genres=genres)

@main_bp.route('/health')
def health():
    """
    ヘルスチェックエンドポイント（JSON形式）
    ロードバランサーやモニタリングツール用
    """
    from flask import current_app
    
    try:
        db_manager = current_app.db_manager
        # データベース接続チェック
        db_manager.execute_query('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    health_data = {
        'status': 'ok' if db_status == 'healthy' else 'error',
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_status,
        'version': '1.0.0'
    }
    
    status_code = 200 if health_data['status'] == 'ok' else 503
    return jsonify(health_data), status_code

@main_bp.route('/deploy-check')
def deploy_check():
    """
    デプロイ確認用ページ（ブラウザ表示用）
    """
    from flask import current_app
    from config import Config
    
    try:
        db_manager = current_app.db_manager
        db_manager.execute_query('SELECT 1')
        db_connected = True
    except:
        db_connected = False
    
    return render_template('health_check.html',
                         status='正常' if db_connected else 'データベース接続エラー',
                         environment='開発環境' if Config.DEBUG else '本番環境',
                         database_type=Config.DATABASE_TYPE.upper(),
                         version='1.0.0',
                         timestamp=datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))

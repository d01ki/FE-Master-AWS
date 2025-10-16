"""
練習問題ルート - ランダム問題とジャンル別演習
"""
from flask import Blueprint, render_template, request, jsonify, session
from auth import login_required

practice_bp = Blueprint('practice', __name__, url_prefix='/practice')

@practice_bp.route('/')
@login_required
def practice():
    """練習問題トップページ"""
    from flask import current_app
    question_manager = current_app.question_manager
    
    genres = question_manager.get_available_genres()
    genre_counts = question_manager.get_question_count_by_genre()
    
    return render_template('practice.html', genres=genres, genre_counts=genre_counts)

@practice_bp.route('/random')
@login_required
def random_practice():
    """ランダム問題"""
    from flask import current_app
    question_manager = current_app.question_manager
    
    question = question_manager.get_random_question()
    
    if not question:
        return render_template('error.html', message='問題が見つかりません')
    
    return render_template('question.html', question=question, mode='random')

@practice_bp.route('/genre/<genre>')
@login_required
def genre_practice(genre):
    """ジャンル別練習"""
    from flask import current_app
    question_manager = current_app.question_manager
    
    questions = question_manager.get_questions_by_genre(genre)
    
    if not questions:
        return render_template('error.html', message=f'{genre}の問題が見つかりません')
    
    return render_template('genre_practice.html', questions=questions, genre=genre)

@practice_bp.route('/submit', methods=['POST'])
@login_required
def submit_answer():
    """解答提出"""
    from flask import current_app
    question_manager = current_app.question_manager
    
    data = request.get_json()
    question_id = data.get('question_id')
    user_answer = data.get('user_answer')
    
    result = question_manager.check_answer(question_id, user_answer)
    
    # 解答履歴を保存
    user_id = session.get('user_id')
    question_manager.save_answer_history(
        question_id, 
        user_answer, 
        result['is_correct'], 
        user_id
    )
    
    return jsonify(result)

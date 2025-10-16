"""
問題管理クラス（PostgreSQL/SQLite対応）
問題の取得、保存、解答処理などを管理
"""

import json
from datetime import datetime
import re
from utils import sanitize_image_url, validate_image_url

class QuestionManager:
    """問題管理クラス（PostgreSQL/SQLite対応）"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.last_question_id = None
    
    def is_image_url(self, text):
        """テキストが画像URLかどうかを判定"""
        if not text or not isinstance(text, str):
            return False
        
        image_patterns = [
            r'/static/images/',
            r'\.png$',
            r'\.jpg$',
            r'\.jpeg$',
            r'\.gif$',
            r'\.svg$',
            r'\.webp$'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in image_patterns)
    
    def get_question(self, question_id):
        """指定されたIDの問題を取得"""
        try:
            if self.db_manager.db_type == 'postgresql':
                result = self.db_manager.execute_query(
                    'SELECT * FROM questions WHERE id = %s', (question_id,)
                )
            else:
                result = self.db_manager.execute_query(
                    'SELECT * FROM questions WHERE id = ?', (question_id,)
                )
            
            if result:
                question = dict(result[0])
                
                if question.get('image_url'):
                    img_url = question['image_url']
                    if img_url in ['null', 'None', '', 'undefined']:
                        question['image_url'] = None
                else:
                    question['image_url'] = None
                
                if isinstance(question['choices'], str):
                    question['choices'] = json.loads(question['choices'])
                
                question['has_image_choices'] = False
                if question['choices']:
                    first_choice = list(question['choices'].values())[0]
                    question['has_image_choices'] = self.is_image_url(first_choice)
                
                if question.get('choice_images'):
                    if isinstance(question['choice_images'], str):
                        question['choice_images'] = json.loads(question['choice_images'])
                else:
                    question['choice_images'] = None
                
                return question
            return None
        except Exception as e:
            print(f"Error getting question {question_id}: {e}")
            return None
    
    def get_questions_by_genre(self, genre):
        """ジャンル別問題を取得"""
        try:
            if self.db_manager.db_type == 'postgresql':
                result = self.db_manager.execute_query(
                    'SELECT * FROM questions WHERE genre = %s ORDER BY question_id', (genre,)
                )
            else:
                result = self.db_manager.execute_query(
                    'SELECT * FROM questions WHERE genre = ? ORDER BY question_id', (genre,)
                )
            
            questions = []
            for row in result:
                question = dict(row)
                
                if question.get('image_url'):
                    img_url = question['image_url']
                    if img_url in ['null', 'None', '', 'undefined']:
                        question['image_url'] = None
                else:
                    question['image_url'] = None
                
                if isinstance(question['choices'], str):
                    question['choices'] = json.loads(question['choices'])
                
                question['has_image_choices'] = False
                if question['choices']:
                    first_choice = list(question['choices'].values())[0]
                    question['has_image_choices'] = self.is_image_url(first_choice)
                
                if question.get('choice_images') and isinstance(question['choice_images'], str):
                    question['choice_images'] = json.loads(question['choice_images'])
                else:
                    question['choice_images'] = None
                
                questions.append(question)
            
            return questions
        except Exception as e:
            print(f"Error getting questions by genre {genre}: {e}")
            return []
    
    def get_random_question(self):
        """ランダムに1問取得"""
        try:
            if self.last_question_id:
                if self.db_manager.db_type == 'postgresql':
                    result = self.db_manager.execute_query(
                        'SELECT * FROM questions WHERE id != %s ORDER BY RANDOM() LIMIT 1',
                        (self.last_question_id,)
                    )
                else:
                    result = self.db_manager.execute_query(
                        'SELECT * FROM questions WHERE id != ? ORDER BY RANDOM() LIMIT 1',
                        (self.last_question_id,)
                    )
            else:
                if self.db_manager.db_type == 'postgresql':
                    result = self.db_manager.execute_query(
                        'SELECT * FROM questions ORDER BY RANDOM() LIMIT 1'
                    )
                else:
                    result = self.db_manager.execute_query(
                        'SELECT * FROM questions ORDER BY RANDOM() LIMIT 1'
                    )
            
            if result:
                question = dict(result[0])
                
                if question.get('image_url'):
                    img_url = question['image_url']
                    if img_url in ['null', 'None', '', 'undefined']:
                        question['image_url'] = None
                else:
                    question['image_url'] = None
                
                if isinstance(question['choices'], str):
                    question['choices'] = json.loads(question['choices'])
                
                question['has_image_choices'] = False
                if question['choices']:
                    first_choice = list(question['choices'].values())[0]
                    question['has_image_choices'] = self.is_image_url(first_choice)
                
                if question.get('choice_images') and isinstance(question['choice_images'], str):
                    question['choice_images'] = json.loads(question['choice_images'])
                else:
                    question['choice_images'] = None
                
                self.last_question_id = question['id']
                return question
            return None
        except Exception as e:
            print(f"Error getting random question: {e}")
            return None
    
    def get_total_questions(self):
        """総問題数を取得"""
        try:
            result = self.db_manager.execute_query('SELECT COUNT(*) as count FROM questions')
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"Error getting total questions count: {e}")
            return 0
    
    def check_answer(self, question_id, user_answer):
        """解答をチェック"""
        try:
            question = self.get_question(question_id)
            if not question:
                return {'error': '問題が見つかりません'}
            
            is_correct = user_answer == question['correct_answer']
            
            return {
                'is_correct': is_correct,
                'correct_answer': question['correct_answer'],
                'explanation': question.get('explanation', ''),
                'user_answer': user_answer
            }
        except Exception as e:
            print(f"Error checking answer: {e}")
            return {'error': '解答の確認中にエラーが発生しました'}
    
    def save_answer_history(self, question_id, user_answer, is_correct, user_id):
        """解答履歴を保存"""
        try:
            if self.db_manager.db_type == 'postgresql':
                self.db_manager.execute_query(
                    '''INSERT INTO user_answers 
                       (user_id, question_id, user_answer, is_correct, answered_at) 
                       VALUES (%s, %s, %s, %s, %s)''',
                    (user_id, question_id, user_answer, is_correct, datetime.now())
                )
            else:
                self.db_manager.execute_query(
                    '''INSERT INTO user_answers 
                       (user_id, question_id, user_answer, is_correct, answered_at) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (user_id, question_id, user_answer, int(is_correct), datetime.now())
                )
            return True
        except Exception as e:
            print(f"解答履歴保存エラー: {e}")
            return False
    
    def save_questions(self, questions, source_file=''):
        """問題リストをデータベースに保存"""
        saved_count = 0
        errors = []
        warnings = []
        
        for i, question in enumerate(questions):
            try:
                required_fields = ['question_text', 'choices', 'correct_answer']
                if not all(field in question for field in required_fields):
                    errors.append(f"Question {i+1}: Missing required fields")
                    continue
                
                question_id = question.get('question_id', f"Q{i+1:03d}_{source_file}")
                choices_data = json.dumps(question['choices'], ensure_ascii=False)
                
                image_url = question.get('image_url')
                image_url = sanitize_image_url(image_url)
                
                if image_url:
                    is_valid, error_message = validate_image_url(image_url)
                    if not is_valid:
                        warnings.append(f"Question {i+1}: Image URL validation failed - {error_message}")
                        image_url = None
                
                choice_images = question.get('choice_images')
                choice_images_json = None
                
                if choice_images and isinstance(choice_images, dict):
                    sanitized_choice_images = {}
                    for key, url in choice_images.items():
                        sanitized_url = sanitize_image_url(url)
                        if sanitized_url:
                            is_valid, error_message = validate_image_url(sanitized_url)
                            if is_valid:
                                sanitized_choice_images[key] = sanitized_url
                    
                    if sanitized_choice_images:
                        choice_images_json = json.dumps(sanitized_choice_images, ensure_ascii=False)
                
                existing = self.db_manager.execute_query(
                    'SELECT id FROM questions WHERE question_id = %s' if self.db_manager.db_type == 'postgresql' else 'SELECT id FROM questions WHERE question_id = ?',
                    (question_id,)
                )
                
                if not existing:
                    if self.db_manager.db_type == 'postgresql':
                        self.db_manager.execute_query("""
                            INSERT INTO questions (question_id, question_text, choices, correct_answer, explanation, genre, image_url, choice_images) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            question_id, question['question_text'], choices_data,
                            question['correct_answer'], question.get('explanation', ''),
                            question.get('genre', 'その他'), image_url, choice_images_json
                        ))
                    else:
                        self.db_manager.execute_query("""
                            INSERT INTO questions (question_id, question_text, choices, correct_answer, explanation, genre, image_url, choice_images) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            question_id, question['question_text'], choices_data,
                            question['correct_answer'], question.get('explanation', ''),
                            question.get('genre', 'その他'), image_url, choice_images_json
                        ))
                else:
                    if self.db_manager.db_type == 'postgresql':
                        self.db_manager.execute_query("""
                            UPDATE questions 
                            SET question_text = %s, choices = %s, correct_answer = %s, 
                                explanation = %s, genre = %s, image_url = %s, choice_images = %s
                            WHERE question_id = %s
                        """, (
                            question['question_text'], choices_data,
                            question['correct_answer'], question.get('explanation', ''),
                            question.get('genre', 'その他'), image_url, choice_images_json, question_id
                        ))
                    else:
                        self.db_manager.execute_query("""
                            UPDATE questions 
                            SET question_text = ?, choices = ?, correct_answer = ?, 
                                explanation = ?, genre = ?, image_url = ?, choice_images = ?
                            WHERE question_id = ?
                        """, (
                            question['question_text'], choices_data,
                            question['correct_answer'], question.get('explanation', ''),
                            question.get('genre', 'その他'), image_url, choice_images_json, question_id
                        ))
                
                saved_count += 1
                
            except Exception as e:
                errors.append(f"Question {i+1}: {str(e)}")
        
        return {
            'saved_count': saved_count, 
            'total_count': len(questions), 
            'errors': errors,
            'warnings': warnings
        }
    
    def get_available_genres(self):
        """利用可能なジャンル一覧を取得"""
        try:
            result = self.db_manager.execute_query(
                'SELECT DISTINCT genre FROM questions WHERE genre IS NOT NULL ORDER BY genre'
            )
            return [row['genre'] for row in result]
        except Exception as e:
            print(f"Error getting genres: {e}")
            return []
    
    def get_question_count_by_genre(self):
        """ジャンル別問題数を取得"""
        try:
            result = self.db_manager.execute_query(
                'SELECT genre, COUNT(*) as count FROM questions WHERE genre IS NOT NULL GROUP BY genre'
            )
            return {row['genre']: row['count'] for row in result}
        except Exception as e:
            print(f"Error getting question count by genre: {e}")
            return {}

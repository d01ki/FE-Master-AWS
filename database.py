import os
import sqlite3
import json
import logging
from utils import sanitize_image_url, validate_image_url

# PostgreSQLライブラリのインポート（エラー時はSQLiteのみ使用）
try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("Warning: psycopg2 not available. PostgreSQL support disabled.")

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, config):
        self.db_type = config['DATABASE_TYPE']
        self.config = config
        
        # PostgreSQLが利用できない場合はSQLiteにフォールバック
        if self.db_type == 'postgresql' and not PSYCOPG2_AVAILABLE:
            print("PostgreSQL requested but psycopg2 not available. Falling back to SQLite.")
            self.db_type = 'sqlite'
            self.config['DATABASE_TYPE'] = 'sqlite'
        
    def get_connection(self):
        if self.db_type == 'postgresql' and PSYCOPG2_AVAILABLE:
            conn = psycopg2.connect(
                host=self.config['DB_HOST'],
                database=self.config['DB_NAME'],
                user=self.config['DB_USER'],
                password=self.config['DB_PASSWORD'],
                port=self.config['DB_PORT']
            )
            conn.autocommit = False
            return conn
        else:
            db_path = self.config.get('DATABASE', 'fe_exam.db')
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def execute_query(self, query, params=None):
        conn = self.get_connection()
        try:
            if self.db_type == 'postgresql' and PSYCOPG2_AVAILABLE:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(query, params or ())
                if query.strip().upper().startswith(('SELECT', 'WITH')):
                    result = cur.fetchall()
                    result = [dict(row) for row in result]
                else:
                    result = cur.rowcount
                    conn.commit()
                cur.close()
            else:
                cur = conn.cursor()
                cur.execute(query, params or ())
                if query.strip().upper().startswith(('SELECT', 'WITH')):
                    result = [dict(row) for row in cur.fetchall()]
                else:
                    result = cur.rowcount
                    conn.commit()
                cur.close()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        if self.db_type == 'postgresql' and PSYCOPG2_AVAILABLE:
            self._init_postgresql()
        else:
            self._init_sqlite()
    
    def _init_postgresql(self):
        queries = [
            """CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS questions (
                id SERIAL PRIMARY KEY,
                question_id VARCHAR(50) UNIQUE NOT NULL,
                question_text TEXT NOT NULL,
                choices JSON NOT NULL,
                correct_answer VARCHAR(10) NOT NULL,
                explanation TEXT,
                genre VARCHAR(100),
                image_url VARCHAR(500),
                choice_images JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS user_answers (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                question_id INTEGER REFERENCES questions(id),
                user_answer VARCHAR(10) NOT NULL,
                is_correct BOOLEAN NOT NULL,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            "CREATE INDEX IF NOT EXISTS idx_questions_genre ON questions(genre)",
            "CREATE INDEX IF NOT EXISTS idx_user_answers_user_id ON user_answers(user_id)",
            """DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='questions' AND column_name='image_url') THEN
                    ALTER TABLE questions ADD COLUMN image_url VARCHAR(500);
                END IF;
            END $$;""",
            """DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='questions' AND column_name='choice_images') THEN
                    ALTER TABLE questions ADD COLUMN choice_images JSON;
                END IF;
            END $$;"""
        ]
        
        for query in queries:
            try:
                self.execute_query(query)
            except Exception as e:
                logger.error(f"PostgreSQL init error: {e}")
    
    def _init_sqlite(self):
        queries = [
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id TEXT UNIQUE NOT NULL,
                question_text TEXT NOT NULL,
                choices TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT,
                genre TEXT,
                image_url TEXT,
                choice_images TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS user_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question_id INTEGER,
                user_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )"""
        ]
        
        for query in queries:
            try:
                self.execute_query(query)
            except Exception as e:
                logger.error(f"SQLite init error: {e}")
        
        # 既存のテーブルにimage_urlカラムを追加（存在しない場合のみ）
        try:
            table_info_result = self.execute_query("PRAGMA table_info(questions)")
            column_names = []
            
            if table_info_result and isinstance(table_info_result, list):
                for row in table_info_result:
                    if isinstance(row, dict) and 'name' in row:
                        column_names.append(row['name'])
                    elif hasattr(row, 'keys') and 'name' in row.keys():
                        column_names.append(row['name'])
            
            if 'image_url' not in column_names:
                self.execute_query("ALTER TABLE questions ADD COLUMN image_url TEXT")
                logger.info("Added image_url column to questions table")
            
            if 'choice_images' not in column_names:
                self.execute_query("ALTER TABLE questions ADD COLUMN choice_images TEXT")
                logger.info("Added choice_images column to questions table")
                
        except Exception as e:
            logger.warning(f"SQLite alter table warning (non-fatal): {e}")
            print(f"SQLite alter table error: {e}")

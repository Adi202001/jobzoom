"""Database operations for JobCopilot"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
import sqlite3
import threading


class Database:
    """SQLite database for persistent storage"""

    DEFAULT_PATH = "/data/jobcopilot/jobcopilot.db"

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or self.DEFAULT_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    def _init_db(self) -> None:
        """Initialize database schema"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                location TEXT,
                remote_status TEXT,
                data JSON NOT NULL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new'
            )
        ''')

        # Applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                app_id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                status TEXT DEFAULT 'preparing',
                match_score REAL DEFAULT 0,
                data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(job_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Agent logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                action TEXT NOT NULL,
                input_data JSON,
                output_data JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status)')

        conn.commit()

    # User operations
    def save_user(self, user_id: str, data: Dict[str, Any]) -> None:
        """Save or update a user profile"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (user_id, data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                data = excluded.data,
                updated_at = CURRENT_TIMESTAMP
        ''', (user_id, json.dumps(data, default=str)))
        conn.commit()

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user profile"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return json.loads(row['data']) if row else None

    def list_users(self) -> List[str]:
        """List all user IDs"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users')
        return [row['user_id'] for row in cursor.fetchall()]

    # Job operations
    def save_job(self, job_id: str, data: Dict[str, Any]) -> None:
        """Save or update a job"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO jobs (job_id, company, title, location, remote_status, data, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
                data = excluded.data,
                status = excluded.status
        ''', (
            job_id,
            data.get('company', ''),
            data.get('title', ''),
            data.get('location', ''),
            data.get('remote_status', ''),
            json.dumps(data, default=str),
            data.get('status', 'new')
        ))
        conn.commit()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a job by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM jobs WHERE job_id = ?', (job_id,))
        row = cursor.fetchone()
        return json.loads(row['data']) if row else None

    def search_jobs(
        self,
        company: Optional[str] = None,
        title: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search jobs with filters"""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = 'SELECT data FROM jobs WHERE 1=1'
        params = []

        if company:
            query += ' AND company LIKE ?'
            params.append(f'%{company}%')
        if title:
            query += ' AND title LIKE ?'
            params.append(f'%{title}%')
        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY scraped_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        return [json.loads(row['data']) for row in cursor.fetchall()]

    def get_jobs_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all jobs with a specific status"""
        return self.search_jobs(status=status, limit=1000)

    # Application operations
    def save_application(self, app_id: str, data: Dict[str, Any]) -> None:
        """Save or update an application"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO applications (app_id, job_id, user_id, status, match_score, data, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(app_id) DO UPDATE SET
                status = excluded.status,
                match_score = excluded.match_score,
                data = excluded.data,
                updated_at = CURRENT_TIMESTAMP
        ''', (
            app_id,
            data.get('job_id', ''),
            data.get('user_id', ''),
            data.get('status', 'preparing'),
            data.get('match_score', 0),
            json.dumps(data, default=str)
        ))
        conn.commit()

    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get an application by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM applications WHERE app_id = ?', (app_id,))
        row = cursor.fetchone()
        return json.loads(row['data']) if row else None

    def get_user_applications(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all applications for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute(
                'SELECT data FROM applications WHERE user_id = ? AND status = ? ORDER BY updated_at DESC',
                (user_id, status)
            )
        else:
            cursor.execute(
                'SELECT data FROM applications WHERE user_id = ? ORDER BY updated_at DESC',
                (user_id,)
            )
        return [json.loads(row['data']) for row in cursor.fetchall()]

    def get_application_stats(self, user_id: str) -> Dict[str, int]:
        """Get application statistics for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM applications
            WHERE user_id = ?
            GROUP BY status
        ''', (user_id,))
        return {row['status']: row['count'] for row in cursor.fetchall()}

    # Agent log operations
    def log_agent_action(
        self,
        agent: str,
        action: str,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None
    ) -> None:
        """Log an agent action"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO agent_logs (agent, action, input_data, output_data)
            VALUES (?, ?, ?, ?)
        ''', (
            agent,
            action,
            json.dumps(input_data, default=str) if input_data else None,
            json.dumps(output_data, default=str) if output_data else None
        ))
        conn.commit()

    def get_agent_logs(
        self,
        agent: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get agent logs"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if agent:
            cursor.execute(
                'SELECT * FROM agent_logs WHERE agent = ? ORDER BY timestamp DESC LIMIT ?',
                (agent, limit)
            )
        else:
            cursor.execute(
                'SELECT * FROM agent_logs ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )

        return [dict(row) for row in cursor.fetchall()]

    def close(self) -> None:
        """Close database connection"""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()

# src/database/connection.py - Versione migliorata
import sqlite3
from contextlib import contextmanager
from typing import Generator
import os
import logging

class DatabaseConnection:
    def __init__(self, db_path: str = "data/organigramma.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Crea directory se non esiste"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _init_database(self):
        """Inizializza database se non esiste"""
        if not os.path.exists(self.db_path):
            self._create_database()
    
    def _create_database(self):
        """Crea database con schema"""
        try:
            schema_path = "database/schema.sql"
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = f.read()
                
                with sqlite3.connect(self.db_path) as conn:
                    conn.executescript(schema)
                    logging.info(f"Database creato: {self.db_path}")
            else:
                # Schema inline come fallback
                self._create_basic_schema()
        except Exception as e:
            logging.error(f"Errore creazione database: {e}")
            raise
    
    def _create_basic_schema(self):
        """Schema di base come fallback"""
        basic_schema = """
        CREATE TABLE persons (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            email TEXT,
            employee_id TEXT UNIQUE,
            hire_date DATE,
            status TEXT DEFAULT 'ACTIVE',
            flags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE functions (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            reports_to TEXT,
            flags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE roles (
            id INTEGER PRIMARY KEY,
            person_name TEXT NOT NULL,
            function_name TEXT NOT NULL,
            organizational_unit TEXT,
            job_title_name TEXT,
            percentage REAL DEFAULT 1.0,
            ad_interim BOOLEAN DEFAULT 0,
            reports_to TEXT,
            start_date DATE,
            end_date DATE,
            flags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(basic_schema)
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params=None):
        """Esegue query con gestione errori migliorata"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Query error: {query[:50]}... - {e}")
            raise
import sqlite3
import pandas as pd
import json
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Connect to the database"""
        try:
            if self.db_path.endswith('.db') or self.db_path.endswith('.sqlite'):
                self.connection = sqlite3.connect(self.db_path)
                self.connection.row_factory = sqlite3.Row
                logger.info(f"Connected to SQLite database: {self.db_path}")
            else:
                logger.warning(f"Unsupported database format: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            
    def disconnect(self):
        """Disconnect from the database"""
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def get_tables(self) -> List[str]:
        """Get list of tables in the database"""
        if not self.connection:
            self.connect()
            
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        return tables
    
    def get_table_schema(self, table_name: str) -> List[Dict]:
        """Get schema of a specific table"""
        if not self.connection:
            self.connect()
            
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        schema = []
        for row in cursor.fetchall():
            schema.append({
                'column': row[1],
                'type': row[2],
                'not_null': bool(row[3]),
                'default': row[4],
                'primary_key': bool(row[5])
            })
        return schema
    
    def get_all_novels(self) -> pd.DataFrame:
        """Get all novels from the database"""
        if not self.connection:
            self.connect()
            
        # Try common table names for fanfiction
        possible_tables = ['novels', 'fanfiction', 'stories', 'books', 'texts']
        
        for table in possible_tables:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table}", self.connection)
                logger.info(f"Found novels in table: {table}")
                return df
            except:
                continue
        
        # Check for chapters table (common in fanfiction databases)
        try:
            # First check if chapters table exists and has content
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM chapters WHERE content IS NOT NULL AND content != ''")
            chapter_count = cursor.fetchone()[0]
            
            if chapter_count > 0:
                logger.info(f"Found {chapter_count} chapters with content")
                # Get chapters with their novel information
                query = """
                SELECT 
                    c.id,
                    n.title as novel_title,
                    c.title as chapter_title,
                    c.content,
                    n.status,
                    n.total_chapters,
                    c.novel_id
                FROM chapters c
                LEFT JOIN novels n ON c.novel_id = n.id
                WHERE c.content IS NOT NULL AND c.content != ''
                ORDER BY c.novel_id, c.id
                """
                df = pd.read_sql_query(query, self.connection)
                logger.info(f"Found chapters data in combined query")
                return df
        except Exception as e:
            logger.warning(f"Error querying chapters: {e}")
                
        # If no standard table found, get the first table
        tables = self.get_tables()
        if tables:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {tables[0]}", self.connection)
                logger.info(f"Using table: {tables[0]}")
                return df
            except Exception as e:
                logger.error(f"Error reading table {tables[0]}: {e}")
        
        logger.error("No suitable table found in database")
        return pd.DataFrame()
    
    def get_novel_by_id(self, novel_id: int) -> Optional[Dict]:
        """Get a specific novel by ID"""
        df = self.get_all_novels()
        if df.empty:
            return None
            
        # Try common ID column names
        id_columns = ['id', 'novel_id', 'story_id', 'book_id']
        id_col = None
        
        for col in id_columns:
            if col in df.columns:
                id_col = col
                break
                
        if not id_col:
            logger.error("No ID column found")
            return None
            
        novel = df[df[id_col] == novel_id]
        if novel.empty:
            return None
            
        return novel.iloc[0].to_dict()
    
    def get_novels_by_criteria(self, criteria: Dict[str, Any]) -> pd.DataFrame:
        """Get novels matching specific criteria"""
        df = self.get_all_novels()
        
        for column, value in criteria.items():
            if column in df.columns:
                if isinstance(value, str):
                    df = df[df[column].str.contains(value, case=False, na=False)]
                else:
                    df = df[df[column] == value]
                    
        return df
    
    def get_sample_novels(self, n: int = 10) -> pd.DataFrame:
        """Get a sample of novels for analysis"""
        df = self.get_all_novels()
        return df.sample(min(n, len(df))) if not df.empty else df
    
    def analyze_database_structure(self) -> Dict[str, Any]:
        """Analyze the structure and content of the database"""
        analysis = {
            'tables': [],
            'total_novels': 0,
            'columns': [],
            'sample_data': {}
        }
        
        tables = self.get_tables()
        analysis['tables'] = tables
        
        for table in tables:
            schema = self.get_table_schema(table)
            analysis['columns'].extend([col['column'] for col in schema])
            
            # Get sample data
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5", self.connection)
                analysis['sample_data'][table] = df.to_dict('records')
                
                # Count total records
                count_df = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", self.connection)
                analysis['total_novels'] += count_df.iloc[0]['count']
            except Exception as e:
                logger.error(f"Error analyzing table {table}: {e}")
                
        return analysis

class CSVHandler:
    """Handler for CSV files containing fanfiction data"""
    
    @staticmethod
    def load_csv(file_path: str) -> pd.DataFrame:
        """Load fanfiction data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} records from CSV: {file_path}")
            return df
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def save_csv(df: pd.DataFrame, file_path: str):
        """Save dataframe to CSV"""
        try:
            df.to_csv(file_path, index=False)
            logger.info(f"Saved {len(df)} records to CSV: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save CSV: {e}")

class JSONHandler:
    """Handler for JSON files containing fanfiction data"""
    
    @staticmethod
    def load_json(file_path: str) -> List[Dict]:
        """Load fanfiction data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} records from JSON: {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load JSON: {e}")
            return []
    
    @staticmethod
    def save_json(data: List[Dict], file_path: str):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(data)} records to JSON: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")

def create_sample_database():
    """Create a sample database for testing"""
    conn = sqlite3.connect('sample_fanfiction.db')
    
    # Create novels table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS novels (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            genre TEXT,
            characters TEXT,
            word_count INTEGER,
            rating TEXT,
            status TEXT,
            created_date TEXT,
            updated_date TEXT,
            summary TEXT,
            tags TEXT
        )
    ''')
    
    # Sample data
    sample_novels = [
        (1, "The Boy Who Lived Again", "HPFan123", "Harry Potter discovered something extraordinary...", "Adventure", "Harry Potter, Hermione Granger", 15000, "T", "Complete", "2023-01-01", "2023-01-15", "Harry returns to Hogwarts with new powers", "time-travel, powerful-harry"),
        (2, "Slytherin's Heir", "SnakeWriter", "What if Harry had been sorted into Slytherin...", "Drama", "Harry Potter, Draco Malfoy", 25000, "M", "In Progress", "2023-02-01", "2023-06-01", "Harry in Slytherin changes everything", "slytherin-harry, dark-harry"),
        (3, "The Brightest Witch", "HermioneSupporter", "Hermione's journey through her seventh year...", "Romance", "Hermione Granger, Ron Weasley", 18000, "T", "Complete", "2023-03-01", "2023-03-20", "Hermione's perspective on the war", "hermione-centric, war-fic")
    ]
    
    conn.executemany('''
        INSERT OR REPLACE INTO novels 
        (id, title, author, content, genre, characters, word_count, rating, status, created_date, updated_date, summary, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_novels)
    
    conn.commit()
    conn.close()
    
    logger.info("Created sample database: sample_fanfiction.db")

if __name__ == "__main__":
    # Create sample database for testing
    create_sample_database()
    
    # Test the database handler
    handler = DatabaseHandler("sample_fanfiction.db")
    analysis = handler.analyze_database_structure()
    print("Database Analysis:")
    print(json.dumps(analysis, indent=2))
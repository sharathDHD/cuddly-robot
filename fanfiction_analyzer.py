#!/usr/bin/env python3
"""
Specialized analyzer for the novel_data.db fanfiction database
"""

import sqlite3
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from text_analyzer import TextAnalyzer, CorpusAnalyzer
from llm_generator import LLMGenerator, FanfictionGenerator
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FanfictionDatabaseAnalyzer:
    def __init__(self, db_path: str = "novel_data.db"):
        self.db_path = db_path
        self.connection = None
        self.text_analyzer = TextAnalyzer()
        self.corpus_analyzer = CorpusAnalyzer(self.text_analyzer)
        
    def connect(self):
        """Connect to the database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get basic database statistics"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        
        stats = {}
        
        try:
            # Novel count
            cursor.execute("SELECT COUNT(*) FROM novels")
            stats['total_novels'] = cursor.fetchone()[0]
            
            # Chapter count (with content)
            cursor.execute("SELECT COUNT(*) FROM chapters WHERE content IS NOT NULL AND content != ''")
            stats['total_chapters_with_content'] = cursor.fetchone()[0]
            
            # Average chapters per novel
            cursor.execute("""
                SELECT AVG(chapter_count) FROM (
                    SELECT novel_id, COUNT(*) as chapter_count 
                    FROM chapters 
                    WHERE content IS NOT NULL AND content != ''
                    GROUP BY novel_id
                )
            """)
            result = cursor.fetchone()[0]
            stats['avg_chapters_per_novel'] = float(result) if result else 0
            
            # Content length statistics
            cursor.execute("""
                SELECT 
                    AVG(LENGTH(content)) as avg_length,
                    MIN(LENGTH(content)) as min_length,
                    MAX(LENGTH(content)) as max_length
                FROM chapters 
                WHERE content IS NOT NULL AND content != ''
            """)
            row = cursor.fetchone()
            stats['content_stats'] = {
                'avg_length': int(row[0]) if row[0] else 0,
                'min_length': int(row[1]) if row[1] else 0,
                'max_length': int(row[2]) if row[2] else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            
        return stats
    
    def get_sample_chapters(self, limit: int = 10) -> pd.DataFrame:
        """Get a sample of chapters for analysis"""
        if not self.connection:
            self.connect()
        
        query = """
        SELECT 
            c.id,
            c.novel_id,
            n.title as novel_title,
            c.title as chapter_title,
            c.content,
            LENGTH(c.content) as content_length
        FROM chapters c
        LEFT JOIN novels n ON c.novel_id = n.id
        WHERE c.content IS NOT NULL AND c.content != ''
        ORDER BY RANDOM()
        LIMIT ?
        """
        
        try:
            df = pd.read_sql_query(query, self.connection, params=[limit])
            logger.info(f"Retrieved {len(df)} sample chapters")
            return df
        except Exception as e:
            logger.error(f"Error getting sample chapters: {e}")
            return pd.DataFrame()
    
    def get_chapters_by_novel(self, novel_id: int) -> pd.DataFrame:
        """Get all chapters for a specific novel"""
        if not self.connection:
            self.connect()
        
        query = """
        SELECT 
            c.id,
            c.novel_id,
            n.title as novel_title,
            c.title as chapter_title,
            c.content,
            LENGTH(c.content) as content_length
        FROM chapters c
        LEFT JOIN novels n ON c.novel_id = n.id
        WHERE c.novel_id = ? AND c.content IS NOT NULL AND c.content != ''
        ORDER BY c.id
        """
        
        try:
            df = pd.read_sql_query(query, self.connection, params=[novel_id])
            return df
        except Exception as e:
            logger.error(f"Error getting chapters for novel {novel_id}: {e}")
            return pd.DataFrame()
    
    def analyze_corpus_sample(self, sample_size: int = 50) -> Dict[str, Any]:
        """Analyze a sample of the corpus"""
        logger.info(f"Analyzing corpus sample of {sample_size} chapters...")
        
        # Get sample chapters
        df = self.get_sample_chapters(sample_size)
        
        if df.empty:
            logger.error("No chapters found for analysis")
            return {}
        
        # Analyze the corpus
        corpus_analysis = self.corpus_analyzer.analyze_corpus(df, 'content')
        
        # Add database-specific statistics
        db_stats = self.get_database_stats()
        corpus_analysis['database_stats'] = db_stats
        
        return corpus_analysis
    
    def get_novel_list(self) -> pd.DataFrame:
        """Get list of all novels with basic info"""
        if not self.connection:
            self.connect()
        
        query = """
        SELECT 
            n.id,
            n.title,
            n.status,
            n.total_chapters,
            COUNT(c.id) as available_chapters,
            SUM(LENGTH(c.content)) as total_content_length
        FROM novels n
        LEFT JOIN chapters c ON n.id = c.novel_id 
            AND c.content IS NOT NULL AND c.content != ''
        GROUP BY n.id, n.title, n.status, n.total_chapters
        HAVING available_chapters > 0
        ORDER BY available_chapters DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.connection)
            logger.info(f"Found {len(df)} novels with content")
            return df
        except Exception as e:
            logger.error(f"Error getting novel list: {e}")
            return pd.DataFrame()

def test_ollama_connection():
    """Test if Ollama is running and has llama3.1"""
    import requests
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            print(f"✅ Ollama is running. Available models: {model_names}")
            
            # Check for llama3.1
            llama_models = [name for name in model_names if 'llama3.1' in name.lower()]
            if llama_models:
                print(f"✅ Found Llama 3.1 models: {llama_models}")
                return True, llama_models[0]
            else:
                print("❌ No Llama 3.1 models found")
                return False, None
        else:
            print(f"❌ Ollama server returned status {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False, None

def generate_story_with_ollama(corpus_analysis: Dict[str, Any], model_name: str = "llama3.1"):
    """Generate a story using Ollama"""
    print(f"\n🤖 Generating story with Ollama model: {model_name}")
    
    # Initialize LLM generator with Ollama
    llm_generator = LLMGenerator(model_type="ollama", model_name=model_name)
    fanfic_generator = FanfictionGenerator(llm_generator, corpus_analysis)
    
    # Set generation parameters
    parameters = {
        'main_character': 'Harry Potter',
        'genre': 'Adventure',
        'setting': 'Hogwarts',
        'theme': 'discovering ancient magic',
        'target_length': 3000
    }
    
    print(f"📝 Generation parameters: {parameters}")
    
    try:
        # Generate story
        story = fanfic_generator.generate_full_story(parameters)
        
        # Save story
        os.makedirs("generated", exist_ok=True)
        story_file = f"generated/ollama_story_{len(os.listdir('generated')) + 1}.json"
        
        with open(story_file, 'w', encoding='utf-8') as f:
            json.dump(story, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Story generated and saved to: {story_file}")
        print(f"📖 Title: {story['title']}")
        print(f"📄 Chapters: {len(story['chapters'])}")
        print(f"📊 Word count: {story['metadata']['estimated_word_count']}")
        
        return story
        
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        return None

def main():
    """Main function to demonstrate the fanfiction analyzer"""
    print("🪄 HARRY POTTER FANFICTION ANALYZER")
    print("=" * 50)
    print("Analyzing your novel_data.db database...")
    
    # Initialize analyzer
    analyzer = FanfictionDatabaseAnalyzer()
    
    # Get database statistics
    print("\n📊 Database Statistics:")
    db_stats = analyzer.get_database_stats()
    for key, value in db_stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v:,}")
        else:
            print(f"  {key}: {value:,}")
    
    # Get novel list
    print("\n📚 Novel List (top 10 by chapter count):")
    novels_df = analyzer.get_novel_list()
    if not novels_df.empty:
        for idx, row in novels_df.head(10).iterrows():
            print(f"  {row['title'][:50]:<50} | {row['available_chapters']:>3} chapters | {row['total_content_length']:>8,} chars")
    
    # Analyze corpus sample
    print("\n🔬 Analyzing corpus sample...")
    corpus_analysis = analyzer.analyze_corpus_sample(sample_size=20)
    
    if corpus_analysis:
        print("✅ Corpus analysis complete!")
        if 'basic_statistics' in corpus_analysis:
            stats = corpus_analysis['basic_statistics']
            print(f"  Average word count per chapter: {stats.get('avg_word_count', 0):.0f}")
            print(f"  Average readability score: {stats.get('avg_readability', 0):.1f}")
        
        if 'character_analysis' in corpus_analysis:
            print("  Top characters:")
            char_analysis = corpus_analysis['character_analysis']
            sorted_chars = sorted(char_analysis.items(), 
                                key=lambda x: x[1].get('total_mentions', 0), 
                                reverse=True)
            for char, stats in sorted_chars[:5]:
                print(f"    {char}: {stats.get('total_mentions', 0)} mentions")
    
    # Test Ollama connection
    print("\n🤖 Testing Ollama connection...")
    ollama_available, model_name = test_ollama_connection()
    
    if ollama_available and corpus_analysis:
        print(f"\n✨ Generating story with {model_name}...")
        story = generate_story_with_ollama(corpus_analysis, model_name)
        
        if story:
            print("\n🎉 Story generation complete!")
            print(f"📜 Preview:")
            print(f"Title: {story['title']}")
            print(f"Summary: {story['summary'][:200]}...")
    else:
        print("\n💡 To use Ollama for story generation:")
        print("1. Install Ollama: https://ollama.ai/")
        print("2. Start Ollama: ollama serve")
        print("3. Pull Llama 3.1: ollama pull llama3.1")
        print("4. Run this script again")
    
    print("\n🎊 Analysis complete!")

if __name__ == "__main__":
    main()
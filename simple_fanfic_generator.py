#!/usr/bin/env python3
"""
Simple fanfiction generator that works with the novel_data.db database
Handles database corruption by avoiding complex joins
"""

import sqlite3
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging
import json
import os
import requests
from text_analyzer import TextAnalyzer, CorpusAnalyzer
from llm_generator import LLMGenerator, FanfictionGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleFanficGenerator:
    def __init__(self, db_path: str = "novel_data.db"):
        self.db_path = db_path
        self.text_analyzer = TextAnalyzer()
        self.corpus_analyzer = CorpusAnalyzer(self.text_analyzer)
        
    def get_chapters_safely(self, limit: int = 50) -> pd.DataFrame:
        """Get chapters from database safely, avoiding corrupted joins"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Simple query without joins to avoid corruption issues
            query = """
            SELECT id, novel_id, title, content
            FROM chapters 
            WHERE content IS NOT NULL AND content != ''
            ORDER BY RANDOM()
            LIMIT ?
            """
            
            df = pd.read_sql_query(query, conn, params=[limit])
            conn.close()
            
            logger.info(f"Successfully loaded {len(df)} chapters")
            return df
            
        except Exception as e:
            logger.error(f"Error loading chapters: {e}")
            return pd.DataFrame()
    
    def analyze_sample(self, sample_size: int = 30) -> Dict[str, Any]:
        """Analyze a sample of chapters"""
        print(f"📊 Analyzing {sample_size} chapters from your database...")
        
        # Get sample chapters
        df = self.get_chapters_safely(sample_size)
        
        if df.empty:
            print("❌ No chapters could be loaded")
            return {}
        
        print(f"✅ Loaded {len(df)} chapters for analysis")
        
        # Show sample data
        print("\n📖 Sample chapters:")
        for idx, row in df.head(3).iterrows():
            print(f"  Chapter {row['id']}: {row['title']}")
            print(f"    Content length: {len(row['content'])} chars")
            print(f"    Preview: {row['content'][:100]}...")
            print()
        
        # Analyze corpus
        try:
            corpus_analysis = self.corpus_analyzer.analyze_corpus(df, 'content')
            
            print("✅ Analysis complete!")
            if 'basic_statistics' in corpus_analysis:
                stats = corpus_analysis['basic_statistics']
                print(f"  📈 Average word count: {stats.get('avg_word_count', 0):.0f}")
                print(f"  📚 Average readability: {stats.get('avg_readability', 0):.1f}")
                print(f"  🎓 Average grade level: {stats.get('avg_grade_level', 0):.1f}")
            
            if 'character_analysis' in corpus_analysis:
                print("  👥 Top characters found:")
                char_analysis = corpus_analysis['character_analysis']
                sorted_chars = sorted(char_analysis.items(), 
                                    key=lambda x: x[1].get('total_mentions', 0), 
                                    reverse=True)
                for char, stats in sorted_chars[:5]:
                    if stats.get('total_mentions', 0) > 0:
                        print(f"    {char}: {stats.get('total_mentions', 0)} mentions")
            
            return corpus_analysis
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            return {}
    
    def test_ollama(self) -> tuple[bool, str]:
        """Test Ollama connection"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                # Look for llama3.1 models
                llama_models = [name for name in model_names if 'llama3.1' in name.lower()]
                if llama_models:
                    return True, llama_models[0]
                elif model_names:
                    return True, model_names[0]  # Use any available model
                else:
                    return False, "No models found"
            else:
                return False, f"Server error: {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def generate_story(self, corpus_analysis: Dict[str, Any], model_name: str = "llama3.1") -> Dict[str, Any]:
        """Generate a story using the analyzed corpus"""
        print(f"\n✨ Generating story with model: {model_name}")
        
        # Initialize generator
        llm_generator = LLMGenerator(model_type="ollama", model_name=model_name)
        fanfic_generator = FanfictionGenerator(llm_generator, corpus_analysis)
        
        # Generation parameters
        parameters = {
            'main_character': 'Harry Potter',
            'genre': 'Adventure',
            'setting': 'Hogwarts',
            'theme': 'discovering hidden magical abilities',
            'target_length': 2000  # Shorter for faster generation
        }
        
        print(f"📝 Parameters: {parameters}")
        
        try:
            # Generate story
            story = fanfic_generator.generate_full_story(parameters)
            
            # Save story
            os.makedirs("generated", exist_ok=True)
            story_file = f"generated/fanfic_story_{len(os.listdir('generated')) + 1}.json"
            
            with open(story_file, 'w', encoding='utf-8') as f:
                json.dump(story, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Story saved to: {story_file}")
            return story
            
        except Exception as e:
            logger.error(f"Error generating story: {e}")
            return {}

def main():
    """Main function"""
    print("🪄 HARRY POTTER FANFICTION GENERATOR")
    print("Using your novel_data.db database with Ollama")
    print("=" * 60)
    
    # Initialize generator
    generator = SimpleFanficGenerator()
    
    # Step 1: Analyze the database
    corpus_analysis = generator.analyze_sample(sample_size=25)
    
    if not corpus_analysis:
        print("❌ Could not analyze database. Exiting.")
        return
    
    # Step 2: Test Ollama
    print("\n🤖 Testing Ollama connection...")
    ollama_available, model_info = generator.test_ollama()
    
    if ollama_available:
        print(f"✅ Ollama is running with model: {model_info}")
        
        # Step 3: Generate story
        story = generator.generate_story(corpus_analysis, model_info)
        
        if story:
            print("\n🎉 Story Generation Complete!")
            print("=" * 40)
            print(f"📖 Title: {story.get('title', 'Untitled')}")
            print(f"📄 Chapters: {len(story.get('chapters', []))}")
            print(f"📊 Word count: {story.get('metadata', {}).get('estimated_word_count', 0)}")
            
            # Show first chapter preview
            if story.get('chapters'):
                print(f"\n📜 First Chapter Preview:")
                first_chapter = story['chapters'][0]
                print(f"{first_chapter[:300]}...")
            
            print(f"\n💾 Full story saved in the 'generated' folder")
        else:
            print("❌ Story generation failed")
    
    else:
        print(f"❌ Ollama not available: {model_info}")
        print("\n💡 To use Ollama:")
        print("1. Install Ollama: https://ollama.ai/")
        print("2. Start Ollama: ollama serve")
        print("3. Pull Llama 3.1: ollama pull llama3.1")
        print("4. Run this script again")
        
        # Generate with mock responses instead
        print("\n🔄 Generating story with mock responses...")
        story = generator.generate_story(corpus_analysis, "mock")
        
        if story:
            print("✅ Mock story generated (for demonstration)")

if __name__ == "__main__":
    main()
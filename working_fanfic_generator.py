#!/usr/bin/env python3
"""
Working fanfiction generator using extracted chapters and Ollama
"""

import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging
import os
import requests
from text_analyzer import TextAnalyzer, CorpusAnalyzer
from llm_generator import LLMGenerator, FanfictionGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkingFanficGenerator:
    def __init__(self, data_file: str = "extracted_chapters.json"):
        self.data_file = data_file
        self.text_analyzer = TextAnalyzer()
        self.corpus_analyzer = CorpusAnalyzer(self.text_analyzer)
        
    def load_chapters(self) -> pd.DataFrame:
        """Load chapters from extracted JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                chapters = json.load(f)
            
            df = pd.DataFrame(chapters)
            logger.info(f"Loaded {len(df)} chapters from {self.data_file}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading chapters: {e}")
            return pd.DataFrame()
    
    def analyze_corpus(self) -> Dict[str, Any]:
        """Analyze the extracted chapters"""
        print("📊 Analyzing your Harry Potter fanfiction corpus...")
        
        # Load chapters
        df = self.load_chapters()
        
        if df.empty:
            print("❌ No chapters could be loaded")
            return {}
        
        print(f"✅ Loaded {len(df)} chapters for analysis")
        
        # Show sample data
        print("\n📖 Sample chapters from your database:")
        for idx, row in df.head(3).iterrows():
            print(f"  Chapter {row['id']}: {row['title']}")
            print(f"    Novel ID: {row['novel_id']}")
            print(f"    Content length: {len(row['content'])} chars")
            print(f"    Preview: {row['content'][:100].strip()}...")
            print()
        
        # Analyze corpus
        try:
            corpus_analysis = self.corpus_analyzer.analyze_corpus(df, 'content')
            
            print("✅ Corpus analysis complete!")
            
            # Display results
            if 'basic_statistics' in corpus_analysis:
                stats = corpus_analysis['basic_statistics']
                print(f"\n📈 Writing Statistics:")
                print(f"  Average word count per chapter: {stats.get('avg_word_count', 0):.0f}")
                print(f"  Average readability score: {stats.get('avg_readability', 0):.1f}")
                print(f"  Average grade level: {stats.get('avg_grade_level', 0):.1f}")
            
            if 'character_analysis' in corpus_analysis:
                print(f"\n👥 Character Analysis:")
                char_analysis = corpus_analysis['character_analysis']
                sorted_chars = sorted(char_analysis.items(), 
                                    key=lambda x: x[1].get('total_mentions', 0), 
                                    reverse=True)
                
                found_chars = [(char, stats) for char, stats in sorted_chars 
                             if stats.get('total_mentions', 0) > 0]
                
                if found_chars:
                    print("  Most mentioned characters:")
                    for char, stats in found_chars[:8]:
                        mentions = stats.get('total_mentions', 0)
                        stories = stats.get('stories_featured', 0)
                        print(f"    {char}: {mentions} mentions in {stories} chapters")
                else:
                    print("  No major HP characters detected (might be OC-focused stories)")
            
            if 'themes' in corpus_analysis and 'topics' in corpus_analysis['themes']:
                print(f"\n🎭 Common Themes:")
                topics = corpus_analysis['themes']['topics']
                for i, topic in enumerate(topics[:3]):
                    words = ', '.join(topic['words'][:5])
                    print(f"  Theme {i+1}: {words}")
            
            return corpus_analysis
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            return {}
    
    def test_ollama(self) -> tuple[bool, str]:
        """Test Ollama connection and available models"""
        print("\n🤖 Testing Ollama connection...")
        
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                print(f"✅ Ollama is running!")
                print(f"📋 Available models: {model_names}")
                
                # Look for llama3.1 models
                llama_models = [name for name in model_names if 'llama3.1' in name.lower()]
                if llama_models:
                    print(f"🎯 Found Llama 3.1: {llama_models[0]}")
                    return True, llama_models[0]
                elif model_names:
                    print(f"🎯 Using available model: {model_names[0]}")
                    return True, model_names[0]
                else:
                    return False, "No models found"
            else:
                return False, f"Server error: {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def generate_story(self, corpus_analysis: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """Generate a story using Ollama"""
        print(f"\n✨ Generating Harry Potter fanfiction...")
        print(f"🤖 Using model: {model_name}")
        
        # Initialize generator
        llm_generator = LLMGenerator(model_type="ollama", model_name=model_name)
        fanfic_generator = FanfictionGenerator(llm_generator, corpus_analysis)
        
        # Generation parameters based on your corpus
        parameters = {
            'main_character': 'Harry Potter',
            'genre': 'Adventure',
            'setting': 'Hogwarts',
            'theme': 'discovering hidden magical powers and ancient secrets',
            'target_length': 2500  # Reasonable length for demonstration
        }
        
        print(f"📝 Story parameters:")
        for key, value in parameters.items():
            print(f"  {key}: {value}")
        
        try:
            # Generate story
            print(f"\n⏳ Generating story... (this may take a minute)")
            story = fanfic_generator.generate_full_story(parameters)
            
            # Save story
            os.makedirs("generated", exist_ok=True)
            story_file = f"generated/hp_fanfic_{len(os.listdir('generated')) + 1}.json"
            
            with open(story_file, 'w', encoding='utf-8') as f:
                json.dump(story, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Story generated and saved to: {story_file}")
            return story
            
        except Exception as e:
            logger.error(f"Error generating story: {e}")
            return {}
    
    def display_story(self, story: Dict[str, Any]):
        """Display the generated story"""
        if not story:
            return
        
        print("\n" + "="*60)
        print("🎉 GENERATED HARRY POTTER FANFICTION")
        print("="*60)
        
        print(f"\n📖 Title: {story.get('title', 'Untitled')}")
        
        if story.get('summary'):
            print(f"\n📝 Summary:")
            print(f"{story['summary']}")
        
        metadata = story.get('metadata', {})
        chapters = story.get('chapters', [])
        
        print(f"\n📊 Story Details:")
        print(f"  Chapters: {len(chapters)}")
        print(f"  Estimated word count: {metadata.get('estimated_word_count', 0)}")
        
        if chapters:
            print(f"\n📜 First Chapter Preview:")
            first_chapter = chapters[0]
            # Clean up the chapter text
            preview = first_chapter.replace('\\n', '\n').strip()
            print(f"{preview[:500]}...")
            
            if len(chapters) > 1:
                print(f"\n📜 Additional chapters available in the saved file.")
        
        print(f"\n💾 Full story saved in JSON format for further use.")

def main():
    """Main function"""
    print("🪄 HARRY POTTER FANFICTION GENERATOR")
    print("Using your extracted novel database with Ollama/Llama 3.1")
    print("="*70)
    
    # Initialize generator
    generator = WorkingFanficGenerator()
    
    # Step 1: Analyze the corpus
    corpus_analysis = generator.analyze_corpus()
    
    if not corpus_analysis:
        print("❌ Could not analyze corpus. Exiting.")
        return
    
    # Step 2: Test Ollama
    ollama_available, model_info = generator.test_ollama()
    
    if ollama_available:
        # Step 3: Generate story
        story = generator.generate_story(corpus_analysis, model_info)
        
        if story:
            # Step 4: Display results
            generator.display_story(story)
        else:
            print("❌ Story generation failed")
    
    else:
        print(f"❌ Ollama not available: {model_info}")
        print("\n💡 To use Ollama with Llama 3.1:")
        print("1. Install Ollama: https://ollama.ai/")
        print("2. Start Ollama server: ollama serve")
        print("3. Pull Llama 3.1: ollama pull llama3.1")
        print("4. Run this script again")
        
        # Generate with mock responses for demonstration
        print("\n🔄 Generating demo story with mock responses...")
        mock_generator = LLMGenerator(model_type="openai")  # Will use mock
        fanfic_generator = FanfictionGenerator(mock_generator, corpus_analysis)
        
        parameters = {
            'main_character': 'Harry Potter',
            'genre': 'Adventure', 
            'setting': 'Hogwarts',
            'theme': 'discovering hidden magical powers',
            'target_length': 1500
        }
        
        story = fanfic_generator.generate_full_story(parameters)
        if story:
            print("✅ Demo story generated!")
            generator.display_story(story)

if __name__ == "__main__":
    main()
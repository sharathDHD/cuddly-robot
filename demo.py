#!/usr/bin/env python3
"""
Demo script for Harry Potter Fanfiction Generator
This script demonstrates the key features of the system.
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from database_handler import DatabaseHandler, CSVHandler, create_sample_database
from text_analyzer import TextAnalyzer, CorpusAnalyzer
from llm_generator import LLMGenerator, FanfictionGenerator
from config import Config

def demo_database_analysis():
    """Demonstrate database analysis capabilities"""
    print("🔍 DEMO: Database Analysis")
    print("=" * 50)
    
    # Create sample database if it doesn't exist
    if not os.path.exists("sample_fanfiction.db"):
        create_sample_database()
        print("✅ Created sample database")
    
    # Initialize handlers
    db_handler = DatabaseHandler("sample_fanfiction.db")
    text_analyzer = TextAnalyzer()
    corpus_analyzer = CorpusAnalyzer(text_analyzer)
    
    # Analyze database structure
    print("\n📊 Database Structure:")
    db_analysis = db_handler.analyze_database_structure()
    print(f"  Tables: {db_analysis['tables']}")
    print(f"  Total novels: {db_analysis['total_novels']}")
    
    # Get novels
    df = db_handler.get_all_novels()
    print(f"  Loaded {len(df)} novels")
    
    # Show sample data
    print("\n📖 Sample Novel Data:")
    for idx, row in df.head(2).iterrows():
        print(f"  Title: {row['title']}")
        print(f"  Author: {row['author']}")
        print(f"  Genre: {row['genre']}")
        print(f"  Characters: {row['characters']}")
        print(f"  Content preview: {row['content'][:100]}...")
        print()
    
    return db_handler, df, text_analyzer, corpus_analyzer

def demo_text_analysis(text_analyzer, df):
    """Demonstrate text analysis features"""
    print("\n🔬 DEMO: Text Analysis")
    print("=" * 50)
    
    # Analyze a sample text
    sample_text = df.iloc[0]['content']
    print(f"📝 Analyzing sample text: '{sample_text[:50]}...'")
    
    # Basic statistics
    stats = text_analyzer.extract_basic_stats(sample_text)
    print(f"\n📊 Basic Statistics:")
    print(f"  Word count: {stats['word_count']}")
    print(f"  Sentence count: {stats['sentence_count']}")
    print(f"  Readability score: {stats['readability_score']:.1f}")
    print(f"  Grade level: {stats['grade_level']:.1f}")
    
    # Character analysis
    characters = text_analyzer.extract_characters(sample_text, Config.MAIN_CHARACTERS)
    print(f"\n👥 Character Mentions:")
    for char, count in characters.items():
        print(f"  {char}: {count} mentions")
    
    # Sentiment analysis
    sentiment = text_analyzer.analyze_sentiment(sample_text)
    print(f"\n😊 Sentiment Analysis:")
    print(f"  Positive: {sentiment['positive']:.2f}")
    print(f"  Negative: {sentiment['negative']:.2f}")
    print(f"  Neutral: {sentiment['neutral']:.2f}")
    print(f"  Compound: {sentiment['compound']:.2f}")
    
    # Writing style
    style = text_analyzer.analyze_writing_style(sample_text)
    print(f"\n✍️ Writing Style:")
    print(f"  Average sentence length: {style['avg_sentence_length']:.1f} words")
    print(f"  Dialogue ratio: {style['dialogue_ratio']:.2f}")
    print(f"  Punctuation density: {style['punctuation_density']:.3f}")

def demo_corpus_analysis(corpus_analyzer, df):
    """Demonstrate corpus-wide analysis"""
    print("\n📚 DEMO: Corpus Analysis")
    print("=" * 50)
    
    # Analyze entire corpus
    corpus_analysis = corpus_analyzer.analyze_corpus(df, 'content')
    
    print(f"📈 Corpus Statistics:")
    basic_stats = corpus_analysis['basic_statistics']
    print(f"  Average word count: {basic_stats['avg_word_count']:.0f}")
    print(f"  Average readability: {basic_stats['avg_readability']:.1f}")
    print(f"  Average grade level: {basic_stats['avg_grade_level']:.1f}")
    
    print(f"\n👥 Character Popularity:")
    char_analysis = corpus_analysis['character_analysis']
    # Sort by popularity
    sorted_chars = sorted(char_analysis.items(), 
                         key=lambda x: x[1]['popularity_score'], 
                         reverse=True)
    
    for char, stats in sorted_chars[:5]:
        print(f"  {char}: {stats['popularity_score']:.2f} popularity, "
              f"{stats['total_mentions']} total mentions")
    
    print(f"\n🎭 Common Themes:")
    if 'themes' in corpus_analysis and 'topics' in corpus_analysis['themes']:
        for i, topic in enumerate(corpus_analysis['themes']['topics'][:3]):
            print(f"  Topic {i+1}: {', '.join(topic['words'][:5])}")
    
    return corpus_analysis

def demo_story_generation(corpus_analysis):
    """Demonstrate story generation"""
    print("\n✨ DEMO: Story Generation")
    print("=" * 50)
    
    # Initialize LLM generator (will use mock responses without API key)
    llm_generator = LLMGenerator(model_type="openai")
    fanfic_generator = FanfictionGenerator(llm_generator, corpus_analysis)
    
    # Set generation parameters
    parameters = {
        'main_character': 'Hermione Granger',
        'genre': 'Mystery',
        'setting': 'Hogwarts',
        'theme': 'uncovering ancient secrets',
        'target_length': 3000
    }
    
    print(f"🎯 Generation Parameters:")
    for key, value in parameters.items():
        print(f"  {key}: {value}")
    
    print(f"\n🔮 Generating story outline...")
    outline = fanfic_generator.generate_story_outline(parameters)
    print(f"📋 Story Outline:")
    print(f"  {outline['outline'][:200]}...")
    
    print(f"\n📖 Generating first chapter...")
    chapter = fanfic_generator.generate_chapter(outline, 1)
    print(f"📄 Chapter 1 Preview:")
    print(f"  {chapter[:200]}...")
    
    print(f"\n📚 Generating complete story...")
    story = fanfic_generator.generate_full_story(parameters)
    
    print(f"\n🎉 Generated Story:")
    print(f"  Title: {story['title']}")
    print(f"  Summary: {story['summary'][:150]}...")
    print(f"  Chapters: {len(story['chapters'])}")
    print(f"  Estimated word count: {story['metadata']['estimated_word_count']}")
    
    # Save the demo story
    demo_story_file = "generated/demo_story.json"
    with open(demo_story_file, 'w', encoding='utf-8') as f:
        json.dump(story, f, indent=2, ensure_ascii=False)
    
    print(f"  💾 Saved to: {demo_story_file}")
    
    return story

def demo_csv_upload():
    """Demonstrate CSV file handling"""
    print("\n📄 DEMO: CSV File Handling")
    print("=" * 50)
    
    # Load CSV file
    if os.path.exists("sample_fanfiction.csv"):
        df = CSVHandler.load_csv("sample_fanfiction.csv")
        print(f"✅ Loaded CSV with {len(df)} novels")
        
        print(f"\n📊 CSV Data Preview:")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Sample titles: {df['title'].head(3).tolist()}")
        
        # Analyze CSV corpus
        text_analyzer = TextAnalyzer()
        corpus_analyzer = CorpusAnalyzer(text_analyzer)
        
        corpus_analysis = corpus_analyzer.analyze_corpus(df, 'content')
        print(f"  Average word count: {corpus_analysis['basic_statistics']['avg_word_count']:.0f}")
        
        return df
    else:
        print("❌ sample_fanfiction.csv not found")
        return None

def main():
    """Run the complete demo"""
    print("🪄 HARRY POTTER FANFICTION GENERATOR DEMO")
    print("=" * 60)
    print("This demo showcases the key features of the system:")
    print("1. Database analysis and structure detection")
    print("2. Text analysis and feature extraction")
    print("3. Corpus-wide analysis and insights")
    print("4. AI-powered story generation")
    print("5. Multiple file format support")
    print()
    
    # Ensure directories exist
    os.makedirs("generated", exist_ok=True)
    
    try:
        # Demo 1: Database Analysis
        db_handler, df, text_analyzer, corpus_analyzer = demo_database_analysis()
        
        # Demo 2: Text Analysis
        demo_text_analysis(text_analyzer, df)
        
        # Demo 3: Corpus Analysis
        corpus_analysis = demo_corpus_analysis(corpus_analyzer, df)
        
        # Demo 4: Story Generation
        story = demo_story_generation(corpus_analysis)
        
        # Demo 5: CSV Handling
        csv_df = demo_csv_upload()
        
        print("\n🎊 DEMO COMPLETE!")
        print("=" * 60)
        print("✅ All features demonstrated successfully!")
        print("\n🚀 Next Steps:")
        print("1. Upload your own fanfiction database (324 novels)")
        print("2. Run the web interface: python main.py --mode web")
        print("3. Generate your own stories with custom parameters")
        print("4. Explore the analysis features for insights")
        print("\n💡 Tips:")
        print("- Set OPENAI_API_KEY or ANTHROPIC_API_KEY for real LLM generation")
        print("- Use larger databases for better analysis and generation")
        print("- Experiment with different generation parameters")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("This might be due to missing dependencies or data files.")
        print("Please check the README.md for setup instructions.")

if __name__ == "__main__":
    main()
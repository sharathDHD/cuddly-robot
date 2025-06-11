#!/usr/bin/env python3
"""
Harry Potter Fanfiction Generator
A comprehensive system for generating new fanfiction stories using LLM
based on analysis of existing fanfiction corpus.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from database_handler import DatabaseHandler, create_sample_database
from text_analyzer import TextAnalyzer, CorpusAnalyzer
from llm_generator import LLMGenerator, FanfictionGenerator
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup the environment and create necessary directories"""
    directories = ['uploads', 'generated', 'static', 'templates']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    logger.info("Environment setup complete")

def analyze_database(db_path: str):
    """Analyze the fanfiction database"""
    logger.info(f"Analyzing database: {db_path}")
    
    # Initialize handlers
    db_handler = DatabaseHandler(db_path)
    text_analyzer = TextAnalyzer()
    corpus_analyzer = CorpusAnalyzer(text_analyzer)
    
    # Get database structure
    db_analysis = db_handler.analyze_database_structure()
    logger.info(f"Database contains {db_analysis['total_novels']} novels")
    
    # Get novels dataframe
    df = db_handler.get_all_novels()
    
    if df.empty:
        logger.error("No novels found in database")
        return None
    
    # Find text column
    text_columns = ['content', 'text', 'story', 'body', 'novel']
    text_column = None
    
    for col in text_columns:
        if col in df.columns:
            text_column = col
            break
    
    if not text_column:
        logger.error("No text column found in database")
        return None
    
    # Analyze corpus
    corpus_analysis = corpus_analyzer.analyze_corpus(df, text_column)
    
    return {
        'db_handler': db_handler,
        'df': df,
        'text_column': text_column,
        'corpus_analysis': corpus_analysis
    }

def generate_story_cli(analysis_result: dict, parameters: dict):
    """Generate a story using command line interface"""
    logger.info("Generating story with parameters:")
    for key, value in parameters.items():
        logger.info(f"  {key}: {value}")
    
    # Initialize LLM generator
    llm_generator = LLMGenerator(
        model_type=parameters.get('model_type', 'openai'),
        model_name=parameters.get('model_name', Config.DEFAULT_MODEL)
    )
    
    # Initialize fanfiction generator
    fanfic_generator = FanfictionGenerator(
        llm_generator, 
        analysis_result['corpus_analysis']
    )
    
    # Generate story
    story = fanfic_generator.generate_full_story(parameters)
    
    # Save story
    story_id = len(os.listdir("generated")) + 1
    story_file = f"generated/story_{story_id}.json"
    
    import json
    with open(story_file, 'w', encoding='utf-8') as f:
        json.dump(story, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Story generated and saved to: {story_file}")
    
    # Print story summary
    print("\n" + "="*60)
    print(f"GENERATED STORY: {story['title']}")
    print("="*60)
    print(f"\nSUMMARY:\n{story['summary']}")
    print(f"\nCHAPTERS: {len(story['chapters'])}")
    print(f"ESTIMATED WORD COUNT: {story['metadata']['estimated_word_count']}")
    print("\n" + "="*60)
    
    return story

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Harry Potter Fanfiction Generator")
    parser.add_argument('--mode', choices=['web', 'cli', 'analyze'], default='web',
                       help='Mode to run the application')
    parser.add_argument('--database', type=str, help='Path to fanfiction database')
    parser.add_argument('--create-sample', action='store_true',
                       help='Create a sample database for testing')
    
    # Story generation parameters
    parser.add_argument('--character', type=str, default='Harry Potter',
                       help='Main character for the story')
    parser.add_argument('--genre', type=str, default='Adventure',
                       help='Genre of the story')
    parser.add_argument('--setting', type=str, default='Hogwarts',
                       help='Setting of the story')
    parser.add_argument('--theme', type=str, default='friendship and courage',
                       help='Theme of the story')
    parser.add_argument('--length', type=int, default=5000,
                       help='Target length in words')
    parser.add_argument('--model-type', type=str, default='ollama',
                       choices=['openai', 'anthropic', 'ollama'],
                       help='LLM model type to use')
    parser.add_argument('--model-name', type=str,
                       help='Specific model name to use')
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Create sample database if requested
    if args.create_sample:
        create_sample_database()
        print("Sample database created: sample_fanfiction.db")
        if not args.database:
            args.database = "sample_fanfiction.db"
    
    if args.mode == 'web':
        # Run web interface
        logger.info("Starting web interface...")
        import uvicorn
        from web_interface import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=12000,
            reload=False
        )
    
    elif args.mode == 'analyze':
        # Analyze database
        if not args.database:
            logger.error("Database path required for analysis mode")
            return
        
        if not os.path.exists(args.database):
            logger.error(f"Database file not found: {args.database}")
            return
        
        analysis_result = analyze_database(args.database)
        if analysis_result:
            print("\nDATABASE ANALYSIS COMPLETE")
            print(f"Total novels: {len(analysis_result['df'])}")
            print(f"Text column: {analysis_result['text_column']}")
            
            corpus_analysis = analysis_result['corpus_analysis']
            if 'basic_statistics' in corpus_analysis:
                stats = corpus_analysis['basic_statistics']
                print(f"Average word count: {stats.get('avg_word_count', 0):.0f}")
                print(f"Average readability: {stats.get('avg_readability', 0):.1f}")
    
    elif args.mode == 'cli':
        # Generate story via CLI
        if not args.database:
            logger.error("Database path required for CLI generation mode")
            return
        
        if not os.path.exists(args.database):
            logger.error(f"Database file not found: {args.database}")
            return
        
        # Analyze database
        analysis_result = analyze_database(args.database)
        if not analysis_result:
            logger.error("Failed to analyze database")
            return
        
        # Set up generation parameters
        parameters = {
            'main_character': args.character,
            'genre': args.genre,
            'setting': args.setting,
            'theme': args.theme,
            'target_length': args.length,
            'model_type': args.model_type,
            'model_name': args.model_name
        }
        
        # Generate story
        story = generate_story_cli(analysis_result, parameters)

if __name__ == "__main__":
    main()
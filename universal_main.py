#!/usr/bin/env python3
"""
Universal Fanfiction Generator - Main Application
===============================================

A comprehensive system for generating epic fanfiction stories from any novel universe.
Supports 1000-chapter epics across 5 arcs with advanced AI integration.

Usage:
    python universal_main.py --mode web                    # Launch web interface
    python universal_main.py --mode cli --help            # CLI help
    python universal_main.py --mode create-epic           # Create epic story
    python universal_main.py --mode generate-chapters     # Generate chapters
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup the environment and dependencies"""
    try:
        import nltk
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        logger.info("NLTK data downloaded successfully")
    except Exception as e:
        logger.warning(f"Could not download NLTK data: {e}")
    
    # Ensure required directories exist
    Path("generated").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    logger.info("Environment setup complete")

def run_web_interface():
    """Launch the web interface"""
    try:
        import uvicorn
        from universal_web_interface import app
        
        logger.info("Starting Universal Fanfiction Generator web interface...")
        
        uvicorn.run(
            "universal_web_interface:app",
            host="0.0.0.0",
            port=12000,
            reload=False,
            log_level="info"
        )
    except ImportError as e:
        logger.error(f"Missing dependencies for web interface: {e}")
        logger.error("Please install: pip install fastapi uvicorn jinja2")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting web interface: {e}")
        sys.exit(1)

def run_cli_mode(args):
    """Run CLI operations"""
    from universal_generator import (
        UniversalDatabaseHandler, 
        UniversalStoryGenerator, 
        POPULAR_UNIVERSES,
        setup_universe
    )
    from llm_generator import LLMGenerator
    
    # Initialize components
    db_handler = UniversalDatabaseHandler("universal_fanfiction.db")
    llm_generator = LLMGenerator()
    story_generator = UniversalStoryGenerator(db_handler, llm_generator)
    
    if args.action == 'list-universes':
        print("\n🌌 Available Universes:")
        print("=" * 50)
        for name, universe in POPULAR_UNIVERSES.items():
            print(f"📚 {name}")
            print(f"   Genre: {universe.genre}")
            print(f"   Characters: {', '.join(universe.main_characters[:3])}...")
            print(f"   Themes: {', '.join(universe.themes[:3])}...")
            print()
    
    elif args.action == 'setup-universe':
        if not args.universe:
            print("❌ Please specify --universe")
            return
        
        try:
            universe = setup_universe(db_handler, args.universe)
            print(f"✅ Successfully setup {args.universe} universe")
            print(f"   Genre: {universe.genre}")
            print(f"   Characters: {len(universe.main_characters)}")
            print(f"   Locations: {len(universe.locations)}")
        except Exception as e:
            print(f"❌ Error setting up universe: {e}")
    
    elif args.action == 'create-epic':
        if not all([args.universe, args.title, args.theme, args.protagonist]):
            print("❌ Required: --universe, --title, --theme, --protagonist")
            return
        
        try:
            # Configure LLM
            llm_generator.configure(args.model_type, args.model_name)
            
            print(f"🎯 Creating epic story: {args.title}")
            print(f"   Universe: {args.universe}")
            print(f"   Theme: {args.theme}")
            print(f"   Protagonist: {args.protagonist}")
            
            story, story_id = story_generator.generate_epic_story(
                universe_name=args.universe,
                main_theme=args.theme,
                protagonist=args.protagonist,
                story_title=args.title
            )
            
            print(f"\n✅ Epic story created successfully!")
            print(f"   Story ID: {story_id}")
            print(f"   Total Chapters: {story.total_chapters}")
            print(f"   Arcs: {len(story.arcs)}")
            
            print(f"\n📖 Arc Structure:")
            for arc in story.arcs:
                print(f"   Arc {arc.number}: {arc.title}")
                print(f"      Theme: {arc.theme}")
                print(f"      Chapters: {len(arc.chapters)}")
            
        except Exception as e:
            print(f"❌ Error creating epic story: {e}")
    
    elif args.action == 'generate-chapters':
        if not all([args.story_id, args.arc]):
            print("❌ Required: --story-id, --arc")
            return
        
        try:
            print(f"📝 Generating chapters for Story ID {args.story_id}, Arc {args.arc}")
            print(f"   Chapters: {args.start_chapter} to {args.start_chapter + args.num_chapters - 1}")
            
            chapters = story_generator.generate_chapters_for_arc(
                story_id=args.story_id,
                arc_number=args.arc,
                start_chapter=args.start_chapter,
                num_chapters=args.num_chapters
            )
            
            print(f"\n✅ Generated {len(chapters)} chapters successfully!")
            
            for chapter in chapters:
                print(f"\n📄 Chapter {chapter.number}: {chapter.title}")
                print(f"   Words: {chapter.word_count}")
                print(f"   Characters: {', '.join(chapter.characters_featured)}")
                print(f"   Preview: {chapter.content[:100]}...")
                
        except Exception as e:
            print(f"❌ Error generating chapters: {e}")
    
    elif args.action == 'list-stories':
        try:
            import sqlite3
            
            with sqlite3.connect(db_handler.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, universe, total_chapters, current_chapter, created_at
                    FROM generated_stories
                    ORDER BY created_at DESC
                ''')
                
                stories = cursor.fetchall()
                
                if not stories:
                    print("📚 No stories found. Create your first epic!")
                    return
                
                print("\n📚 Your Epic Stories:")
                print("=" * 80)
                
                for story in stories:
                    print(f"🎭 {story[1]} (ID: {story[0]})")
                    print(f"   Universe: {story[2]}")
                    print(f"   Progress: {story[4]}/{story[3]} chapters")
                    print(f"   Created: {story[5]}")
                    print()
                    
        except Exception as e:
            print(f"❌ Error listing stories: {e}")
    
    else:
        print("❌ Unknown action. Use --help for available commands.")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Universal Fanfiction Generator - Create epic stories from any universe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch web interface
  python universal_main.py --mode web
  
  # List available universes
  python universal_main.py --mode cli --action list-universes
  
  # Setup a universe
  python universal_main.py --mode cli --action setup-universe --universe "Harry Potter"
  
  # Create epic story
  python universal_main.py --mode cli --action create-epic \\
    --universe "Harry Potter" \\
    --title "The Chronicles of Magic" \\
    --theme "ancient magic awakening" \\
    --protagonist "Harry Potter"
  
  # Generate chapters
  python universal_main.py --mode cli --action generate-chapters \\
    --story-id 1 --arc 1 --start-chapter 1 --num-chapters 10
  
  # List all stories
  python universal_main.py --mode cli --action list-stories
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['web', 'cli'],
        default='web',
        help='Application mode (default: web)'
    )
    
    # CLI-specific arguments
    parser.add_argument(
        '--action',
        choices=[
            'list-universes', 'setup-universe', 'create-epic', 
            'generate-chapters', 'list-stories'
        ],
        help='CLI action to perform'
    )
    
    # Story creation arguments
    parser.add_argument('--universe', help='Universe name')
    parser.add_argument('--title', help='Story title')
    parser.add_argument('--theme', help='Main theme')
    parser.add_argument('--protagonist', help='Main protagonist')
    
    # Chapter generation arguments
    parser.add_argument('--story-id', type=int, help='Story ID')
    parser.add_argument('--arc', type=int, help='Arc number (1-5)')
    parser.add_argument('--start-chapter', type=int, default=1, help='Starting chapter number')
    parser.add_argument('--num-chapters', type=int, default=10, help='Number of chapters to generate')
    
    # AI model arguments
    parser.add_argument('--model-type', default='ollama', choices=['ollama', 'openai', 'anthropic'], help='AI model type')
    parser.add_argument('--model-name', default='llama3.1:8b', help='AI model name')
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    if args.mode == 'web':
        run_web_interface()
    elif args.mode == 'cli':
        if not args.action:
            parser.print_help()
            print("\n❌ CLI mode requires --action parameter")
            sys.exit(1)
        run_cli_mode(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
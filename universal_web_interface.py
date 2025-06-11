#!/usr/bin/env python3
"""
Universal Fanfiction Generator Web Interface
===========================================

A beautiful web interface for generating epic fanfiction stories
from any novel universe with 1000+ chapters across 5 arcs.
"""

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import json
import asyncio
from typing import Optional, List, Dict
import logging
from pathlib import Path

from universal_generator import (
    UniversalDatabaseHandler, 
    UniversalStoryGenerator, 
    POPULAR_UNIVERSES,
    setup_universe
)
from llm_generator import LLMGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Universal Fanfiction Generator", version="2.0.0")
templates = Jinja2Templates(directory="templates")

# Global instances
db_handler = None
story_generator = None
llm_generator = None

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    global db_handler, story_generator, llm_generator
    
    # Initialize database
    db_handler = UniversalDatabaseHandler("universal_fanfiction.db")
    
    # Initialize LLM
    llm_generator = LLMGenerator()
    
    # Initialize story generator
    story_generator = UniversalStoryGenerator(db_handler, llm_generator)
    
    # Setup popular universes
    for universe_name in POPULAR_UNIVERSES:
        try:
            setup_universe(db_handler, universe_name)
        except Exception as e:
            logger.warning(f"Could not setup {universe_name}: {e}")
    
    logger.info("Universal Fanfiction Generator started successfully!")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page"""
    return templates.TemplateResponse("universal_index.html", {
        "request": request,
        "universes": list(POPULAR_UNIVERSES.keys())
    })

@app.post("/upload-corpus")
async def upload_corpus(
    universe: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload fanfiction corpus for any universe"""
    try:
        content = await file.read()
        
        if file.filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
            count = 0
            
            for story in data:
                db_handler.add_fanfiction(
                    universe=universe,
                    title=story.get('title', 'Untitled'),
                    content=story.get('content', ''),
                    author=story.get('author', ''),
                    characters=story.get('characters', []),
                    genre=story.get('genre', ''),
                    themes=story.get('themes', []),
                    tags=story.get('tags', [])
                )
                count += 1
            
            return JSONResponse({
                "status": "success",
                "message": f"Successfully uploaded {count} stories to {universe} corpus"
            })
        
        elif file.filename.endswith('.csv'):
            # Handle CSV upload
            import csv
            import io
            
            csv_content = content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(csv_content))
            count = 0
            
            for row in reader:
                db_handler.add_fanfiction(
                    universe=universe,
                    title=row.get('title', 'Untitled'),
                    content=row.get('content', ''),
                    author=row.get('author', ''),
                    characters=json.loads(row.get('characters', '[]')) if row.get('characters') else [],
                    genre=row.get('genre', ''),
                    themes=json.loads(row.get('themes', '[]')) if row.get('themes') else []
                )
                count += 1
            
            return JSONResponse({
                "status": "success", 
                "message": f"Successfully uploaded {count} stories to {universe} corpus"
            })
        
        else:
            return JSONResponse({
                "status": "error",
                "message": "Unsupported file format. Please use JSON or CSV."
            })
    
    except Exception as e:
        logger.error(f"Error uploading corpus: {e}")
        return JSONResponse({
            "status": "error",
            "message": f"Error uploading corpus: {str(e)}"
        })

@app.post("/create-epic-story")
async def create_epic_story(
    universe: str = Form(...),
    story_title: str = Form(...),
    main_theme: str = Form(...),
    protagonist: str = Form(...),
    model_type: str = Form("ollama"),
    model_name: str = Form("llama3.1:8b")
):
    """Create a new epic 1000-chapter story structure"""
    try:
        # Configure LLM
        llm_generator.configure(model_type, model_name)
        
        # Generate epic story structure
        story, story_id = story_generator.generate_epic_story(
            universe_name=universe,
            main_theme=main_theme,
            protagonist=protagonist,
            story_title=story_title
        )
        
        return JSONResponse({
            "status": "success",
            "message": f"Epic story '{story_title}' created successfully!",
            "story_id": story_id,
            "story": {
                "title": story.title,
                "universe": story.universe,
                "summary": story.summary,
                "total_chapters": story.total_chapters,
                "arcs": [{"number": arc.number, "title": arc.title, "theme": arc.theme} for arc in story.arcs]
            }
        })
    
    except Exception as e:
        logger.error(f"Error creating epic story: {e}")
        return JSONResponse({
            "status": "error",
            "message": f"Error creating story: {str(e)}"
        })

@app.post("/generate-chapters")
async def generate_chapters(
    story_id: int = Form(...),
    arc_number: int = Form(...),
    start_chapter: int = Form(1),
    num_chapters: int = Form(10)
):
    """Generate chapters for a specific arc"""
    try:
        chapters = story_generator.generate_chapters_for_arc(
            story_id=story_id,
            arc_number=arc_number,
            start_chapter=start_chapter,
            num_chapters=num_chapters
        )
        
        return JSONResponse({
            "status": "success",
            "message": f"Generated {len(chapters)} chapters for Arc {arc_number}",
            "chapters": [
                {
                    "number": ch.number,
                    "title": ch.title,
                    "word_count": ch.word_count,
                    "characters": ch.characters_featured,
                    "preview": ch.content[:200] + "..."
                }
                for ch in chapters
            ]
        })
    
    except Exception as e:
        logger.error(f"Error generating chapters: {e}")
        return JSONResponse({
            "status": "error",
            "message": f"Error generating chapters: {str(e)}"
        })

@app.get("/get-chapter/{story_id}/{chapter_number}")
async def get_chapter(story_id: int, chapter_number: int):
    """Get full chapter content"""
    try:
        import sqlite3
        
        with sqlite3.connect(db_handler.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT title, content, arc_number, characters_featured, plot_points, word_count, cliffhanger
                FROM story_chapters 
                WHERE story_id = ? AND chapter_number = ?
            ''', (story_id, chapter_number))
            
            row = cursor.fetchone()
            if row:
                return JSONResponse({
                    "status": "success",
                    "chapter": {
                        "title": row[0],
                        "content": row[1],
                        "arc_number": row[2],
                        "characters_featured": json.loads(row[3]) if row[3] else [],
                        "plot_points": json.loads(row[4]) if row[4] else [],
                        "word_count": row[5],
                        "cliffhanger": row[6]
                    }
                })
            else:
                return JSONResponse({
                    "status": "error",
                    "message": "Chapter not found"
                })
    
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error retrieving chapter: {str(e)}"
        })

@app.get("/get-stories")
async def get_stories():
    """Get all generated stories"""
    try:
        import sqlite3
        
        with sqlite3.connect(db_handler.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, universe, summary, total_chapters, current_chapter, created_at
                FROM generated_stories
                ORDER BY created_at DESC
            ''')
            
            stories = []
            for row in cursor.fetchall():
                stories.append({
                    "id": row[0],
                    "title": row[1],
                    "universe": row[2],
                    "summary": row[3],
                    "total_chapters": row[4],
                    "current_chapter": row[5],
                    "created_at": row[6]
                })
            
            return JSONResponse({
                "status": "success",
                "stories": stories
            })
    
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error retrieving stories: {str(e)}"
        })

@app.get("/get-universe-info/{universe_name}")
async def get_universe_info(universe_name: str):
    """Get information about a specific universe"""
    try:
        universe = db_handler.get_universe(universe_name)
        if universe:
            return JSONResponse({
                "status": "success",
                "universe": {
                    "name": universe.name,
                    "genre": universe.genre,
                    "main_characters": universe.main_characters,
                    "locations": universe.locations,
                    "themes": universe.themes,
                    "magic_system": universe.magic_system,
                    "time_period": universe.time_period,
                    "world_building_elements": universe.world_building_elements
                }
            })
        else:
            return JSONResponse({
                "status": "error",
                "message": "Universe not found"
            })
    
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error retrieving universe info: {str(e)}"
        })

@app.post("/add-custom-universe")
async def add_custom_universe(
    name: str = Form(...),
    genre: str = Form(...),
    main_characters: str = Form(...),  # JSON string
    locations: str = Form(...),        # JSON string
    themes: str = Form(...),           # JSON string
    magic_system: str = Form(""),
    time_period: str = Form(""),
    world_building_elements: str = Form("[]")  # JSON string
):
    """Add a custom universe"""
    try:
        from universal_generator import Universe
        
        universe = Universe(
            name=name,
            genre=genre,
            main_characters=json.loads(main_characters),
            locations=json.loads(locations),
            themes=json.loads(themes),
            magic_system=magic_system if magic_system else None,
            time_period=time_period if time_period else None,
            world_building_elements=json.loads(world_building_elements)
        )
        
        db_handler.add_universe(universe)
        
        return JSONResponse({
            "status": "success",
            "message": f"Custom universe '{name}' added successfully!"
        })
    
    except Exception as e:
        logger.error(f"Error adding custom universe: {e}")
        return JSONResponse({
            "status": "error",
            "message": f"Error adding universe: {str(e)}"
        })

@app.get("/corpus-stats/{universe_name}")
async def get_corpus_stats(universe_name: str):
    """Get statistics about the corpus for a universe"""
    try:
        import sqlite3
        
        with sqlite3.connect(db_handler.db_path) as conn:
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute('''
                SELECT COUNT(*), AVG(word_count), SUM(word_count)
                FROM fanfiction_corpus 
                WHERE universe = ?
            ''', (universe_name,))
            
            basic_stats = cursor.fetchone()
            
            # Get character frequency
            cursor.execute('''
                SELECT characters FROM fanfiction_corpus 
                WHERE universe = ? AND characters IS NOT NULL
            ''', (universe_name,))
            
            character_counts = {}
            for row in cursor.fetchall():
                chars = json.loads(row[0]) if row[0] else []
                for char in chars:
                    character_counts[char] = character_counts.get(char, 0) + 1
            
            return JSONResponse({
                "status": "success",
                "stats": {
                    "total_stories": basic_stats[0] or 0,
                    "average_word_count": round(basic_stats[1] or 0),
                    "total_words": basic_stats[2] or 0,
                    "top_characters": sorted(character_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                }
            })
    
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error getting corpus stats: {str(e)}"
        })

if __name__ == "__main__":
    uvicorn.run(
        "universal_web_interface:app",
        host="0.0.0.0",
        port=12000,
        reload=True
    )
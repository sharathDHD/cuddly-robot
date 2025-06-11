from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import os
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path

from database_handler import DatabaseHandler, CSVHandler, JSONHandler
from text_analyzer import TextAnalyzer, CorpusAnalyzer
from llm_generator import LLMGenerator, FanfictionGenerator
from config import Config

app = FastAPI(title="Harry Potter Fanfiction Generator", version="1.0.0")

# Create directories
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global variables for the application state
db_handler = None
text_analyzer = TextAnalyzer()
corpus_analyzer = CorpusAnalyzer(text_analyzer)
corpus_analysis = {}
current_df = pd.DataFrame()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "db_connected": db_handler is not None,
        "corpus_size": len(current_df) if not current_df.empty else 0
    })

@app.post("/upload-database")
async def upload_database(file: UploadFile = File(...)):
    """Upload and analyze database"""
    global db_handler, current_df, corpus_analysis
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    # Save uploaded file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Handle different file types
        if file.filename.endswith(('.db', '.sqlite')):
            db_handler = DatabaseHandler(file_path)
            analysis = db_handler.analyze_database_structure()
            current_df = db_handler.get_all_novels()
            
        elif file.filename.endswith('.csv'):
            current_df = CSVHandler.load_csv(file_path)
            analysis = {"tables": ["csv_data"], "total_novels": len(current_df)}
            
        elif file.filename.endswith('.json'):
            data = JSONHandler.load_json(file_path)
            current_df = pd.DataFrame(data)
            analysis = {"tables": ["json_data"], "total_novels": len(current_df)}
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Analyze corpus if we have text data
        if not current_df.empty:
            # Try to find text column
            text_columns = ['content', 'text', 'story', 'body', 'novel']
            text_column = None
            
            for col in text_columns:
                if col in current_df.columns:
                    text_column = col
                    break
            
            if text_column:
                corpus_analysis = corpus_analyzer.analyze_corpus(current_df, text_column)
            else:
                corpus_analysis = {"error": "No text column found"}
        
        return {
            "status": "success",
            "message": f"Database uploaded successfully. Found {len(current_df)} novels.",
            "analysis": analysis,
            "corpus_analysis": corpus_analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing database: {str(e)}")

@app.get("/database-info")
async def get_database_info():
    """Get information about the current database"""
    if current_df.empty:
        return {"status": "no_database", "message": "No database loaded"}
    
    return {
        "status": "connected",
        "novel_count": len(current_df),
        "columns": list(current_df.columns),
        "sample_data": current_df.head(3).to_dict('records'),
        "corpus_analysis": corpus_analysis
    }

@app.post("/generate-story")
async def generate_story(
    main_character: str = Form(...),
    genre: str = Form(...),
    setting: str = Form(...),
    theme: str = Form(...),
    target_length: int = Form(5000),
    model_type: str = Form("openai"),
    model_name: str = Form("gpt-3.5-turbo")
):
    """Generate a new fanfiction story"""
    
    if current_df.empty:
        raise HTTPException(status_code=400, detail="No database loaded. Please upload your fanfiction database first.")
    
    try:
        # Initialize LLM generator
        llm_generator = LLMGenerator(model_type=model_type, model_name=model_name)
        fanfic_generator = FanfictionGenerator(llm_generator, corpus_analysis)
        
        # Set generation parameters
        parameters = {
            'main_character': main_character,
            'genre': genre,
            'setting': setting,
            'theme': theme,
            'target_length': target_length
        }
        
        # Generate the story
        story = fanfic_generator.generate_full_story(parameters)
        
        # Save generated story
        story_id = len(os.listdir("generated")) + 1
        story_file = f"generated/story_{story_id}.json"
        
        with open(story_file, 'w', encoding='utf-8') as f:
            json.dump(story, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "story_id": story_id,
            "story": story,
            "message": f"Story generated successfully! Saved as {story_file}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating story: {str(e)}")

@app.get("/analyze-text")
async def analyze_text(text: str):
    """Analyze a piece of text"""
    try:
        analysis = {
            'basic_stats': text_analyzer.extract_basic_stats(text),
            'characters': text_analyzer.extract_characters(text, Config.MAIN_CHARACTERS),
            'locations': text_analyzer.extract_locations(text, Config.LOCATIONS),
            'magical_elements': text_analyzer.extract_magical_elements(text, Config.MAGICAL_ELEMENTS),
            'sentiment': text_analyzer.analyze_sentiment(text),
            'writing_style': text_analyzer.analyze_writing_style(text)
        }
        
        return {"status": "success", "analysis": analysis}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")

@app.get("/stories")
async def list_generated_stories():
    """List all generated stories"""
    try:
        stories = []
        generated_dir = Path("generated")
        
        if generated_dir.exists():
            for story_file in generated_dir.glob("story_*.json"):
                with open(story_file, 'r', encoding='utf-8') as f:
                    story_data = json.load(f)
                
                stories.append({
                    'id': story_file.stem.split('_')[1],
                    'title': story_data.get('title', 'Untitled'),
                    'summary': story_data.get('summary', '')[:200] + '...',
                    'chapter_count': len(story_data.get('chapters', [])),
                    'word_count': story_data.get('metadata', {}).get('estimated_word_count', 0),
                    'file': str(story_file)
                })
        
        return {"status": "success", "stories": stories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing stories: {str(e)}")

@app.get("/story/{story_id}")
async def get_story(story_id: str):
    """Get a specific generated story"""
    try:
        story_file = f"generated/story_{story_id}.json"
        
        if not os.path.exists(story_file):
            raise HTTPException(status_code=404, detail="Story not found")
        
        with open(story_file, 'r', encoding='utf-8') as f:
            story = json.load(f)
        
        return {"status": "success", "story": story}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving story: {str(e)}")

@app.get("/corpus-stats")
async def get_corpus_statistics():
    """Get detailed corpus statistics"""
    if current_df.empty:
        return {"status": "no_data", "message": "No corpus loaded"}
    
    try:
        # Basic statistics
        stats = {
            "total_novels": len(current_df),
            "columns": list(current_df.columns),
            "corpus_analysis": corpus_analysis
        }
        
        # Add column-specific statistics
        for col in current_df.columns:
            if current_df[col].dtype == 'object':  # Text columns
                stats[f"{col}_stats"] = {
                    "unique_values": current_df[col].nunique(),
                    "null_count": current_df[col].isnull().sum(),
                    "sample_values": current_df[col].dropna().head(5).tolist()
                }
            elif pd.api.types.is_numeric_dtype(current_df[col]):  # Numeric columns
                stats[f"{col}_stats"] = {
                    "mean": float(current_df[col].mean()) if not current_df[col].isnull().all() else None,
                    "min": float(current_df[col].min()) if not current_df[col].isnull().all() else None,
                    "max": float(current_df[col].max()) if not current_df[col].isnull().all() else None,
                    "null_count": current_df[col].isnull().sum()
                }
        
        return {"status": "success", "statistics": stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

@app.post("/create-sample-db")
async def create_sample_database():
    """Create a sample database for testing"""
    try:
        from database_handler import create_sample_database
        create_sample_database()
        
        return {
            "status": "success",
            "message": "Sample database created as 'sample_fanfiction.db'",
            "file_path": "sample_fanfiction.db"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sample database: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "web_interface:app",
        host="0.0.0.0",
        port=12000,
        reload=True,
        reload_dirs=["./"]
    )
#!/usr/bin/env python3
"""
Universal Novel Fanfiction Generator
====================================

A comprehensive system for generating epic fanfiction stories from any novel universe.
Supports multi-arc narratives with 1000+ chapters and advanced story planning.

Features:
- Universal genre support (any novel series)
- Epic story structure (5 arcs, 200 chapters each)
- Advanced character development tracking
- Story continuity management
- Flexible database schema
"""

import json
import sqlite3
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Universe:
    """Represents a fictional universe/series"""
    name: str
    genre: str
    main_characters: List[str]
    locations: List[str]
    themes: List[str]
    magic_system: Optional[str] = None
    time_period: Optional[str] = None
    world_building_elements: List[str] = None

@dataclass
class Character:
    """Represents a character in the story"""
    name: str
    universe: str
    role: str  # protagonist, antagonist, supporting, etc.
    traits: List[str]
    relationships: Dict[str, str]  # character_name: relationship_type
    arc_development: Dict[int, str]  # arc_number: development_notes

@dataclass
class Arc:
    """Represents a story arc"""
    number: int
    title: str
    theme: str
    main_conflict: str
    character_focus: List[str]
    chapters: List[int]  # chapter numbers in this arc
    resolution: str
    leads_to_next: str

@dataclass
class Chapter:
    """Represents a single chapter"""
    number: int
    arc: int
    title: str
    content: str
    characters_featured: List[str]
    plot_points: List[str]
    word_count: int
    cliffhanger: Optional[str] = None

@dataclass
class EpicStory:
    """Represents the complete epic story"""
    title: str
    universe: str
    summary: str
    total_chapters: int
    arcs: List[Arc]
    characters: List[Character]
    chapters: List[Chapter]
    metadata: Dict[str, Any]

class UniversalDatabaseHandler:
    """Handles database operations for any novel universe"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the universal database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Universes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS universes (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    genre TEXT NOT NULL,
                    main_characters TEXT,  -- JSON array
                    locations TEXT,        -- JSON array
                    themes TEXT,          -- JSON array
                    magic_system TEXT,
                    time_period TEXT,
                    world_building_elements TEXT,  -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Fanfiction corpus table (flexible for any universe)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fanfiction_corpus (
                    id INTEGER PRIMARY KEY,
                    universe TEXT NOT NULL,
                    title TEXT,
                    author TEXT,
                    content TEXT,
                    characters TEXT,      -- JSON array
                    genre TEXT,
                    themes TEXT,         -- JSON array
                    word_count INTEGER,
                    chapter_count INTEGER,
                    rating TEXT,
                    tags TEXT,           -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Generated stories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generated_stories (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    universe TEXT NOT NULL,
                    summary TEXT,
                    total_chapters INTEGER,
                    current_chapter INTEGER DEFAULT 0,
                    arcs_data TEXT,      -- JSON
                    characters_data TEXT, -- JSON
                    metadata TEXT,       -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Chapters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS story_chapters (
                    id INTEGER PRIMARY KEY,
                    story_id INTEGER,
                    chapter_number INTEGER,
                    arc_number INTEGER,
                    title TEXT,
                    content TEXT,
                    characters_featured TEXT,  -- JSON array
                    plot_points TEXT,         -- JSON array
                    word_count INTEGER,
                    cliffhanger TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (story_id) REFERENCES generated_stories (id)
                )
            ''')
            
            conn.commit()
    
    def add_universe(self, universe: Universe) -> int:
        """Add a new universe to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO universes 
                (name, genre, main_characters, locations, themes, magic_system, time_period, world_building_elements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                universe.name,
                universe.genre,
                json.dumps(universe.main_characters),
                json.dumps(universe.locations),
                json.dumps(universe.themes),
                universe.magic_system,
                universe.time_period,
                json.dumps(universe.world_building_elements or [])
            ))
            return cursor.lastrowid
    
    def get_universe(self, name: str) -> Optional[Universe]:
        """Get universe by name"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM universes WHERE name = ?', (name,))
            row = cursor.fetchone()
            
            if row:
                return Universe(
                    name=row[1],
                    genre=row[2],
                    main_characters=json.loads(row[3]),
                    locations=json.loads(row[4]),
                    themes=json.loads(row[5]),
                    magic_system=row[6],
                    time_period=row[7],
                    world_building_elements=json.loads(row[8]) if row[8] else []
                )
        return None
    
    def add_fanfiction(self, universe: str, title: str, content: str, **metadata) -> int:
        """Add fanfiction to the corpus"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO fanfiction_corpus 
                (universe, title, author, content, characters, genre, themes, word_count, chapter_count, rating, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                universe,
                title,
                metadata.get('author', ''),
                content,
                json.dumps(metadata.get('characters', [])),
                metadata.get('genre', ''),
                json.dumps(metadata.get('themes', [])),
                metadata.get('word_count', len(content.split())),
                metadata.get('chapter_count', 1),
                metadata.get('rating', ''),
                json.dumps(metadata.get('tags', []))
            ))
            return cursor.lastrowid
    
    def get_corpus_for_universe(self, universe: str) -> List[Dict]:
        """Get all fanfiction for a specific universe"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT title, content, characters, genre, themes, tags 
                FROM fanfiction_corpus 
                WHERE universe = ?
            ''', (universe,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'title': row[0],
                    'content': row[1],
                    'characters': json.loads(row[2]) if row[2] else [],
                    'genre': row[3],
                    'themes': json.loads(row[4]) if row[4] else [],
                    'tags': json.loads(row[5]) if row[5] else []
                })
            return results

class EpicStoryPlanner:
    """Plans epic multi-arc stories with 1000+ chapters"""
    
    def __init__(self, universe: Universe):
        self.universe = universe
    
    def create_epic_structure(self, main_theme: str, protagonist: str) -> List[Arc]:
        """Create 5-arc structure for epic story"""
        
        arc_templates = [
            {
                "title": "The Awakening",
                "theme": "Discovery and Introduction",
                "conflict_type": "Internal/Setup",
                "description": "Protagonist discovers their destiny, new powers, or hidden truth"
            },
            {
                "title": "The Rising Storm", 
                "theme": "Challenges and Growth",
                "conflict_type": "External/Building",
                "description": "First major conflicts, allies and enemies revealed"
            },
            {
                "title": "The Crucible",
                "theme": "Trials and Transformation", 
                "conflict_type": "Major Crisis",
                "description": "Greatest challenges, character transformation, major losses"
            },
            {
                "title": "The Convergence",
                "theme": "Preparation and Alliance",
                "conflict_type": "Building to Climax",
                "description": "Gathering forces, final preparations, ultimate confrontation approaches"
            },
            {
                "title": "The Resolution",
                "theme": "Climax and New Beginning",
                "conflict_type": "Final Battle/Resolution",
                "description": "Ultimate confrontation, resolution of all conflicts, new world order"
            }
        ]
        
        arcs = []
        for i, template in enumerate(arc_templates, 1):
            arc = Arc(
                number=i,
                title=f"{template['title']}: {main_theme}",
                theme=template['theme'],
                main_conflict=self._generate_arc_conflict(template['conflict_type'], main_theme),
                character_focus=[protagonist] + self._select_arc_characters(i),
                chapters=list(range((i-1)*200 + 1, i*200 + 1)),  # 200 chapters per arc
                resolution=self._generate_arc_resolution(i, template['description']),
                leads_to_next=self._generate_arc_transition(i) if i < 5 else "Epic Conclusion"
            )
            arcs.append(arc)
        
        return arcs
    
    def _generate_arc_conflict(self, conflict_type: str, main_theme: str) -> str:
        """Generate specific conflict for arc based on type and theme"""
        conflicts = {
            "Internal/Setup": f"Discovering the truth about {main_theme} and accepting responsibility",
            "External/Building": f"First confrontations with forces opposing {main_theme}",
            "Major Crisis": f"The greatest threat to {main_theme} emerges, testing all beliefs",
            "Building to Climax": f"Final preparations to resolve the {main_theme} crisis",
            "Final Battle/Resolution": f"Ultimate confrontation that determines the fate of {main_theme}"
        }
        return conflicts.get(conflict_type, f"Major conflict involving {main_theme}")
    
    def _select_arc_characters(self, arc_number: int) -> List[str]:
        """Select key characters for each arc"""
        if arc_number <= len(self.universe.main_characters):
            return self.universe.main_characters[:arc_number + 1]
        return self.universe.main_characters
    
    def _generate_arc_resolution(self, arc_number: int, description: str) -> str:
        """Generate resolution for each arc"""
        return f"Arc {arc_number} concludes with {description.lower()}, setting stage for next phase"
    
    def _generate_arc_transition(self, arc_number: int) -> str:
        """Generate transition to next arc"""
        transitions = [
            "New threats emerge from the shadows",
            "Unexpected allies reveal hidden agendas", 
            "The true scope of the conflict becomes clear",
            "Final pieces fall into place for ultimate confrontation"
        ]
        return transitions[arc_number - 1] if arc_number <= len(transitions) else "The story continues..."

class UniversalStoryGenerator:
    """Generates stories for any universe with epic structure"""
    
    def __init__(self, db_handler: UniversalDatabaseHandler, llm_generator):
        self.db = db_handler
        self.llm = llm_generator
        self.planner = None
    
    def set_universe(self, universe_name: str):
        """Set the current universe for generation"""
        universe = self.db.get_universe(universe_name)
        if universe:
            self.planner = EpicStoryPlanner(universe)
            return universe
        else:
            raise ValueError(f"Universe '{universe_name}' not found in database")
    
    def generate_epic_story(self, 
                           universe_name: str,
                           main_theme: str, 
                           protagonist: str,
                           story_title: str,
                           chapters_per_batch: int = 10) -> EpicStory:
        """Generate an epic 1000-chapter story"""
        
        universe = self.set_universe(universe_name)
        
        # Create epic structure
        arcs = self.planner.create_epic_structure(main_theme, protagonist)
        
        # Create story metadata
        story = EpicStory(
            title=story_title,
            universe=universe_name,
            summary=f"An epic {universe.genre} saga spanning 1000 chapters across 5 arcs, following {protagonist} through {main_theme}",
            total_chapters=1000,
            arcs=arcs,
            characters=[],
            chapters=[],
            metadata={
                'created_at': datetime.now().isoformat(),
                'main_theme': main_theme,
                'protagonist': protagonist,
                'universe_genre': universe.genre,
                'generation_method': 'epic_multi_arc'
            }
        )
        
        # Save story structure to database
        story_id = self._save_story_structure(story)
        
        logger.info(f"Created epic story structure: {story_title}")
        logger.info(f"5 arcs planned, 1000 chapters total")
        
        return story, story_id
    
    def generate_chapters_for_arc(self, 
                                 story_id: int, 
                                 arc_number: int, 
                                 start_chapter: int = 1,
                                 num_chapters: int = 10) -> List[Chapter]:
        """Generate specific chapters for an arc"""
        
        # Get story and arc info
        story_data = self._get_story_data(story_id)
        arc = story_data['arcs'][arc_number - 1]
        
        chapters = []
        for i in range(num_chapters):
            chapter_num = start_chapter + i
            if chapter_num > 200:  # Max chapters per arc
                break
                
            chapter = self._generate_single_chapter(
                story_data, arc, chapter_num, arc_number
            )
            chapters.append(chapter)
            
            # Save chapter to database
            self._save_chapter(story_id, chapter)
            
            logger.info(f"Generated Chapter {chapter_num} of Arc {arc_number}")
        
        return chapters
    
    def _generate_single_chapter(self, story_data: Dict, arc: Dict, chapter_num: int, arc_number: int) -> Chapter:
        """Generate a single chapter using LLM"""
        
        # Determine chapter position in arc
        arc_progress = chapter_num / 200  # Progress through current arc
        
        # Create chapter prompt
        prompt = self._create_chapter_prompt(story_data, arc, chapter_num, arc_progress)
        
        # Generate content using LLM
        content = self.llm.generate_text(prompt, max_tokens=2000)
        
        # Extract chapter title from content or generate one
        title = self._extract_or_generate_title(content, chapter_num, arc)
        
        # Create chapter object
        chapter = Chapter(
            number=chapter_num,
            arc=arc_number,
            title=title,
            content=content,
            characters_featured=self._extract_characters(content, story_data['universe']),
            plot_points=self._extract_plot_points(content),
            word_count=len(content.split()),
            cliffhanger=self._extract_cliffhanger(content) if chapter_num % 10 == 0 else None
        )
        
        return chapter
    
    def _create_chapter_prompt(self, story_data: Dict, arc: Dict, chapter_num: int, arc_progress: float) -> str:
        """Create detailed prompt for chapter generation"""
        
        universe = story_data['universe']
        corpus_sample = self.db.get_corpus_for_universe(universe)[:5]  # Sample for style
        
        prompt = f"""
Generate Chapter {chapter_num} of the epic {universe} fanfiction "{story_data['title']}".

STORY CONTEXT:
- Universe: {universe}
- Main Theme: {story_data.get('main_theme', 'Epic Adventure')}
- Current Arc: {arc['title']} (Arc {arc['number']}/5)
- Arc Theme: {arc['theme']}
- Arc Conflict: {arc['main_conflict']}
- Chapter Position: {chapter_num}/200 in this arc ({arc_progress:.1%} through arc)

STYLE REFERENCE:
Based on the writing style of the {universe} fanfiction corpus, maintain consistency with:
{self._format_style_reference(corpus_sample)}

CHAPTER REQUIREMENTS:
- Word count: 1500-2500 words
- Include character development for: {', '.join(arc['character_focus'])}
- Advance the arc's main conflict: {arc['main_conflict']}
- Maintain continuity with previous chapters
- End with appropriate tension for chapter position in arc

CHAPTER STRUCTURE:
1. Opening scene that connects to previous events
2. Character interactions and development
3. Plot advancement related to arc theme
4. Conflict escalation or resolution moment
5. Transition setup for next chapter

Generate the chapter content now:
"""
        return prompt
    
    def _format_style_reference(self, corpus_sample: List[Dict]) -> str:
        """Format corpus sample for style reference"""
        if not corpus_sample:
            return "Standard narrative style"
        
        styles = []
        for story in corpus_sample[:3]:
            excerpt = story['content'][:200] + "..."
            styles.append(f"- {story['title']}: {excerpt}")
        
        return "\n".join(styles)
    
    def _extract_characters(self, content: str, universe: str) -> List[str]:
        """Extract character names mentioned in chapter"""
        universe_data = self.db.get_universe(universe)
        if not universe_data:
            return []
        
        characters = []
        for char in universe_data.main_characters:
            if char.lower() in content.lower():
                characters.append(char)
        
        return characters
    
    def _extract_plot_points(self, content: str) -> List[str]:
        """Extract key plot points from chapter"""
        # Simple extraction - could be enhanced with NLP
        sentences = content.split('.')
        plot_points = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in ['discovered', 'revealed', 'decided', 'confronted', 'realized']):
                plot_points.append(sentence.strip())
        
        return plot_points[:3]  # Top 3 plot points
    
    def _extract_cliffhanger(self, content: str) -> Optional[str]:
        """Extract cliffhanger from chapter ending"""
        sentences = content.split('.')
        last_sentences = sentences[-3:]  # Last 3 sentences
        
        for sentence in reversed(last_sentences):
            if any(word in sentence.lower() for word in ['suddenly', 'but then', 'however', 'unexpectedly']):
                return sentence.strip()
        
        return None
    
    def _extract_or_generate_title(self, content: str, chapter_num: int, arc: Dict) -> str:
        """Extract title from content or generate one"""
        # Look for title in first line
        first_line = content.split('\n')[0].strip()
        if len(first_line) < 100 and any(word in first_line.lower() for word in ['chapter', 'part']):
            return first_line
        
        # Generate title based on arc theme
        return f"Chapter {chapter_num}: {arc['theme']} Continues"
    
    def _save_story_structure(self, story: EpicStory) -> int:
        """Save story structure to database"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO generated_stories 
                (title, universe, summary, total_chapters, arcs_data, characters_data, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                story.title,
                story.universe,
                story.summary,
                story.total_chapters,
                json.dumps([asdict(arc) for arc in story.arcs]),
                json.dumps([asdict(char) for char in story.characters]),
                json.dumps(story.metadata)
            ))
            return cursor.lastrowid
    
    def _save_chapter(self, story_id: int, chapter: Chapter):
        """Save chapter to database"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO story_chapters 
                (story_id, chapter_number, arc_number, title, content, characters_featured, plot_points, word_count, cliffhanger)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                story_id,
                chapter.number,
                chapter.arc,
                chapter.title,
                chapter.content,
                json.dumps(chapter.characters_featured),
                json.dumps(chapter.plot_points),
                chapter.word_count,
                chapter.cliffhanger
            ))
    
    def _get_story_data(self, story_id: int) -> Dict:
        """Get story data from database"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT title, universe, summary, arcs_data, metadata 
                FROM generated_stories WHERE id = ?
            ''', (story_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'title': row[0],
                    'universe': row[1],
                    'summary': row[2],
                    'arcs': json.loads(row[3]),
                    'metadata': json.loads(row[4])
                }
        return {}

# Predefined popular universes
POPULAR_UNIVERSES = {
    "Harry Potter": Universe(
        name="Harry Potter",
        genre="Fantasy",
        main_characters=["Harry Potter", "Hermione Granger", "Ron Weasley", "Albus Dumbledore", "Severus Snape", "Draco Malfoy"],
        locations=["Hogwarts", "Diagon Alley", "Ministry of Magic", "Grimmauld Place", "The Burrow"],
        themes=["Magic", "Friendship", "Good vs Evil", "Coming of Age", "Sacrifice"],
        magic_system="Wand-based magic with spells and potions",
        time_period="Modern era (1990s-2000s)",
        world_building_elements=["Wizarding World", "Houses", "Quidditch", "Dark Arts", "Magical Creatures"]
    ),
    
    "Lord of the Rings": Universe(
        name="Lord of the Rings",
        genre="High Fantasy",
        main_characters=["Frodo Baggins", "Gandalf", "Aragorn", "Legolas", "Gimli", "Boromir", "Samwise Gamgee"],
        locations=["The Shire", "Rivendell", "Moria", "Rohan", "Gondor", "Mordor", "Isengard"],
        themes=["Good vs Evil", "Friendship", "Sacrifice", "Power Corruption", "Nature vs Industry"],
        magic_system="Subtle magic through rings, wizards, and ancient powers",
        time_period="Third Age of Middle-earth",
        world_building_elements=["The One Ring", "Different Races", "Ancient Languages", "Prophecies"]
    ),
    
    "Game of Thrones": Universe(
        name="Game of Thrones",
        genre="Dark Fantasy",
        main_characters=["Jon Snow", "Daenerys Targaryen", "Tyrion Lannister", "Arya Stark", "Sansa Stark", "Jaime Lannister"],
        locations=["Winterfell", "King's Landing", "The Wall", "Dragonstone", "Braavos", "Meereen"],
        themes=["Power Struggle", "Political Intrigue", "Family Honor", "Survival", "Prophecy"],
        magic_system="Dragons, faceless men, warging, and ancient magic",
        time_period="Medieval fantasy setting",
        world_building_elements=["Seven Kingdoms", "Iron Throne", "White Walkers", "Dragons", "Great Houses"]
    ),
    
    "Naruto": Universe(
        name="Naruto",
        genre="Ninja Fantasy",
        main_characters=["Naruto Uzumaki", "Sasuke Uchiha", "Sakura Haruno", "Kakashi Hatake", "Itachi Uchiha"],
        locations=["Hidden Leaf Village", "Hidden Sand Village", "Hidden Mist Village", "Valley of the End"],
        themes=["Friendship", "Perseverance", "Redemption", "Legacy", "Peace vs War"],
        magic_system="Chakra-based jutsu and ninja techniques",
        time_period="Ninja world with modern elements",
        world_building_elements=["Hidden Villages", "Tailed Beasts", "Sharingan", "Sage Mode", "Ninja Clans"]
    ),
    
    "Marvel Universe": Universe(
        name="Marvel Universe",
        genre="Superhero",
        main_characters=["Spider-Man", "Iron Man", "Captain America", "Thor", "Hulk", "Black Widow"],
        locations=["New York City", "Asgard", "Wakanda", "X-Mansion", "Stark Tower", "S.H.I.E.L.D. Helicarrier"],
        themes=["Responsibility", "Heroism", "Sacrifice", "Identity", "Team Work"],
        magic_system="Superpowers, technology, magic, and cosmic forces",
        time_period="Modern era",
        world_building_elements=["Mutants", "Infinity Stones", "Multiverse", "S.H.I.E.L.D.", "Avengers"]
    )
}

def setup_universe(db_handler: UniversalDatabaseHandler, universe_name: str):
    """Setup a predefined universe in the database"""
    if universe_name in POPULAR_UNIVERSES:
        universe = POPULAR_UNIVERSES[universe_name]
        db_handler.add_universe(universe)
        logger.info(f"Added {universe_name} universe to database")
        return universe
    else:
        raise ValueError(f"Universe {universe_name} not found in predefined universes")

if __name__ == "__main__":
    # Example usage
    db = UniversalDatabaseHandler("universal_fanfiction.db")
    
    # Setup Harry Potter universe
    hp_universe = setup_universe(db, "Harry Potter")
    
    # Add sample fanfiction (you would load your actual corpus here)
    db.add_fanfiction(
        universe="Harry Potter",
        title="Sample Story",
        content="Harry walked through the corridors of Hogwarts...",
        characters=["Harry Potter", "Hermione Granger"],
        genre="Adventure",
        themes=["Friendship", "Magic"]
    )
    
    print("Universal Fanfiction Generator initialized!")
    print("Ready to generate epic 1000-chapter stories for any universe!")
import os
from typing import Optional

class Config:
    # Database settings
    DATABASE_PATH = os.getenv("DATABASE_PATH", "fanfiction.db")
    
    # LLM settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.1")
    
    # Generation settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.8"))
    TOP_P = float(os.getenv("TOP_P", "0.9"))
    
    # Text processing
    MIN_CHAPTER_LENGTH = int(os.getenv("MIN_CHAPTER_LENGTH", "500"))
    MAX_CHAPTER_LENGTH = int(os.getenv("MAX_CHAPTER_LENGTH", "5000"))
    
    # Harry Potter specific
    MAIN_CHARACTERS = [
        "Harry Potter", "Hermione Granger", "Ron Weasley", "Draco Malfoy",
        "Severus Snape", "Albus Dumbledore", "Voldemort", "Tom Riddle",
        "Ginny Weasley", "Luna Lovegood", "Neville Longbottom", "Sirius Black",
        "Remus Lupin", "James Potter", "Lily Potter", "Minerva McGonagall"
    ]
    
    HOUSES = ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff"]
    
    LOCATIONS = [
        "Hogwarts", "Diagon Alley", "Hogsmeade", "Forbidden Forest",
        "Great Hall", "Common Room", "Quidditch Pitch", "Ministry of Magic",
        "Grimmauld Place", "Burrow", "Privet Drive"
    ]
    
    MAGICAL_ELEMENTS = [
        "wand", "spell", "potion", "magic", "wizard", "witch", "muggle",
        "quidditch", "house points", "detention", "patronus", "animagus",
        "horcrux", "death eater", "order of the phoenix"
    ]
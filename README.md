# ⚡ Magical Fanfiction Generator ⚡

<div align="center">

![Harry Potter](https://img.shields.io/badge/Harry%20Potter-Fanfiction-gold?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSIjRkZENzAwIi8+Cjwvc3ZnPgo=)
![AI Powered](https://img.shields.io/badge/AI%20Powered-Ollama%20%7C%20OpenAI%20%7C%20Claude-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

**Create enchanting Harry Potter fanfiction using AI trained on your own collection of stories**

[🚀 Quick Start](#-quick-start) • [✨ Features](#-features) • [🎯 Demo](#-demo) • [📖 Documentation](#-documentation)

</div>

---

## 🌟 Overview

The **Magical Fanfiction Generator** is a comprehensive AI-powered system that analyzes your collection of Harry Potter fanfiction and generates new, original stories in the same style. With support for local AI models (Ollama), cloud APIs, and a beautiful web interface, it's the ultimate tool for fanfiction enthusiasts.

## Features

### 🧙‍♂️ Core Functionality
- **Database Analysis**: Comprehensive analysis of your fanfiction corpus
- **Character Analysis**: Identifies popular characters and their usage patterns
- **Theme Extraction**: Discovers common themes and plot elements
- **Style Analysis**: Analyzes writing patterns and narrative structures
- **Story Generation**: Creates new stories using LLM based on corpus insights

### 📊 Text Analysis
- Basic statistics (word count, readability, etc.)
- Character mention frequency and relationships
- Location and magical element extraction
- Sentiment analysis and emotional arcs
- Writing style patterns (dialogue ratio, punctuation usage, etc.)
- Plot structure analysis

### 🤖 AI Generation
- Support for OpenAI GPT and Anthropic Claude models
- Customizable story parameters (character, genre, setting, theme)
- Multi-chapter story generation
- Automatic title and summary generation
- Style consistency based on corpus analysis

### 🌐 Web Interface
- Beautiful, responsive web interface with Harry Potter theming
- Easy database upload (SQLite, CSV, JSON formats)
- Interactive story generation with real-time feedback
- Story library with preview and management
- Corpus statistics and analysis visualization

### 💻 Command Line Interface
- Database analysis mode
- Story generation mode
- Sample database creation
- Batch processing capabilities

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Download NLTK data** (will be done automatically on first run):
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
```

4. **Set up API keys** (optional, for LLM generation):
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## Usage

### Web Interface (Recommended)

1. **Start the web server**:
```bash
python main.py --mode web
```

2. **Open your browser** and go to: `http://localhost:12000`

3. **Upload your database** or create a sample database for testing

4. **Generate stories** using the interactive interface

### Command Line Interface

1. **Create a sample database** (for testing):
```bash
python main.py --create-sample
```

2. **Analyze your database**:
```bash
python main.py --mode analyze --database your_fanfiction.db
```

3. **Generate a story**:
```bash
python main.py --mode cli --database your_fanfiction.db \
    --character "Harry Potter" \
    --genre "Adventure" \
    --setting "Hogwarts" \
    --theme "discovering hidden magic" \
    --length 5000
```

## Database Format

The system supports multiple database formats:

### SQLite Database
Expected table structure (flexible column names):
- `id` - Unique identifier
- `title` - Story title
- `author` - Author name
- `content`/`text`/`story` - Main story text
- `genre` - Story genre
- `characters` - Character list
- `summary` - Story summary
- Additional metadata columns

### CSV Format
CSV file with columns similar to SQLite structure.

### JSON Format
Array of objects with story data:
```json
[
  {
    "id": 1,
    "title": "Story Title",
    "author": "Author Name",
    "content": "Story text...",
    "genre": "Adventure",
    "characters": "Harry Potter, Hermione Granger"
  }
]
```

## Configuration

Edit `config.py` to customize:

- **LLM Settings**: API keys, model names, generation parameters
- **Text Processing**: Minimum/maximum chapter lengths
- **Harry Potter Elements**: Character lists, locations, magical terms
- **Analysis Parameters**: Theme extraction settings

## API Endpoints

The web interface provides a REST API:

- `POST /upload-database` - Upload and analyze database
- `POST /generate-story` - Generate new story
- `GET /stories` - List generated stories
- `GET /story/{id}` - Get specific story
- `GET /database-info` - Get database information
- `GET /corpus-stats` - Get corpus statistics

## Example Output

The system generates complete stories with:

- **Title**: AI-generated title based on story content
- **Summary**: Compelling summary for readers
- **Multiple Chapters**: Structured narrative with proper pacing
- **Metadata**: Word count, generation parameters, etc.

Example generated story structure:
```json
{
  "title": "The Hidden Chamber's Secret",
  "summary": "When Harry discovers an ancient spell...",
  "chapters": [
    "Chapter 1 content...",
    "Chapter 2 content..."
  ],
  "metadata": {
    "chapter_count": 3,
    "estimated_word_count": 4500,
    "generation_parameters": {...}
  }
}
```

## Advanced Features

### Corpus Analysis
- Character popularity and relationship analysis
- Theme extraction using topic modeling
- Writing style pattern recognition
- Emotional arc analysis
- Similar story detection

### Generation Customization
- Character-specific voice and mannerisms
- Genre-appropriate plot structures
- Setting-specific descriptions
- Theme-consistent narrative development

### Quality Control
- Readability analysis
- Character consistency checking
- Plot coherence validation
- Style matching with corpus

## Troubleshooting

### Common Issues

1. **No API Key**: The system will use mock responses if no API keys are provided
2. **Database Format**: Ensure your database has a text column with story content
3. **Memory Issues**: For large databases, consider processing in batches
4. **Generation Errors**: Check API key validity and model availability

### Performance Tips

- Use smaller target lengths for faster generation
- Analyze corpus once and reuse results
- Consider using local models for privacy
- Batch process multiple stories

## Contributing

This system is designed to be extensible:

- Add new LLM providers in `llm_generator.py`
- Extend analysis features in `text_analyzer.py`
- Add new database formats in `database_handler.py`
- Customize UI in `templates/index.html`

## License

This project is for educational and personal use. Please respect the intellectual property rights of original fanfiction authors and the Harry Potter franchise.

## Acknowledgments

- Built for Harry Potter fanfiction enthusiasts
- Uses advanced NLP and LLM technologies
- Inspired by the creativity of the fanfiction community

---

**Note**: This system requires your own fanfiction database. The sample database is for testing purposes only. For actual use, you'll need to provide your collection of 324 Harry Potter fanfiction novels in one of the supported formats.
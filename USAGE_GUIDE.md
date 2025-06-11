# Harry Potter Fanfiction Generator - Usage Guide

## 🎯 Quick Start

### Option 1: Web Interface (Recommended)
```bash
python main.py --mode web
```
Then open: http://localhost:12000

### Option 2: Command Line
```bash
# Create sample database for testing
python main.py --create-sample

# Analyze your database
python main.py --mode analyze --database your_fanfiction.db

# Generate a story
python main.py --mode cli --database your_fanfiction.db \
    --character "Harry Potter" --genre "Adventure" \
    --setting "Hogwarts" --theme "discovering hidden magic"
```

### Option 3: Run Demo
```bash
python demo.py
```

## 📁 Database Formats Supported

### 1. SQLite Database (.db, .sqlite)
Your database should have a table with these columns (flexible names):
- `id` - Unique identifier
- `title` - Story title  
- `author` - Author name
- `content`/`text`/`story` - Main story text (REQUIRED)
- `genre` - Story genre
- `characters` - Character list
- `summary` - Story summary
- Additional metadata columns

### 2. CSV File (.csv)
```csv
id,title,author,content,genre,characters,word_count,rating,status,summary,tags
1,"Story Title","Author","Story text here...","Adventure","Harry Potter, Hermione",5000,"T","Complete","Summary","tags"
```

### 3. JSON File (.json)
```json
[
  {
    "id": 1,
    "title": "Story Title",
    "author": "Author Name", 
    "content": "Story text here...",
    "genre": "Adventure",
    "characters": "Harry Potter, Hermione Granger"
  }
]
```

## 🔧 Configuration

### API Keys (Optional)
For real LLM generation, set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

Without API keys, the system uses mock responses for demonstration.

### Custom Settings
Edit `config.py` to customize:
- Model parameters (temperature, max tokens)
- Character lists and magical elements
- Text processing settings
- Generation parameters

## 🌐 Web Interface Features

### 1. Database Upload
- Drag & drop your database file
- Automatic format detection
- Real-time analysis and feedback
- Support for SQLite, CSV, JSON

### 2. Story Generation
- Interactive parameter selection
- Character, genre, setting options
- Custom themes and length
- Real-time generation progress

### 3. Story Library
- View all generated stories
- Preview and full text display
- Download generated stories
- Story metadata and statistics

### 4. Analysis Dashboard
- Corpus statistics
- Character popularity analysis
- Theme extraction
- Writing style patterns

## 📊 Analysis Features

### Text Analysis
- **Basic Statistics**: Word count, readability, grade level
- **Character Analysis**: Mention frequency, relationships
- **Sentiment Analysis**: Emotional tone and progression
- **Style Analysis**: Dialogue ratio, punctuation patterns
- **Plot Structure**: Pacing, tension, emotional arcs

### Corpus Analysis
- **Character Popularity**: Most featured characters across corpus
- **Theme Extraction**: Common themes using topic modeling
- **Style Patterns**: Writing style consistency and variations
- **Quality Metrics**: Readability and engagement scores

## 🤖 Generation Options

### Story Parameters
- **Main Character**: Choose from popular HP characters
- **Genre**: Adventure, Romance, Mystery, Drama, etc.
- **Setting**: Hogwarts, Diagon Alley, Ministry, etc.
- **Theme**: Custom themes like "discovering hidden magic"
- **Length**: Target word count (1000-50000 words)

### AI Models
- **OpenAI GPT**: GPT-3.5-turbo, GPT-4 (requires API key)
- **Anthropic Claude**: Claude-3 models (requires API key)
- **Mock Mode**: Demo responses without API keys

### Generation Quality
The system uses your corpus analysis to:
- Match writing style patterns
- Include popular characters appropriately
- Follow common plot structures
- Maintain thematic consistency
- Generate authentic dialogue

## 📈 Best Practices

### Database Preparation
1. **Clean Text**: Ensure story content is clean and readable
2. **Consistent Format**: Use consistent column names and data types
3. **Rich Metadata**: Include genre, character, and tag information
4. **Quality Content**: Higher quality input = better generation

### Generation Tips
1. **Start Small**: Begin with shorter stories (2000-5000 words)
2. **Specific Themes**: Use specific, descriptive themes
3. **Character Focus**: Choose characters well-represented in your corpus
4. **Iterative Refinement**: Generate multiple versions and refine

### Analysis Insights
1. **Character Popularity**: Focus on well-represented characters
2. **Theme Trends**: Use popular themes from your corpus
3. **Style Matching**: Match the average style metrics
4. **Quality Benchmarks**: Aim for similar readability scores

## 🔍 Troubleshooting

### Common Issues

**"No text column found"**
- Ensure your database has a column named: content, text, story, body, or novel
- Check that the column contains actual story text, not just metadata

**"Generation failed"**
- Verify API keys are set correctly
- Check internet connection for API calls
- Try using mock mode first (no API key needed)

**"Database upload failed"**
- Verify file format (SQLite, CSV, or JSON)
- Check file size (large files may take time)
- Ensure proper encoding (UTF-8 recommended)

**"Low quality generation"**
- Use larger, higher-quality corpus
- Provide more specific generation parameters
- Try different AI models
- Increase target length for better development

### Performance Tips
- **Large Databases**: Process in batches for very large corpora
- **Memory Usage**: Close other applications for large analyses
- **Generation Speed**: Shorter stories generate faster
- **API Limits**: Be aware of API rate limits and costs

## 📚 Example Workflows

### Workflow 1: First-Time User
1. Run `python demo.py` to see all features
2. Create sample database with `--create-sample`
3. Start web interface and explore
4. Upload your own database when ready

### Workflow 2: Researcher/Analyst
1. Upload large fanfiction corpus
2. Run comprehensive analysis
3. Export statistics and insights
4. Use findings to guide generation parameters

### Workflow 3: Story Generator
1. Upload curated, high-quality corpus
2. Analyze popular characters and themes
3. Generate multiple stories with different parameters
4. Refine based on quality and preferences

### Workflow 4: Developer/Customizer
1. Modify `config.py` for custom settings
2. Extend analysis features in `text_analyzer.py`
3. Add new generation prompts in `llm_generator.py`
4. Customize web interface in `templates/`

## 🎨 Customization

### Adding New Characters
Edit `config.py`:
```python
MAIN_CHARACTERS = [
    "Harry Potter", "Hermione Granger", 
    "Your Custom Character"
]
```

### Custom Analysis Features
Extend `TextAnalyzer` class:
```python
def custom_analysis(self, text):
    # Your custom analysis logic
    return results
```

### New Generation Prompts
Add to `PromptTemplates`:
```python
@staticmethod
def custom_prompt(parameters):
    return f"Custom prompt with {parameters}"
```

## 📞 Support

### Getting Help
1. Check this usage guide first
2. Review the README.md for setup instructions
3. Run the demo script to verify installation
4. Check the generated log files for error details

### Contributing
The system is designed to be extensible:
- Add new LLM providers
- Extend analysis capabilities
- Improve generation quality
- Enhance the web interface

---

**Happy Fanfiction Generating! 🪄✨**
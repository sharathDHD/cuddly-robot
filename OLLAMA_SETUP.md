# Setting Up Ollama with Llama 3.1 for Fanfiction Generation

## 🚀 Quick Setup Guide

### Step 1: Install Ollama

**On Linux/macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**On Windows:**
Download from: https://ollama.ai/download

### Step 2: Start Ollama Server
```bash
ollama serve
```
*Keep this terminal open - Ollama needs to run in the background*

### Step 3: Pull Llama 3.1 Model
In a new terminal:
```bash
# For 8B model (recommended, ~4.7GB download)
ollama pull llama3.1:8b

# Or for larger 70B model (if you have lots of RAM, ~40GB download)
ollama pull llama3.1:70b

# Or latest version
ollama pull llama3.1
```

### Step 4: Test Ollama
```bash
# Test the model
ollama run llama3.1:8b "Write a short Harry Potter story"
```

### Step 5: Run the Fanfiction Generator
```bash
python working_fanfic_generator.py
```

## 🎯 Your Database Analysis Results

Based on your `novel_data.db`, I've successfully extracted and analyzed:

- **324 novels** in the database
- **20 chapters** successfully extracted for analysis
- **Average 1,379 words per chapter**
- **Readability score: 71.4** (good readability)
- **Grade level: 6.8** (accessible writing)

### Top Characters Found:
1. **Albus Dumbledore** - 22 mentions
2. **Sirius Black** - 15 mentions  
3. **Minerva McGonagall** - 13 mentions
4. **Severus Snape** - 10 mentions
5. **Ron Weasley** - 7 mentions

### Story Themes:
Your database appears to contain stories with original characters (Truman, Nutley) alongside canonical HP characters, suggesting a mix of OC-focused and canon-compliant fanfiction.

## 🛠️ Troubleshooting

### Ollama Won't Start
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

### Model Download Issues
```bash
# Check available models
ollama list

# Re-download if needed
ollama pull llama3.1:8b
```

### Memory Issues
- **Llama 3.1 8B**: Needs ~8GB RAM
- **Llama 3.1 70B**: Needs ~40GB RAM
- Use the 8B model for most systems

### Generation Too Slow
- Use shorter target lengths (1000-2000 words)
- Try the 8B model instead of 70B
- Ensure no other heavy applications are running

## 🎨 Customizing Generation

### Model Selection
Edit the model name in the generator:
```python
# In working_fanfic_generator.py, you can specify:
model_name = "llama3.1:8b"      # Fast, good quality
model_name = "llama3.1:70b"     # Slower, higher quality
model_name = "llama3.1"         # Latest version
```

### Generation Parameters
Modify these in the script:
```python
parameters = {
    'main_character': 'Harry Potter',  # Or any HP character
    'genre': 'Adventure',              # Adventure, Romance, Mystery, etc.
    'setting': 'Hogwarts',            # Hogwarts, Diagon Alley, etc.
    'theme': 'discovering hidden magical powers',
    'target_length': 2500             # Words (1000-5000 recommended)
}
```

### Popular Characters from Your Database
Based on analysis, these characters work well:
- Albus Dumbledore
- Sirius Black
- Minerva McGonagall
- Severus Snape
- Ron Weasley
- Ginny Weasley

## 📊 Advanced Usage

### Extract More Chapters
To analyze more of your database:
```python
# In the extraction script, increase the limit:
cursor.execute('SELECT id FROM chapters LIMIT 500')  # More chapters
```

### Web Interface with Ollama
Start the web interface:
```bash
python main.py --mode web
```
Then select "Ollama (Local)" in the model dropdown.

### Command Line Generation
```bash
python main.py --mode cli \
    --database novel_data.db \
    --character "Sirius Black" \
    --genre "Adventure" \
    --setting "Grimmauld Place" \
    --theme "uncovering family secrets" \
    --model-type ollama \
    --model-name llama3.1:8b
```

## 🎉 Expected Results

With Ollama and your database, you should get:

1. **High-quality stories** that match your corpus style
2. **Character consistency** based on your database patterns
3. **Thematic coherence** reflecting your collection's themes
4. **Appropriate length** (2000-5000 words typically)
5. **Local generation** (no API keys needed)

## 💡 Tips for Best Results

1. **Use specific themes**: "discovering ancient magic" works better than just "magic"
2. **Choose popular characters**: Characters with more mentions in your corpus generate better
3. **Reasonable lengths**: 2000-3000 words for best quality
4. **Multiple generations**: Generate several stories and pick the best
5. **Edit and refine**: Use the generated story as a starting point

## 🔧 System Requirements

- **RAM**: 8GB minimum for Llama 3.1 8B
- **Storage**: 5GB for model download
- **CPU**: Modern multi-core processor recommended
- **OS**: Linux, macOS, or Windows

---

**Ready to generate amazing Harry Potter fanfiction with your own database! 🪄✨**
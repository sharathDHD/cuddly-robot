import openai
import anthropic
import requests
from typing import List, Dict, Any, Optional
import json
import random
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMGenerator:
    def __init__(self, model_type: str = "openai", model_name: str = None):
        self.model_type = model_type
        self.model_name = model_name or Config.DEFAULT_MODEL
        
        if model_type == "openai":
            if not Config.OPENAI_API_KEY:
                logger.warning("OpenAI API key not found. Using mock responses.")
                self.client = None
            else:
                openai.api_key = Config.OPENAI_API_KEY
                self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        elif model_type == "anthropic":
            if not Config.ANTHROPIC_API_KEY:
                logger.warning("Anthropic API key not found. Using mock responses.")
                self.client = None
            else:
                self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        elif model_type == "ollama":
            self.ollama_url = Config.OLLAMA_URL
            self.client = "ollama"
            logger.info(f"Using Ollama with model: {self.model_name}")
            # Test Ollama connection
            try:
                self._test_ollama_connection()
            except Exception as e:
                logger.error(f"Failed to connect to Ollama: {e}")
                self.client = None
    
    def _test_ollama_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                logger.info(f"Available Ollama models: {model_names}")
                
                # Check if our model is available
                if not any(self.model_name in name for name in model_names):
                    logger.warning(f"Model {self.model_name} not found. Available: {model_names}")
                    # Try to pull the model
                    self._pull_ollama_model()
            else:
                raise Exception(f"Ollama server returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Cannot connect to Ollama server at {self.ollama_url}: {e}")
    
    def _pull_ollama_model(self):
        """Pull the specified model in Ollama"""
        logger.info(f"Attempting to pull model: {self.model_name}")
        try:
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": self.model_name},
                timeout=300  # 5 minutes timeout for model download
            )
            if response.status_code == 200:
                logger.info(f"Successfully pulled model: {self.model_name}")
            else:
                logger.error(f"Failed to pull model: {response.text}")
        except Exception as e:
            logger.error(f"Error pulling model: {e}")

    def generate_text(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """Generate text using the specified LLM"""
        max_tokens = max_tokens or Config.MAX_TOKENS
        temperature = temperature or Config.TEMPERATURE
        
        if not self.client:
            return self._mock_response(prompt)
        
        try:
            if self.model_type == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=Config.TOP_P
                )
                return response.choices[0].message.content
            
            elif self.model_type == "anthropic":
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif self.model_type == "ollama":
                return self._generate_ollama(prompt, max_tokens, temperature)
                
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return self._mock_response(prompt)
    
    def _generate_ollama(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text using Ollama"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": Config.TOP_P
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120  # 2 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return self._mock_response(prompt)
                
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Generate a mock response when API is not available"""
        mock_responses = [
            "Harry Potter stood at the edge of the Forbidden Forest, his heart pounding with anticipation...",
            "The Great Hall was unusually quiet that morning, as if the very walls of Hogwarts were holding their breath...",
            "Hermione's eyes widened as she discovered the ancient spell hidden within the dusty tome...",
            "The sorting hat seemed to whisper secrets that only Harry could hear...",
            "In the depths of the dungeons, Severus Snape contemplated the choices that had led him here..."
        ]
        return random.choice(mock_responses)

class FanfictionGenerator:
    def __init__(self, llm_generator: LLMGenerator, corpus_analysis: Dict[str, Any]):
        self.llm = llm_generator
        self.corpus_analysis = corpus_analysis
        
    def generate_story_outline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a story outline based on parameters"""
        prompt = self._create_outline_prompt(parameters)
        outline_text = self.llm.generate_text(prompt, max_tokens=1000)
        
        return {
            'outline': outline_text,
            'parameters': parameters,
            'estimated_length': parameters.get('target_length', 5000)
        }
    
    def generate_chapter(self, outline: Dict[str, Any], chapter_number: int, 
                        previous_chapters: List[str] = None) -> str:
        """Generate a single chapter"""
        prompt = self._create_chapter_prompt(outline, chapter_number, previous_chapters)
        chapter_text = self.llm.generate_text(prompt, max_tokens=Config.MAX_CHAPTER_LENGTH)
        
        return chapter_text
    
    def generate_full_story(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete fanfiction story"""
        # Generate outline
        outline = self.generate_story_outline(parameters)
        
        # Determine number of chapters
        target_length = parameters.get('target_length', 5000)
        chapter_count = max(1, target_length // Config.MAX_CHAPTER_LENGTH)
        
        # Generate chapters
        chapters = []
        for i in range(chapter_count):
            chapter = self.generate_chapter(outline, i + 1, chapters)
            chapters.append(chapter)
            logger.info(f"Generated chapter {i + 1}/{chapter_count}")
        
        # Generate title and summary
        title = self.generate_title(outline, chapters)
        summary = self.generate_summary(outline, chapters)
        
        return {
            'title': title,
            'summary': summary,
            'outline': outline,
            'chapters': chapters,
            'metadata': {
                'chapter_count': len(chapters),
                'estimated_word_count': sum(len(ch.split()) for ch in chapters),
                'generation_parameters': parameters
            }
        }
    
    def _create_outline_prompt(self, parameters: Dict[str, Any]) -> str:
        """Create prompt for story outline generation"""
        main_character = parameters.get('main_character', 'Harry Potter')
        genre = parameters.get('genre', 'Adventure')
        setting = parameters.get('setting', 'Hogwarts')
        theme = parameters.get('theme', 'friendship and courage')
        
        # Use corpus analysis to inform the prompt
        popular_characters = self._get_popular_characters()
        common_themes = self._get_common_themes()
        
        prompt = f"""
        Create a detailed outline for a Harry Potter fanfiction story with the following parameters:
        
        Main Character: {main_character}
        Genre: {genre}
        Setting: {setting}
        Theme: {theme}
        
        Based on analysis of 324 similar fanfiction stories, popular elements include:
        - Characters: {', '.join(popular_characters[:5])}
        - Common themes: {', '.join(common_themes[:3])}
        
        Please create a compelling story outline that includes:
        1. A brief premise (2-3 sentences)
        2. Main plot points (5-7 key events)
        3. Character development arc for the protagonist
        4. Conflict and resolution
        5. Emotional journey
        
        The story should feel authentic to the Harry Potter universe while offering something fresh and engaging.
        """
        
        return prompt
    
    def _create_chapter_prompt(self, outline: Dict[str, Any], chapter_number: int, 
                              previous_chapters: List[str] = None) -> str:
        """Create prompt for chapter generation"""
        outline_text = outline['outline']
        parameters = outline['parameters']
        
        context = ""
        if previous_chapters:
            # Summarize previous chapters for context
            last_chapter = previous_chapters[-1]
            context = f"\nPrevious chapter summary: {last_chapter[:500]}..."
        
        prompt = f"""
        Write Chapter {chapter_number} of a Harry Potter fanfiction story.
        
        Story Outline:
        {outline_text}
        
        Story Parameters:
        - Main Character: {parameters.get('main_character', 'Harry Potter')}
        - Genre: {parameters.get('genre', 'Adventure')}
        - Setting: {parameters.get('setting', 'Hogwarts')}
        {context}
        
        Chapter Requirements:
        - Length: {Config.MIN_CHAPTER_LENGTH}-{Config.MAX_CHAPTER_LENGTH} words
        - Include dialogue and character interactions
        - Advance the plot meaningfully
        - Maintain consistent characterization
        - Use vivid descriptions of magical elements
        - End with a hook for the next chapter (if not the final chapter)
        
        Write the chapter in a style consistent with Harry Potter fanfiction, focusing on:
        - Rich magical atmosphere
        - Character development
        - Engaging dialogue
        - Descriptive but not overly verbose prose
        """
        
        return prompt
    
    def generate_title(self, outline: Dict[str, Any], chapters: List[str]) -> str:
        """Generate a title for the story"""
        first_chapter = chapters[0] if chapters else ""
        outline_text = outline['outline']
        
        prompt = f"""
        Generate a compelling title for this Harry Potter fanfiction story.
        
        Story Outline:
        {outline_text[:500]}...
        
        First Chapter Opening:
        {first_chapter[:300]}...
        
        The title should be:
        - Evocative and memorable
        - Relevant to the story's themes
        - Appropriate for the Harry Potter universe
        - Between 2-6 words
        
        Provide only the title, nothing else.
        """
        
        return self.llm.generate_text(prompt, max_tokens=50)
    
    def generate_summary(self, outline: Dict[str, Any], chapters: List[str]) -> str:
        """Generate a summary for the story"""
        outline_text = outline['outline']
        
        prompt = f"""
        Write a compelling summary for this Harry Potter fanfiction story.
        
        Story Outline:
        {outline_text}
        
        The summary should be:
        - 2-3 paragraphs long
        - Engaging and intriguing without spoiling major plot points
        - Written in third person
        - Highlighting the main conflict and stakes
        - Appealing to Harry Potter fans
        
        Write the summary:
        """
        
        return self.llm.generate_text(prompt, max_tokens=300)
    
    def _get_popular_characters(self) -> List[str]:
        """Get popular characters from corpus analysis"""
        if 'character_analysis' in self.corpus_analysis:
            char_analysis = self.corpus_analysis['character_analysis']
            # Sort by popularity score
            sorted_chars = sorted(char_analysis.items(), 
                                key=lambda x: x[1].get('popularity_score', 0), 
                                reverse=True)
            return [char for char, _ in sorted_chars]
        return Config.MAIN_CHARACTERS
    
    def _get_common_themes(self) -> List[str]:
        """Get common themes from corpus analysis"""
        if 'themes' in self.corpus_analysis and 'topics' in self.corpus_analysis['themes']:
            topics = self.corpus_analysis['themes']['topics']
            theme_words = []
            for topic in topics[:3]:  # Top 3 topics
                theme_words.extend(topic['words'][:3])  # Top 3 words per topic
            return theme_words
        return ['friendship', 'magic', 'adventure', 'love', 'courage']

class PromptTemplates:
    """Collection of prompt templates for different types of generation"""
    
    @staticmethod
    def character_development_prompt(character_name: str, story_context: str) -> str:
        return f"""
        Develop the character of {character_name} in the context of this story:
        
        {story_context}
        
        Consider:
        - Their motivations and goals
        - Internal conflicts
        - Relationships with other characters
        - Growth arc throughout the story
        - Unique voice and mannerisms
        
        Provide a detailed character development plan.
        """
    
    @staticmethod
    def dialogue_generation_prompt(characters: List[str], situation: str, tone: str) -> str:
        return f"""
        Write a dialogue scene between {', '.join(characters)} in the following situation:
        
        Situation: {situation}
        Tone: {tone}
        
        Requirements:
        - Each character should have a distinct voice
        - Include action beats and descriptions
        - Advance the plot or reveal character
        - Stay true to Harry Potter universe characterizations
        - Length: 200-400 words
        """
    
    @staticmethod
    def scene_description_prompt(location: str, mood: str, time_of_day: str) -> str:
        return f"""
        Write a vivid scene description for:
        
        Location: {location}
        Mood: {mood}
        Time: {time_of_day}
        
        Include:
        - Sensory details (sight, sound, smell, touch)
        - Magical elements appropriate to the Harry Potter universe
        - Atmosphere that supports the mood
        - Details that could be relevant to plot
        - Length: 150-250 words
        """

if __name__ == "__main__":
    # Test the generator
    llm = LLMGenerator(model_type="openai")
    
    # Mock corpus analysis for testing
    mock_analysis = {
        'character_analysis': {
            'Harry Potter': {'popularity_score': 0.9},
            'Hermione Granger': {'popularity_score': 0.8},
            'Draco Malfoy': {'popularity_score': 0.7}
        },
        'themes': {
            'topics': [
                {'words': ['friendship', 'loyalty', 'trust']},
                {'words': ['magic', 'power', 'spell']},
                {'words': ['love', 'romance', 'relationship']}
            ]
        }
    }
    
    generator = FanfictionGenerator(llm, mock_analysis)
    
    parameters = {
        'main_character': 'Harry Potter',
        'genre': 'Adventure',
        'setting': 'Hogwarts',
        'theme': 'discovering hidden magic',
        'target_length': 3000
    }
    
    outline = generator.generate_story_outline(parameters)
    print("Generated Outline:")
    print(outline['outline'])
import re
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
import textstat
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextAnalyzer:
    def __init__(self):
        self.download_nltk_data()
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        
    def download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
    
    def extract_basic_stats(self, text: str) -> Dict[str, Any]:
        """Extract basic statistics from text"""
        if not text:
            return {}
            
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())
        words_no_punct = [word for word in words if word.isalnum()]
        
        return {
            'word_count': len(words_no_punct),
            'sentence_count': len(sentences),
            'character_count': len(text),
            'avg_words_per_sentence': len(words_no_punct) / len(sentences) if sentences else 0,
            'avg_sentence_length': len(text) / len(sentences) if sentences else 0,
            'readability_score': textstat.flesch_reading_ease(text),
            'grade_level': textstat.flesch_kincaid_grade(text)
        }
    
    def extract_characters(self, text: str, known_characters: List[str]) -> Dict[str, int]:
        """Extract character mentions from text"""
        character_counts = {}
        text_lower = text.lower()
        
        for character in known_characters:
            # Count full name matches
            full_name_count = len(re.findall(r'\b' + re.escape(character.lower()) + r'\b', text_lower))
            
            # Count last name matches (for characters with multiple names)
            if ' ' in character:
                last_name = character.split()[-1]
                last_name_count = len(re.findall(r'\b' + re.escape(last_name.lower()) + r'\b', text_lower))
                character_counts[character] = max(full_name_count, last_name_count)
            else:
                character_counts[character] = full_name_count
                
        return {char: count for char, count in character_counts.items() if count > 0}
    
    def extract_locations(self, text: str, known_locations: List[str]) -> Dict[str, int]:
        """Extract location mentions from text"""
        location_counts = {}
        text_lower = text.lower()
        
        for location in known_locations:
            count = len(re.findall(r'\b' + re.escape(location.lower()) + r'\b', text_lower))
            if count > 0:
                location_counts[location] = count
                
        return location_counts
    
    def extract_magical_elements(self, text: str, magical_terms: List[str]) -> Dict[str, int]:
        """Extract magical elements from text"""
        magic_counts = {}
        text_lower = text.lower()
        
        for term in magical_terms:
            count = len(re.findall(r'\b' + re.escape(term.lower()) + r'\b', text_lower))
            if count > 0:
                magic_counts[term] = count
                
        return magic_counts
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of the text"""
        scores = self.sia.polarity_scores(text)
        return {
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'compound': scores['compound']
        }
    
    def extract_themes(self, texts: List[str], n_topics: int = 5) -> Dict[str, Any]:
        """Extract themes using topic modeling"""
        if not texts:
            return {}
            
        # Preprocess texts
        processed_texts = []
        for text in texts:
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalnum() and word not in self.stop_words]
            processed_texts.append(' '.join(words))
        
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(processed_texts)
        
        # Topic modeling with LDA
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        lda.fit(tfidf_matrix)
        
        # Extract topics
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        
        for topic_idx, topic in enumerate(lda.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topics.append({
                'topic_id': topic_idx,
                'words': top_words,
                'weights': [topic[i] for i in top_words_idx]
            })
        
        return {
            'topics': topics,
            'model': lda,
            'vectorizer': vectorizer
        }
    
    def analyze_writing_style(self, text: str) -> Dict[str, Any]:
        """Analyze writing style characteristics"""
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        # Sentence length distribution
        sentence_lengths = [len(word_tokenize(sent)) for sent in sentences]
        
        # Punctuation analysis
        punctuation_counts = {
            'exclamation': text.count('!'),
            'question': text.count('?'),
            'comma': text.count(','),
            'semicolon': text.count(';'),
            'colon': text.count(':'),
            'dash': text.count('--') + text.count('—'),
            'ellipsis': text.count('...') + text.count('…')
        }
        
        # Dialogue analysis
        dialogue_pattern = r'"[^"]*"'
        dialogue_matches = re.findall(dialogue_pattern, text)
        dialogue_ratio = len(''.join(dialogue_matches)) / len(text) if text else 0
        
        # Paragraph analysis
        paragraphs = text.split('\n\n')
        paragraph_lengths = [len(para.split()) for para in paragraphs if para.strip()]
        
        return {
            'avg_sentence_length': np.mean(sentence_lengths) if sentence_lengths else 0,
            'sentence_length_std': np.std(sentence_lengths) if sentence_lengths else 0,
            'punctuation_density': sum(punctuation_counts.values()) / len(words) if words else 0,
            'punctuation_breakdown': punctuation_counts,
            'dialogue_ratio': dialogue_ratio,
            'avg_paragraph_length': np.mean(paragraph_lengths) if paragraph_lengths else 0,
            'paragraph_count': len(paragraph_lengths)
        }
    
    def find_similar_stories(self, target_text: str, corpus_texts: List[str], n_similar: int = 5) -> List[Tuple[int, float]]:
        """Find similar stories using TF-IDF similarity"""
        if not corpus_texts:
            return []
            
        all_texts = [target_text] + corpus_texts
        
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Calculate cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Get top similar stories
        similar_indices = similarities.argsort()[-n_similar:][::-1]
        similar_scores = similarities[similar_indices]
        
        return list(zip(similar_indices, similar_scores))
    
    def extract_plot_structure(self, text: str) -> Dict[str, Any]:
        """Analyze plot structure and pacing"""
        sentences = sent_tokenize(text)
        
        # Divide text into sections for pacing analysis
        section_size = len(sentences) // 5 if len(sentences) >= 5 else 1
        sections = [sentences[i:i+section_size] for i in range(0, len(sentences), section_size)]
        
        section_analysis = []
        for i, section in enumerate(sections):
            section_text = ' '.join(section)
            sentiment = self.analyze_sentiment(section_text)
            
            section_analysis.append({
                'section': i + 1,
                'sentence_count': len(section),
                'word_count': len(word_tokenize(section_text)),
                'sentiment': sentiment,
                'tension_indicators': self.count_tension_words(section_text)
            })
        
        return {
            'total_sections': len(sections),
            'section_analysis': section_analysis,
            'overall_arc': self.analyze_emotional_arc(section_analysis)
        }
    
    def count_tension_words(self, text: str) -> int:
        """Count words that indicate tension or action"""
        tension_words = [
            'suddenly', 'quickly', 'rushed', 'panic', 'fear', 'danger', 'urgent',
            'immediately', 'frantically', 'desperately', 'shocked', 'surprised',
            'gasped', 'screamed', 'shouted', 'whispered', 'trembled', 'shaking'
        ]
        
        text_lower = text.lower()
        count = 0
        for word in tension_words:
            count += len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))
        
        return count
    
    def analyze_emotional_arc(self, section_analysis: List[Dict]) -> Dict[str, Any]:
        """Analyze the emotional arc of the story"""
        sentiments = [section['sentiment']['compound'] for section in section_analysis]
        
        # Find peaks and valleys
        peaks = []
        valleys = []
        
        for i in range(1, len(sentiments) - 1):
            if sentiments[i] > sentiments[i-1] and sentiments[i] > sentiments[i+1]:
                peaks.append(i)
            elif sentiments[i] < sentiments[i-1] and sentiments[i] < sentiments[i+1]:
                valleys.append(i)
        
        return {
            'sentiment_progression': sentiments,
            'emotional_peaks': peaks,
            'emotional_valleys': valleys,
            'overall_trend': 'positive' if sentiments[-1] > sentiments[0] else 'negative',
            'volatility': np.std(sentiments) if sentiments else 0
        }

class CorpusAnalyzer:
    """Analyze a corpus of fanfiction texts"""
    
    def __init__(self, text_analyzer: TextAnalyzer):
        self.analyzer = text_analyzer
    
    def analyze_corpus(self, df: pd.DataFrame, text_column: str = 'content') -> Dict[str, Any]:
        """Comprehensive analysis of the entire corpus"""
        if df.empty or text_column not in df.columns:
            return {}
        
        texts = df[text_column].dropna().tolist()
        
        # Basic statistics
        basic_stats = []
        for text in texts:
            stats = self.analyzer.extract_basic_stats(text)
            basic_stats.append(stats)
        
        stats_df = pd.DataFrame(basic_stats)
        
        # Character analysis
        from config import Config
        character_analysis = self.analyze_character_usage(texts, Config.MAIN_CHARACTERS)
        
        # Theme extraction
        theme_analysis = self.analyzer.extract_themes(texts)
        
        # Writing style patterns
        style_patterns = self.analyze_style_patterns(texts)
        
        return {
            'corpus_size': len(texts),
            'basic_statistics': {
                'avg_word_count': stats_df['word_count'].mean(),
                'avg_readability': stats_df['readability_score'].mean(),
                'avg_grade_level': stats_df['grade_level'].mean(),
                'word_count_distribution': stats_df['word_count'].describe().to_dict()
            },
            'character_analysis': character_analysis,
            'themes': theme_analysis,
            'style_patterns': style_patterns
        }
    
    def analyze_character_usage(self, texts: List[str], characters: List[str]) -> Dict[str, Any]:
        """Analyze character usage across the corpus"""
        character_stats = defaultdict(list)
        
        for text in texts:
            char_counts = self.analyzer.extract_characters(text, characters)
            for char in characters:
                character_stats[char].append(char_counts.get(char, 0))
        
        character_summary = {}
        for char, counts in character_stats.items():
            character_summary[char] = {
                'total_mentions': sum(counts),
                'stories_featured': sum(1 for count in counts if count > 0),
                'avg_mentions_per_story': np.mean([c for c in counts if c > 0]) if any(counts) else 0,
                'popularity_score': sum(1 for count in counts if count > 0) / len(counts)
            }
        
        return character_summary
    
    def analyze_style_patterns(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze writing style patterns across the corpus"""
        style_stats = []
        
        for text in texts:
            style = self.analyzer.analyze_writing_style(text)
            style_stats.append(style)
        
        style_df = pd.DataFrame(style_stats)
        
        return {
            'avg_sentence_length': style_df['avg_sentence_length'].mean(),
            'dialogue_usage': style_df['dialogue_ratio'].mean(),
            'punctuation_patterns': {
                'exclamation_usage': style_df['punctuation_breakdown'].apply(lambda x: x['exclamation']).mean(),
                'question_usage': style_df['punctuation_breakdown'].apply(lambda x: x['question']).mean(),
                'ellipsis_usage': style_df['punctuation_breakdown'].apply(lambda x: x['ellipsis']).mean()
            }
        }

if __name__ == "__main__":
    # Test the analyzer
    analyzer = TextAnalyzer()
    
    sample_text = """
    Harry Potter walked through the corridors of Hogwarts, his wand clutched tightly in his hand. 
    The castle felt different somehow, as if magic itself was holding its breath. 
    "Hermione," he whispered, "do you feel that?"
    She nodded, her bushy hair catching the torchlight. "Something's not right, Harry."
    """
    
    stats = analyzer.extract_basic_stats(sample_text)
    print("Basic Stats:", stats)
    
    from config import Config
    characters = analyzer.extract_characters(sample_text, Config.MAIN_CHARACTERS)
    print("Characters:", characters)
    
    sentiment = analyzer.analyze_sentiment(sample_text)
    print("Sentiment:", sentiment)
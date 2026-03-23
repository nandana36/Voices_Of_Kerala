"""
Malayalam Dialect Translation System - Optimized Backend
=========================================================
Memory-optimized version with:
- Lazy loading (models load only when needed)
- Google Speech Recognition (no Whisper)
- Fuzzy matching
- Smart caching
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
import speech_recognition as sr
import warnings
warnings.filterwarnings('ignore')

# Optional: Only load if needed
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass


# ============================================================
# CONFIGURATION
# ============================================================

class Config:
    """System configuration"""
    DATA_DIR = "malayalam_data"
    IMAGES_DIR = "images"
    LOOKUP_FILE = "lookup.json"
    CONCEPTS_FILE = "concepts.json"
    IMAGES_FILE = "images.json"
    
    # Fuzzy matching
    FUZZY_MATCH_THRESHOLD = 0.7
    
    # LLM settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-flash-latest"  # Best model - works and accurate!


# ============================================================
# FUZZY MATCHER
# ============================================================

class FuzzyMatcher:
    """Handles fuzzy matching for similar words"""
    
    def __init__(self, threshold: float = Config.FUZZY_MATCH_THRESHOLD):
        self.threshold = threshold
    
    def find_similar_word(self, input_word: str, database: Dict) -> Tuple[Optional[str], float]:
        """Find most similar word in database"""
        best_match = None
        best_score = 0.0
        
        for db_word in database.keys():
            similarity = SequenceMatcher(None, input_word, db_word).ratio()
            
            if similarity > best_score:
                best_score = similarity
                best_match = db_word
        
        if best_score >= self.threshold:
            print(f"🔍 Fuzzy match: '{input_word}' → '{best_match}' ({best_score:.1%})")
            return best_match, best_score
        
        return None, 0.0
    
    def get_suggestions(self, input_word: str, database: Dict, top_n: int = 3) -> List[Tuple[str, float]]:
        """Get top N similar words"""
        similarities = []
        
        for db_word in database.keys():
            similarity = SequenceMatcher(None, input_word, db_word).ratio()
            similarities.append((db_word, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]


# ============================================================
# DATA MANAGER
# ============================================================

class DataManager:
    """Manages JSON file operations"""
    
    def __init__(self):
        self.data_dir = Config.DATA_DIR  # ADD THIS LINE!
        self.lookup_path = os.path.join(Config.DATA_DIR, Config.LOOKUP_FILE)
        self.concepts_path = os.path.join(Config.DATA_DIR, Config.CONCEPTS_FILE)
        self.images_path = os.path.join(Config.DATA_DIR, Config.IMAGES_FILE)
        
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.IMAGES_DIR, exist_ok=True)
        
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files with sample data"""
        sample_lookup = {
            "ഒമക്കായ": {"region": "south", "concept": "papaya"},
            "കപ്പളങ്ങ": {"region": "central", "concept": "papaya"},
            "പപ്പായ": {"region": "north", "concept": "papaya"},
            "മുല്ലപെരുക്ക": {"region": "south", "concept": "chilli"},
            "മുളക്": {"region": "central", "concept": "chilli"}
        }
        
        sample_concepts = {
            "papaya": {
                "english": "Papaya",
                "south": ["ഒമക്കായ"],
                "central": ["കപ്പളങ്ങ"],
                "north": ["പപ്പായ"]
            },
            "chilli": {
                "english": "Chilli",
                "south": ["മുല്ലപെരുക്ക"],
                "central": ["മുളക്"],
                "north": ["മുളക്"]
            }
        }
        
        sample_images = {
            "papaya": "images/papaya.jpg",
            "chilli": "images/chilli.jpg"
        }
        
        if not os.path.exists(self.lookup_path):
            self.save_lookup(sample_lookup)
        if not os.path.exists(self.concepts_path):
            self.save_concepts(sample_concepts)
        if not os.path.exists(self.images_path):
            self.save_images(sample_images)
    
    def load_lookup(self) -> Dict:
        with open(self.lookup_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_concepts(self) -> Dict:
        with open(self.concepts_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_images(self) -> Dict:
        with open(self.images_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_lookup(self, data: Dict):
        with open(self.lookup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_concepts(self, data: Dict):
        with open(self.concepts_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_images(self, data: Dict):
        with open(self.images_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_to_pending(self, word: str, data: Dict):
        """Save LLM-generated word to pending review - NOT directly to database"""
        from datetime import datetime
        
        try:
            pending_file = os.path.join(self.data_dir, "pending_review.json")
            
            print(f"🔍 DEBUG: Attempting to save to: {pending_file}")
            print(f"🔍 DEBUG: Word: {word}")
            print(f"🔍 DEBUG: Data: {data}")
            
            # Load existing pending words
            if os.path.exists(pending_file):
                with open(pending_file, 'r', encoding='utf-8') as f:
                    pending = json.load(f)
                print(f"🔍 DEBUG: Loaded existing pending with {len(pending)} items")
            else:
                pending = {}
                print(f"🔍 DEBUG: Creating new pending file")
            
            # Add new word with metadata
            pending[word] = {
                'english': data.get('english', ''),
                'south': data.get('south', [word]),
                'central': data.get('central', [word]),
                'north': data.get('north', [word]),
                'food_type': data.get('food_type', 'unknown'),
                'source': 'llm_generated',
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"🔍 DEBUG: Now pending has {len(pending)} items")
            
            # Save to pending_review.json
            with open(pending_file, 'w', encoding='utf-8') as f:
                json.dump(pending, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Saved '{word}' to pending_review.json (awaiting admin approval)")
            print(f"✅ File written successfully!")
            
            # Verify it was written
            if os.path.exists(pending_file):
                with open(pending_file, 'r', encoding='utf-8') as f:
                    verify = json.load(f)
                if word in verify:
                    print(f"✅ VERIFIED: '{word}' is in the file!")
                else:
                    print(f"❌ WARNING: '{word}' NOT found after save!")
            
        except Exception as e:
            print(f"❌ ERROR in save_to_pending: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def add_new_entry(self, word: str, region: str, concept: str,
                      translations: Dict, image_path: Optional[str] = None):
        """Add new entry to all data files"""
        lookup = self.load_lookup()
        lookup[word] = {"region": region, "concept": concept}
        self.save_lookup(lookup)
        
        concepts = self.load_concepts()
        if concept not in concepts:
            concepts[concept] = translations
        self.save_concepts(concepts)
        
        if image_path:
            images = self.load_images()
            images[concept] = image_path
            self.save_images(images)


# ============================================================
# SPEECH-TO-TEXT - GOOGLE (LIGHTWEIGHT!)
# ============================================================

class SpeechToText:
    """Google Speech Recognition - no heavy models needed!"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        print("✅ Google Speech Recognition ready!")
    
    def transcribe(self, audio_path: str) -> str:
        """Transcribe audio to Malayalam text"""
        try:
            if not os.path.exists(audio_path):
                print(f"❌ File not found: {audio_path}")
                return ""
            
            with sr.AudioFile(audio_path) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(
                audio,
                language='ml-IN',
                show_all=False
            )
            
            print(f"🎙️  Google heard: '{text}'")
            return self._normalize_text(text)
                
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"❌ API error: {e}")
            return ""
        except Exception as e:
            print(f"❌ Error: {e}")
            return ""
    
    def _normalize_text(self, text: str) -> str:
        """Clean text but preserve ENTIRE phrase (including multi-word inputs)"""
        # Just clean up whitespace, don't split!
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Keep the ENTIRE text - don't take just first word!
        # This is important for phrases like "jack fruit", "pine apple", etc.
        return text


# ============================================================
# LLM MANAGER (LAZY LOADED)
# ============================================================

class LLMManager:
    """Gemini LLM - only loads when needed"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model = None
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            print("⚠️  No API key - LLM disabled")
    
    def _load_model(self):
        """Lazy load the model only when first needed"""
        if self.model is None and self.enabled:
            try:
                # Use old library (google.generativeai) - it works!
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                
                print("📥 Loading Gemini model...")
                self.model = genai.GenerativeModel(
                    Config.GEMINI_MODEL,
                    generation_config={
                        'temperature': 0.3,
                        'top_p': 0.8,
                        'max_output_tokens': 2048,
                    }
                )
                print("✅ Gemini ready!")
            except Exception as e:
                print(f"❌ Failed to load Gemini: {e}")
                self.enabled = False
    
    def query_word(self, word: str, region_hint: str = "south") -> Optional[Dict]:
        """Query LLM for translation"""
        if not self.enabled:
            print("⚠️  LLM disabled - no API key")
            return None
        
        self._load_model()  # Lazy load
        
        if not self.model:
            print("⚠️  Model failed to load")
            return None
        
        # OPTIMIZED PROMPT with FOOD VALIDATION
        prompt = f'''You are a Kerala food expert. Analyze "{word}" as a Malayalam word.

CRITICAL FIRST STEP - VALIDATE IF THIS IS FOOD:
Before translating, check if "{word}" is actually a FOOD ITEM (fruit, vegetable, spice, grain, dish, ingredient, etc.)

NON-FOOD EXAMPLES (REJECT THESE):
- Furniture: chair, table, bed (കസേര, മേശ, കട്ടിൽ)
- Animals (not for eating): dog, cat (നായ, പൂച്ച)
- Objects: pen, book, phone (പേന, പുസ്തകം, ഫോൺ)
- Places: house, school (വീട്, സ്കൂൾ)
- Concepts: love, time (സ്നേഹം, സമയം)

IF NOT FOOD - Return this exact JSON:
{{
  "is_food": false,
  "english": "English translation",
  "category": "furniture/animal/object/place/concept/other",
  "message": "This is not a food item. This system only translates food-related words."
}}

IF IT IS FOOD - Continue with regional analysis:

TASK: Find regional dialect variations for this FOOD across Kerala.

REGIONS:
- South: Trivandrum, Kollam, Pathanamthitta
- Central: Kochi, Thrissur, Palakkad
- North: Calicut, Kannur, Kasaragod

SEARCH HARD for DIFFERENT words in each region. Check:
- Old vs new terms
- Market names vs home names
- Local varieties
- Alternative spellings

PROVEN EXAMPLES with variations:
- Papaya: ഒമക്കായ (South) | കപ്പളങ്ങ (Central) | പപ്പായ (North)
- Chilli: മുല്ലപെരുക്ക (South) | മുളക് (Central/North)
- Pomelo: ബബ്ലൂസ് (South) | മധുരനാരങ്ങ (Central) | ചക്കോത (North)
- Tapioca: കൂവ | മരച്ചീനി (different areas)

IMPORTANT:
- Try VERY HARD to find different words for each region
- If genuinely same everywhere, repeat the same word
- NEVER make up fake words
- Malayalam script ONLY

Return ONLY JSON (no markdown, no extra text):
{{
  "is_food": true,
  "english": "food name",
  "food_type": "fruit/vegetable/spice/grain/dish/other",
  "south": ["word1", "word2_if_exists"],
  "central": ["word1", "word2_if_exists"],
  "north": ["word1", "word2_if_exists"]
}}

Word: "{word}"
JSON:'''
        
        try:
            print("📤 Asking Gemini (gemini-flash-latest)...")
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "top_p": 0.8,
                    "max_output_tokens": 2048  # Increased for complete responses
                }
            )
            
            if not response.text:
                print("❌ Empty response from Gemini")
                return None
            
            # Get full response
            response_text = response.text.strip()
            print(f"📥 Gemini responded ({len(response_text)} chars)")
            
            result = self._parse_json(response_text)
            
            if result:
                # Check if it's actually food
                if result.get('is_food') == False:
                    print(f"⚠️ NOT FOOD: {result.get('english', 'Unknown')}")
                    print(f"   Category: {result.get('category', 'unknown')}")
                    print(f"   Message: {result.get('message', '')}")
                    
                    # Return non-food info so UI can display proper message
                    return {
                        "is_food": False,
                        "english": result.get('english', 'Unknown'),
                        "category": result.get('category', 'unknown'),
                        "message": result.get('message', 'This is not a food item.')
                    }
                
                # Verify all words are Malayalam (not other languages)
                for region in ["south", "central", "north"]:
                    if region in result and isinstance(result[region], list):
                        for w in result[region]:
                            if not self._is_malayalam(w):
                                print(f"⚠️  Warning: '{w}' might not be Malayalam")
                
                print(f"✅ Parsed successfully: {result['english']}")
                print(f"   South: {result.get('south', [])}")
                print(f"   Central: {result.get('central', [])}")
                print(f"   North: {result.get('north', [])}")
                
                # Check if variations exist
                south = result.get('south', [])
                central = result.get('central', [])
                north = result.get('north', [])
                
                if south and central and north:
                    if south != central or central != north:
                        print("   ✨ Regional variations found!")
                    else:
                        print("   ℹ️  Same word across all regions")
            else:
                print(f"❌ Failed to parse response")
                print(f"Response preview: {response_text[:200]}...")
            
            return result
            
        except Exception as e:
            print(f"❌ LLM error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _is_malayalam(self, text: str) -> bool:
        """Check if text contains Malayalam characters"""
        # Malayalam Unicode range: 0D00-0D7F
        return any(0x0D00 <= ord(c) <= 0x0D7F for c in text)
    
    def _parse_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from response - improved handling"""
        import json
        
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        
        # Try direct parse first
        try:
            data = json.loads(text)
            if self._validate(data):
                return data
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON object in text
        # Look for { ... } pattern
        json_match = re.search(r'\{[^{}]*"english"[^{}]*\}', text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                if self._validate(data):
                    return data
            except json.JSONDecodeError:
                pass
        
        # Try more aggressive extraction
        # Find content between first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                json_text = text[start:end+1]
                data = json.loads(json_text)
                if self._validate(data):
                    return data
            except json.JSONDecodeError:
                pass
        
        print(f"⚠️  Could not extract valid JSON")
        return None
    
    def _validate(self, data: Dict) -> bool:
        """Validate JSON structure - handles both food and non-food responses"""
        
        # Check if it's a non-food response
        if "is_food" in data and data["is_food"] == False:
            # Non-food response only needs: is_food, english, category, message
            required_non_food = ["is_food", "english", "category", "message"]
            return all(k in data for k in required_non_food)
        
        # Food response needs: english, south, central, north
        required_food = ["english", "south", "central", "north"]
        if not all(k in data for k in required_food):
            return False
        if data["english"] == "unknown":
            return False
        for region in ["south", "central", "north"]:
            if not isinstance(data[region], list) or not data[region]:
                return False
        return True


# ============================================================
# RETRIEVAL LAYER
# ============================================================

class RetrievalLayer:
    """Handles database lookup with fuzzy matching"""
    
    def __init__(self, data_manager: DataManager, fuzzy_matcher: FuzzyMatcher):
        self.data_manager = data_manager
        self.fuzzy_matcher = fuzzy_matcher
    
    def lookup_word(self, word: str, use_fuzzy: bool = True) -> Optional[Dict]:
        """Look up word with optional fuzzy matching"""
        lookup = self.data_manager.load_lookup()
        
        # Try exact match
        if word in lookup:
            print("✅ Exact match found!")
            return self._build_result(word, lookup, is_fuzzy=False)
        
        # Try fuzzy match
        if use_fuzzy:
            print("⚠️  No exact match, trying fuzzy...")
            fuzzy_word, similarity = self.fuzzy_matcher.find_similar_word(word, lookup)
            
            if fuzzy_word:
                return self._build_result(
                    fuzzy_word, lookup, is_fuzzy=True,
                    original_word=word, similarity=similarity
                )
        
        return None
    
    def _build_result(self, word: str, lookup: Dict, is_fuzzy: bool = False,
                     original_word: str = None, similarity: float = 1.0) -> Dict:
        """Build result dictionary"""
        word_info = lookup[word]
        concept = word_info["concept"]
        region = word_info["region"]
        
        concepts = self.data_manager.load_concepts()
        if concept not in concepts:
            return None
        
        concept_data = concepts[concept]
        images = self.data_manager.load_images()
        
        result = {
            "detected_region": region,
            "english": concept_data.get("english", "unknown"),
            "south": concept_data.get("south", []),
            "central": concept_data.get("central", []),
            "north": concept_data.get("north", []),
            "image": images.get(concept),
            "source": "fuzzy_retrieval" if is_fuzzy else "retrieval"
        }
        
        if is_fuzzy:
            result["fuzzy_match"] = {
                "original_word": original_word,
                "matched_word": word,
                "similarity": similarity
            }
        
        return result
    
    def get_suggestions(self, word: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """Get word suggestions"""
        lookup = self.data_manager.load_lookup()
        return self.fuzzy_matcher.get_suggestions(word, lookup, top_n)


# ============================================================
# MAIN SYSTEM
# ============================================================

class MalayalamDialectSystem:
    """Main system with lazy loading"""
    
    def __init__(self, data_manager, stt, llm_manager, retrieval, fuzzy_matcher):
        self.data_manager = data_manager
        self.stt = stt
        self.llm_manager = llm_manager
        self.retrieval = retrieval
        self.fuzzy_matcher = fuzzy_matcher
    
    def process_word(self, word: str, use_fuzzy: bool = True) -> Dict:
        """Process Malayalam word"""
        print(f"\n{'='*60}")
        print(f"Processing: '{word}'")
        print(f"{'='*60}\n")
        
        # Step 1: Retrieval (exact + fuzzy)
        result = self.retrieval.lookup_word(word, use_fuzzy=use_fuzzy)
        
        if result:
            return result
        
        print("❌ Not found in database\n")
        
        # Step 2: Get suggestions
        suggestions = self.retrieval.get_suggestions(word, top_n=3)
        if suggestions:
            print("💡 Similar words:")
            for sug_word, score in suggestions:
                print(f"   - {sug_word} ({score:.0%})")
            print()
        
        # Step 3: Try LLM
        print("Step 3: Querying AI...")
        ai_result = self.llm_manager.query_word(word, "south")
        
        if not ai_result:
            print("❌ AI could not help")
            return self._unknown_response(word, suggestions)
        
        # Check if it's a non-food item
        if ai_result.get('is_food') == False:
            print(f"⚠️ Returning non-food response to UI")
            return {
                "detected_region": "unknown",
                "english": ai_result.get('english', 'Unknown'),
                "category": ai_result.get('category', 'unknown'),
                "message": ai_result.get('message', 'This is not a food item. This system only translates food-related words.'),
                "original_word": word,
                "is_food": False
            }
        
        print(f"✅ AI found: {ai_result['english']}")
        
        # Step 4: Save to PENDING (NOT directly to database!)
        print("\nStep 4: Saving to pending review...")
        self.data_manager.save_to_pending(word, ai_result)
        print("💾 Saved to pending_review.json - Admin will review before adding to database")
        
        return {
            "detected_region": "south",
            "english": ai_result["english"],
            "south": ai_result["south"],
            "central": ai_result["central"],
            "north": ai_result["north"],
            "image": None,
            "source": "llm_generated",
            "status": "pending_review"
        }
    
    def _store_word(self, word: str, region: str, translations: Dict):
        """Store new word"""
        concept = translations["english"].lower().replace(" ", "_")
        
        self.data_manager.add_new_entry(
            word, region, concept,
            {
                "english": translations["english"],
                "south": translations["south"],
                "central": translations["central"],
                "north": translations["north"]
            }
        )
    
    def _unknown_response(self, word: str, suggestions: List = None) -> Dict:
        """Return unknown response with suggestions"""
        response = {
            "detected_region": "unknown",
            "english": "unknown",
            "message": "Word not in database. Please add it manually or check API key.",
            "image": None,
            "original_word": word
        }
        
        if suggestions:
            response["suggestions"] = [
                {"word": w, "similarity": f"{s:.0%}"} 
                for w, s in suggestions
            ]
            
            # If there's a very close match (>85%), suggest user might mean it
            if suggestions and suggestions[0][1] > 0.85:
                response["message"] = f"Did you mean '{suggestions[0][0]}'? Click the suggestion above."
        else:
            response["message"] = "No similar words found. This is a new word!"
        
        return response
    
    def process_audio(self, audio_path: str) -> Dict:
        """Process audio file"""
        print("\n🎙️  Transcribing...")
        word = self.stt.transcribe(audio_path)
        
        if not word:
            return {
                "error": "Transcription failed",
                "detected_region": "unknown",
                "english": "unknown",
                "image": None
            }
        
        print(f"✅ Heard: '{word}'\n")
        return self.process_word(word)


# ============================================================
# INITIALIZATION
# ============================================================

def initialize_system(api_key: str = None):
    """Initialize system - lightweight and fast!"""
    print("\n🚀 Initializing Malayalam System...")
    
    # Lightweight components (load immediately)
    data_manager = DataManager()
    stt = SpeechToText()
    fuzzy_matcher = FuzzyMatcher()
    retrieval = RetrievalLayer(data_manager, fuzzy_matcher)
    
    # Heavy components (lazy load)
    llm_manager = LLMManager(api_key)
    
    # Create system
    system = MalayalamDialectSystem(
        data_manager=data_manager,
        stt=stt,
        llm_manager=llm_manager,
        retrieval=retrieval,
        fuzzy_matcher=fuzzy_matcher
    )
    
    print("✅ System ready!\n")
    return system


# ============================================================
# COMMAND LINE INTERFACE
# ============================================================

def main():
    """CLI"""
    import sys
    
    system = initialize_system()
    
    if len(sys.argv) > 1:
        word = sys.argv[1]
        result = system.process_word(word)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: python malayalam_system.py <word>")
        print("Example: python malayalam_system.py ഒമക്കായ")


if __name__ == "__main__":
    main()

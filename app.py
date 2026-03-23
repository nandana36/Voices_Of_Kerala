"""
VOICES OF KERALA - COMPLETE UNIFIED APP
=========================================
Everything in one place:
✅ Voice input 
✅ Text input
✅ Translation
✅ User registration & API keys
✅ Admin panel
✅ Word validation
"""

import os
import streamlit as st

os.environ["SARVAM_API_KEY"] = st.secrets["SARVAM_API_KEY"]
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

import streamlit as st

import requests
import json
import os
from typing import Dict, List, Optional
import time
import hashlib
from datetime import datetime
import secrets
import re
import numpy as np

# ============================================================================
# CONFIGURATION
# ============================================================================
import os
class Config:
    DATA_DIR = "malayalam_data"
    VERIFIED_FILE = "lookup.json"
    PENDING_FILE = "pending_review.json"
    API_KEYS_FILE = "api_keys.json"
    API_REQUESTS_FILE = "api_requests.json"
    USERS_FILE = "users.json"
    ADMIN_PASSWORD_HASH = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # "password"
    
    # Sarvam AI Configuration
    
    SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

# ============================================================================
# PAGE SETUP
# ============================================================================

st.set_page_config(
    page_title="Voices of Kerala",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS (from original app)
# ============================================================================

# ============================================================================
# UPDATED CSS - WITH BETTER GREEN AND CARD LAYOUT
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Dark Theme Variables - ORIGINAL GREEN */
    :root {
        --primary-green: #6366f1;      /* Original indigo-blue */
        --primary-dark: #4f46e5;
        --primary-light: #818cf8;
        --accent-gold: #FFB703;
        --bg-main: #0A0E27;
        --bg-card: #151B3D;
        --bg-secondary: #1E2749;
        --text-primary: #E8E9F3;
        --text-secondary: #9BA3AF;
        --border-color: #2A3456;
        --shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    /* Base */
    .stApp {
        background: linear-gradient(135deg, #0A0E27 0%, #151B3D 100%) !important;
        font-family: 'Inter', sans-serif;
        color: var(--text-primary) !important;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Text */
    p, div, span, label, li, td, th {
        color: var(--text-primary) !important;
    }
    
    h1, h2, h3 {
        color: var(--text-primary) !important;
        font-weight: 600;
    }
    
    strong, b {
        color: var(--primary-light) !important;
        font-weight: 700;
    }
    
    /* Cards */
    .main-card {
        background: var(--bg-card) !important;
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow);
        margin: 1.5rem 0;
    }
    
    .result-card {
        background: var(--bg-card) !important;
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid var(--primary-green);
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.2);
        margin: 0;  /* Remove top margin */
    }
    
    /* Region Cards */
    .region-card {
        background: var(--bg-secondary) !important;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .region-card:hover {
        border-color: var(--primary-green);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
    }
    
    .region-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary-light) !important;
        margin-bottom: 0.25rem;
    }
    
    .region-city {
        font-size: 0.875rem;
        color: var(--text-secondary) !important;
        margin-bottom: 1rem;
    }
    
    .word-display {
        font-size: 1.8rem;
        font-weight: 600;
        color: var(--text-primary) !important;
        margin: 1rem 0;
        padding: 1rem;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 8px;
        border-left: 4px solid var(--primary-green);
    }
    
    /* English Title - BOLD */
    .english-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--primary-light) !important;
        margin: 0 0 1.5rem 0;
        text-align: center;
    }
    
    /* Title */
    .title {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-green), var(--primary-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: var(--text-secondary) !important;
        margin-bottom: 2rem;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary-green), var(--primary-dark)) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.5);
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: var(--primary-green) !important;
    }
    
    /* Status */
    .stSuccess {
        background: rgba(99, 102, 241, 0.2) !important;
        border-left: 4px solid var(--primary-green) !important;
        color: var(--text-primary) !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.2) !important;
        border-left: 4px solid #EF4444 !important;
        color: var(--text-primary) !important;
    }
    
    .stWarning {
        background: rgba(255, 183, 3, 0.2) !important;
        border-left: 4px solid var(--accent-gold) !important;
        color: var(--text-primary) !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.2) !important;
        border-left: 4px solid #3B82F6 !important;
        color: var(--text-primary) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-card), var(--bg-secondary)) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-secondary) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-green), var(--primary-dark)) !important;
        color: white !important;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color);
    }
    
    [data-testid="stMetricValue"] {
        color: var(--primary-light) !important;
    }
    
    /* Mic */
    .mic {
        font-size: 4rem;
        text-align: center;
        color: var(--primary-green);
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.15); }
    }
    
    /* Detected Word */
    .detected-word {
        background: linear-gradient(135deg, var(--primary-green), var(--primary-dark)) !important;
        color: white !important;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 1.5rem 0;
    }
    
    /* Hide "Transcribing" message */
    .stSpinner {
        display: none;
    }
    
    /* Audio player */
    audio {
        width: 100%;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)
# ============================================================================
# SESSION STATE
# ============================================================================

if 'page' not in st.session_state:
    st.session_state.page = 'main'

if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'history' not in st.session_state:
    st.session_state.history = []

if 'sarvam_api_key' not in st.session_state:
    st.session_state.sarvam_api_key = Config.SARVAM_API_KEY  # Use hardcoded key from Config

if 'system_initialized' not in st.session_state:
    st.session_state.system_initialized = False
    st.session_state.system = None

# ============================================================================
# DATA MANAGER
# ============================================================================

class DataManager:
    """Manage all data files"""
    
    def __init__(self):
        self.data_dir = Config.DATA_DIR
        self.verified_path = os.path.join(self.data_dir, Config.VERIFIED_FILE)
        self.pending_path = os.path.join(self.data_dir, Config.PENDING_FILE)
        self.api_keys_path = os.path.join(self.data_dir, Config.API_KEYS_FILE)
        self.api_requests_path = os.path.join(self.data_dir, Config.API_REQUESTS_FILE)
        self.users_path = os.path.join(self.data_dir, Config.USERS_FILE)
        
        os.makedirs(self.data_dir, exist_ok=True)
        self._init_files()
    
    def _init_files(self):
        for path in [self.verified_path, self.pending_path, self.api_keys_path, 
                     self.api_requests_path, self.users_path]:
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    # User management
    def load_users(self) -> Dict:
        try:
            with open(self.users_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_users(self, data: Dict):
        with open(self.users_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_user(self, email: str, name: str, password: str, organization: str = "") -> bool:
        users = self.load_users()
        
        if email in users:
            return False
        
        users[email] = {
            'name': name,
            'password_hash': hashlib.sha256(password.encode()).hexdigest(),
            'organization': organization,
            'created_date': datetime.now().isoformat(),
            'api_keys': []
        }
        
        self.save_users(users)
        return True
    
    def verify_user(self, email: str, password: str) -> bool:
        users = self.load_users()
        
        if email not in users:
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return users[email]['password_hash'] == password_hash
    
    # API request management
    def load_api_requests(self) -> Dict:
        try:
            with open(self.api_requests_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_api_requests(self, data: Dict):
        with open(self.api_requests_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def request_api_key(self, email: str, tier: str, use_case: str) -> str:
        requests_data = self.load_api_requests()
        
        request_id = f"req_{secrets.token_urlsafe(16)}"
        
        requests_data[request_id] = {
            'email': email,
            'tier': tier,
            'use_case': use_case,
            'status': 'pending',
            'requested_date': datetime.now().isoformat(),
            'api_key': None
        }
        
        self.save_api_requests(requests_data)
        return request_id
    
    def approve_api_request(self, request_id: str) -> Optional[str]:
        requests_data = self.load_api_requests()
        
        if request_id not in requests_data:
            return None
        
        req = requests_data[request_id]
        
        # Generate API key
        api_key = self.generate_api_key(req['email'], req['tier'])
        
        # Update request
        req['status'] = 'approved'
        req['approved_date'] = datetime.now().isoformat()
        req['api_key'] = api_key
        
        self.save_api_requests(requests_data)
        
        # Update user record
        users = self.load_users()
        if req['email'] in users:
            users[req['email']]['api_keys'].append(api_key)
            self.save_users(users)
        
        return api_key
    
    def reject_api_request(self, request_id: str, reason: str = ""):
        requests_data = self.load_api_requests()
        
        if request_id in requests_data:
            requests_data[request_id]['status'] = 'rejected'
            requests_data[request_id]['rejected_date'] = datetime.now().isoformat()
            requests_data[request_id]['rejection_reason'] = reason
            self.save_api_requests(requests_data)
    
    # Word management
    def load_verified(self) -> Dict:
        try:
            with open(self.verified_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def load_pending(self) -> Dict:
        try:
            with open(self.pending_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_verified(self, data: Dict):
        with open(self.verified_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_pending(self, data: Dict):
        with open(self.pending_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def approve_word(self, word: str, data: Dict):
        verified = self.load_verified()
        pending = self.load_pending()
        
        verified[word] = data
        verified[word]['approved_date'] = datetime.now().isoformat()
        verified[word]['source'] = 'admin_approved'
        
        if word in pending:
            del pending[word]
        
        self.save_verified(verified)
        self.save_pending(pending)
        return True
    
    def reject_word(self, word: str, reason: str = ""):
        pending = self.load_pending()
        
        if word in pending:
            rejected_log = os.path.join(self.data_dir, "rejected_log.json")
            rejected_data = {}
            
            if os.path.exists(rejected_log):
                with open(rejected_log, 'r', encoding='utf-8') as f:
                    rejected_data = json.load(f)
            
            rejected_data[word] = {
                'data': pending[word],
                'rejected_date': datetime.now().isoformat(),
                'reason': reason
            }
            
            with open(rejected_log, 'w', encoding='utf-8') as f:
                json.dump(rejected_data, f, ensure_ascii=False, indent=2)
            
            del pending[word]
            self.save_pending(pending)
        
        return True
    
    # API key management
    def load_api_keys(self) -> Dict:
        try:
            with open(self.api_keys_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_api_keys(self, data: Dict):
        with open(self.api_keys_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def generate_api_key(self, email: str, key_name: str) -> str:
        """Generate API key instantly - no approval needed"""
        api_key = f"vok_{secrets.token_urlsafe(32)}"
        
        api_keys = self.load_api_keys()
        
        # Get user info
        users = self.load_users()
        user_name = users.get(email, {}).get('name', 'Unknown')
        
        api_keys[api_key] = {
            'user_email': email,
            'user_name': user_name,
            'key_name': key_name,
            'created_date': datetime.now().isoformat(),
            'status': 'active',
            'usage_count': 0,
            'last_used': None
        }
        
        self.save_api_keys(api_keys)
        
        # Add to user's key list
        if email in users:
            if 'api_keys' not in users[email]:
                users[email]['api_keys'] = []
            users[email]['api_keys'].append(api_key)
            self.save_users(users)
        
        return api_key

dm = DataManager()

# ============================================================================
# BACKEND INITIALIZATION (from original app)
# ============================================================================

def initialize_system():
    """Initialize backend"""
    try:
        from malayalam_system import initialize_system as init_backend
        st.session_state.system = init_backend()
        st.session_state.system_initialized = True
        return True
    except Exception as e:
        st.warning(f"⚠️ Backend not available: {e}")
        return False

def process_word(word: str) -> Dict:
    """Process word through backend"""
    if st.session_state.system_initialized and st.session_state.system:
        try:
            return st.session_state.system.process_word(word)
        except Exception as e:
            return {"error": str(e), "detected_region": "unknown", "english": "unknown"}
    else:
        # Fallback to database only
        verified = dm.load_verified()
        if word in verified:
            return verified[word]
        else:
            return {
                "detected_region": "unknown",
                "english": "unknown",
                "message": "Word not found"
            }

# ============================================================================
# SARVAM AI RECORDING (from original app)
# ============================================================================

def transcribe_with_sarvam(audio_bytes: bytes, api_key=None):
    """
    Transcribe audio bytes with Sarvam AI
    95%+ accuracy for Malayalam!
    """
    
    if not api_key:
        return None, "❌ Sarvam AI API key not set"
    
    if not audio_bytes or len(audio_bytes) == 0:
        return None, "❌ No audio data received"
    
    try:
        st.info("🚀 Transcribing...")
        
        url = "https://api.sarvam.ai/speech-to-text"
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        files = {
            "file": ("audio.wav", audio_bytes, "audio/wav")
        }
        
        data = {
            "model": "saarika:v2.5",
            "language_code": "ml-IN"
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if 'transcript' in result:
                return result['transcript'], None
            else:
                return None, f"❌ Unexpected response: {result}"
        else:
            return None, f"❌ API error ({response.status_code}): {response.text}"
            
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

# ============================================================================
# SARVAM TEXT-TO-SPEECH
# ============================================================================

def text_to_speech_sarvam(text: str, api_key: str) -> tuple:
    """
    Convert Malayalam text to speech using Sarvam AI
    Returns: (audio_bytes, error_message)
    """
    
    if not api_key:
        print("❌ TTS: No API key")
        return None, "No API key"
    
    try:
        print(f"🔊 TTS: Converting '{text}' to speech...")
        
        url = "https://api.sarvam.ai/text-to-speech"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "inputs": [text],  # Send original text as-is
            "target_language_code": "ml-IN",
            "speaker": "manisha",
            "pitch": 0,
            "pace": 0.68,  # Much slower (30% slower than normal)
            "loudness": 1.5,
            "speech_sample_rate": 22050,  # Even higher quality
            "enable_preprocessing": True,
            "model": "bulbul:v2"
        }
        
        print(f"📤 TTS: Calling Sarvam API (pace=0.7 for slower speech)...")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"📥 TTS: Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract base64 audio
            if 'audios' in result and len(result['audios']) > 0:
                import base64
                audio_base64 = result['audios'][0]
                audio_bytes = base64.b64decode(audio_base64)
                print(f"✅ TTS: Success! Generated {len(audio_bytes)} bytes")
                return audio_bytes, None
            else:
                print(f"❌ TTS: No audio in response: {result}")
                return None, "No audio in response"
        else:
            error_msg = f"API error {response.status_code}"
            print(f"❌ TTS: {error_msg}")
            print(f"   Response: {response.text[:200]}")
            return None, error_msg
            
    except Exception as e:
        print(f"❌ TTS Exception: {type(e).__name__}: {str(e)}")
        return None, f"Error: {str(e)}"

# ============================================================================
# DISPLAY FUNCTIONS (from original app)
# ============================================================================

def display_result(result: Dict, context="main"):
    """Display translation result"""
    
    # Check if it's a non-food item FIRST
    if result.get('is_food') == False:
        st.warning("⚠️ **Not a Food Item**")
        st.info(f"""
        **"{result.get('original_word', 'This word')}"** appears to be **{result.get('category', 'not food-related')}**.
        
        🍽️ **This system specializes in FOOD words only:**
        - Fruits, Vegetables, Spices, Grains, Dishes, Ingredients
        
        **Try searching for:**
        - **Fruits:** ഒമക്കായ (papaya), മാമ്പഴം (mango), വാഴപ്പഴം (banana)
        - **Vegetables:** കപ്പ (tapioca), ചേന (yam), മുളക് (chilli)
        - **Spices:** മഞ്ഞൾ (turmeric), കുരുമുളക് (pepper)
        - **Grains:** അരി (rice), ഗോതമ്പ് (wheat)
        """)
        return
    
    if result.get('detected_region') == 'unknown':
        # Check if it's a non-food item
        if 'message' in result and 'not a food item' in result.get('message', '').lower():
            st.warning("⚠️ **Not a Food Item**")
            st.info(f"""
            **"{result.get('original_word', 'This word')}"** appears to be **{result.get('category', 'not food-related')}**.
            
            This system specializes in **food words only** (fruits, vegetables, spices, dishes, grains, ingredients).
            
            **Try searching for:**
            - Fruits: ഒമക്കായ (papaya), മാമ്പഴം (mango)
            - Vegetables: കപ്പ (tapioca), ചേന (yam)
            - Spices: മുളക് (chilli), മഞ്ഞൾ (turmeric)
            """)
        else:
            st.error("❌ Word not found")
            
            if 'suggestions' in result and result['suggestions']:
                st.warning("💡 **Did you mean?**")
                cols = st.columns(min(3, len(result['suggestions'])))
                for idx, sug in enumerate(result['suggestions'][:3]):
                    with cols[idx]:
                        # Handle both dict format {"word": "...", "similarity": "..."} and string format
                        if isinstance(sug, dict):
                            sug_word = sug.get('word', str(sug))
                            similarity = sug.get('similarity', '')
                            button_label = f"{sug_word} ({similarity})" if similarity else sug_word
                        else:
                            button_label = str(sug)
                        
                        if st.button(button_label, key=f"{context}_sug_{idx}"):
                            # Re-process with suggestion
                            pass
    else:
        st.success(f"✅ **{result.get('english', 'Unknown')}**")
        
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🟡 South Kerala**")
            st.markdown("*Trivandrum*")
            for idx, variant in enumerate(result.get('south', [])):
                st.markdown(f"**{variant}**")
                
                # Try to generate TTS
                with st.spinner('🔊 Generating audio...'):
                    audio_bytes, error = text_to_speech_sarvam(variant, st.session_state.sarvam_api_key)
                
                if audio_bytes:
                    st.audio(audio_bytes, format='audio/wav')
                elif error:
                    st.caption(f"🔇 Audio: {error[:50]}")
        
        with col2:
            st.markdown("**🟢 Central Kerala**")
            st.markdown("*Kochi*")
            for idx, variant in enumerate(result.get('central', [])):
                st.markdown(f"**{variant}**")
                
                # Try to generate TTS
                with st.spinner('🔊 Generating audio...'):
                    audio_bytes, error = text_to_speech_sarvam(variant, st.session_state.sarvam_api_key)
                
                if audio_bytes:
                    st.audio(audio_bytes, format='audio/wav')
                elif error:
                    st.caption(f"🔇 Audio: {error[:50]}")
        
        with col3:
            st.markdown("**🔵 North Kerala**")
            st.markdown("*Calicut*")
            for idx, variant in enumerate(result.get('north', [])):
                st.markdown(f"**{variant}**")
                
                # Try to generate TTS
                with st.spinner('🔊 Generating audio...'):
                    audio_bytes, error = text_to_speech_sarvam(variant, st.session_state.sarvam_api_key)
                
                if audio_bytes:
                    st.audio(audio_bytes, format='audio/wav')
                elif error:
                    st.caption(f"🔇 Audio: {error[:50]}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    if 'source' in result:
        if result['source'] == 'retrieval':
            st.success("✅ Instant retrieval")
        elif result['source'] == 'fuzzy_retrieval':
            st.success("✅ Fuzzy match")
        elif result['source'] == 'llm_validated':
            st.info("🤖 AI-powered")
    


# ============================================================================
# AUTHENTICATION
# ============================================================================

def check_admin_password():
    """Check admin password"""
    
    def password_entered():
        password_hash = hashlib.sha256(st.session_state["admin_password"].encode()).hexdigest()
        
        if password_hash == Config.ADMIN_PASSWORD_HASH:
            st.session_state.admin_authenticated = True
            del st.session_state["admin_password"]
        else:
            st.error("❌ Incorrect password")
    
    if not st.session_state.admin_authenticated:
        st.markdown("### 🔐 Admin Login")
        st.text_input(
            "Password",
            type="password",
            key="admin_password",
            on_change=password_entered
        )
        
        st.info("**Default password:** `password`")
        
        return False
    
    return True

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ============================================================================
# NAVIGATION SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("# 🎙️ Voices of Kerala")
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📍 Navigation")
    
    if st.button("🏠 Translator", key="nav_main", use_container_width=True, type="primary" if st.session_state.page == 'main' else "secondary"):
        st.session_state.page = 'main'
        st.rerun()
    
    if st.button("🔑 API Access", key="nav_api", use_container_width=True, type="primary" if st.session_state.page == 'api' else "secondary"):
        st.session_state.page = 'api'
        st.rerun()
    
    if st.button("📖 API Docs", key="nav_docs", use_container_width=True, type="primary" if st.session_state.page == 'docs' else "secondary"):
        st.session_state.page = 'docs'
        st.rerun()
    
    if st.button("👨‍💼 Admin", key="nav_admin", use_container_width=True, type="primary" if st.session_state.page == 'admin' else "secondary"):
        st.session_state.page = 'admin'
        st.rerun()
    
    st.markdown("---")
    
    # User status
    if st.session_state.user_logged_in:
        st.success(f"👤 {st.session_state.current_user}")
        if st.button("🚪 Logout", key="logout_user", use_container_width=True):
            st.session_state.user_logged_in = False
            st.session_state.current_user = None
            st.rerun()
    
    # Admin status
    if st.session_state.page == 'admin' and st.session_state.admin_authenticated:
        st.markdown("---")
        st.info("👨‍💼 Admin Mode")
        if st.button("🚪 Logout Admin", key="logout_admin", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()
    
    st.markdown("---")
    
    # Quick stats
    verified = dm.load_verified()
    pending = dm.load_pending()
    
   
    
    if st.session_state.admin_authenticated:
        st.metric("Pending Words", len(pending))
        
        api_requests = dm.load_api_requests()
        pending_requests = sum(1 for r in api_requests.values() if r.get('status') == 'pending')
        st.metric("API Requests", pending_requests)

# ============================================================================
# MAIN TRANSLATION PAGE (ORIGINAL APP)
# ============================================================================

def main_page():
    """Main translation interface with voice and text"""
    
    # Initialize backend if not done
    if not st.session_state.system_initialized:
        initialize_system()
    
    st.markdown('<div class="title">🎙️ Voices of Kerala</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Malayalam Dialect Normalisation System</div>', unsafe_allow_html=True)
    
    # Tabs - VOICE AND TEXT!
    tab1, tab2, tab3 = st.tabs(["🎤 Voice Input", "⌨️ Text Input", "📊 History"])
    
    # TAB 1: VOICE with Sarvam AI
    with tab1:
        
        
        st.markdown("### 🎧 Speak a Malayalam Word")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Click the mic button below to start recording. Click again to stop.**")
            audio_file = st.audio_input("🎤 Record your voice")

            if audio_file is not None:
                 with open("temp.wav", "wb") as f:
                          f.write(audio_file.read())    
                 st.success("✅ Audio recorded!")        
            
            
            if audio_file is not None:
                # Show the recorded audio for playback
                st.audio(audio_file)
                
                # Export to bytes and send to Sarvam
                audio_bytes = audio_file.read()
                
                transcript, error = transcribe_with_sarvam(
                    audio_bytes=audio_bytes,
                    api_key=st.session_state.sarvam_api_key
                )
                
                if error:
                    st.error(error)
                elif transcript:
                    # Show what was transcribed
                    st.markdown(
                        f"<div class='detected-word'>✅ Word Captured: {transcript}</div>",
                        unsafe_allow_html=True
                    )
                    
                    final_word = transcript.strip()
                    
                    # Process full phrase
                    result = process_word(final_word)
                    
                    # Add to history
                    st.session_state.history.append({
                        "input": f"Voice (Sarvam): {final_word}",
                        "result": result,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    # Display result
                    st.markdown("---")
                    display_result(result, context="voice_tab")
                else:
                    st.error("❌ No transcription received")
        
        with col2:
            st.markdown("""
            **📝 Tips for Best Results:**
            
            **DO:**
            - 🔊 Speak **clearly**
            - 🐌 Speak at **normal speed**
            - 🔇 Use **quiet** environment
            - 📏 Mic **close** to mouth
            
            **Examples:**
            - ഒമക്കായ (papaya)
            - മുളക് (chilli)
            - വാഴപ്പഴം (banana)
            
            
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: TEXT INPUT
    with tab2:
        
        
        st.markdown("### ⌨️ Type Malayalam Word")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            word_input = st.text_input("Word", placeholder="ഒമക്കായ", label_visibility="collapsed")
        
        with col2:
            translate_btn = st.button("🔍 Translate", key="translate_text", type="primary", use_container_width=True)
        
        # Examples
        st.markdown("**Examples:**")
        example_cols = st.columns(5)
        examples = ["ഒമക്കായ", "കപ്പളങ്ങ", "മുളക്", "വാഴപ്പഴം", "നെല്ല്"]
        
        for idx, ex in enumerate(examples):
            with example_cols[idx]:
                if st.button(ex, key=f"ex_{idx}"):
                    word_input = ex
                    translate_btn = True
        
        if translate_btn and word_input:
            result = process_word(word_input)
            
            st.session_state.history.append({
                "input": f"Text: {word_input}",
                "result": result,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            st.markdown("---")
            display_result(result, context="text_tab")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 3: HISTORY
    with tab3:
        
        
        st.markdown("### 📊 Translation History")
        
        if not st.session_state.history:
            st.info("No translations yet")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                voice = sum(1 for h in st.session_state.history if 'Voice' in h['input'])
                st.metric("Voice", voice)
            with col2:
                text = sum(1 for h in st.session_state.history if 'Text' in h['input'])
                st.metric("Text", text)
            with col3:
                st.metric("Total", len(st.session_state.history))
            
            st.markdown("---")
            
            for idx, item in enumerate(reversed(st.session_state.history)):
                icon = "🎤" if "Voice" in item['input'] else "⌨️"
                
                with st.expander(f"{icon} {item['timestamp']} - {item['input']}"):
                    display_result(item['result'], context=f"hist_{idx}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    
    """, unsafe_allow_html=True)

# ============================================================================
# API ACCESS PAGE (NEW)
# ============================================================================

def api_page():
    """API access page - same as before"""
    
    st.markdown("# 🔑 API Access")
    st.markdown("### Get programmatic access to our translation API")
    
    # Same implementation as the complete_unified_app.py
    # (Code for login/register/request API key)
    
    if not st.session_state.user_logged_in:
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab1:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown("### Login to Your Account")
            
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("🔑 Login", type="primary"):
                    if dm.verify_user(email, password):
                        st.session_state.user_logged_in = True
                        st.session_state.current_user = email
                        st.success("✅ Logged in!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown("### Create New Account")
            
            with st.form("register_form"):
                name = st.text_input("Full Name *")
                email = st.text_input("Email *")
                organization = st.text_input("Organization (Optional)")
                password = st.text_input("Password *", type="password")
                confirm_password = st.text_input("Confirm Password *", type="password")
                
                agree = st.checkbox("I agree to Terms of Service")
                
                if st.form_submit_button("📝 Create Account", type="primary"):
                    if not name or not email or not password:
                        st.error("❌ Fill all required fields")
                    elif not validate_email(email):
                        st.error("❌ Invalid email format")
                    elif len(password) < 8:
                        st.error("❌ Password must be 8+ characters")
                    elif password != confirm_password:
                        st.error("❌ Passwords don't match")
                    elif not agree:
                        st.error("❌ Please agree to Terms")
                    else:
                        if dm.create_user(email, name, password, organization):
                            st.success("✅ Account created! Please login")
                        else:
                            st.error("❌ Email already registered")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Logged in - show API keys and request form
        user_email = st.session_state.current_user
        users = dm.load_users()
        user_data = users.get(user_email, {})
        
        st.success(f"👤 Logged in as: **{user_data.get('name', 'User')}**")
        
        st.markdown("## 🔑 Your API Keys")
        
        user_api_keys = user_data.get('api_keys', [])
        all_api_keys = dm.load_api_keys()
        
        if user_api_keys:
            for key in user_api_keys:
                if key in all_api_keys:
                    key_info = all_api_keys[key]
                    
                    if key_info.get('status') == 'active':
                        with st.expander(f"🔑 {key_info.get('key_name', 'API Key')} - Created {key_info.get('created_date', '')[:10]}", expanded=False):
                            st.markdown(f"""
                            <div class="api-key-box">
                                {key}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Status", "ACTIVE")
                                st.metric("Usage Count", key_info.get('usage_count', 0))
                            
                            with col2:
                                last_used = key_info.get('last_used')
                                if last_used:
                                    st.markdown(f"**Last Used:** {last_used[:10]}")
                                else:
                                    st.markdown("**Last Used:** Never")
                                
                                if st.button(f"🗑️ Revoke Key", key=f"revoke_{key}"):
                                    dm.revoke_api_key(key)
                                    st.success("✅ Key revoked!")
                                    st.rerun()
        else:
            st.info("No API keys yet. Request one below!")
        
        st.markdown("---")
        st.markdown("## ➕ Generate New API Key")
        
        st.info("💡 **Instant Generation!** Your API key is created immediately - no waiting for approval!")
        
        with st.form("create_api_key"):
            key_name = st.text_input(
                "Key Name *",
                placeholder="My App Key",
                help="Give your API key a descriptive name (e.g., 'Production App', 'Mobile App', 'Testing')"
            )
            
            st.info("**Tip:** Use descriptive names like 'Production Server', 'Mobile App', 'Testing Environment'")
            
            if st.form_submit_button("🔑 Generate API Key Now", type="primary", use_container_width=True):
                if not key_name or len(key_name) < 3:
                    st.error("❌ Key name must be at least 3 characters")
                else:
                    # INSTANT GENERATION - No approval needed!
                    new_key = dm.generate_api_key(user_email, key_name)
                    
                    st.success("✅ API Key Generated Successfully!")
                    st.balloons()
                    
                    st.markdown(f"""
                    <div class="api-key-box">
                        {new_key}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.warning("⚠️ **IMPORTANT:** Copy this key now! You won't be able to see it again.")
                    
                    # Show usage instructions
                    st.markdown("### 🚀 Start Using Your Key")
                    st.code(f'''# Python example
import requests

API_KEY = "{new_key}"
response = requests.post(
    "http://localhost:8000/api/v1/translate",
    headers={{"X-API-Key": API_KEY}},
    json={{"word": "ഒമക്കായ"}}
)
print(response.json())
                    ''', language="python")
                    
                    st.info("📖 See **API Docs** page for complete examples in Python, JavaScript, and more!")

# ============================================================================
# ADMIN PANEL PAGE (NEW)
# ============================================================================

def admin_page():
    """Admin panel - same as before"""
    
    if not check_admin_password():
        return
    
    st.markdown("# 👨‍💼 Admin Panel")
    
    # Load data
    verified = dm.load_verified()
    pending = dm.load_pending()
    api_requests = dm.load_api_requests()
    
    # Stats dashboard
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Verified Words", len(verified))
    with col2:
        st.metric("Pending Words", len(pending))
    with col3:
        pending_reqs = sum(1 for r in api_requests.values() if r.get('status') == 'pending')
        st.metric("API Requests", pending_reqs)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2 = st.tabs([f"⏳ Pending Words ({len(pending)})", "📊 API Usage Monitor"])
    
    with tab1:
        st.markdown("## ⏳ Words Awaiting Approval")
        st.info("Review Gemini-generated words before adding to database")
        
        if pending:
            for word, data in pending.items():
                with st.expander(f"🔍 {word} - {data.get('english', 'Unknown')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Malayalam:** {word}")
                        st.markdown(f"**English:** {data.get('english')}")
                    with col2:
                        st.markdown(f"**Source:** {data.get('source', 'llm')}")
                        st.markdown(f"**Added:** {data.get('timestamp', '')[:10]}")
                    
                    st.markdown(f"**South:** {', '.join(data.get('south', []))}")
                    st.markdown(f"**Central:** {', '.join(data.get('central', []))}")
                    st.markdown(f"**North:** {', '.join(data.get('north', []))}")
                    
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Approve", key=f"approve_{word}", type="primary", use_container_width=True):
                            dm.approve_word(word, data)
                            st.success(f"✅ Approved: {word}")
                            st.rerun()
                    with col2:
                        if st.button(f"❌ Reject", key=f"reject_{word}", use_container_width=True):
                            dm.reject_word(word, "Admin rejected")
                            st.success(f"🗑️ Rejected: {word}")
                            st.rerun()
        else:
            st.success("🎉 No pending words!")
    
    with tab2:
        st.markdown("## 📊 API Key Usage")
        st.info("Monitor all API keys. Users generate keys instantly - you can revoke if needed.")
        
        api_keys_all = dm.load_api_keys()
        
        if not api_keys_all:
            st.info("No API keys generated yet")
        else:
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Keys", len(api_keys_all))
            with col2:
                active = sum(1 for k in api_keys_all.values() if k.get('status') == 'active')
                st.metric("Active Keys", active)
            with col3:
                total_calls = sum(k.get('usage_count', 0) for k in api_keys_all.values())
                st.metric("Total API Calls", total_calls)
            
            st.markdown("---")
            
            # Show keys sorted by usage
            sorted_keys = sorted(
                api_keys_all.items(),
                key=lambda x: x[1].get('usage_count', 0),
                reverse=True
            )
            
            for api_key, key_info in sorted_keys:
                status = key_info.get('status', 'unknown')
                usage = key_info.get('usage_count', 0)
                
                with st.expander(
                    f"{'✅' if status == 'active' else '🚫'} {key_info.get('user_name')} - {key_info.get('key_name')} ({usage} calls)"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**User:** {key_info.get('user_name')}")
                        st.markdown(f"**Email:** {key_info.get('user_email')}")
                        st.markdown(f"**Key Name:** {key_info.get('key_name')}")
                        st.markdown(f"**Created:** {key_info.get('created_date', '')[:10]}")
                    
                    with col2:
                        st.metric("Status", status.upper())
                        st.metric("Calls", usage)
                        last = key_info.get('last_used')
                        st.markdown(f"**Last Used:** {last[:10] if last else 'Never'}")
                    
                    st.code(api_key[:30] + "...", language="text")
                    
                    if status == 'active':
                        if st.button(f"🚫 Revoke", key=f"admin_revoke_{api_key}"):
                            dm.revoke_api_key(api_key)
                            st.success("Revoked!")
                            st.rerun()

# ============================================================================
# MAIN ROUTER
# ============================================================================

# ============================================================================
# API DOCUMENTATION PAGE
# ============================================================================

def api_docs_page():
    """Complete API documentation for users"""
    
    st.markdown("# 📖 API Documentation")
    st.markdown("### Complete guide to using the Voices of Kerala API")
    
    st.info("👉 **First time?** Get your API key from the **🔑 API Access** page - it's instant!")
    
    # Quick Navigation
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**[Quick Start](#quick-start)**")
    with col2:
        st.markdown("**[Python](#python)**")
    with col3:
        st.markdown("**[JavaScript](#javascript)**")
    with col4:
        st.markdown("**[Field Selection](#field-selection)**")
    
    st.markdown("---")
    
    # QUICK START
    st.markdown("## 🚀 Quick Start")
    
    st.markdown("### Step 1: Get API Key")
    st.info("Click **🔑 API Access** → Login/Register → Click **Generate API Key** → Copy it!")
    
    st.markdown("### Step 2: Make Your First Request")
    st.code('''curl -X POST "http://localhost:8000/api/v1/translate" \\
     -H "X-API-Key: your_api_key_here" \\
     -H "Content-Type: application/json" \\
     -d '{"word": "ഒമക്കായ"}'
    ''', language="bash")
    
    st.markdown("### Step 3: Get Response")
    st.code('''{
  "input_word": "ഒമക്കായ",
  "english": "Papaya",
  "south": ["ഒമക്കായ"],
  "central": ["കപ്പളങ്ങ"],
  "north": ["പപ്പായ"],
  "source": "verified"
}''', language="json")
    
    st.success("✅ That's it! You're ready to start translating!")
    
    st.markdown("---")
    
    # PYTHON
    st.markdown("## 🐍 Python Examples")
    
    tab1, tab2, tab3 = st.tabs(["Basic Usage", "Field Selection", "Complete Class"])
    
    with tab1:
        st.markdown("### Basic Translation")
        st.code('''import requests

API_KEY = "your_api_key_here"
BASE_URL = "http://localhost:8000/api/v1"

def translate(word):
    response = requests.post(
        f"{BASE_URL}/translate",
        headers={"X-API-Key": API_KEY},
        json={"word": word}
    )
    return response.json()

# Usage
result = translate("ഒമക്കായ")
print(f"English: {result['english']}")
print(f"South: {', '.join(result['south'])}")
print(f"Central: {', '.join(result['central'])}")
print(f"North: {', '.join(result['north'])}")
        ''', language="python")
    
    with tab2:
        st.markdown("### Get Only Specific Fields")
        st.code('''import requests

API_KEY = "your_api_key_here"
BASE_URL = "http://localhost:8000/api/v1"

# Get only English
result = requests.post(
    f"{BASE_URL}/translate",
    headers={"X-API-Key": API_KEY},
    json={"word": "ഒമക്കായ", "fields": ["english"]}
).json()

print(result)
# Output: {"input_word": "ഒമക്കായ", "english": "Papaya"}

# Get English + South region
result = requests.post(
    f"{BASE_URL}/translate",
    headers={"X-API-Key": API_KEY},
    json={"word": "മുളക്", "fields": ["english", "south"]}
).json()

print(result)
# Output: {"input_word": "മുളക്", "english": "Chilli", "south": ["മുല്ലപെരുക്ക"]}
        ''', language="python")
    
    with tab3:
        st.markdown("### Ready-to-Use Translator Class")
        st.code('''import requests
from typing import List, Optional, Dict

class MalayalamTranslator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://localhost:8000/api/v1"
        self.headers = {"X-API-Key": api_key}
    
    def translate(self, word: str, fields: Optional[List[str]] = None) -> Dict:
        payload = {"word": word}
        if fields:
            payload["fields"] = fields
        
        try:
            response = requests.post(
                f"{self.base_url}/translate",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return {"error": "Word not found"}
            elif e.response.status_code == 401:
                return {"error": "Invalid API key"}
            else:
                return {"error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_english_only(self, word: str) -> Optional[str]:
        result = self.translate(word, ["english"])
        return result.get("english")
    
    def get_all_regions(self, word: str) -> Dict:
        return self.translate(word)

# Usage
translator = MalayalamTranslator("your_api_key")

# Get everything
all_data = translator.get_all_regions("ഒമക്കായ")
print(all_data)

# Get only English
english = translator.get_english_only("മുളക്")
print(f"English: {english}")
        ''', language="python")
    
    st.markdown("---")
    
    # JAVASCRIPT
    st.markdown("## 📜 JavaScript Examples")
    
    tab1, tab2 = st.tabs(["Node.js", "Browser"])
    
    with tab1:
        st.markdown("### Node.js with Fetch")
        st.code('''const API_KEY = 'your_api_key';
const BASE_URL = 'http://localhost:8000/api/v1';

// Translate function
async function translate(word, fields = null) {
    const body = { word };
    if (fields) body.fields = fields;
    
    try {
        const response = await fetch(`${BASE_URL}/translate`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

// Usage
const result = await translate('ഒമക്കായ');
console.log(result);

// Get only English
const english = await translate('മുളക്', ['english']);
console.log(english);
        ''', language="javascript")
    
    with tab2:
        st.markdown("### Browser Example")
        st.code('''const API_KEY = 'your_api_key';

async function translate(word, fields = null) {
    const body = { word };
    if (fields) body.fields = fields;
    
    const response = await fetch('http://localhost:8000/api/v1/translate', {
        method: 'POST',
        headers: {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    });
    
    return await response.json();
}

// Use in your web app
document.getElementById('translateBtn').onclick = async () => {
    const word = document.getElementById('wordInput').value;
    const result = await translate(word);
    
    if (result) {
        document.getElementById('english').textContent = result.english;
        document.getElementById('south').textContent = result.south.join(', ');
        document.getElementById('central').textContent = result.central.join(', ');
        document.getElementById('north').textContent = result.north.join(', ');
    }
};
        ''', language="javascript")
    
    st.markdown("---")
    
    # FIELD SELECTION
    st.markdown("## 🎯 Field Selection")
    
    st.markdown("""
    Choose which fields to return in the API response.
    
    **Available fields:**
    - `english` - English translation
    - `south` - South Kerala dialect (Trivandrum)
    - `central` - Central Kerala dialect (Kochi)
    - `north` - North Kerala dialect (Calicut)
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Get All Fields (default):**")
        st.code('{"word": "ഒമക്കായ"}', language="json")
        st.caption("→ Returns ALL fields")
        
        st.markdown("**Get Only English:**")
        st.code('{"word": "ഒമക്കായ", "fields": ["english"]}', language="json")
        st.caption("→ Returns ONLY english")
    
    with col2:
        st.markdown("**Get English + South:**")
        st.code('{"word": "മുളക്", "fields": ["english", "south"]}', language="json")
        st.caption("→ Returns english + south")
        
        st.markdown("**Get All Regions:**")
        st.code('{"word": "വാഴപ്പഴം", "fields": ["south", "central", "north"]}', language="json")
        st.caption("→ Returns regions only (no english)")
    
    st.markdown("---")
    
    # ERROR HANDLING
    st.markdown("## ⚠️ Error Handling")
    
    st.markdown("### HTTP Status Codes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Status Codes:**
        - `200` - Success
        - `401` - Invalid API key
        - `404` - Word not found
        - `422` - Invalid request
        - `500` - Server error
        """)
    
    with col2:
        st.markdown("**Python Error Handling:**")
        st.code('''try:
    result = translate(word)
except requests.HTTPError as e:
    if e.response.status_code == 404:
        print("Word not found")
    elif e.response.status_code == 401:
        print("Invalid API key")
        ''', language="python")
    
    st.markdown("---")
    
    # BEST PRACTICES
    st.markdown("## 💡 Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Security:**
        - Use environment variables for API keys
        - Never expose keys in client-side code
        - Rotate keys regularly
        - Revoke unused keys
        
        **Performance:**
        - Use field selection to reduce response size
        - Cache frequent translations
        - Set appropriate timeouts (10s recommended)
        - Implement retry logic for failures
        """)
    
    with col2:
        st.markdown("""
        **Code Quality:**
        - Validate input before API calls
        - Handle all error cases gracefully
        - Log requests for debugging
        - Use connection pooling for multiple requests
        
        **Monitoring:**
        - Track API usage in 🔑 API Access page
        - Monitor response times
        - Alert on repeated failures
        - Review error logs
        """)
    
    st.markdown("---")
    
    # QUICK REFERENCE
    st.markdown("## 📋 Quick Reference")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Endpoint:**")
        st.code("POST /api/v1/translate", language="text")
        
        st.markdown("**Headers:**")
        st.code("""X-API-Key: your_api_key
Content-Type: application/json""", language="text")
        
        st.markdown("**Request:**")
        st.code('''{
  "word": "string",
  "fields": ["string"]  // optional
}''', language="json")
    
    with col2:
        st.markdown("**Response:**")
        st.code('''{
  "input_word": "string",
  "english": "string",
  "south": ["string"],
  "central": ["string"],
  "north": ["string"],
  "source": "string"
}''', language="json")
        
        st.markdown("**Available Fields:**")
        st.code("""english
south
central
north""", language="text")
    
    st.markdown("---")
    
    # FOOTER
    st.success("""
    **✅ Ready to start?**
    
    1. Get your API key from **🔑 API Access** page
    2. Copy one of the code examples above
    3. Replace `your_api_key_here` with your actual key
    4. Start translating!
    """)
    
    st.info("""
    **Need help?**
    
    - Try the **🏠 Translator** page for live examples
    - Review your keys in **🔑 API Access**
    - Contact support if you encounter issues
    """)

# ============================================================================
# MAIN ROUTER
# ============================================================================

def main():
    """Main app router"""
    
    if st.session_state.page == 'main':
        main_page()
    elif st.session_state.page == 'api':
        api_page()
    elif st.session_state.page == 'docs':
        api_docs_page()
    elif st.session_state.page == 'admin':
        admin_page()

if __name__ == "__main__":
    main()

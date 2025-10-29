"""
Expect Miracles Superhero Generator
====================================
A Streamlit app that transforms event attendees into superheroes fighting cancer.
Built for live fundraising events with 350-500 attendees accessing via QR code.

Author: Expect Miracles Foundation
Tech Stack: Streamlit + OpenAI gpt-image-1
"""

import streamlit as st
from openai import OpenAI
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import os
import tempfile
import requests

# Import HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False

# ============================================================================
# PAGE CONFIGURATION - Must be the first Streamlit command
# ============================================================================
st.set_page_config(
    page_title="Expect Miracles - Superhero Generator",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CUSTOM CSS STYLING - Expect Miracles Branding
# ============================================================================
def apply_custom_css():
    """Apply custom CSS for mobile-first, branded design"""
    st.markdown("""
    <style>
    /* Brand colors: Navy (#1a237e), Blue (#3949ab), Gold (#ffd700), White */
    
    /* Force blue gradient background on all container elements */
    .stApp {
        background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
    }
    
    /* Main app background - blue gradient like reference images */
    .main {
        background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
        padding: 1rem;
        min-height: 100vh;
    }
    
    /* Streamlit's default block container */
    .block-container {
        background: transparent !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Override any white backgrounds */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
    }
    
    [data-testid="stHeader"] {
        background: transparent;
    }
    
    /* Only make text white when directly on blue background (not in cards) */
    .main > .block-container > div > div > div > p,
    .main > .block-container > div > div > div > h1,
    .main > .block-container > div > div > div > h2,
    .main > .block-container > div > div > div > h3 {
        color: white;
    }
    
    /* Header styling - keep white background with dark text */
    .header-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .header-container * {
        color: inherit;
    }
    
    .main-title {
        color: #1a237e !important;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #ffd700 !important;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .tagline {
        color: #666 !important;
        font-size: 1.1rem;
    }
    
    /* Card styling for main content - white cards with dark text */
    .content-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .content-card * {
        color: #333 !important;
    }
    
    .content-card h1, .content-card h2, .content-card h3 {
        color: #1a237e !important;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(90deg, #1a237e 0%, #3949ab 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        width: 100%;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #0d1642 0%, #283593 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Download button styling */
    .stDownloadButton>button {
        background: #ffd700;
        color: #1a237e;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        width: 100%;
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #ddd;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stSelectbox>div>div>select {
        border-radius: 10px;
        border: 2px solid #ddd;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: white;
        margin-top: 3rem;
        padding: 1rem;
        font-size: 0.9rem;
    }
    
    .footer p, .footer strong {
        color: white !important;
    }
    
    /* Info/warning boxes on blue background */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.8rem;
        }
        .subtitle {
            font-size: 1.2rem;
        }
        .content-card {
            padding: 1rem;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================
def init_session_state():
    """Initialize all session state variables"""
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    if 'generated_image_url' not in st.session_state:
        st.session_state.generated_image_url = None
    if 'first_name' not in st.session_state:
        st.session_state.first_name = ""
    if 'last_name' not in st.session_state:
        st.session_state.last_name = ""
    if 'accessory' not in st.session_state:
        st.session_state.accessory = "None"
    if 'openai_client' not in st.session_state:
        st.session_state.openai_client = None

# ============================================================================
# OPENAI API SETUP
# ============================================================================
def setup_openai():
    """Configure OpenAI API with secrets management"""
    try:
        # Get API key from secrets or environment
        if hasattr(st, 'secrets') and 'openai' in st.secrets:
            api_key = st.secrets['openai']['api_key']
        elif os.getenv('OPENAI_API_KEY'):
            api_key = os.getenv('OPENAI_API_KEY')
        else:
            return None
        
        if not api_key or not api_key.startswith('sk-'):
            return None
        
        # Create OpenAI client with minimal configuration
        client = OpenAI(api_key=api_key)
        return client
        
    except Exception as e:
        return None

# ============================================================================
# IMAGE PROCESSING FUNCTIONS
# ============================================================================
def image_to_base64(image):
    """Convert PIL Image to base64 string for API"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def save_generated_image(image_url, first_name):
    """
    Save generated image locally with timestamp
    Creates a 'generated_images' folder if it doesn't exist
    """
    try:
        # Create directory if it doesn't exist
        if not os.path.exists('generated_images'):
            os.makedirs('generated_images')
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_images/{first_name}_{timestamp}.png"
        
        # Note: In production, you'd download the image from the URL
        # For now, we'll just return the filename pattern
        return filename
    except Exception as e:
        st.warning(f"Could not save image locally: {e}")
        return None

# ============================================================================
# AI IMAGE GENERATION
# ============================================================================
def generate_superhero_image(uploaded_image, first_name, last_name, accessory):
    """
    Generate superhero action figure image using OpenAI gpt-image-1
    
    Parameters:
    - uploaded_image: PIL Image object
    - first_name: User's first name
    - last_name: User's last name
    - accessory: Selected accessory/prop
    
    Returns:
    - image_url: URL of generated image or None if failed
    """
    
    # Get OpenAI client from session state
    if 'openai_client' not in st.session_state or st.session_state.openai_client is None:
        st.error("OpenAI client not initialized")
        return None
    
    client = st.session_state.openai_client
    
    # Build full name for display
    full_name = f"{first_name} {last_name}"
    
    # Build accessories text based on user selection
    if accessory == "None":
        accessories_text = "No additional accessories are needed - just the figure in confident heroic pose."
    elif accessory == "Golf Club":
        accessories_text = "Include two accessories: a golf club and a golf ball — both neatly positioned in the packaging alongside the figure."
    elif accessory == "Tennis Racket":
        accessories_text = "Include two accessories: a tennis racket and a tennis ball — both neatly positioned in the packaging alongside the figure."
    elif accessory == "Stethoscope":
        accessories_text = "Include two accessories: a stethoscope and a medical bag — both neatly positioned in the packaging alongside the figure."
    elif accessory == "Basketball":
        accessories_text = "Include two accessories: a basketball and a sports drink — both neatly positioned in the packaging alongside the figure."
    elif accessory == "Camera":
        accessories_text = "Include two accessories: a professional camera and photography equipment — both neatly positioned in the packaging alongside the figure."
    elif accessory == "Microphone":
        accessories_text = "Include two accessories: a microphone and a speaker — both neatly positioned in the packaging alongside the figure."
    elif accessory == "Chef's Hat":
        accessories_text = "Include two accessories: a chef's hat and cooking utensils — both neatly positioned in the packaging alongside the figure."
    elif accessory == "Artist's Paintbrush":
        accessories_text = "Include two accessories: a paintbrush and an art palette — both neatly positioned in the packaging alongside the figure."
    elif accessory == "Laptop":
        accessories_text = "Include two accessories: a laptop and tech gadgets — both neatly positioned in the packaging alongside the figure."
    elif accessory == "Music Instrument":
        accessories_text = "Include two accessories: a musical instrument and headphones — both neatly positioned in the packaging alongside the figure."
    else:
        accessories_text = f"Include accessories: {accessory.lower()} — neatly positioned in the packaging alongside the figure."
    
    # Create the prompt for gpt-image-1
    prompt = f"""Create a realistic, store-ready action figure of a person named {full_name}, based on the uploaded reference image. 
The final result should look like a premium Hasbro or Marvel Legends collectible toy photographed for retail packaging.

Packaging Design:
- Vertical portrait orientation, resembling authentic toy box packaging.
- {full_name}'s figure should appear centered inside a clear plastic blister on a sturdy cardboard backing.
- Prominently display the phrase "I'M TAKING ACTION AGAINST CANCER" near the top or middle of the box in bold, inspiring, heroic typography.
- Include the name "{full_name}" clearly visible on the packaging.
- Include stylish brand-like markings and subtle charity branding (without logos).
- The background should be vibrant and motivational — glowing gradients, heroic energy bursts, or metallic blues and golds that evoke hope and strength.

Action Figure Details:
- Maintain {full_name}'s exact facial likeness from the uploaded photo.
- Keep the person in their actual clothing from the photo (do not change outfits).
- Give them a confident, heroic stance with strong lighting and realistic reflections.
- Ensure the figure accurately represents the person's appearance, gender, hair, and style from the reference image.
- {accessories_text}
- Ensure realistic lighting, materials, and shadows so the scene looks like a professional product photo.

Overall Style:
- Photorealistic finish with professional toy photography quality.
- Clean edges, clear focus, and rich textures.
- Ready-for-market presentation — bold, inspiring, and polished.
- The figure should look like a collectible action figure of a real person, not a fictional character."""
    
    try:
        # Convert PIL Image to bytes for upload with proper format
        import io
        img_byte_arr = io.BytesIO()
        
        # Convert to RGB if needed (removes alpha channel)
        if uploaded_image.mode == 'RGBA':
            uploaded_image = uploaded_image.convert('RGB')
        
        # Save as PNG
        uploaded_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Give the BytesIO object a name attribute so the API recognizes it as a PNG file
        img_byte_arr.name = "uploaded_image.png"
        
        # Show progress to user
        with st.spinner("🦸 Transforming you into a superhero action figure... This may take 30-60 seconds..."):
            # Call OpenAI gpt-image-1 API with image editing
            response = client.images.edit(
                model="gpt-image-1",
                image=img_byte_arr,
                prompt=prompt,
                size="1024x1536",
                n=1
            )
            
            # Extract image from response
            image_url = None
            
            if hasattr(response.data[0], 'url') and response.data[0].url:
                image_url = response.data[0].url
            elif hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
                # Convert base64 to data URL
                image_base64 = response.data[0].b64_json
                image_url = f"data:image/png;base64,{image_base64}"
            
            if not image_url:
                st.error("❌ Could not extract image from response")
                return None
            
            # Save image reference
            save_generated_image(image_url, first_name)
            
            return image_url
            
    except Exception as e:
        st.error(f"⚠️ Image Generation Error: {str(e)}")
        
        # Show full error details
        st.markdown("### 🔍 Error Details:")
        import traceback
        error_details = traceback.format_exc()
        st.code(error_details, language="python")
        
        # Show debugging info
        st.markdown("### 🐛 Debug Information:")
        st.write(f"- First Name: {first_name}")
        st.write(f"- Last Name: {last_name}")
        st.write(f"- Full Name: {full_name}")
        st.write(f"- Accessory: {accessory}")
        st.write(f"- Image Mode: {uploaded_image.mode}")
        st.write(f"- Image Size: {uploaded_image.size}")
        
        return None

# ============================================================================
# UI COMPONENTS
# ============================================================================
def render_header():
    """Render the app header with branding"""
    st.markdown("""
    <div class="header-container">
        <div class="main-title">💪 Take Action Against Cancer</div>
        <div class="subtitle">Become a Superhero and Join the Fight</div>
        <div class="tagline">Transform yourself into a hero fighting for cancer research</div>
    </div>
    """, unsafe_allow_html=True)

def render_step_indicator(current_step):
    """Render step progress indicator"""
    
    # Using Streamlit columns instead of HTML for better compatibility
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    steps = [
        (col1, "1", "Upload", 1),
        (col2, "2", "Details", 2),
        (col3, "3", "Generate", 3),
        (col4, "4", "Share", 4)
    ]
    
    for col, num, label, step_num in steps:
        with col:
            # Determine if step is active
            if step_num <= current_step:
                # Active step - cyan background
                st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="
                            width: 50px;
                            height: 50px;
                            border-radius: 50%;
                            background: #00d4ff;
                            color: white;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: bold;
                            font-size: 1.2rem;
                            margin: 0 auto;
                        ">{num}</div>
                        <div style="color: white; margin-top: 0.5rem; font-size: 0.9rem;">{label}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Inactive step - gray background
                st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="
                            width: 50px;
                            height: 50px;
                            border-radius: 50%;
                            background: #ddd;
                            color: #999;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: bold;
                            font-size: 1.2rem;
                            margin: 0 auto;
                        ">{num}</div>
                        <div style="color: white; margin-top: 0.5rem; font-size: 0.9rem;">{label}</div>
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

def render_footer():
    """Render app footer"""
    st.markdown("""
    <div class="footer">
        <p>Powered by <strong>Expect Miracles Foundation</strong> | Built with Streamlit & OpenAI</p>
        <p>Every superhero created supports cancer research and brings hope to families affected by cancer.</p>
        <p>© 2025 Expect Miracles Foundation - All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN APP STEPS
# ============================================================================
def step_1_upload():
    """Step 1: Photo Upload"""
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    st.markdown("### 📸 Step 1: Upload Your Photo")
    st.markdown("Choose a clear photo of yourself for the best superhero transformation")
    
    # Add helpful tips for best results
    st.info("💡 **Best Results:** Use a clear headshot or upper-body photo with good lighting and a plain background. Professional headshots work great!")
    
    # Determine accepted file types based on HEIC support
    if HEIC_SUPPORTED:
        file_types = ['png', 'jpg', 'jpeg', 'heic', 'heif']
        help_text = "JPG, PNG, HEIC up to 10MB - iPhone photos supported!"
    else:
        file_types = ['png', 'jpg', 'jpeg']
        help_text = "JPG, PNG up to 10MB"
        st.warning("⚠️ HEIC support not available. iPhone users: Convert HEIC to JPG before uploading, or the app will attempt automatic conversion.")
    
    # File uploader with camera support for mobile
    uploaded_file = st.file_uploader(
        "Take a photo or upload from your device",
        type=file_types,
        help=help_text,
        key="photo_upload"
    )
    
    if uploaded_file is not None:
        try:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            
            # Convert HEIC to RGB if needed
            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGB')
            
            st.image(image, caption="Your Photo", width='stretch')
            
            # Store in session state
            st.session_state.uploaded_image = image
            
            # Button to proceed
            if st.button("✅ Continue to Personal Details", key="continue_to_step2"):
                st.session_state.step = 2
                st.rerun()
        except Exception as e:
            st.error(f"⚠️ Error loading image: {e}")
            st.info("💡 If you're uploading a HEIC file from iPhone, try converting it to JPG first.")
    else:
        st.info("👆 Tap above to take a photo or select one from your device")
    
    st.markdown('</div>', unsafe_allow_html=True)

def step_2_details():
    """Step 2: Personal Details"""
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    st.markdown("### 🦸 Step 2: Your Details")
    st.markdown("Tell us about yourself to create your unique superhero identity")
    
    # Show uploaded image thumbnail
    if st.session_state.uploaded_image:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(st.session_state.uploaded_image, caption="Your Photo", width=200)
    
    # Name input fields - First and Last name side by side
    col1, col2 = st.columns(2)
    
    with col1:
        first_name = st.text_input(
            "First Name *",
            value=st.session_state.first_name,
            placeholder="e.g., Sarah",
            help="Required - this will appear on your action figure",
            key="first_name_input"
        )
    
    with col2:
        last_name = st.text_input(
            "Last Name *",
            value=st.session_state.last_name,
            placeholder="e.g., Johnson",
            help="Required - this will appear on your action figure",
            key="last_name_input"
        )
    
    # Accessory selection
    accessory_options = [
        "None",
        "Golf Club",
        "Tennis Racket",
        "Stethoscope",
        "Basketball",
        "Camera",
        "Microphone",
        "Chef's Hat",
        "Artist's Paintbrush",
        "Laptop",
        "Music Instrument"
    ]
    
    accessory = st.selectbox(
        "Choose Your Superhero Accessory (Optional)",
        options=accessory_options,
        help="These will be incorporated into your action figure packaging!",
        key="accessory_select"
    )
    
    if accessory == "None":
        st.info("💡 **Tip:** Selecting an accessory will add themed items to your action figure packaging!")
    else:
        st.info(f"💡 **Selected:** Your action figure will include a {accessory.lower()} and related accessories!")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Photo", key="back_to_step1"):
            st.session_state.step = 1
            st.rerun()
    
    with col2:
        if st.button("🚀 Generate My Superhero!", key="generate_button", type="primary"):
            if not first_name.strip():
                st.error("⚠️ Please enter your first name to continue")
            elif not last_name.strip():
                st.error("⚠️ Please enter your last name to continue")
            else:
                # Save to session state
                st.session_state.first_name = first_name
                st.session_state.last_name = last_name
                st.session_state.accessory = accessory
                st.session_state.step = 3
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def step_3_generate():
    """Step 3: Generate Superhero Image"""
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    # Auto-generate if not already generated
    if st.session_state.generated_image_url is None:
        st.markdown("### ⚡ Generating Your Superhero...")
        
        # Generate the image
        try:
            image_url = generate_superhero_image(
                st.session_state.uploaded_image,
                st.session_state.first_name,
                st.session_state.last_name,
                st.session_state.accessory
            )
            
            if image_url:
                st.session_state.generated_image_url = image_url
                st.session_state.step = 4
                st.rerun()
            else:
                # Error occurred - the error details should have been shown
                st.error("❌ Generation returned no image. Check error details above.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Try Again", key="retry_generation"):
                        st.rerun()
                with col2:
                    if st.button("⬅️ Back to Details", key="back_to_details_from_error"):
                        st.session_state.step = 2
                        st.rerun()
        except Exception as e:
            st.error(f"❌ Critical error during generation: {e}")
            import traceback
            st.code(traceback.format_exc())
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Try Again", key="retry_generation_exception"):
                    st.rerun()
            with col2:
                if st.button("⬅️ Back to Details", key="back_to_details_exception"):
                    st.session_state.step = 2
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def step_4_share():
    """Step 4: Display and Share Results"""
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    st.markdown(f"### 🎉 Congratulations, {st.session_state.first_name} {st.session_state.last_name}!")
    st.markdown("**You are now a superhero in the fight against cancer!**")
    
    # Display the generated image
    if st.session_state.generated_image_url:
        st.image(
            st.session_state.generated_image_url,
            caption=f"{st.session_state.first_name} {st.session_state.last_name} - Cancer Fighting Superhero",
            width='stretch'
        )
        
        st.markdown("---")
        
        # Action buttons
        st.markdown("### 📤 Share Your Superhero")
        
        # Download button - Handle both URL and base64 data
        try:
            # Check if we need to prepare the image for download
            if 'downloaded_image' not in st.session_state:
                image_data = None
                
                # Check if it's a data URL (base64)
                if st.session_state.generated_image_url.startswith('data:image'):
                    # Extract base64 data from data URL
                    # Format: data:image/png;base64,ACTUALBASE64DATA
                    base64_data = st.session_state.generated_image_url.split(',', 1)[1]
                    image_data = base64.b64decode(base64_data)
                    st.session_state.downloaded_image = image_data
                else:
                    # It's a regular URL - download it
                    with st.spinner("Preparing download..."):
                        response = requests.get(st.session_state.generated_image_url, timeout=10)
                        response.raise_for_status()
                        st.session_state.downloaded_image = response.content
            
            # Create download button with the prepared image data
            st.download_button(
                label="📥 Download Your Action Figure",
                data=st.session_state.downloaded_image,
                file_name=f"{st.session_state.first_name}_{st.session_state.last_name}_action_figure.png",
                mime="image/png",
                key="download_image",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Unable to prepare download: {str(e)[:100]}")
            # Fallback: right-click to save
            st.markdown("**Alternative Download Method:**")
            st.markdown("Right-click the image above and select 'Save Image As...'")
        
        st.markdown("---")
        
        # Social sharing instructions
        st.markdown("### 📱 Share on Social Media")
        
        st.info("💡 **How to Share:**\n1. Download your action figure image using the button above\n2. Share it on your favorite social media platform\n3. Use the hashtags: #ExpectMiracles #CancerResearch #TakeAction")
        
        # LinkedIn sharing instructions
        with st.expander("📱 Share on LinkedIn"):
            st.markdown("""
            **To share on LinkedIn:**
            1. Click the download button above
            2. Go to [LinkedIn.com](https://www.linkedin.com)
            3. Click "Start a post"
            4. Upload your downloaded image
            5. Add this message:
            
            *"I just became a superhero in the fight against cancer with Expect Miracles Foundation! Join me in taking action against cancer. #ExpectMiracles #CancerResearch #TakeAction"*
            """)
        
        # Email sharing
        with st.expander("📧 Share via Email"):
            st.markdown("""
            **To share via email:**
            1. Download your action figure image
            2. Compose a new email
            3. Attach the downloaded image
            4. Share your story about taking action against cancer!
            """)
        
        st.markdown("---")
        
        # Create another
        if st.button("🔄 Create Another Superhero", key="create_another"):
            # Reset session state including downloaded image
            st.session_state.step = 1
            st.session_state.uploaded_image = None
            st.session_state.generated_image_url = None
            st.session_state.first_name = ""
            st.session_state.last_name = ""
            st.session_state.accessory = "None"
            if 'downloaded_image' in st.session_state:
                del st.session_state.downloaded_image
            st.rerun()
        
        st.success("✨ Thank you for joining the fight against cancer!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MAIN APP FLOW
# ============================================================================
def main():
    """Main application function"""
    
    # Apply custom styling
    apply_custom_css()
    
    # Initialize session state FIRST
    init_session_state()
    
    # Setup OpenAI client if not already done
    if st.session_state.openai_client is None:
        st.session_state.openai_client = setup_openai()
    
    # Render header
    render_header()
    
    # Show status message based on API configuration (simpler version)
    if st.session_state.openai_client is not None:
        st.success("✅ **API Connected**: Ready to generate superhero images!")
    else:
        st.error("⚠️ **API Not Configured**: Please check your OpenAI API key configuration.")
    
    # Render step indicator
    render_step_indicator(st.session_state.step)
    
    # Route to appropriate step
    if st.session_state.step == 1:
        step_1_upload()
    elif st.session_state.step == 2:
        step_2_details()
    elif st.session_state.step == 3:
        step_3_generate()
    elif st.session_state.step == 4:
        step_4_share()
    
    # Render footer
    render_footer()

# ============================================================================
# RUN APP
# ============================================================================
if __name__ == "__main__":
    main()
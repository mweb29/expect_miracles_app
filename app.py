"""
Expect Miracles Superhero Generator
====================================
A Streamlit app that transforms event attendees into superheroes fighting cancer.
Built for live fundraising events with 350-500 attendees accessing via QR code.

Author: Expect Miracles Foundation
Tech Stack: Streamlit + OpenAI DALL-E 3
"""

import streamlit as st
from openai import OpenAI
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import os
import tempfile

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
        # Debug: Check what's available
        api_key = None
        
        # Try to get from Streamlit secrets
        if hasattr(st, 'secrets') and 'openai' in st.secrets:
            api_key = st.secrets['openai']['api_key']
            st.info(f"🔍 Found API key in secrets (starts with: {api_key[:10]}...)")
        # Try environment variable
        elif os.getenv('OPENAI_API_KEY'):
            api_key = os.getenv('OPENAI_API_KEY')
            st.info(f"🔍 Found API key in environment (starts with: {api_key[:10]}...)")
        else:
            st.error("❌ No API key found in secrets.toml or environment variables")
            return None
        
        if not api_key or not api_key.startswith('sk-'):
            st.error(f"❌ Invalid API key format. Key should start with 'sk-' but got: {api_key[:10] if api_key else 'None'}...")
            return None
        
        # Create OpenAI client with minimal configuration
        client = OpenAI(api_key=api_key)
        st.success("✅ OpenAI client created successfully")
        return client
        
    except Exception as e:
        st.error(f"⚠️ Error configuring OpenAI: {str(e)}")
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
    Generate superhero action figure image using OpenAI DALL-E 3
    
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
        accessories_text = ""
        accessories_instruction = "- No additional accessories included in the blister pack"
    elif accessory == "Golf Club":
        accessories_text = "golf club and golf ball"
        accessories_instruction = f"- Display these accessories next to the figure in the blister pack: {accessories_text}"
    elif accessory == "Tennis Racket":
        accessories_text = "tennis racket and tennis ball"
        accessories_instruction = f"- Display these accessories next to the figure in the blister pack: {accessories_text}"
    elif accessory == "Stethoscope":
        accessories_text = "stethoscope and medical bag"
        accessories_instruction = f"- Display these accessories next to the figure in the blister pack: {accessories_text}"
    elif accessory == "Basketball":
        accessories_text = "basketball and sports drink"
        accessories_instruction = f"- Display these accessories next to the figure in the blister pack: {accessories_text}"
    elif accessory == "Camera":
        accessories_text = "camera and photography equipment"
        accessories_instruction = f"- Display these accessories next to the figure in the blister pack: {accessories_text}"
    elif accessory == "Microphone":
        accessories_text = "microphone and speaker"
        accessories_instruction = f"- Display these accessories next to the figure in the blister pack: {accessories_text}"
    elif accessory == "Chef's Hat":
        accessories_text = "chef's hat and cooking utensils"
        accessories_instruction = f"- Display these accessories next to the figure in the blister pack: {accessories_text}"
    elif accessory == "Artist's Paintbrush":
        accessories_text = "paintbrush and art palette"
        accessories_instruction = f"- Display these accessories next to the figure in the blister pack: {accessories_text}"
    elif accessory == "Laptop":
        accessories_text = "laptop and tech gadgets"
        accessories_instruction = f"- Display these accessories next to the figure in the blister pack: {accessories_text}"
    elif accessory == "Music Instrument":
        accessories_text = "musical instrument and headphones"
        accessories_instruction = f"- Display these accessories next to the figure in the blister pack: {accessories_text}"
    else:
        accessories_text = f"{accessory.lower()} and related equipment"
        accessories_instruction = f"- Display these accessories next to the figure in the blister pack: {accessories_text}"
    
    # Use the vintage-style prompt with Expect Miracles color scheme
    prompt = f"""Create a vintage-style retail action figure package design based on the uploaded photo. This is for a cancer charity event with the theme "Taking Action Against Cancer."

CRITICAL REQUIREMENTS:
- The action figure MUST accurately represent the person in the uploaded photo - matching their gender, appearance, facial features, hair color and style, and clothing
- The package should face directly forward (front view), not at an angle
- Style: Classic 1970s-80s action figure packaging (similar to vintage Kenner or Mego toys) - simple, nostalgic, retro aesthetic
- The figure should look realistic and lifelike, representing the actual person
- Only include text that is specifically requested below - no other words or phrases

PACKAGING DESIGN:
- Retro blister pack style with clear plastic bubble showing the figure
- Simple cardboard backing with rounded corners
- Color palette: Navy blue and gold/yellow accents (Expect Miracles brand colors) with warm vintage tones
- Clean, straightforward design - not cluttered or busy
- Front-facing orientation (viewer looking directly at the front of the package)

PACKAGING TEXT (ONLY THESE):
- Name at top: "{full_name}"
- Main phrase somewhere on package: "I'M TAKING ACTION AGAINST CANCER"
- Small label: "ACTION FIGURE"
- No other text, descriptions, warnings, or fine print

INCLUDED ACCESSORIES:
{accessories_instruction}

DESIGN SPECIFICATIONS:
- Vintage toy aesthetic - simple and iconic
- The figure should be dressed in casual/normal clothing (as shown in the photo)
- Bold, inspiring but tasteful presentation
- Do NOT depict cancer cells or medical imagery
- Professional product photography lighting
- Make it look like a collectible from a classic toy line

Create a nostalgic, store-ready design that captures the charm of vintage action figure packaging with navy blue and gold color scheme."""
    
    try:
        # Show progress to user
        with st.spinner("🦸 Transforming you into a vintage action figure... This may take 30-60 seconds..."):
            # Call OpenAI DALL-E 3 API
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",  # High quality square image
                quality="standard",  # Can use "hd" for better quality but slower
                n=1,
            )
            
            # Extract image URL from response
            image_url = response.data[0].url
            
            # Save image reference
            save_generated_image(image_url, first_name)
            
            return image_url
            
    except Exception as e:
        st.error(f"⚠️ Our hero factory is taking a short break — please try again! (Error: {e})")
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
    
    # File uploader with camera support for mobile
    uploaded_file = st.file_uploader(
        "Take a photo or upload from your device",
        type=['png', 'jpg', 'jpeg'],
        help="JPG, PNG up to 10MB",
        key="photo_upload"
    )
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Your Photo", use_container_width=True)
        
        # Store in session state
        st.session_state.uploaded_image = image
        
        # Button to proceed
        if st.button("✅ Continue to Personal Details", key="continue_to_step2"):
            st.session_state.step = 2
            st.rerun()
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
            # Error occurred
            st.error("Generation failed. Please try again.")
            if st.button("🔄 Try Again", key="retry_generation"):
                st.rerun()
            if st.button("⬅️ Back to Details", key="back_to_details_from_error"):
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
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Action buttons
        st.markdown("### 📤 Share Your Superhero")
        
        # Download button (note: direct download from URL requires additional handling)
        st.markdown(f"[📥 Download Image]({st.session_state.generated_image_url})")
        
        # LinkedIn share
        linkedin_text = f"I just became a superhero in the fight against cancer with Expect Miracles Foundation! Join me in taking action against cancer. #ExpectMiracles #CancerResearch #TakeAction"
        linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={st.session_state.generated_image_url}"
        
        if st.button("📱 Share to LinkedIn", key="linkedin_share"):
            st.markdown(f"[Click here to share on LinkedIn]({linkedin_url})")
        
        # Email option
        email_subject = "I'm a Superhero Fighting Cancer!"
        email_body = f"Check out my superhero transformation with Expect Miracles Foundation! {st.session_state.generated_image_url}"
        mailto_link = f"mailto:?subject={email_subject}&body={email_body}"
        
        if st.button("📧 Email This Image", key="email_share"):
            st.markdown(f"[Click here to email]({mailto_link})")
        
        st.markdown("---")
        
        # Create another
        if st.button("🔄 Create Another Superhero", key="create_another"):
            # Reset session state
            st.session_state.step = 1
            st.session_state.uploaded_image = None
            st.session_state.generated_image_url = None
            st.session_state.first_name = ""
            st.session_state.last_name = ""
            st.session_state.accessory = "None"
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
    
    # Show status message based on API configuration
    if st.session_state.openai_client is not None:
        st.success("✅ **API Connected**: Ready to generate superhero images!")
    else:
        st.warning("⚠️ **API Not Configured**: Add your OpenAI API key to `.streamlit/secrets.toml` to enable image generation.")
        st.code("""
# Create .streamlit/secrets.toml with:
[openai]
api_key = "sk-your-api-key-here"
        """)
    
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
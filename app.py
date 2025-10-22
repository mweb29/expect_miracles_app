"""
Expect Miracles Superhero Generator
====================================
A Streamlit app that transforms event attendees into superheroes fighting cancer.
Built for live fundraising events with 350-500 attendees accessing via QR code.

Author: Expect Miracles Foundation
Tech Stack: Streamlit + OpenAI DALL-E 3
"""

import streamlit as st
import openai
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
    /* Brand colors: Navy (#1a237e), Gold (#ffd700), White */
    
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%);
        padding: 1rem;
    }
    
    /* Header styling */
    .header-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-title {
        color: #1a237e;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #ffd700;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .tagline {
        color: #666;
        font-size: 1.1rem;
    }
    
    /* Card styling for main content */
    .content-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Step indicator */
    .step-indicator {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 2rem auto;
        padding: 1rem;
        max-width: 600px;
    }
    
    .step-indicator > div {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
    }
    
    .step {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    .step-active {
        background: #00d4ff;
        color: white;
    }
    
    .step-inactive {
        background: #ddd;
        color: #999;
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
    if 'accessory' not in st.session_state:
        st.session_state.accessory = "None"

# ============================================================================
# OPENAI API SETUP
# ============================================================================
def setup_openai():
    """Configure OpenAI API with secrets management"""
    # INTERFACE DEVELOPMENT MODE: Always return True to bypass API check
    # This allows you to work on the interface without an API key
    return True
    
    # COMMENTED OUT FOR INTERFACE DEVELOPMENT
    # Uncomment this section when ready to enable API functionality
    # try:
    #     # In production, use Streamlit secrets
    #     if 'openai' in st.secrets:
    #         openai.api_key = st.secrets['openai']['api_key']
    #     else:
    #         # Fallback for local development
    #         openai.api_key = os.getenv('OPENAI_API_KEY')
    #     return True
    # except Exception as e:
    #     st.error(f"⚠️ OpenAI API key not configured. Please add it to secrets.toml")
    #     return False

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
def generate_superhero_image(uploaded_image, first_name, accessory):
    """
    Generate superhero image using OpenAI DALL-E 3
    
    Parameters:
    - uploaded_image: PIL Image object
    - first_name: User's first name
    - accessory: Selected accessory/prop
    
    Returns:
    - image_url: URL of generated image or None if failed
    """
    
    # Build the prompt based on user inputs
    accessory_text = f" holding a {accessory}" if accessory != "None" else ""
    
    prompt = f"""Create a heroic, inspiring portrait of a person{accessory_text} standing confidently 
    as a superhero fighting against cancer. The scene should be uplifting and powerful, 
    with a vibrant background featuring symbolic elements like:
    - Hope and strength imagery (light rays, empowering colors)
    - Subtle cancer awareness elements (ribbons, medical symbols)
    - A heroic, determined pose
    
    Style: Photorealistic, professional, inspiring, full of positive energy.
    The person should look confident and heroic, ready to take action against cancer.
    Make it look like a professional superhero portrait with warm, hopeful lighting.
    
    Name to incorporate (subtle text or as inspiration): {first_name}"""
    
    try:
        # Show progress to user
        with st.spinner("🦸 Transforming you into a superhero... This may take 30-60 seconds..."):
            # Call OpenAI DALL-E 3 API
            response = openai.images.generate(
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
            
    except openai.APIError as e:
        st.error(f"⚠️ OpenAI API error: {e}")
        return None
    except openai.RateLimitError:
        st.error("⚠️ Our hero factory is experiencing high demand. Please try again in a moment!")
        return None
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
                        <div style="color: black; margin-top: 0.5rem; font-size: 0.9rem;">{label}</div>
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
                        <div style="color: black; margin-top: 0.5rem; font-size: 0.9rem;">{label}</div>
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
    
    st.markdown("### Step 1: Upload Your Photo")
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
    
    st.markdown("### Step 2: Your Details")
    st.markdown("Tell us about yourself to create your unique superhero identity")
    
    # Show uploaded image thumbnail
    if st.session_state.uploaded_image:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(st.session_state.uploaded_image, caption="Your Photo", width=200)
    
    # Input fields
    first_name = st.text_input(
        "First Name *",
        value=st.session_state.first_name,
        placeholder="e.g., Sarah",
        help="Required - this will personalize your superhero",
        key="first_name_input"
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
        help="These will determine your superhero tools and weapons!",
        key="accessory_select"
    )
    
    st.info("💡 **Tip:** Your accessory will be incorporated into your superhero image!")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Photo", key="back_to_step1"):
            st.session_state.step = 1
            st.rerun()
    
    with col2:
        if st.button("Generate My Superhero!", key="generate_button", type="primary"):
            if not first_name.strip():
                st.error("⚠️ Please enter your first name to continue")
            else:
                # Save to session state
                st.session_state.first_name = first_name
                st.session_state.accessory = accessory
                st.session_state.step = 3
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def step_3_generate():
    """Step 3: Generate Superhero Image"""
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    # COMMENTED OUT FOR INTERFACE DEVELOPMENT
    # Auto-generate if not already generated
    # if st.session_state.generated_image_url is None:
    #     st.markdown("### ⚡ Generating Your Superhero...")
    #     
    #     # Generate the image
    #     image_url = generate_superhero_image(
    #         st.session_state.uploaded_image,
    #         st.session_state.first_name,
    #         st.session_state.accessory
    #     )
    #     
    #     if image_url:
    #         st.session_state.generated_image_url = image_url
    #         st.session_state.step = 4
    #         st.rerun()
    #     else:
    #         # Error occurred
    #         st.error("Generation failed. Please try again.")
    #         if st.button("🔄 Try Again", key="retry_generation"):
    #             st.rerun()
    #         if st.button("⬅️ Back to Details", key="back_to_details_from_error"):
    #             st.session_state.step = 2
    #             st.rerun()
    
    # TEMPORARY: Skip to step 4 for interface testing
    st.markdown("### ⚡ Generating Your Superhero...")
    st.info("**Interface Testing Mode**: Image generation is disabled. Click below to preview the results page.")
    
    if st.button("⏭️ Skip to Results Page (Testing)", key="skip_to_results"):
        # Use a placeholder image URL for testing
        st.session_state.generated_image_url = "https://via.placeholder.com/1024x1024.png?text=Your+Superhero+Image"
        st.session_state.step = 4
        st.rerun()
    
    if st.button("⬅️ Back to Details", key="back_to_details_from_generate"):
        st.session_state.step = 2
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def step_4_share():
    """Step 4: Display and Share Results"""
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    st.markdown(f"### 🎉 Congratulations, {st.session_state.first_name}!")
    st.markdown("**You are now a superhero in the fight against cancer!**")
    
    # Display the generated image
    if st.session_state.generated_image_url:
        st.image(
            st.session_state.generated_image_url,
            caption=f"{st.session_state.first_name} - Cancer Fighting Superhero",
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
    
    # Initialize session state
    init_session_state()
    
    # Setup OpenAI (always returns True in interface development mode)
    api_configured = setup_openai()
    
    # Render header
    render_header()
    
    # Show interface development mode notice
    st.info("🎨 **Interface Development Mode Active**: You can design and test the full interface without an API key. Image generation is disabled.")
    
    # Render step indicator
    render_step_indicator(st.session_state.step)
    
    # Always show the interface - no API check blocking
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
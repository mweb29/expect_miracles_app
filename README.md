# Expect Miracles - Superhero Generator 💪

A Streamlit web application that transforms event attendees into superheroes fighting cancer. Built for live fundraising events with 350-500 attendees accessing via QR code.

## About

The Expect Miracles Superhero Generator is an interactive web app designed for the Expect Miracles Foundation's fundraising events. Attendees can upload their photos and transform into cancer-fighting superhero action figures using AI-powered image generation.

**Key Features:**
- **Mobile-First Design:** Optimized for smartphones with responsive UI
- **AI-Powered Transformation:** Uses OpenAI's gpt-image-1 model to create realistic action figure packaging
- **4-Step Process:** Upload photo → Enter details → Generate → Share
- **HEIC Support:** Native support for iPhone photos (HEIC/HEIF format)
- **11 Accessory Options:** Golf club, tennis racket, stethoscope, basketball, camera, microphone, chef's hat, paintbrush, laptop, music instrument, or none
- **Social Sharing:** LinkedIn, email, and direct download capabilities
- **Branded Experience:** Navy blue gradient background with Expect Miracles Foundation colors
- **Portrait Orientation:** Creates 1024x1536 action figure packaging images

**Tech Stack:**
- **Frontend Framework:** Streamlit 1.28+
- **AI Image Generation:** OpenAI gpt-image-1 API (image editing model)
- **Image Processing:** Pillow (PIL) with HEIC support via pillow-heif
- **Language:** Python 3.8+
- **Additional Libraries:** python-dotenv, requests, qrcode

## Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one at https://platform.openai.com/api-keys)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mweb29/expect_miracles_app.git
cd expect_miracles_app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your OpenAI API key:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

4. Edit `.streamlit/secrets.toml` and add your OpenAI API key:
```toml
[openai]
api_key = "your-actual-api-key-here"
```

### Running the App

Start the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### For Event Deployment

For live events, deploy to Streamlit Community Cloud or another hosting platform:

1. Push your code to GitHub
2. Go to https://streamlit.io/cloud
3. Connect your repository
4. Add your OpenAI API key in the Streamlit Cloud secrets
5. Deploy and share the generated URL via QR code

## Project Structure

```
expect_miracles_app/
├── app.py                          # Main Streamlit application
├── generate_qr.py                  # QR code generator for events
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── .streamlit/
│   └── secrets.toml.example        # Example secrets configuration
└── README.md                       # This file
```

## Usage

### Step-by-Step Process

1. **Step 1 - Upload Photo**:
   - Take a selfie or upload an existing photo
   - Supports JPG, PNG, and HEIC formats (iPhone photos work natively)
   - Best results with clear headshots or upper-body photos with good lighting

2. **Step 2 - Enter Details**:
   - Provide your **first name** (required)
   - Provide your **last name** (required)
   - Select an optional superhero accessory from 11 options:
     - None (no accessories)
     - Golf Club (includes golf ball)
     - Tennis Racket (includes tennis ball)
     - Stethoscope (includes medical bag)
     - Basketball (includes sports drink)
     - Camera (includes photography equipment)
     - Microphone (includes speaker)
     - Chef's Hat (includes cooking utensils)
     - Artist's Paintbrush (includes art palette)
     - Laptop (includes tech gadgets)
     - Music Instrument (includes headphones)

3. **Step 3 - Generate**:
   - AI automatically generates your superhero action figure
   - Takes approximately 30-60 seconds
   - Creates a realistic action figure packaging with:
     - Your exact facial likeness
     - Your actual clothing from the photo
     - "I'M TAKING ACTION AGAINST CANCER" message
     - Your name prominently displayed
     - Selected accessories in packaging

4. **Step 4 - Share**:
   - Download your superhero image
   - Share to LinkedIn with pre-written message
   - Send via email
   - Create another superhero (resets the process)

## QR Code Generator for Events

The `generate_qr.py` script creates branded QR codes for your event in multiple sizes.

### Generate QR Codes

1. Deploy your Streamlit app and get the URL
2. Update the `APP_URL` in `generate_qr.py`
3. Run the generator:

```bash
pip install qrcode[pil]
python generate_qr.py
```

This will create three QR code sizes:
- **Standard** (300px): Perfect for table tents and handouts (3x5 inches)
- **Large** (600px): Ideal for posters and banners (11x17 inches)
- **Poster** (900px): Best for large displays and projection (24x36 inches)

### QR Code Features

- Branded in Expect Miracles colors (Navy blue on white)
- Rounded corners for modern appearance
- High error correction for reliable scanning
- Optimized for print at 300 DPI

### Printing Tips

- Print at 300 DPI for best quality
- Use high-quality cardstock for table tents
- Test QR codes before printing large quantities
- Include a short URL or text backup below the QR code

## Configuration

### API Settings

The app uses OpenAI's **gpt-image-1** model with the following settings:
- **Model:** gpt-image-1 (image editing model)
- **API Endpoint:** `client.images.edit()`
- **Size:** 1024x1536 pixels (portrait orientation for action figure packaging)
- **Input Format:** PNG (automatically converted from uploaded images)
- **Generation Time:** Approximately 30-60 seconds per image

**Important Notes:**
- The app uses the `images.edit()` endpoint, not `images.generate()`
- Requires the uploaded photo as input to create personalized action figures
- Automatically converts HEIC images to PNG for API compatibility
- Includes detailed prompt engineering for consistent action figure packaging style

### Branding

Brand colors (defined in `app.py` CSS):
- **Primary Navy:** #1a237e (header text, buttons)
- **Blue Gradient:** #1e3a8a → #3b82f6 → #60a5fa (background)
- **Gold:** #ffd700 (subtitle, download buttons)
- **White:** #ffffff (card backgrounds, footer text)
- **Accent Cyan:** #00d4ff (step indicators)

### Prompt Engineering

The app uses a sophisticated prompt that:
- Maintains exact facial likeness from the uploaded photo
- Keeps original clothing from the reference image
- Creates realistic action figure packaging aesthetic
- Includes "I'M TAKING ACTION AGAINST CANCER" message
- Adds user's name to the packaging
- Incorporates selected accessories with themed props
- Emulates premium Hasbro/Marvel Legends collectible style

## Technical Implementation

### Image Processing Pipeline

1. **Upload Handling:**
   - Accepts JPG, PNG, HEIC/HEIF formats
   - Uses pillow-heif for HEIC support
   - Converts all images to RGB mode (removes alpha channel)
   - Stores in Streamlit session state (temporary, not persisted)

2. **API Integration:**
   - Converts PIL Image to BytesIO stream
   - Saves as PNG format with `.name` attribute for API recognition
   - Sends to OpenAI `images.edit()` endpoint
   - Handles both URL and base64 responses

3. **Error Handling:**
   - Comprehensive try-catch blocks
   - Debug information display for troubleshooting
   - Detailed error messages with traceback
   - Retry options on failure

4. **Session State Management:**
   - Tracks current step (1-4)
   - Stores uploaded image, generated image URL, and user details
   - Persists OpenAI client instance
   - Allows multiple generations in same session

### UI/UX Design

- **Mobile-First:** Optimized for event attendees using smartphones
- **Progress Indicators:** 4-step visual progress tracker
- **Responsive Cards:** White content cards on blue gradient background
- **Custom CSS:** Extensive styling for branded experience
- **Auto-Navigation:** Automatically proceeds through generation steps
- **Accessibility:** Clear instructions, helpful tips, and status messages

## Security Notes

- **API Key Protection:**
  - Never commit `.streamlit/secrets.toml` to git (included in `.gitignore`)
  - Use Streamlit secrets or environment variables for API keys
  - Keys are validated at startup (must start with 'sk-')

- **Data Privacy:**
  - Uploaded photos stored only in session state (temporary memory)
  - No photos are saved to disk or database
  - Generated images are temporary URLs from OpenAI
  - Each session is isolated and cleaned on reset

- **Production Deployment:**
  - Configure secrets in Streamlit Cloud settings
  - Monitor API usage and costs in OpenAI dashboard
  - Test thoroughly with various image types before event
  - Consider rate limiting for large events (350-500 users)

## Troubleshooting

### Common Issues

**"API key not found"**
- Ensure `.streamlit/secrets.toml` exists with your OpenAI API key
- Check that the key starts with 'sk-'
- Verify file is in the correct location

**"HEIC not supported"**
- Install pillow-heif: `pip install pillow-heif`
- Alternative: Convert HEIC to JPG before uploading

**"Image generation failed"**
- Check OpenAI API status and account credits
- Verify image is under 10MB
- Ensure stable internet connection
- Review error details in debug output

**Slow performance at events**
- Each generation takes 30-60 seconds (expected)
- Consider multiple deployment instances for 350+ simultaneous users
- Test bandwidth at event venue beforehand
- Have backup QR codes ready

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- AI image generation powered by [OpenAI gpt-image-1](https://openai.com/api)
- HEIC support via [pillow-heif](https://github.com/bigcat88/pillow_heif)
- QR code generation using [python-qrcode](https://github.com/lincolnloop/python-qrcode)
- Created for the Expect Miracles Foundation

## License

© 2025 Expect Miracles Foundation - All Rights Reserved

## Support

For questions, issues, or feature requests, please open an issue on GitHub.

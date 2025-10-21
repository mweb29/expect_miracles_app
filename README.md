# Expect Miracles - Superhero Generator 💪

A Streamlit web application that transforms event attendees into superheroes fighting cancer. Built for live fundraising events with 350-500 attendees accessing via QR code.

## About

The Expect Miracles Superhero Generator is an interactive web app designed for the Expect Miracles Foundation's fundraising events. Attendees can upload their photos and transform into cancer-fighting superheroes using AI-powered image generation.

**Key Features:**
- Mobile-first design optimized for event attendees
- AI-powered superhero transformation using OpenAI DALL-E 3
- Customizable superhero accessories
- Social sharing capabilities (LinkedIn, Email)
- Branded with Expect Miracles Foundation colors and styling

**Tech Stack:**
- **Frontend Framework:** Streamlit
- **AI Image Generation:** OpenAI DALL-E 3 API
- **Image Processing:** Pillow (PIL)
- **Language:** Python 3.8+

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

1. **Upload Photo**: Attendees take a selfie or upload an existing photo
2. **Enter Details**: Provide first name and select an optional superhero accessory
3. **Generate**: AI creates a unique superhero transformation
4. **Share**: Download and share the superhero image on social media

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

The app uses OpenAI's DALL-E 3 model with the following default settings:
- **Model:** dall-e-3
- **Size:** 1024x1024 pixels
- **Quality:** standard (can be upgraded to "hd" for better quality)

### Branding

Brand colors (customizable in `app.py`):
- **Primary Navy:** #1a237e
- **Gold:** #ffd700
- **Accent Blue:** #00d4ff

## Security Notes

- Never commit `.streamlit/secrets.toml` to git (it's in `.gitignore`)
- Use environment variables or Streamlit secrets for API keys
- The app doesn't store uploaded photos permanently (they're in session state only)

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- AI image generation powered by [OpenAI DALL-E 3](https://openai.com/dall-e-3)
- Created for the Expect Miracles Foundation

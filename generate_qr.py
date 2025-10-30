"""
QR Code Generator for Expect Miracles Superhero App
====================================================
Generates QR codes in Expect Miracles brand colors for event printing.

Usage:
    python generate_qr.py

Requirements:
    pip install qrcode[pil]
"""

import qrcode

def generate_qr_code(url, filename="expect_miracles_qr.png", size="standard"):
    """
    Generate a QR code with Expect Miracles branding

    Args:
        url (str): The Streamlit app URL
        filename (str): Output filename
        size (str): 'standard', 'large', or 'poster'
    """

    # Expect Miracles brand colors (from logo)
    DEEP_BLUE = "#003087"      # Primary blue from logo
    PURPLE = "#7b2c85"         # Purple/magenta accent from logo
    WHITE = "#ffffff"          # Background

    # Set box size based on desired output
    size_configs = {
        "standard": 10,  # ~300px (good for table tents)
        "large": 20,     # ~600px (good for posters)
        "poster": 30     # ~900px (good for large prints)
    }

    box_size = size_configs.get(size, 10)

    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=box_size,
        border=4,
    )

    # Add URL data
    qr.add_data(url)
    qr.make(fit=True)

    # Create image with brand colors (using deep blue for QR pattern)
    # Note: Using standard QR code for better compatibility and scannability
    img = qr.make_image(
        fill_color=DEEP_BLUE,  # QR code pattern in deep blue
        back_color=WHITE       # White background
    )

    # Save the image
    img.save(filename)
    print(f"✅ QR code saved as: {filename}")
    print(f"📏 Size: {size} ({img.size[0]}x{img.size[1]} pixels)")
    print(f"🔗 URL: {url}")

    return filename


def generate_all_sizes(url):
    """Generate QR codes in all standard sizes"""
    sizes = {
        "standard": "expect_miracles_qr_standard.png",
        "large": "expect_miracles_qr_large.png",
        "poster": "expect_miracles_qr_poster.png"
    }

    print("\n" + "="*60)
    print("🎨 Generating QR Codes for Expect Miracles Event")
    print("="*60 + "\n")

    for size, filename in sizes.items():
        generate_qr_code(url, filename, size)
        print()

    print("="*60)
    print("✨ All QR codes generated successfully!")
    print("="*60)
    print("\n📋 Recommended usage:")
    print("  • standard: Table tents, handouts (3x5 inches)")
    print("  • large: Posters, banners (11x17 inches)")
    print("  • poster: Large displays, projection (24x36 inches)")
    print("\n💡 Print at 300 DPI for best quality")


if __name__ == "__main__":
    # ============================================================================
    # CONFIGURATION - Update this with your deployed Streamlit app URL
    # ============================================================================

    # Replace with your actual Streamlit Cloud URL
    # Example: "https://superhero-expectmiracles.streamlit.app"
    APP_URL = "https://expect-miracles-event.streamlit.app"

    # ============================================================================

    # Check if URL has been updated
    if "your-app-name" in APP_URL:
        print("\n⚠️  WARNING: Please update APP_URL with your actual Streamlit app URL!")
        print("   Edit the APP_URL variable in this script.\n")

        # Ask user for URL
        user_url = input("Enter your Streamlit app URL (or press Enter to skip): ").strip()
        if user_url:
            APP_URL = user_url
        else:
            print("❌ Exiting. Please update APP_URL and run again.")
            exit(1)

    # Generate all QR code sizes
    generate_all_sizes(APP_URL)

    print("\n🎉 Ready for your event!")
    print("📧 Questions? Open an issue on GitHub.")
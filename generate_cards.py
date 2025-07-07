"""
Generate basic visual cards for the Special Kids Assistant application.
This script creates simple placeholder images for the visual communication cards.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)

def create_visual_card(text, icon, filename, size=(200, 150), bg_color="#FFE4E1", text_color="#4B0082"):
    """Create a colorful, engaging visual card with rainbow theme."""
    try:
        # Create gradient background for more visual appeal
        image = Image.new('RGB', size, bg_color)
        draw = ImageDraw.Draw(image)
        
        # Add a subtle rainbow border
        border_colors = ["#FF6B9D", "#C44569", "#F8B500", "#6BCF7F", "#4BCFFA", "#A29BFE"]
        for i, color in enumerate(border_colors):
            draw.rectangle([(i, i), (size[0]-1-i, size[1]-1-i)], outline=color, width=1)
        
        # Try to load a font, fall back to default if not available
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        except (OSError, IOError):
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw icon (emoji) with more space
        icon_bbox = draw.textbbox((0, 0), icon, font=font_large)
        icon_width = icon_bbox[2] - icon_bbox[0]
        icon_height = icon_bbox[3] - icon_bbox[1]
        icon_x = (size[0] - icon_width) // 2
        icon_y = 25
        draw.text((icon_x, icon_y), icon, font=font_large)
        
        # Draw text with colorful styling
        text_bbox = draw.textbbox((0, 0), text, font=font_small)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (size[0] - text_width) // 2
        text_y = icon_y + icon_height + 15
        
        # Add text shadow for better readability
        draw.text((text_x + 1, text_y + 1), text, fill="#E0E0E0", font=font_small)
        draw.text((text_x, text_y), text, fill=text_color, font=font_small)
        
        # Save image
        image.save(filename)
        print(f"🌈 Created colorful card: {filename}")
        
    except Exception as e:
        logger.error(f"Failed to create visual card {filename}: {str(e)}")

def generate_all_cards():
    """Generate all rainbow-themed visual communication cards."""
    cards_dir = "static/images/visual_cards"
    os.makedirs(cards_dir, exist_ok=True)
    
    # Define all cards with their emojis and rainbow colors
    cards = [
        # Emotions - warm colors
        ("happy", "😊", "Happy"),
        ("sad", "😢", "Sad"),
        ("angry", "😠", "Angry"),
        ("calm", "😌", "Calm"),
        ("excited", "🤩", "Excited"),
        ("tired", "😴", "Tired"),
        
        # Needs - cool colors
        ("eat", "🍽️", "Eat"),
        ("drink", "🥤", "Drink"),
        ("bathroom", "🚻", "Bathroom"),
        ("sleep", "🛏️", "Sleep"),
        ("help", "🆘", "Help"),
        ("break", "⏸️", "Break"),
        
        # Activities - bright colors
        ("play", "🎮", "Play"),
        ("read", "📚", "Read"),
        ("music", "🎵", "Music"),
        ("draw", "🎨", "Draw"),
        ("outside", "🌳", "Outside"),
        ("quiet_time", "🤫", "Quiet Time"),
        
        # Social - rainbow colors
        ("yes", "✅", "Yes"),
        ("no", "❌", "No"),
        ("please", "🙏", "Please"),
        ("thank_you", "🙏", "Thank You"),
        ("hello", "👋", "Hello"),
        ("goodbye", "👋", "Goodbye")
    ]
    
    # Color themes for different categories
    color_themes = {
        0: "#FFE4E1",   # Light pink for emotions
        6: "#E0F6FF",   # Light blue for needs  
        12: "#F0FFF0",  # Light green for activities
        18: "#FFF8DC"   # Light yellow for social
    }
    
    for i, (card_id, icon, text) in enumerate(cards):
        # Determine background color based on category
        bg_color = "#FFE4E1"  # Default
        for start_idx, theme_color in color_themes.items():
            if i >= start_idx:
                bg_color = theme_color
        
        filename = os.path.join(cards_dir, f"{card_id}.png")
        create_visual_card(text, icon, filename, bg_color=bg_color)
    
    print(f"\n🌈 Generated {len(cards)} magical Rainbow Bridge communication cards!")
    print("🎨 Each card is designed with beautiful colors and engaging visuals!")
    print("✨ Cards are ready for your colorful communication adventures!")

if __name__ == "__main__":
    generate_all_cards()

"""
Communication Helper - Visual and Multi-Modal Communication Support

This module provides visual communication aids, symbol libraries,
and alternative communication methods for autistic children.
"""

import os
import aiofiles
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

@dataclass
class VisualCard:
    """Represents a visual communication card."""
    id: str
    name: str
    category: str
    image_path: str
    description: str
    tags: List[str]
    emotional_context: Optional[str] = None

@dataclass
class CommunicationSequence:
    """Represents a sequence of visual cards for complex communication."""
    id: str
    name: str
    cards: List[VisualCard]
    description: str
    use_cases: List[str]

class CommunicationHelper:
    """Provides visual and alternative communication support."""
    
    def __init__(self):
        self.visual_cards_db = self._initialize_visual_cards()
        self.communication_sequences = self._initialize_sequences()
        self.custom_cards_path = "static/custom_cards"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        directories = [
            "static/images/visual_cards",
            "static/custom_cards",
            "static/generated_cards"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _initialize_visual_cards(self) -> Dict[str, VisualCard]:
        """Initialize the visual cards database."""
        cards = {}
        
        # Basic emotion cards
        emotion_cards = [
            {"id": "happy", "name": "Happy", "category": "emotions", "description": "Feeling good and cheerful", "tags": ["positive", "emotion"], "emotional_context": "positive"},
            {"id": "sad", "name": "Sad", "category": "emotions", "description": "Feeling down or upset", "tags": ["negative", "emotion"], "emotional_context": "negative"},
            {"id": "angry", "name": "Angry", "category": "emotions", "description": "Feeling mad or frustrated", "tags": ["negative", "emotion"], "emotional_context": "negative"},
            {"id": "calm", "name": "Calm", "category": "emotions", "description": "Feeling peaceful and relaxed", "tags": ["neutral", "emotion"], "emotional_context": "neutral"},
            {"id": "excited", "name": "Excited", "category": "emotions", "description": "Feeling energetic and enthusiastic", "tags": ["positive", "emotion"], "emotional_context": "positive"},
            {"id": "tired", "name": "Tired", "category": "emotions", "description": "Feeling sleepy or low energy", "tags": ["neutral", "emotion"], "emotional_context": "neutral"}
        ]
        
        # Basic need cards
        need_cards = [
            {"id": "eat", "name": "Eat", "category": "needs", "description": "Want food or hungry", "tags": ["basic_need", "food"]},
            {"id": "drink", "name": "Drink", "category": "needs", "description": "Want water or thirsty", "tags": ["basic_need", "drink"]},
            {"id": "bathroom", "name": "Bathroom", "category": "needs", "description": "Need to use the toilet", "tags": ["basic_need", "hygiene"]},
            {"id": "sleep", "name": "Sleep", "category": "needs", "description": "Want to rest or sleep", "tags": ["basic_need", "rest"]},
            {"id": "help", "name": "Help", "category": "needs", "description": "Need assistance", "tags": ["support", "request"]},
            {"id": "break", "name": "Break", "category": "needs", "description": "Need a pause or rest", "tags": ["rest", "pause"]}
        ]
        
        # Activity cards
        activity_cards = [
            {"id": "play", "name": "Play", "category": "activities", "description": "Want to play or have fun", "tags": ["fun", "activity"]},
            {"id": "read", "name": "Read", "category": "activities", "description": "Want to read books", "tags": ["learning", "quiet"]},
            {"id": "music", "name": "Music", "category": "activities", "description": "Want to listen to music", "tags": ["audio", "entertainment"]},
            {"id": "draw", "name": "Draw", "category": "activities", "description": "Want to draw or color", "tags": ["creative", "art"]},
            {"id": "outside", "name": "Outside", "category": "activities", "description": "Want to go outdoors", "tags": ["outdoor", "fresh_air"]},
            {"id": "quiet_time", "name": "Quiet Time", "category": "activities", "description": "Want peaceful quiet activity", "tags": ["calm", "sensory"]}
        ]
        
        # Social cards
        social_cards = [
            {"id": "yes", "name": "Yes", "category": "social", "description": "Agreement or approval", "tags": ["response", "positive"]},
            {"id": "no", "name": "No", "category": "social", "description": "Disagreement or refusal", "tags": ["response", "negative"]},
            {"id": "please", "name": "Please", "category": "social", "description": "Polite request", "tags": ["manners", "request"]},
            {"id": "thank_you", "name": "Thank You", "category": "social", "description": "Showing gratitude", "tags": ["manners", "gratitude"]},
            {"id": "hello", "name": "Hello", "category": "social", "description": "Greeting others", "tags": ["greeting", "social"]},
            {"id": "goodbye", "name": "Goodbye", "category": "social", "description": "Saying farewell", "tags": ["farewell", "social"]}
        ]
        
        # Combine all cards
        all_cards = emotion_cards + need_cards + activity_cards + social_cards
        
        for card_data in all_cards:
            card = VisualCard(
                id=card_data["id"],
                name=card_data["name"],
                category=card_data["category"],
                image_path=f"static/images/visual_cards/{card_data['id']}.png",
                description=card_data["description"],
                tags=card_data["tags"],
                emotional_context=card_data.get("emotional_context")
            )
            cards[card.id] = card
        
        return cards
    
    def _initialize_sequences(self) -> Dict[str, CommunicationSequence]:
        """Initialize common communication sequences."""
        sequences = {}
        
        # Morning routine sequence
        morning_sequence = CommunicationSequence(
            id="morning_routine",
            name="Morning Routine",
            cards=[
                self.visual_cards_db["hello"],
                self.visual_cards_db["eat"],
                self.visual_cards_db["bathroom"],
                self.visual_cards_db["happy"]
            ],
            description="Common morning routine communication",
            use_cases=["daily_routine", "morning_checkin"]
        )
        sequences[morning_sequence.id] = morning_sequence
        
        # Need help sequence
        help_sequence = CommunicationSequence(
            id="need_help",
            name="Need Help",
            cards=[
                self.visual_cards_db["help"],
                self.visual_cards_db["please"]
            ],
            description="Asking for assistance politely",
            use_cases=["request_support", "problem_solving"]
        )
        sequences[help_sequence.id] = help_sequence
        
        # Feeling overwhelmed sequence
        overwhelmed_sequence = CommunicationSequence(
            id="feeling_overwhelmed",
            name="Feeling Overwhelmed",
            cards=[
                self.visual_cards_db["tired"],
                self.visual_cards_db["break"],
                self.visual_cards_db["quiet_time"]
            ],
            description="Expressing need for calm and break",
            use_cases=["sensory_overload", "stress_management"]
        )
        sequences[overwhelmed_sequence.id] = overwhelmed_sequence
        
        return sequences
    
    async def get_visual_cards(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get visual cards filtered by category or tags."""
        try:
            cards = list(self.visual_cards_db.values())
            
            # Filter by category
            if category:
                cards = [card for card in cards if card.category == category]
            
            # Filter by tags
            if tags:
                cards = [
                    card for card in cards 
                    if any(tag in card.tags for tag in tags)
                ]
            
            # Convert to dictionaries for JSON serialization
            return [self._card_to_dict(card) for card in cards]
        
        except Exception as e:
            logger.error(f"Failed to get visual cards: {str(e)}")
            return []
    
    def _card_to_dict(self, card: VisualCard) -> Dict[str, Any]:
        """Convert a VisualCard to a dictionary."""
        return {
            "id": card.id,
            "name": card.name,
            "category": card.category,
            "image_path": card.image_path,
            "description": card.description,
            "tags": card.tags,
            "emotional_context": card.emotional_context
        }
    
    async def get_communication_sequences(
        self,
        use_case: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get communication sequences, optionally filtered by use case."""
        try:
            sequences = list(self.communication_sequences.values())
            
            if use_case:
                sequences = [
                    seq for seq in sequences 
                    if use_case in seq.use_cases
                ]
            
            return [self._sequence_to_dict(seq) for seq in sequences]
        
        except Exception as e:
            logger.error(f"Failed to get communication sequences: {str(e)}")
            return []
    
    def _sequence_to_dict(self, sequence: CommunicationSequence) -> Dict[str, Any]:
        """Convert a CommunicationSequence to a dictionary."""
        return {
            "id": sequence.id,
            "name": sequence.name,
            "cards": [self._card_to_dict(card) for card in sequence.cards],
            "description": sequence.description,
            "use_cases": sequence.use_cases
        }
    
    async def save_custom_image(
        self,
        child_id: int,
        image,
        category: str = "custom"
    ) -> str:
        """Save a custom uploaded image as a visual card."""
        try:
            # Generate unique filename
            timestamp = int(datetime.now().timestamp())
            filename = f"custom_{child_id}_{timestamp}.png"
            file_path = os.path.join(self.custom_cards_path, filename)
            
            # Save the uploaded image
            async with aiofiles.open(file_path, 'wb') as f:
                content = await image.read()
                await f.write(content)
            
            # Create visual card entry
            card_id = f"custom_{child_id}_{timestamp}"
            custom_card = VisualCard(
                id=card_id,
                name=image.filename.split('.')[0] if image.filename else "Custom Image",
                category=category,
                image_path=file_path,
                description=f"Custom image uploaded for child {child_id}",
                tags=["custom", "uploaded"]
            )
            
            # Add to visual cards database
            self.visual_cards_db[card_id] = custom_card
            
            logger.info(f"Saved custom image for child {child_id}: {filename}")
            return file_path
        
        except Exception as e:
            logger.error(f"Failed to save custom image: {str(e)}")
            raise
    
    async def generate_visual_card(
        self,
        text: str,
        category: str = "generated",
        background_color: str = "#FFFFFF",
        text_color: str = "#000000"
    ) -> str:
        """Generate a simple text-based visual card."""
        try:
            # Create image
            width, height = 200, 150
            image = Image.new('RGB', (width, height), background_color)
            draw = ImageDraw.Draw(image)
            
            # Try to load a font, fall back to default if not available
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            except (OSError, IOError):
                font = ImageFont.load_default()
            
            # Calculate text position for centering
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Draw text
            draw.text((x, y), text, fill=text_color, font=font)
            
            # Save image
            timestamp = int(datetime.now().timestamp())
            filename = f"generated_{timestamp}.png"
            file_path = os.path.join("static/generated_cards", filename)
            
            image.save(file_path)
            
            # Create visual card entry
            card_id = f"generated_{timestamp}"
            generated_card = VisualCard(
                id=card_id,
                name=text,
                category=category,
                image_path=file_path,
                description=f"Generated visual card: {text}",
                tags=["generated", "text"]
            )
            
            # Add to visual cards database
            self.visual_cards_db[card_id] = generated_card
            
            logger.info(f"Generated visual card: {text}")
            return file_path
        
        except Exception as e:
            logger.error(f"Failed to generate visual card: {str(e)}")
            raise
    
    async def suggest_cards_for_context(
        self,
        context: str,
        emotion: Optional[str] = None,
        max_suggestions: int = 6
    ) -> List[Dict[str, Any]]:
        """Suggest appropriate visual cards based on context and emotion."""
        try:
            suggested_cards = []
            context_lower = context.lower()
            
            # Context-based suggestions
            if any(word in context_lower for word in ["hungry", "eat", "food"]):
                suggested_cards.append(self.visual_cards_db["eat"])
            
            if any(word in context_lower for word in ["thirsty", "drink", "water"]):
                suggested_cards.append(self.visual_cards_db["drink"])
            
            if any(word in context_lower for word in ["tired", "sleep", "rest"]):
                suggested_cards.append(self.visual_cards_db["sleep"])
            
            if any(word in context_lower for word in ["bathroom", "toilet"]):
                suggested_cards.append(self.visual_cards_db["bathroom"])
            
            if any(word in context_lower for word in ["help", "assist", "support"]):
                suggested_cards.append(self.visual_cards_db["help"])
            
            if any(word in context_lower for word in ["play", "fun", "game"]):
                suggested_cards.append(self.visual_cards_db["play"])
            
            # Emotion-based suggestions
            if emotion:
                emotion_cards = [
                    card for card in self.visual_cards_db.values()
                    if card.emotional_context == emotion or emotion in card.tags
                ]
                suggested_cards.extend(emotion_cards[:2])
            
            # Always include basic social cards
            if not any(card.category == "social" for card in suggested_cards):
                suggested_cards.extend([
                    self.visual_cards_db["yes"],
                    self.visual_cards_db["no"]
                ])
            
            # Remove duplicates and limit to max_suggestions
            unique_cards = list({card.id: card for card in suggested_cards}.values())
            
            return [self._card_to_dict(card) for card in unique_cards[:max_suggestions]]
        
        except Exception as e:
            logger.error(f"Failed to suggest cards: {str(e)}")
            return []
    
    async def create_custom_sequence(
        self,
        child_id: int,
        name: str,
        card_ids: List[str],
        description: str,
        use_cases: List[str]
    ) -> str:
        """Create a custom communication sequence."""
        try:
            # Validate card IDs
            cards = []
            for card_id in card_ids:
                if card_id in self.visual_cards_db:
                    cards.append(self.visual_cards_db[card_id])
                else:
                    logger.warning(f"Card ID not found: {card_id}")
            
            if not cards:
                raise ValueError("No valid cards provided for sequence")
            
            # Create sequence
            sequence_id = f"custom_{child_id}_{int(datetime.now().timestamp())}"
            custom_sequence = CommunicationSequence(
                id=sequence_id,
                name=name,
                cards=cards,
                description=description,
                use_cases=use_cases
            )
            
            # Add to sequences database
            self.communication_sequences[sequence_id] = custom_sequence
            
            logger.info(f"Created custom sequence for child {child_id}: {name}")
            return sequence_id
        
        except Exception as e:
            logger.error(f"Failed to create custom sequence: {str(e)}")
            raise
    
    async def get_cards_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all visual cards grouped by category."""
        try:
            categorized_cards = {}
            
            for card in self.visual_cards_db.values():
                if card.category not in categorized_cards:
                    categorized_cards[card.category] = []
                categorized_cards[card.category].append(self._card_to_dict(card))
            
            return categorized_cards
        
        except Exception as e:
            logger.error(f"Failed to get cards by category: {str(e)}")
            return {}
    
    async def search_cards(self, query: str) -> List[Dict[str, Any]]:
        """Search for visual cards by name, description, or tags."""
        try:
            query_lower = query.lower()
            matching_cards = []
            
            for card in self.visual_cards_db.values():
                # Check name, description, and tags
                if (query_lower in card.name.lower() or
                    query_lower in card.description.lower() or
                    any(query_lower in tag.lower() for tag in card.tags)):
                    matching_cards.append(card)
            
            return [self._card_to_dict(card) for card in matching_cards]
        
        except Exception as e:
            logger.error(f"Failed to search cards: {str(e)}")
            return []

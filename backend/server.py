from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class WasteClassification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image_base64: str
    classification: str
    category: str  # recycle, compost, landfill
    suggestions: str
    points_awarded: int = 10
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = "default_user"

class WasteClassificationRequest(BaseModel):
    image_base64: str
    user_id: Optional[str] = "default_user"

class WasteClassificationResponse(BaseModel):
    id: str
    classification: str
    category: str
    suggestions: str
    points_awarded: int

class BinLocation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # recycling, compost, general, e-waste
    latitude: float
    longitude: float
    address: str
    status: str = "active"  # active, full, maintenance
    capacity: int = 100  # percentage
    last_emptied: Optional[datetime] = None
    timings: str = "24/7"

class BinLocationCreate(BaseModel):
    name: str
    type: str
    latitude: float
    longitude: float
    address: str
    status: str = "active"
    capacity: int = 100
    timings: str = "24/7"

class UserStats(BaseModel):
    user_id: str = "default_user"
    total_points: int = 0
    items_scanned: int = 0
    items_recycled: int = 0
    co2_saved_kg: float = 0.0
    badges: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WasteReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    location: str
    latitude: float
    longitude: float
    description: str
    image_base64: Optional[str] = None
    status: str = "pending"  # pending, resolved, in_progress
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WasteReportCreate(BaseModel):
    user_id: Optional[str] = "default_user"
    location: str
    latitude: float
    longitude: float
    description: str
    image_base64: Optional[str] = None


# AI Waste Classification using Emergent LLM Key
@api_router.post("/classify-waste", response_model=WasteClassificationResponse)
async def classify_waste(request: WasteClassificationRequest):
    try:
        # Initialize LLM chat with Emergent LLM Key
        llm_key = os.environ['EMERGENT_LLM_KEY']
        chat = LlmChat(
            api_key=llm_key,
            session_id=f"waste-classification-{uuid.uuid4()}",
            system_message="You are an expert waste management AI assistant. Classify waste items and provide disposal recommendations."
        ).with_model("openai", "gpt-4o-mini")
        
        # Create prompt for waste classification
        prompt = f"""Based on the user's description of waste, classify it into one of these categories and provide disposal suggestions.

Please analyze and provide:
1. Classification: What type of waste is this? (be specific)
2. Category: Choose ONE from: RECYCLE, COMPOST, or LANDFILL
3. Suggestions: How should this be disposed of properly? (2-3 sentences)

Format your response EXACTLY as:
CLASSIFICATION: [specific item type]
CATEGORY: [RECYCLE/COMPOST/LANDFILL]
SUGGESTIONS: [disposal instructions]

The user will describe the waste item now."""

        user_message = UserMessage(
            text=f"I have waste to classify. It appears to be a general waste item that I photographed. Please classify this waste item and tell me how to dispose of it properly."
        )
        
        # Get AI response
        response = await chat.send_message(user_message)
        
        # Parse the response
        lines = response.strip().split('\n')
        classification = ""
        category = "LANDFILL"
        suggestions = ""
        
        for line in lines:
            if line.startswith("CLASSIFICATION:"):
                classification = line.replace("CLASSIFICATION:", "").strip()
            elif line.startswith("CATEGORY:"):
                category = line.replace("CATEGORY:", "").strip()
            elif line.startswith("SUGGESTIONS:"):
                suggestions = line.replace("SUGGESTIONS:", "").strip()
        
        # Default fallback
        if not classification:
            classification = "General Waste"
        if not suggestions:
            suggestions = "Please dispose of this item in the appropriate waste bin. Check with your local waste management for specific guidelines."
        
        # Store in database
        waste_obj = WasteClassification(
            image_base64=request.image_base64[:100],  # Store truncated for db efficiency
            classification=classification,
            category=category,
            suggestions=suggestions,
            points_awarded=10,
            user_id=request.user_id
        )
        
        await db.waste_classifications.insert_one(waste_obj.dict())
        
        # Update user stats
        user_stats = await db.user_stats.find_one({"user_id": request.user_id})
        if not user_stats:
            user_stats = UserStats(user_id=request.user_id)
            await db.user_stats.insert_one(user_stats.dict())
        else:
            # Update stats
            await db.user_stats.update_one(
                {"user_id": request.user_id},
                {
                    "$inc": {
                        "total_points": 10,
                        "items_scanned": 1,
                        "items_recycled": 1 if category == "RECYCLE" else 0,
                        "co2_saved_kg": 0.5
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        
        return WasteClassificationResponse(
            id=waste_obj.id,
            classification=classification,
            category=category,
            suggestions=suggestions,
            points_awarded=10
        )
        
    except Exception as e:
        logging.error(f"Error classifying waste: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error classifying waste: {str(e)}")


# Bin Location endpoints
@api_router.get("/bins", response_model=List[BinLocation])
async def get_bins(latitude: Optional[float] = None, longitude: Optional[float] = None):
    """Get all bin locations, optionally filtered by proximity"""
    try:
        bins = await db.bin_locations.find().to_list(100)
        return [BinLocation(**bin) for bin in bins]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bins", response_model=BinLocation)
async def create_bin(bin_data: BinLocationCreate):
    """Create a new bin location"""
    try:
        bin_obj = BinLocation(**bin_data.dict())
        await db.bin_locations.insert_one(bin_obj.dict())
        return bin_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# User Stats endpoints
@api_router.get("/user-stats/{user_id}", response_model=UserStats)
async def get_user_stats(user_id: str = "default_user"):
    """Get user statistics and rewards"""
    try:
        user_stats = await db.user_stats.find_one({"user_id": user_id})
        if not user_stats:
            # Create default stats for new user
            new_stats = UserStats(user_id=user_id)
            await db.user_stats.insert_one(new_stats.dict())
            return new_stats
        
        # Award badges based on achievements
        stats_obj = UserStats(**user_stats)
        if stats_obj.items_scanned >= 10 and "Eco Warrior" not in stats_obj.badges:
            stats_obj.badges.append("Eco Warrior")
            await db.user_stats.update_one(
                {"user_id": user_id},
                {"$set": {"badges": stats_obj.badges}}
            )
        if stats_obj.items_recycled >= 5 and "Plastic Reducer" not in stats_obj.badges:
            stats_obj.badges.append("Plastic Reducer")
            await db.user_stats.update_one(
                {"user_id": user_id},
                {"$set": {"badges": stats_obj.badges}}
            )
        
        return stats_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Waste Report endpoints
@api_router.post("/reports", response_model=WasteReport)
async def create_report(report_data: WasteReportCreate):
    """Report waste in a location"""
    try:
        report_obj = WasteReport(**report_data.dict())
        await db.waste_reports.insert_one(report_obj.dict())
        
        # Award points for reporting
        await db.user_stats.update_one(
            {"user_id": report_data.user_id},
            {
                "$inc": {"total_points": 5},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return report_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/reports", response_model=List[WasteReport])
async def get_reports():
    """Get all waste reports"""
    try:
        reports = await db.waste_reports.find().sort("timestamp", -1).to_list(50)
        return [WasteReport(**report) for report in reports]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@api_router.get("/")
async def root():
    return {"message": "CleanCity API is running", "status": "healthy"}


# Seed data endpoint (for testing)
@api_router.post("/seed-data")
async def seed_data():
    """Seed the database with sample bin locations"""
    try:
        # Check if bins already exist
        existing_bins = await db.bin_locations.count_documents({})
        if existing_bins > 0:
            return {"message": "Data already seeded"}
        
        sample_bins = [
            {
                "name": "Central Park Recycling Station",
                "type": "recycling",
                "latitude": 40.7829,
                "longitude": -73.9654,
                "address": "Central Park, New York, NY",
                "status": "active",
                "capacity": 75,
                "timings": "6 AM - 10 PM"
            },
            {
                "name": "Downtown Compost Center",
                "type": "compost",
                "latitude": 40.7489,
                "longitude": -73.9680,
                "address": "Downtown Manhattan, NY",
                "status": "active",
                "capacity": 60,
                "timings": "24/7"
            },
            {
                "name": "Brooklyn E-Waste Drop-off",
                "type": "e-waste",
                "latitude": 40.6782,
                "longitude": -73.9442,
                "address": "Brooklyn, NY",
                "status": "active",
                "capacity": 90,
                "timings": "9 AM - 6 PM"
            },
            {
                "name": "Queens General Waste Hub",
                "type": "general",
                "latitude": 40.7282,
                "longitude": -73.7949,
                "address": "Queens, NY",
                "status": "active",
                "capacity": 45,
                "timings": "24/7"
            },
            {
                "name": "Bronx Recycling Point",
                "type": "recycling",
                "latitude": 40.8448,
                "longitude": -73.8648,
                "address": "Bronx, NY",
                "status": "full",
                "capacity": 100,
                "timings": "7 AM - 9 PM"
            }
        ]
        
        for bin_data in sample_bins:
            bin_obj = BinLocation(**bin_data)
            await db.bin_locations.insert_one(bin_obj.dict())
        
        return {"message": f"Successfully seeded {len(sample_bins)} bin locations"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

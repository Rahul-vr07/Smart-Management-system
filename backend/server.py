from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage
import math
from collections import defaultdict


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


# ============================================
# WASTE CATEGORIES DATABASE
# ============================================
WASTE_CATEGORIES = {
    "RECYCLE": {
        "items": ["plastic bottle", "glass bottle", "aluminum can", "cardboard", "paper", 
                  "metal can", "newspaper", "magazine", "plastic container", "steel can"],
        "color": "#4CAF50",
        "icon": "recycle",
        "co2_saved_per_item": 0.8,  # kg
        "points": 10
    },
    "COMPOST": {
        "items": ["food waste", "fruit peel", "vegetable scraps", "coffee grounds", 
                  "tea bags", "eggshells", "yard waste", "leaves", "grass clippings"],
        "color": "#FF9800",
        "icon": "leaf",
        "co2_saved_per_item": 0.5,
        "points": 8
    },
    "E_WASTE": {
        "items": ["battery", "phone", "laptop", "computer", "electronics", "charger", 
                  "circuit board", "cable", "printer", "monitor"],
        "color": "#9C27B0",
        "icon": "laptop",
        "co2_saved_per_item": 1.5,
        "points": 15
    },
    "HAZARDOUS": {
        "items": ["paint", "chemical", "oil", "pesticide", "cleaning product", 
                  "fluorescent bulb", "medicine", "needle"],
        "color": "#F44336",
        "icon": "alert",
        "co2_saved_per_item": 0.3,
        "points": 5
    },
    "LANDFILL": {
        "items": ["styrofoam", "dirty diaper", "ceramic", "broken glass", "mirror", 
                  "light bulb", "contaminated items"],
        "color": "#757575",
        "icon": "delete",
        "co2_saved_per_item": 0.0,
        "points": 5
    }
}

# Badge definitions with requirements
BADGES = {
    "Eco Warrior": {
        "requirement": "items_scanned >= 10",
        "icon": "shield-sword",
        "description": "Scan 10 waste items",
        "points_bonus": 50
    },
    "Plastic Reducer": {
        "requirement": "items_recycled >= 5",
        "icon": "bottle-soda",
        "description": "Recycle 5 items",
        "points_bonus": 30
    },
    "Green Champion": {
        "requirement": "items_scanned >= 50",
        "icon": "trophy",
        "description": "Scan 50 waste items",
        "points_bonus": 100
    },
    "Composting Hero": {
        "requirement": "compost_items >= 10",
        "icon": "leaf",
        "description": "Compost 10 items",
        "points_bonus": 40
    },
    "E-Waste Expert": {
        "requirement": "ewaste_items >= 5",
        "icon": "laptop",
        "description": "Dispose 5 e-waste items",
        "points_bonus": 60
    },
    "Streak Master": {
        "requirement": "daily_streak >= 7",
        "icon": "fire",
        "description": "7-day scanning streak",
        "points_bonus": 70
    },
    "Climate Guardian": {
        "requirement": "co2_saved_kg >= 10.0",
        "icon": "earth",
        "description": "Save 10kg of CO2",
        "points_bonus": 80
    }
}


# ============================================
# MODELS
# ============================================
class WasteClassification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image_base64: str
    classification: str
    category: str
    sub_category: Optional[str] = None
    suggestions: str
    recycling_info: str
    environmental_impact: str
    points_awarded: int = 10
    co2_saved: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str = "default_user"
    location: Optional[Dict[str, float]] = None

class WasteClassificationRequest(BaseModel):
    image_base64: str
    user_id: Optional[str] = "default_user"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None

class WasteClassificationResponse(BaseModel):
    id: str
    classification: str
    category: str
    sub_category: Optional[str]
    suggestions: str
    recycling_info: str
    environmental_impact: str
    points_awarded: int
    co2_saved: float
    nearest_bins: Optional[List[Dict[str, Any]]] = None

class BinLocation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str
    latitude: float
    longitude: float
    address: str
    status: str = "active"
    capacity: int = 100
    last_emptied: Optional<br>] = None
    timings: str = "24/7"
    accepted_waste_types: List[str] = []
    contact: Optional[str] = None
    special_instructions: Optional[str] = None

class BinLocationCreate(BaseModel):
    name: str
    type: str
    latitude: float
    longitude: float
    address: str
    status: str = "active"
    capacity: int = 100
    timings: str = "24/7"
    accepted_waste_types: List[str] = []
    contact: Optional[str] = None
    special_instructions: Optional[str] = None

class UserStats(BaseModel):
    user_id: str = "default_user"
    total_points: int = 0
    items_scanned: int = 0
    items_recycled: int = 0
    compost_items: int = 0
    ewaste_items: int = 0
    co2_saved_kg: float = 0.0
    badges: List[str] = []
    daily_streak: int = 0
    last_scan_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    monthly_stats: Dict[str, Any] = {}
    level: int = 1
    rank: Optional[str] = None

class WasteReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    location: str
    latitude: float
    longitude: float
    description: str
    image_base64: Optional[str] = None
    status: str = "pending"
    priority: str = "medium"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

class WasteReportCreate(BaseModel):
    user_id: Optional[str] = "default_user"
    location: str
    latitude: float
    longitude: float
    description: str
    image_base64: Optional[str] = None
    priority: Optional[str] = "medium"

class LeaderboardEntry(BaseModel):
    user_id: str
    username: str
    total_points: int
    items_scanned: int
    co2_saved_kg: float
    badges: List[str]
    rank: int
    level: int

class MonthlyReport(BaseModel):
    user_id: str
    month: str
    total_scans: int
    total_points: int
    co2_saved: float
    category_breakdown: Dict[str, int]
    badges_earned: List[str]
    comparison_to_last_month: Dict[str, Any]


# ============================================
# HELPER FUNCTIONS
# ============================================
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in km"""
    R = 6371  # Earth's radius in km
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance

async def find_nearest_bins(latitude: float, longitude: float, waste_category: str, limit: int = 3):
    """Find nearest bins for a specific waste category"""
    try:
        bins = await db.bin_locations.find().to_list(100)
        
        bins_with_distance = []
        for bin_data in bins:
            distance = calculate_distance(latitude, longitude, bin_data['latitude'], bin_data['longitude'])
            
            # Check if bin accepts this waste type
            bin_types = bin_data.get('accepted_waste_types', [])
            if waste_category.lower() in [t.lower() for t in bin_types] or bin_data['type'].upper() == waste_category:
                bins_with_distance.append({
                    "id": bin_data['id'],
                    "name": bin_data['name'],
                    "address": bin_data['address'],
                    "distance_km": round(distance, 2),
                    "status": bin_data['status'],
                    "timings": bin_data['timings'],
                    "capacity": bin_data['capacity']
                })
        
        # Sort by distance and return top results
        bins_with_distance.sort(key=lambda x: x['distance_km'])
        return bins_with_distance[:limit]
    except Exception as e:
        logging.error(f"Error finding nearest bins: {e}")
        return []

async def calculate_user_level(total_points: int) -> int:
    """Calculate user level based on points"""
    if total_points < 100:
        return 1
    elif total_points < 500:
        return 2
    elif total_points < 1000:
        return 3
    elif total_points < 2500:
        return 4
    elif total_points < 5000:
        return 5
    else:
        return 6

async def check_and_award_badges(stats: UserStats) -> List[str]:
    """Check and award new badges based on user stats"""
    new_badges = []
    current_badges = set(stats.badges)
    
    for badge_name, badge_info in BADGES.items():
        if badge_name not in current_badges:
            requirement = badge_info['requirement']
            # Evaluate requirement
            if eval(requirement, {"__builtins__": {}}, stats.dict()):
                new_badges.append(badge_name)
                current_badges.add(badge_name)
    
    return new_badges

async def update_daily_streak(user_id: str, last_scan_date: Optional[datetime]) -> int:
    """Update and calculate daily streak"""
    now = datetime.utcnow()
    
    if not last_scan_date:
        return 1
    
    days_diff = (now.date() - last_scan_date.date()).days
    
    if days_diff == 0:
        # Same day, keep current streak
        user_stats = await db.user_stats.find_one({"user_id": user_id})
        return user_stats.get('daily_streak', 1)
    elif days_diff == 1:
        # Consecutive day, increment streak
        user_stats = await db.user_stats.find_one({"user_id": user_id})
        return user_stats.get('daily_streak', 0) + 1
    else:
        # Streak broken, reset to 1
        return 1

def categorize_waste_from_classification(classification: str) -> tuple:
    """Determine category and sub-category from classification"""
    classification_lower = classification.lower()
    
    for category, data in WASTE_CATEGORIES.items():
        for item in data['items']:
            if item in classification_lower:
                return category, data
    
    return "LANDFILL", WASTE_CATEGORIES["LANDFILL"]

async def get_waste_disposal_tips(category: str, classification: str) -> Dict[str, str]:
    """Get detailed disposal tips for waste item"""
    tips = {
        "RECYCLE": f"Great choice! Clean and dry your {classification} before placing it in the recycling bin. Remove any caps or labels if possible.",
        "COMPOST": f"Perfect for composting! Add your {classification} to your compost bin or pile. Mix with brown materials for best results.",
        "E_WASTE": f"Important! {classification} contains valuable materials. Take it to an e-waste collection center. Never throw in regular trash!",
        "HAZARDOUS": f"Warning! {classification} requires special handling. Contact your local hazardous waste facility for proper disposal.",
        "LANDFILL": f"Unfortunately, {classification} cannot be recycled. Try to reduce usage of similar items in the future."
    }
    
    environmental_impact = {
        "RECYCLE": f"By recycling this {classification}, you're helping conserve natural resources and reduce landfill waste!",
        "COMPOST": f"Composting this {classification} enriches soil and reduces methane emissions from landfills!",
        "E_WASTE": f"Proper e-waste disposal prevents toxic materials from polluting our environment!",
        "HAZARDOUS": f"Safe disposal of {classification} protects our water and soil from contamination!",
        "LANDFILL": f"Let's work together to reduce waste that goes to landfills!"
    }
    
    return {
        "suggestions": tips.get(category, tips["LANDFILL"]),
        "environmental_impact": environmental_impact.get(category, environmental_impact["LANDFILL"])
    }


# ============================================
# AI CLASSIFICATION WITH ADVANCED LOGIC
# ============================================
@api_router.post("/classify-waste", response_model=WasteClassificationResponse)
async def classify_waste(request: WasteClassificationRequest):
    try:
        # Initialize LLM chat
        llm_key = os.environ['EMERGENT_LLM_KEY']
        chat = LlmChat(
            api_key=llm_key,
            session_id=f"waste-{uuid.uuid4()}",
            system_message="You are an expert waste management AI. Classify waste items accurately and provide detailed disposal guidance."
        ).with_model("openai", "gpt-4o-mini")
        
        # Enhanced prompt with user description
        prompt = f"""Analyze this waste item and provide classification.

{f"User description: {request.description}" if request.description else ""}

Classify into ONE category: RECYCLE, COMPOST, E_WASTE, HAZARDOUS, or LANDFILL

Provide:
1. CLASSIFICATION: Specific item name (e.g., "Plastic Water Bottle", "Banana Peel")
2. CATEGORY: ONE of [RECYCLE, COMPOST, E_WASTE, HAZARDOUS, LANDFILL]
3. DETAILS: Brief why it belongs in this category (1 sentence)

Format:
CLASSIFICATION: [item name]
CATEGORY: [category]
DETAILS: [reason]"""
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse AI response
        lines = response.strip().split('\n')
        classification = "Unknown Waste"
        category = "LANDFILL"
        details = ""
        
        for line in lines:
            if line.startswith("CLASSIFICATION:"):
                classification = line.replace("CLASSIFICATION:", "").strip()
            elif line.startswith("CATEGORY:"):
                category = line.replace("CATEGORY:", "").strip().upper()
            elif line.startswith("DETAILS:"):
                details = line.replace("DETAILS:", "").strip()
        
        # Validate and normalize category
        if category not in WASTE_CATEGORIES:
            category, category_data = categorize_waste_from_classification(classification)
        else:
            category_data = WASTE_CATEGORIES[category]
        
        # Calculate points and CO2 saved
        points_awarded = category_data['points']
        co2_saved = category_data['co2_saved_per_item']
        
        # Get disposal tips
        tips = await get_waste_disposal_tips(category, classification)
        
        # Find nearest bins if location provided
        nearest_bins = None
        if request.latitude and request.longitude:
            nearest_bins = await find_nearest_bins(
                request.latitude, 
                request.longitude, 
                category, 
                limit=3
            )
        
        # Store classification in database
        waste_obj = WasteClassification(
            image_base64=request.image_base64[:100],
            classification=classification,
            category=category,
            sub_category=details,
            suggestions=tips['suggestions'],
            recycling_info=f"{category} - {details}",
            environmental_impact=tips['environmental_impact'],
            points_awarded=points_awarded,
            co2_saved=co2_saved,
            user_id=request.user_id,
            location={"latitude": request.latitude, "longitude": request.longitude} if request.latitude else None
        )
        
        await db.waste_classifications.insert_one(waste_obj.dict())
        
        # Update user stats with advanced logic
        await update_user_stats_advanced(request.user_id, category, points_awarded, co2_saved)
        
        return WasteClassificationResponse(
            id=waste_obj.id,
            classification=classification,
            category=category,
            sub_category=details,
            suggestions=tips['suggestions'],
            recycling_info=f"{category} - {details}",
            environmental_impact=tips['environmental_impact'],
            points_awarded=points_awarded,
            co2_saved=co2_saved,
            nearest_bins=nearest_bins
        )
        
    except Exception as e:
        logging.error(f"Classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


async def update_user_stats_advanced(user_id: str, category: str, points: int, co2_saved: float):
    """Advanced user stats update with streak, level, and badge logic"""
    user_stats = await db.user_stats.find_one({"user_id": user_id})
    
    if not user_stats:
        user_stats = UserStats(user_id=user_id).dict()
        await db.user_stats.insert_one(user_stats)
        user_stats = await db.user_stats.find_one({"user_id": user_id})
    
    # Calculate new streak
    new_streak = await update_daily_streak(user_id, user_stats.get('last_scan_date'))
    
    # Update counters based on category
    category_increments = {}
    if category == "RECYCLE":
        category_increments['items_recycled'] = 1
    elif category == "COMPOST":
        category_increments['compost_items'] = 1
    elif category == "E_WASTE":
        category_increments['ewaste_items'] = 1
    
    # Update user stats
    update_data = {
        "$inc": {
            "total_points": points,
            "items_scanned": 1,
            "co2_saved_kg": co2_saved,
            **category_increments
        },
        "$set": {
            "updated_at": datetime.utcnow(),
            "last_scan_date": datetime.utcnow(),
            "daily_streak": new_streak
        }
    }
    
    await db.user_stats.update_one({"user_id": user_id}, update_data)
    
    # Reload stats and check badges
    updated_stats = await db.user_stats.find_one({"user_id": user_id})
    stats_obj = UserStats(**updated_stats)
    
    # Check and award new badges
    new_badges = await check_and_award_badges(stats_obj)
    
    if new_badges:
        for badge in new_badges:
            bonus_points = BADGES[badge]['points_bonus']
            await db.user_stats.update_one(
                {"user_id": user_id},
                {
                    "$push": {"badges": badge},
                    "$inc": {"total_points": bonus_points}
                }
            )
        
        logging.info(f"Awarded badges: {new_badges} to user {user_id}")
    
    # Update level
    total_points = stats_obj.total_points + sum(BADGES[b]['points_bonus'] for b in new_badges)
    new_level = await calculate_user_level(total_points)
    
    await db.user_stats.update_one(
        {"user_id": user_id},
        {"$set": {"level": new_level}}
    )


# ============================================
# BIN LOCATIONS WITH ADVANCED FEATURES
# ============================================
@api_router.get("/bins", response_model=List[BinLocation])
async def get_bins(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    waste_type: Optional[str] = None,
    radius_km: Optional[float] = 10.0,
    status: Optional[str] = None
):
    """Get bin locations with filtering and sorting options"""
    try:
        query = {}
        if status:
            query['status'] = status
        
        bins = await db.bin_locations.find(query).to_list(100)
        
        # Filter by waste type
        if waste_type:
            bins = [b for b in bins if waste_type.lower() in [t.lower() for t in b.get('accepted_waste_types', [])] 
                    or b['type'].lower() == waste_type.lower()]
        
        # Calculate distances and filter by radius
        if latitude and longitude:
            bins_with_distance = []
            for bin_data in bins:
                distance = calculate_distance(latitude, longitude, bin_data['latitude'], bin_data['longitude'])
                if distance <= radius_km:
                    bin_data['distance'] = round(distance, 2)
                    bins_with_distance.append(bin_data)
            
            # Sort by distance
            bins_with_distance.sort(key=lambda x: x.get('distance', float('inf')))
            bins = bins_with_distance
        
        return [BinLocation(**bin_data) for bin_data in bins]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bins", response_model=BinLocation)
async def create_bin(bin_data: BinLocationCreate):
    """Create new bin location"""
    try:
        bin_obj = BinLocation(**bin_data.dict())
        await db.bin_locations.insert_one(bin_obj.dict())
        return bin_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/bins/{bin_id}/capacity")
async def update_bin_capacity(bin_id: str, capacity: int):
    """Update bin capacity"""
    try:
        result = await db.bin_locations.update_one(
            {"id": bin_id},
            {"$set": {"capacity": capacity}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Bin not found")
        return {"message": "Capacity updated", "bin_id": bin_id, "new_capacity": capacity}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# USER STATS WITH ADVANCED ANALYTICS
# ============================================
@api_router.get("/user-stats/{user_id}", response_model=UserStats)
async def get_user_stats(user_id: str = "default_user"):
    """Get comprehensive user statistics"""
    try:
        user_stats = await db.user_stats.find_one({"user_id": user_id})
        
        if not user_stats:
            new_stats = UserStats(user_id=user_id)
            await db.user_stats.insert_one(new_stats.dict())
            return new_stats
        
        stats_obj = UserStats(**user_stats)
        
        # Check for new badges
        new_badges = await check_and_award_badges(stats_obj)
        if new_badges:
            for badge in new_badges:
                bonus_points = BADGES[badge]['points_bonus']
                await db.user_stats.update_one(
                    {"user_id": user_id},
                    {
                        "$push": {"badges": badge},
                        "$inc": {"total_points": bonus_points}
                    }
                )
            stats_obj = UserStats(**await db.user_stats.find_one({"user_id": user_id}))
        
        # Update rank
        all_users = await db.user_stats.find().sort("total_points", -1).to_list(1000)
        rank_position = next((i+1 for i, u in enumerate(all_users) if u['user_id'] == user_id), None)
        
        if rank_position:
            rank_title = "Beginner" if rank_position > 100 else "Expert" if rank_position > 10 else "Master" if rank_position > 3 else "Legend"
            await db.user_stats.update_one(
                {"user_id": user_id},
                {"$set": {"rank": rank_title}}
            )
            stats_obj.rank = rank_title
        
        return stats_obj
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/user-stats/{user_id}/history")
async def get_user_history(user_id: str, days: int = 30):
    """Get user's waste classification history"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        history = await db.waste_classifications.find({
            "user_id": user_id,
            "timestamp": {"$gte": cutoff_date}
        }).sort("timestamp", -1).to_list(100)
        
        # Aggregate by category
        category_breakdown = defaultdict(int)
        daily_scans = defaultdict(int)
        
        for item in history:
            category_breakdown[item['category']] += 1
            date_key = item['timestamp'].strftime("%Y-%m-%d")
            daily_scans[date_key] += 1
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_scans": len(history),
            "category_breakdown": dict(category_breakdown),
            "daily_activity": dict(daily_scans),
            "recent_items": history[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/user-stats/{user_id}/monthly-report", response_model=MonthlyReport)
async def get_monthly_report(user_id: str, month: Optional[str] = None):
    """Generate monthly report for user"""
    try:
        if not month:
            month = datetime.utcnow().strftime("%Y-%m")
        
        # Parse month
        year, month_num = map(int, month.split("-"))
        start_date = datetime(year, month_num, 1)
        
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month_num + 1, 1)
        
        # Get this month's data
        this_month_data = await db.waste_classifications.find({
            "user_id": user_id,
            "timestamp": {"$gte": start_date, "$lt": end_date}
        }).to_list(1000)
        
        # Get last month's data for comparison
        last_month_start = start_date - timedelta(days=30)
        last_month_data = await db.waste_classifications.find({
            "user_id": user_id,
            "timestamp": {"$gte": last_month_start, "$lt": start_date}
        }).to_list(1000)
        
        # Calculate statistics
        category_breakdown = defaultdict(int)
        total_points = 0
        total_co2 = 0.0
        
        for item in this_month_data:
            category_breakdown[item['category']] += 1
            total_points += item.get('points_awarded', 0)
            total_co2 += item.get('co2_saved', 0.0)
        
        # Get badges earned this month
        user_stats = await db.user_stats.find_one({"user_id": user_id})
        badges_earned = user_stats.get('badges', []) if user_stats else []
        
        # Comparison to last month
        comparison = {
            "scans_change": len(this_month_data) - len(last_month_data),
            "scans_change_percent": ((len(this_month_data) - len(last_month_data)) / max(len(last_month_data), 1)) * 100
        }
        
        return MonthlyReport(
            user_id=user_id,
            month=month,
            total_scans=len(this_month_data),
            total_points=total_points,
            co2_saved=round(total_co2, 2),
            category_breakdown=dict(category_breakdown),
            badges_earned=badges_earned,
            comparison_to_last_month=comparison
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# LEADERBOARD SYSTEM
# ============================================
@api_router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 10, timeframe: str = "all_time"):
    """Get leaderboard rankings"""
    try:
        # Determine time filter
        query = {}
        if timeframe == "weekly":
            cutoff = datetime.utcnow() - timedelta(days=7)
            # Get weekly leaders based on recent activity
            users = await db.user_stats.find({
                "last_scan_date": {"$gte": cutoff}
            }).sort("total_points", -1).limit(limit).to_list(limit)
        elif timeframe == "monthly":
            cutoff = datetime.utcnow() - timedelta(days=30)
            users = await db.user_stats.find({
                "last_scan_date": {"$gte": cutoff}
            }).sort("total_points", -1).limit(limit).to_list(limit)
        else:
            users = await db.user_stats.find().sort("total_points", -1).limit(limit).to_list(limit)
        
        leaderboard = []
        for rank, user in enumerate(users, 1):
            leaderboard.append(LeaderboardEntry(
                user_id=user['user_id'],
                username=f"User{user['user_id'][-4:]}",  # Anonymous username
                total_points=user['total_points'],
                items_scanned=user['items_scanned'],
                co2_saved_kg=user['co2_saved_kg'],
                badges=user['badges'],
                rank=rank,
                level=user.get('level', 1)
            ))
        
        return leaderboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# WASTE REPORTS WITH PRIORITY
# ============================================
@api_router.post("/reports", response_model=WasteReport)
async def create_report(report_data: WasteReportCreate):
    """Create waste report with priority assignment"""
    try:
        report_obj = WasteReport(**report_data.dict())
        await db.waste_reports.insert_one(report_obj.dict())
        
        # Award points based on priority
        points = {"low": 3, "medium": 5, "high": 10}.get(report_data.priority, 5)
        
        await db.user_stats.update_one(
            {"user_id": report_data.user_id},
            {
                "$inc": {"total_points": points},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return report_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/reports", response_model=List[WasteReport])
async def get_reports(status: Optional[str] = None, priority: Optional[str] = None, limit: int = 50):
    """Get waste reports with filtering"""
    try:
        query = {}
        if status:
            query['status'] = status
        if priority:
            query['priority'] = priority
        
        reports = await db.waste_reports.find(query).sort("timestamp", -1).limit(limit).to_list(limit)
        return [WasteReport(**report) for report in reports]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/reports/{report_id}/status")
async def update_report_status(report_id: str, status: str):
    """Update report status"""
    try:
        update_data = {"status": status}
        if status == "resolved":
            update_data["resolved_at"] = datetime.utcnow()
        
        result = await db.waste_reports.update_one(
            {"id": report_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {"message": "Report status updated", "report_id": report_id, "new_status": status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ANALYTICS & INSIGHTS
# ============================================
@api_router.get("/analytics/global")
async def get_global_analytics():
    """Get global platform analytics"""
    try:
        total_users = await db.user_stats.count_documents({})
        total_scans = await db.waste_classifications.count_documents({})
        
        # Aggregate CO2 saved
        pipeline = [
            {"$group": {
                "_id": None,
                "total_co2": {"$sum": "$co2_saved_kg"},
                "total_points": {"$sum": "$total_points"}
            }}
        ]
        
        result = await db.user_stats.aggregate(pipeline).to_list(1)
        total_co2 = result[0]['total_co2'] if result else 0
        total_points_global = result[0]['total_points'] if result else 0
        
        # Category breakdown
        category_pipeline = [
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1}
            }}
        ]
        
        category_data = await db.waste_classifications.aggregate(category_pipeline).to_list(10)
        category_breakdown = {item['_id']: item['count'] for item in category_data}
        
        return {
            "total_users": total_users,
            "total_scans": total_scans,
            "total_co2_saved_kg": round(total_co2, 2),
            "total_points_awarded": total_points_global,
            "category_breakdown": category_breakdown,
            "active_bins": await db.bin_locations.count_documents({"status": "active"}),
            "reports_resolved": await db.waste_reports.count_documents({"status": "resolved"})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tips/{category}")
async def get_waste_tips(category: str):
    """Get waste management tips for a category"""
    try:
        category = category.upper()
        if category not in WASTE_CATEGORIES:
            raise HTTPException(status_code=404, detail="Category not found")
        
        category_data = WASTE_CATEGORIES[category]
        
        tips_database = {
            "RECYCLE": [
                "Rinse containers before recycling to avoid contamination",
                "Remove caps and lids from bottles",
                "Flatten cardboard boxes to save space",
                "Don't bag recyclables - keep them loose",
                "Check local guidelines for specific materials"
            ],
            "COMPOST": [
                "Balance green and brown materials",
                "Turn your compost regularly for faster decomposition",
                "Keep compost moist but not waterlogged",
                "Avoid meat, dairy, and oily foods",
                "Chop large items for faster breakdown"
            ],
            "E_WASTE": [
                "Never throw electronics in regular trash",
                "Remove batteries before recycling devices",
                "Delete personal data before disposing",
                "Look for manufacturer take-back programs",
                "E-waste contains valuable recoverable materials"
            ],
            "HAZARDOUS": [
                "Store hazardous waste in original containers",
                "Never mix different chemicals",
                "Contact local hazardous waste facility",
                "Use up products completely when possible",
                "Consider safer alternatives for future purchases"
            ],
            "LANDFILL": [
                "Try to reduce landfill waste",
                "Consider repairing instead of discarding",
                "Explore creative reuse options",
                "Check if items can be donated",
                "Future purchases: choose recyclable alternatives"
            ]
        }
        
        return {
            "category": category,
            "accepted_items": category_data['items'],
            "tips": tips_database.get(category, []),
            "co2_impact_per_item": category_data['co2_saved_per_item'],
            "points_per_item": category_data['points']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HEALTH CHECK & SEED DATA
# ============================================
@api_router.get("/")
async def root():
    return {
        "message": "CleanCity API v2.0 - Enhanced Edition",
        "status": "healthy",
        "features": [
            "AI Waste Classification",
            "Location-based Bin Finder",
            "Advanced User Stats & Levels",
            "Badge System with 7 achievements",
            "Daily Streak Tracking",
            "Leaderboard",
            "Monthly Reports",
            "Global Analytics",
            "Waste Management Tips"
        ]
    }

@api_router.post("/seed-data")
async def seed_data():
    """Seed database with enhanced sample data"""
    try:
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
                "timings": "6 AM - 10 PM",
                "accepted_waste_types": ["RECYCLE", "paper", "plastic", "metal", "glass"],
                "contact": "+1-212-555-0100",
                "special_instructions": "Please rinse containers before disposal"
            },
            {
                "name": "Downtown Compost Center",
                "type": "compost",
                "latitude": 40.7489,
                "longitude": -73.9680,
                "address": "Downtown Manhattan, NY",
                "status": "active",
                "capacity": 60,
                "timings": "24/7",
                "accepted_waste_types": ["COMPOST", "organic", "food waste"],
                "contact": "+1-212-555-0101",
                "special_instructions": "No meat or dairy products"
            },
            {
                "name": "Brooklyn E-Waste Drop-off",
                "type": "e-waste",
                "latitude": 40.6782,
                "longitude": -73.9442,
                "address": "Brooklyn, NY",
                "status": "active",
                "capacity": 90,
                "timings": "9 AM - 6 PM",
                "accepted_waste_types": ["E_WASTE", "electronics", "batteries"],
                "contact": "+1-718-555-0102",
                "special_instructions": "Remove batteries and delete personal data"
            },
            {
                "name": "Queens Hazardous Waste Facility",
                "type": "hazardous",
                "latitude": 40.7282,
                "longitude": -73.7949,
                "address": "Queens, NY",
                "status": "active",
                "capacity": 45,
                "timings": "Mon-Fri 8 AM - 4 PM",
                "accepted_waste_types": ["HAZARDOUS", "chemicals", "paint", "oil"],
                "contact": "+1-718-555-0103",
                "special_instructions": "Bring items in original containers"
            },
            {
                "name": "Bronx Recycling Point",
                "type": "recycling",
                "latitude": 40.8448,
                "longitude": -73.8648,
                "address": "Bronx, NY",
                "status": "full",
                "capacity": 100,
                "timings": "7 AM - 9 PM",
                "accepted_waste_types": ["RECYCLE", "plastic", "cardboard"],
                "contact": "+1-718-555-0104",
                "special_instructions": "Currently at full capacity - will be emptied soon"
            },
            {
                "name": "Staten Island Mixed Waste Center",
                "type": "general",
                "latitude": 40.5795,
                "longitude": -74.1502,
                "address": "Staten Island, NY",
                "status": "active",
                "capacity": 55,
                "timings": "24/7",
                "accepted_waste_types": ["RECYCLE", "COMPOST", "LANDFILL"],
                "contact": "+1-718-555-0105",
                "special_instructions": "Separate waste by category at drop-off"
            }
        ]
        
        for bin_data in sample_bins:
            bin_obj = BinLocation(**bin_data)
            await db.bin_locations.insert_one(bin_obj.dict())
        
        return {
            "message": f"Successfully seeded {len(sample_bins)} bin locations with enhanced data",
            "features": "Contact info, special instructions, and accepted waste types added"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Include router and configure app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

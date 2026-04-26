#!/usr/bin/env python3
"""
FastAPI приложение для фитнес-трекера
"""

from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from datetime import datetime, date
from bson import ObjectId
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Fitness Tracker API", description="API для фитнес-трекера")

# Подключение к MongoDB
client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
db = client[os.getenv("MONGODB_DB", "fitness_tracker")]

# Pydantic модели
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserCreate(BaseModel):
    login: str = Field(..., min_length=3, max_length=30, pattern="^[a-zA-Z0-9_]+$")
    firstName: str = Field(..., min_length=1, max_length=50)
    lastName: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    dateOfBirth: date
    weight: Optional[float] = Field(None, ge=20, le=300)
    height: Optional[float] = Field(None, ge=100, le=250)

class UserResponse(BaseModel):
    id: str
    login: str
    firstName: str
    lastName: str
    email: str
    dateOfBirth: date
    weight: Optional[float]
    height: Optional[float]
    createdAt: datetime

class ExerciseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    muscleGroup: List[str]
    difficulty: str = Field(..., pattern="^(beginner|intermediate|advanced)$")
    caloriesPerMinute: float = Field(..., ge=0, le=50)

class ExerciseResponse(BaseModel):
    id: str
    name: str
    category: str
    muscleGroup: List[str]
    difficulty: str
    caloriesPerMinute: float

class SetCreate(BaseModel):
    setNumber: int
    reps: int = Field(..., ge=1, le=100)
    weight: Optional[float] = Field(None, ge=0)
    timeInSeconds: Optional[int] = Field(None, ge=0)

class WorkoutExerciseCreate(BaseModel):
    exerciseId: str
    exerciseName: str
    sets: List[SetCreate]
    restTime: int = Field(..., ge=0, le=300)

class WorkoutCreate(BaseModel):
    workoutDate: datetime
    duration: int = Field(..., ge=1, le=720)
    notes: Optional[str] = ""
    exercises: List[WorkoutExerciseCreate]
    rating: Optional[int] = Field(None, ge=1, le=5)

class WorkoutResponse(BaseModel):
    id: str
    userId: str
    workoutDate: datetime
    duration: int
    notes: str
    exercises: List[dict]
    caloriesBurned: Optional[int]
    rating: Optional[int]
    createdAt: datetime

# Вспомогательные функции
def serialize_doc(doc):
    """Преобразование MongoDB документа в JSON-сериализуемый объект"""
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc

# API endpoints
@app.post("/api/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """Создание нового пользователя"""
    # Проверка на уникальность логина
    existing = db.users.find_one({"login": user.login})
    if existing:
        raise HTTPException(status_code=409, detail="Login already exists")
    
    user_dict = user.dict()
    user_dict["dateOfBirth"] = datetime.combine(user.dateOfBirth, datetime.min.time())
    user_dict["createdAt"] = datetime.now()
    
    result = db.users.insert_one(user_dict)
    created = db.users.find_one({"_id": result.inserted_id})
    return serialize_doc(created)

@app.get("/api/users/login/{login}", response_model=UserResponse)
async def find_user_by_login(login: str):
    """Поиск пользователя по логину"""
    user = db.users.find_one({"login": login})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_doc(user)

@app.get("/api/users/search")
async def find_users_by_name_mask(
    firstName: Optional[str] = Query(None, min_length=1),
    lastName: Optional[str] = Query(None, min_length=1)
):
    """Поиск пользователя по маске имени и фамилии"""
    query = {}
    if firstName:
        query["firstName"] = {"$regex": firstName, "$options": "i"}
    if lastName:
        query["lastName"] = {"$regex": lastName, "$options": "i"}
    
    users = list(db.users.find(query))
    return [serialize_doc(u) for u in users]

@app.post("/api/exercises", response_model=ExerciseResponse, status_code=201)
async def create_exercise(exercise: ExerciseCreate):
    """Создание упражнения"""
    exercise_dict = exercise.dict()
    result = db.exercises.insert_one(exercise_dict)
    created = db.exercises.find_one({"_id": result.inserted_id})
    return serialize_doc(created)

@app.get("/api/exercises")
async def get_exercises(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500)
):
    """Получение списка упражнений с фильтрацией"""
    query = {}
    if category:
        query["category"] = category
    if difficulty:
        query["difficulty"] = difficulty
    
    exercises = list(db.exercises.find(query).limit(limit))
    return [serialize_doc(ex) for ex in exercises]

@app.post("/api/workouts", response_model=WorkoutResponse, status_code=201)
async def create_workout(user_id: str, workout: WorkoutCreate):
    """Создание тренировки для пользователя"""
    # Проверка существования пользователя
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    workout_dict = workout.dict()
    workout_dict["userId"] = ObjectId(user_id)
    workout_dict["createdAt"] = datetime.now()
    
    # Расчет калорий
    total_calories = 0
    for ex in workout_dict["exercises"]:
        exercise = db.exercises.find_one({"_id": ObjectId(ex["exerciseId"])})
        if exercise:
            # Упрощенный расчет
            ex_duration = workout_dict["duration"] / len(workout_dict["exercises"])
            total_calories += exercise["caloriesPerMinute"] * ex_duration
    workout_dict["caloriesBurned"] = int(total_calories)
    
    result = db.workouts.insert_one(workout_dict)
    created = db.workouts.find_one({"_id": result.inserted_id})
    return serialize_doc(created)

@app.put("/api/workouts/{workout_id}/exercises")
async def add_exercise_to_workout(workout_id: str, exercise: WorkoutExerciseCreate):
    """Добавление упражнения в тренировку"""
    exercise_dict = exercise.dict()
    exercise_dict["exerciseId"] = ObjectId(exercise.exerciseId)
    
    result = db.workouts.update_one(
        {"_id": ObjectId(workout_id)},
        {"$push": {"exercises": exercise_dict}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    updated = db.workouts.find_one({"_id": ObjectId(workout_id)})
    return serialize_doc(updated)

@app.get("/api/users/{user_id}/workouts")
async def get_user_workout_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0)
):
    """Получение истории тренировок пользователя"""
    # Проверка существования пользователя
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    workouts = list(db.workouts.find(
        {"userId": ObjectId(user_id)}
    ).sort("workoutDate", -1).skip(skip).limit(limit))
    
    return [serialize_doc(w) for w in workouts]

@app.get("/api/users/{user_id}/statistics")
async def get_workout_statistics(
    user_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Получение статистики тренировок за период"""
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = {"userId": ObjectId(user_id)}
    
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = datetime.combine(start_date, datetime.min.time())
        if end_date:
            date_filter["$lte"] = datetime.combine(end_date, datetime.max.time())
        query["workoutDate"] = date_filter
    
    workouts = list(db.workouts.find(query))
    
    if not workouts:
        return {
            "totalWorkouts": 0,
            "totalDuration": 0,
            "totalCalories": 0,
            "avgDuration": 0,
            "avgRating": 0
        }
    
    total_workouts = len(workouts)
    total_duration = sum(w.get("duration", 0) for w in workouts)
    total_calories = sum(w.get("caloriesBurned", 0) for w in workouts)
    avg_duration = total_duration / total_workouts
    ratings = [w.get("rating") for w in workouts if w.get("rating")]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    return {
        "totalWorkouts": total_workouts,
        "totalDuration": total_duration,
        "totalCalories": total_calories,
        "avgDuration": round(avg_duration, 0),
        "avgRating": round(avg_rating, 1)
    }

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str):
    """Удаление пользователя и всех его тренировок"""
    # Удаляем все тренировки пользователя
    db.workouts.delete_many({"userId": ObjectId(user_id)})
    # Удаляем пользователя
    result = db.users.delete_one({"_id": ObjectId(user_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User and all associated workouts deleted"}

@app.get("/api/health")
async def health_check():
    """Проверка здоровья сервиса"""
    try:
        client.admin.command('ping')
        return {"status": "healthy", "mongodb": "connected"}
    except:
        raise HTTPException(status_code=503, detail="MongoDB connection failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
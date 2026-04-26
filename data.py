#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных тестовыми данными
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# Подключение к MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['fitness_tracker']

def clear_collections():
    """Очистка существующих коллекций"""
    db.users.delete_many({})
    db.exercises.delete_many({})
    db.workouts.delete_many({})
    print("Collections cleared")

def insert_users():
    """Вставка пользователей"""
    users = [
        {
            "login": "john_doe",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "dateOfBirth": datetime(1990, 1, 15),
            "weight": 75.5,
            "height": 180,
            "createdAt": datetime.now()
        },
        {
            "login": "jane_smith",
            "firstName": "Jane",
            "lastName": "Smith",
            "email": "jane@example.com",
            "dateOfBirth": datetime(1988, 5, 22),
            "weight": 62.3,
            "height": 165,
            "createdAt": datetime.now()
        },
        {
            "login": "mike_johnson",
            "firstName": "Mike",
            "lastName": "Johnson",
            "email": "mike@example.com",
            "dateOfBirth": datetime(1995, 8, 10),
            "weight": 82.1,
            "height": 185,
            "createdAt": datetime.now()
        },
        {
            "login": "sarah_wilson",
            "firstName": "Sarah",
            "lastName": "Wilson",
            "email": "sarah@example.com",
            "dateOfBirth": datetime(1992, 3, 17),
            "weight": 58.7,
            "height": 162,
            "createdAt": datetime.now()
        },
        {
            "login": "alex_brown",
            "firstName": "Alex",
            "lastName": "Brown",
            "email": "alex@example.com",
            "dateOfBirth": datetime(1985, 11, 30),
            "weight": 88.4,
            "height": 190,
            "createdAt": datetime.now()
        },
        {
            "login": "emily_davis",
            "firstName": "Emily",
            "lastName": "Davis",
            "email": "emily@example.com",
            "dateOfBirth": datetime(1998, 7, 4),
            "weight": 55.2,
            "height": 158,
            "createdAt": datetime.now()
        },
        {
            "login": "chris_martin",
            "firstName": "Chris",
            "lastName": "Martin",
            "email": "chris@example.com",
            "dateOfBirth": datetime(1987, 9, 12),
            "weight": 79.3,
            "height": 178,
            "createdAt": datetime.now()
        },
        {
            "login": "lisa_anderson",
            "firstName": "Lisa",
            "lastName": "Anderson",
            "email": "lisa@example.com",
            "dateOfBirth": datetime(1993, 12, 1),
            "weight": 65.8,
            "height": 170,
            "createdAt": datetime.now()
        },
        {
            "login": "tom_wilson",
            "firstName": "Tom",
            "lastName": "Wilson",
            "email": "tom@example.com",
            "dateOfBirth": datetime(1991, 6, 18),
            "weight": 72.5,
            "height": 175,
            "createdAt": datetime.now()
        },
        {
            "login": "amy_clark",
            "firstName": "Amy",
            "lastName": "Clark",
            "email": "amy@example.com",
            "dateOfBirth": datetime(1994, 2, 28),
            "weight": 60.4,
            "height": 168,
            "createdAt": datetime.now()
        }
    ]
    
    result = db.users.insert_many(users)
    print(f"Inserted {len(result.inserted_ids)} users")
    return result.inserted_ids

def insert_exercises():
    """Вставка упражнений"""
    exercises = [
        {
            "name": "Bench Press",
            "category": "chest",
            "muscleGroup": ["pectoralis major", "triceps", "anterior deltoid"],
            "difficulty": "intermediate",
            "caloriesPerMinute": 8.5
        },
        {
            "name": "Squat",
            "category": "legs",
            "muscleGroup": ["quadriceps", "hamstrings", "glutes", "erector spinae"],
            "difficulty": "advanced",
            "caloriesPerMinute": 10.2
        },
        {
            "name": "Deadlift",
            "category": "back",
            "muscleGroup": ["erector spinae", "glutes", "hamstrings", "traps"],
            "difficulty": "advanced",
            "caloriesPerMinute": 11.5
        },
        {
            "name": "Pull-Up",
            "category": "back",
            "muscleGroup": ["latissimus dorsi", "biceps", "rhomboids"],
            "difficulty": "advanced",
            "caloriesPerMinute": 9.8
        },
        {
            "name": "Push-Up",
            "category": "chest",
            "muscleGroup": ["pectoralis major", "triceps", "anterior deltoid"],
            "difficulty": "beginner",
            "caloriesPerMinute": 7.2
        },
        {
            "name": "Overhead Press",
            "category": "shoulders",
            "muscleGroup": ["deltoids", "triceps", "upper traps"],
            "difficulty": "intermediate",
            "caloriesPerMinute": 8.9
        },
        {
            "name": "Barbell Row",
            "category": "back",
            "muscleGroup": ["latissimus dorsi", "rhomboids", "biceps", "rear delts"],
            "difficulty": "intermediate",
            "caloriesPerMinute": 9.1
        },
        {
            "name": "Leg Press",
            "category": "legs",
            "muscleGroup": ["quadriceps", "hamstrings", "glutes"],
            "difficulty": "beginner",
            "caloriesPerMinute": 7.8
        },
        {
            "name": "Dumbbell Curl",
            "category": "arms",
            "muscleGroup": ["biceps", "brachialis"],
            "difficulty": "beginner",
            "caloriesPerMinute": 6.5
        },
        {
            "name": "Triceps Pushdown",
            "category": "arms",
            "muscleGroup": ["triceps brachii"],
            "difficulty": "beginner",
            "caloriesPerMinute": 6.8
        }
    ]
    
    result = db.exercises.insert_many(exercises)
    print(f"Inserted {len(result.inserted_ids)} exercises")
    
    # Возвращаем словарь с id упражнений для удобства
    exercises_dict = {}
    for ex in exercises:
        found = db.exercises.find_one({"name": ex["name"]})
        if found:
            exercises_dict[ex["name"]] = found["_id"]
    return exercises_dict

def insert_workouts(users, exercises):
    """Вставка тренировок"""
    workouts = []
    
    # Получаем ID пользователей
    john = db.users.find_one({"login": "john_doe"})
    jane = db.users.find_one({"login": "jane_smith"})
    mike = db.users.find_one({"login": "mike_johnson"})
    sarah = db.users.find_one({"login": "sarah_wilson"})
    
    # Тренировка 1: John - Chest day
    workouts.append({
        "userId": john["_id"],
        "workoutDate": datetime(2024, 1, 10, 9, 30),
        "duration": 45,
        "notes": "Good chest workout, felt strong",
        "exercises": [
            {
                "exerciseId": exercises["Bench Press"],
                "exerciseName": "Bench Press",
                "sets": [
                    {"setNumber": 1, "reps": 12, "weight": 60, "timeInSeconds": None},
                    {"setNumber": 2, "reps": 10, "weight": 80, "timeInSeconds": None},
                    {"setNumber": 3, "reps": 8, "weight": 90, "timeInSeconds": None},
                    {"setNumber": 4, "reps": 6, "weight": 100, "timeInSeconds": None}
                ],
                "restTime": 90
            },
            {
                "exerciseId": exercises["Push-Up"],
                "exerciseName": "Push-Up",
                "sets": [
                    {"setNumber": 1, "reps": 15, "weight": None, "timeInSeconds": None},
                    {"setNumber": 2, "reps": 15, "weight": None, "timeInSeconds": None},
                    {"setNumber": 3, "reps": 12, "weight": None, "timeInSeconds": None}
                ],
                "restTime": 60
            }
        ],
        "caloriesBurned": 380,
        "rating": 5
    })
    
    # Тренировка 2: John - Leg day
    workouts.append({
        "userId": john["_id"],
        "workoutDate": datetime(2024, 1, 12, 17, 0),
        "duration": 60,
        "notes": "Heavy leg day, PR on squat",
        "exercises": [
            {
                "exerciseId": exercises["Squat"],
                "exerciseName": "Squat",
                "sets": [
                    {"setNumber": 1, "reps": 10, "weight": 80, "timeInSeconds": None},
                    {"setNumber": 2, "reps": 8, "weight": 100, "timeInSeconds": None},
                    {"setNumber": 3, "reps": 6, "weight": 120, "timeInSeconds": None},
                    {"setNumber": 4, "reps": 5, "weight": 130, "timeInSeconds": None}
                ],
                "restTime": 120
            },
            {
                "exerciseId": exercises["Leg Press"],
                "exerciseName": "Leg Press",
                "sets": [
                    {"setNumber": 1, "reps": 12, "weight": 150, "timeInSeconds": None},
                    {"setNumber": 2, "reps": 10, "weight": 180, "timeInSeconds": None},
                    {"setNumber": 3, "reps": 8, "weight": 200, "timeInSeconds": None}
                ],
                "restTime": 90
            }
        ],
        "caloriesBurned": 520,
        "rating": 5
    })
    
    # Тренировка 3: Jane - Back day
    workouts.append({
        "userId": jane["_id"],
        "workoutDate": datetime(2024, 1, 11, 8, 0),
        "duration": 50,
        "notes": "Focus on form",
        "exercises": [
            {
                "exerciseId": exercises["Deadlift"],
                "exerciseName": "Deadlift",
                "sets": [
                    {"setNumber": 1, "reps": 8, "weight": 60, "timeInSeconds": None},
                    {"setNumber": 2, "reps": 6, "weight": 80, "timeInSeconds": None},
                    {"setNumber": 3, "reps": 5, "weight": 90, "timeInSeconds": None}
                ],
                "restTime": 120
            },
            {
                "exerciseId": exercises["Pull-Up"],
                "exerciseName": "Pull-Up",
                "sets": [
                    {"setNumber": 1, "reps": 8, "weight": None, "timeInSeconds": None},
                    {"setNumber": 2, "reps": 7, "weight": None, "timeInSeconds": None},
                    {"setNumber": 3, "reps": 6, "weight": None, "timeInSeconds": None}
                ],
                "restTime": 90
            }
        ],
        "caloriesBurned": 420,
        "rating": 4
    })
    
    # Тренировка 4: Mike - Full body
    workouts.append({
        "userId": mike["_id"],
        "workoutDate": datetime(2024, 1, 13, 18, 30),
        "duration": 75,
        "notes": "High volume day",
        "exercises": [
            {
                "exerciseId": exercises["Overhead Press"],
                "exerciseName": "Overhead Press",
                "sets": [
                    {"setNumber": 1, "reps": 10, "weight": 40, "timeInSeconds": None},
                    {"setNumber": 2, "reps": 8, "weight": 50, "timeInSeconds": None},
                    {"setNumber": 3, "reps": 8, "weight": 50, "timeInSeconds": None}
                ],
                "restTime": 90
            },
            {
                "exerciseId": exercises["Barbell Row"],
                "exerciseName": "Barbell Row",
                "sets": [
                    {"setNumber": 1, "reps": 10, "weight": 50, "timeInSeconds": None},
                    {"setNumber": 2, "reps": 10, "weight": 60, "timeInSeconds": None},
                    {"setNumber": 3, "reps": 8, "weight": 70, "timeInSeconds": None}
                ],
                "restTime": 90
            },
            {
                "exerciseId": exercises["Dumbbell Curl"],
                "exerciseName": "Dumbbell Curl",
                "sets": [
                    {"setNumber": 1, "reps": 12, "weight": 12, "timeInSeconds": None},
                    {"setNumber": 2, "reps": 10, "weight": 14, "timeInSeconds": None},
                    {"setNumber": 3, "reps": 8, "weight": 16, "timeInSeconds": None}
                ],
                "restTime": 60
            }
        ],
        "caloriesBurned": 650,
        "rating": 4
    })
    
    # Тренировка 5: Sarah - Quick cardio + arms
    workouts.append({
        "userId": sarah["_id"],
        "workoutDate": datetime(2024, 1, 14, 7, 30),
        "duration": 35,
        "notes": "Morning workout, limited time",
        "exercises": [
            {
                "exerciseId": exercises["Triceps Pushdown"],
                "exerciseName": "Triceps Pushdown",
                "sets": [
                    {"setNumber": 1, "reps": 15, "weight": 20, "timeInSeconds": None},
                    {"setNumber": 2, "reps": 12, "weight": 25, "timeInSeconds": None},
                    {"setNumber": 3, "reps": 10, "weight": 30, "timeInSeconds": None}
                ],
                "restTime": 60
            },
            {
                "exerciseId": exercises["Dumbbell Curl"],
                "exerciseName": "Dumbbell Curl",
                "sets": [
                    {"setNumber": 1, "reps": 12, "weight": 8, "timeInSeconds": None},
                    {"setNumber": 2, "reps": 12, "weight": 8, "timeInSeconds": None},
                    {"setNumber": 3, "reps": 10, "weight": 10, "timeInSeconds": None}
                ],
                "restTime": 60
            }
        ],
        "caloriesBurned": 280,
        "rating": 3
    })
    
    # Добавляем еще 5 тренировок для статистики
    for i in range(5):
        workouts.append({
            "userId": john["_id"],
            "workoutDate": datetime(2024, 1, 5 + i, random.randint(8, 20), random.randint(0, 59)),
            "duration": random.randint(30, 90),
            "notes": f"Regular workout #{i+1}",
            "exercises": [
                {
                    "exerciseId": exercises["Bench Press"],
                    "exerciseName": "Bench Press",
                    "sets": [
                        {"setNumber": 1, "reps": 10, "weight": 70, "timeInSeconds": None},
                        {"setNumber": 2, "reps": 8, "weight": 80, "timeInSeconds": None}
                    ],
                    "restTime": 90
                }
            ],
            "caloriesBurned": random.randint(200, 500),
            "rating": random.randint(3, 5)
        })
    
    result = db.workouts.insert_many(workouts)
    print(f"Inserted {len(result.inserted_ids)} workouts")

def create_indexes():
    """Создание индексов для оптимизации запросов"""
    # Уникальный индекс по логину
    db.users.create_index([("login", 1)], unique=True)
    
    # Текстовый индекс для поиска по имени и фамилии
    db.users.create_index([("firstName", "text"), ("lastName", "text")])
    
    # Составной индекс для фильтрации тренировок
    db.workouts.create_index([("userId", 1), ("workoutDate", -1)])
    
    # Индекс для поиска по категории упражнений
    db.exercises.create_index([("category", 1)])
    
    print("Indexes created")

def main():
    """Главная функция"""
    print("Starting data insertion...")
    clear_collections()
    users = insert_users()
    exercises = insert_exercises()
    insert_workouts(users, exercises)
    create_indexes()
    print("Data insertion completed!")

if __name__ == "__main__":
    main()
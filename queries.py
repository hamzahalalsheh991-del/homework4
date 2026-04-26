#!/usr/bin/env python3
"""
MongoDB запросы для CRUD операций
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
import re

class FitnessTrackerQueries:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client['fitness_tracker']
    
    # ==================== CREATE (Вставка) ====================
    
    def create_user(self, login, first_name, last_name, email, date_of_birth, weight=None, height=None):
        """Создание нового пользователя"""
        user = {
            "login": login,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "dateOfBirth": date_of_birth,
            "weight": weight,
            "height": height,
            "createdAt": datetime.now()
        }
        return self.db.users.insert_one(user)
    
    def create_exercise(self, name, category, muscle_group, difficulty, calories_per_minute):
        """Создание упражнения"""
        exercise = {
            "name": name,
            "category": category,
            "muscleGroup": muscle_group,
            "difficulty": difficulty,
            "caloriesPerMinute": calories_per_minute
        }
        return self.db.exercises.insert_one(exercise)
    
    def create_workout(self, user_id, workout_date, duration, exercises, notes="", rating=None):
        """Создание тренировки"""
        workout = {
            "userId": ObjectId(user_id),
            "workoutDate": workout_date,
            "duration": duration,
            "notes": notes,
            "exercises": exercises,
            "caloriesBurned": None,
            "rating": rating,
            "createdAt": datetime.now()
        }
        
        # Примерный расчет калорий (упрощенно)
        total_calories = 0
        for ex in exercises:
            exercise_data = self.db.exercises.find_one({"_id": ObjectId(ex["exerciseId"])})
            if exercise_data:
                total_calories += exercise_data["caloriesPerMinute"] * (duration / len(exercises))
        workout["caloriesBurned"] = int(total_calories)
        
        return self.db.workouts.insert_one(workout)
    
    def add_exercise_to_workout(self, workout_id, exercise_id, exercise_name, sets, rest_time):
        """Добавление упражнения в тренировку"""
        new_exercise = {
            "exerciseId": ObjectId(exercise_id),
            "exerciseName": exercise_name,
            "sets": sets,
            "restTime": rest_time
        }
        return self.db.workouts.update_one(
            {"_id": ObjectId(workout_id)},
            {"$push": {"exercises": new_exercise}}
        )
    
    # ==================== READ (Поиск) ====================
    
    def find_user_by_login(self, login):
        """Поиск пользователя по логину"""
        return self.db.users.find_one({"login": login})
    
    def find_users_by_name_mask(self, first_name_mask=None, last_name_mask=None):
        """Поиск пользователя по маске имени и фамилии"""
        query = {}
        if first_name_mask:
            query["firstName"] = {"$regex": first_name_mask, "$options": "i"}
        if last_name_mask:
            query["lastName"] = {"$regex": last_name_mask, "$options": "i"}
        return list(self.db.users.find(query))
    
    def get_all_exercises(self, category=None, difficulty=None, limit=100):
        """Получение списка упражнений с фильтрацией"""
        query = {}
        if category:
            query["category"] = category
        if difficulty:
            query["difficulty"] = difficulty
        return list(self.db.exercises.find(query).limit(limit))
    
    def get_user_workout_history(self, user_id, limit=50):
        """Получение истории тренировок пользователя"""
        return list(self.db.workouts.find(
            {"userId": ObjectId(user_id)}
        ).sort("workoutDate", -1).limit(limit))
    
    def get_workouts_by_date_range(self, user_id, start_date, end_date):
        """Получение тренировок за период"""
        return list(self.db.workouts.find({
            "userId": ObjectId(user_id),
            "workoutDate": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).sort("workoutDate", 1))
    
    # ==================== UPDATE (Обновление) ====================
    
    def update_user_weight(self, user_id, new_weight):
        """Обновление веса пользователя"""
        return self.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"weight": new_weight, "updatedAt": datetime.now()}}
        )
    
    def update_workout_rating(self, workout_id, rating):
        """Обновление рейтинга тренировки"""
        return self.db.workouts.update_one(
            {"_id": ObjectId(workout_id)},
            {"$set": {"rating": rating}}
        )
    
    def update_exercise_difficulty(self, exercise_id, new_difficulty):
        """Обновление сложности упражнения"""
        return self.db.exercises.update_one(
            {"_id": ObjectId(exercise_id)},
            {"$set": {"difficulty": new_difficulty}}
        )
    
    # ==================== DELETE (Удаление) ====================
    
    def delete_user(self, user_id):
        """Удаление пользователя (и всех его тренировок)"""
        # Удаляем тренировки пользователя
        self.db.workouts.delete_many({"userId": ObjectId(user_id)})
        # Удаляем пользователя
        return self.db.users.delete_one({"_id": ObjectId(user_id)})
    
    def delete_exercise(self, exercise_id):
        """Удаление упражнения"""
        return self.db.exercises.delete_one({"_id": ObjectId(exercise_id)})
    
    def delete_workout(self, workout_id):
        """Удаление тренировки"""
        return self.db.workouts.delete_one({"_id": ObjectId(workout_id)})
    
    # ==================== Дополнительные операторы ====================
    
    def get_users_with_weight_range(self, min_weight, max_weight):
        """Поиск пользователей с весом в диапазоне (использует $gte, $lte)"""
        return list(self.db.users.find({
            "weight": {"$gte": min_weight, "$lte": max_weight}
        }))
    
    def get_workouts_by_duration(self, min_duration, max_duration):
        """Поиск тренировок по длительности (использует $gt, $lt)"""
        return list(self.db.workouts.find({
            "duration": {"$gt": min_duration, "$lt": max_duration}
        }))
    
    def get_exercises_by_categories(self, categories):
        """Поиск упражнений по списку категорий (использует $in)"""
        return list(self.db.exercises.find({
            "category": {"$in": categories}
        }))
    
    def get_users_not_in_list(self, logins_to_exclude):
        """Поиск пользователей не из списка (использует $nin)"""
        return list(self.db.users.find({
            "login": {"$nin": logins_to_exclude}
        }))
    
    def get_advanced_exercises_not_beginner(self):
        """Поиск упражнений advanced ИЛИ intermediate (использует $or)"""
        return list(self.db.exercises.find({
            "$or": [
                {"difficulty": "advanced"},
                {"difficulty": "intermediate"}
            ]
        }))
    
    def get_exercises_with_calories_and_category(self, min_calories, categories):
        """Поиск упражнений с калориями > значения И категорией из списка (использует $and)"""
        return list(self.db.exercises.find({
            "$and": [
                {"caloriesPerMinute": {"$gt": min_calories}},
                {"category": {"$in": categories}}
            ]
        }))
    
    def add_set_to_exercise_in_workout(self, workout_id, exercise_index, new_set):
        """Добавление подхода в упражнение (использует $push)"""
        return self.db.workouts.update_one(
            {"_id": ObjectId(workout_id)},
            {"$push": {f"exercises.{exercise_index}.sets": new_set}}
        )
    
    def remove_set_from_exercise(self, workout_id, exercise_index, set_number):
        """Удаление подхода из упражнения (использует $pull)"""
        return self.db.workouts.update_one(
            {"_id": ObjectId(workout_id)},
            {"$pull": {f"exercises.{exercise_index}.sets": {"setNumber": set_number}}}
        )
    
    def add_muscle_group_to_exercise(self, exercise_id, muscle_group):
        """Добавление мышечной группы к упражнению без дубликатов (использует $addToSet)"""
        return self.db.exercises.update_one(
            {"_id": ObjectId(exercise_id)},
            {"$addToSet": {"muscleGroup": muscle_group}}
        )
    
    def increment_workout_count(self, user_id):
        """Инкремент счетчика тренировок (использует $inc)"""
        return self.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"workoutCount": 1}}
        )
    
    def unset_field(self, user_id, field_name):
        """Удаление поля (использует $unset)"""
        return self.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$unset": {field_name: ""}}
        )
    
    def rename_field(self, old_field, new_field):
        """Переименование поля (использует $rename)"""
        return self.db.users.update_many(
            {},
            {"$rename": {old_field: new_field}}
        )

def demo_queries():
    """Демонстрация всех запросов"""
    q = FitnessTrackerQueries()
    
    print("="*60)
    print("Демонстрация MongoDB запросов")
    print("="*60)
    
    # CREATE
    print("\n--- CREATE Operations ---")
    user_id = q.create_user("new_user", "New", "User", "new@example.com", datetime(1995, 5, 5), 70, 175)
    print(f"✓ Создан пользователь: {user_id.inserted_id}")
    
    # READ
    print("\n--- READ Operations ---")
    user = q.find_user_by_login("john_doe")
    print(f"✓ Найден пользователь по логину: {user['firstName']} {user['lastName']}")
    
    users_by_mask = q.find_users_by_name_mask(first_name_mask="Jo")
    print(f"✓ Найдено {len(users_by_mask)} пользователей с именем, начинающимся на 'Jo'")
    
    exercises = q.get_all_exercises(category="chest")
    print(f"✓ Найдено {len(exercises)} упражнений для груди")
    
    # UPDATE
    print("\n--- UPDATE Operations ---")
    result = q.update_user_weight(user_id.inserted_id, 72.5)
    print(f"✓ Обновлен вес: {result.modified_count} документ(ов)")
    
    result = q.add_muscle_group_to_exercise(exercises[0]["_id"], "core")
    print(f"✓ Добавлена мышечная группа: {result.modified_count} документ(ов)")
    
    # DELETE
    print("\n--- DELETE Operations ---")
    result = q.delete_user(user_id.inserted_id)
    print(f"✓ Удален пользователь: {result.deleted_count} документ(ов)")
    
    # Сложные запросы с операторами
    print("\n--- Advanced Query Operators ---")
    
    users_by_weight = q.get_users_with_weight_range(60, 80)
    print(f"✓ Пользователи с весом 60-80кг: {len(users_by_weight)}")
    
    exercises_by_cat = q.get_exercises_by_categories(["chest", "back"])
    print(f"✓ Упражнения для груди или спины: {len(exercises_by_cat)}")
    
    advanced_exercises = q.get_advanced_exercises_not_beginner()
    print(f"✓ Упражнения уровня advanced или intermediate: {len(advanced_exercises)}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    demo_queries()
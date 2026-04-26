#!/usr/bin/env python3
"""
Сложные агрегационные запросы
"""

from pymongo import MongoClient
from datetime import datetime, timedelta

class FitnessAggregations:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client['fitness_tracker']
    
    def get_workout_statistics_for_period(self, user_login, start_date, end_date):
        """
        Получение статистики тренировок за период
        Использует stages: $match, $group, $project, $sort
        """
        # Сначала находим пользователя
        user = self.db.users.find_one({"login": user_login})
        if not user:
            return None
        
        pipeline = [
            # Фильтрация тренировок по пользователю и дате
            {
                "$match": {
                    "userId": user["_id"],
                    "workoutDate": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            # Группировка и вычисление статистики
            {
                "$group": {
                    "_id": None,
                    "totalWorkouts": {"$sum": 1},
                    "totalDuration": {"$sum": "$duration"},
                    "totalCalories": {"$sum": "$caloriesBurned"},
                    "avgDuration": {"$avg": "$duration"},
                    "avgCalories": {"$avg": "$caloriesBurned"},
                    "avgRating": {"$avg": "$rating"},
                    "workoutsList": {"$push": "$$ROOT"}
                }
            },
            # Проекция с форматированием
            {
                "$project": {
                    "_id": 0,
                    "totalWorkouts": 1,
                    "totalDuration": 1,
                    "totalCalories": 1,
                    "avgDuration": {"$round": ["$avgDuration", 0]},
                    "avgCalories": {"$round": ["$avgCalories", 0]},
                    "avgRating": {"$round": ["$avgRating", 1]},
                    "workoutsList": {"$slice": ["$workoutsList", 10]}
                }
            }
        ]
        
        result = list(self.db.workouts.aggregate(pipeline))
        return result[0] if result else None
    
    def get_exercise_popularity(self):
        """
        Получение популярности упражнений
        Использует stages: $unwind, $group, $sort
        """
        pipeline = [
            # Разворачиваем массив упражнений
            {"$unwind": "$exercises"},
            # Группируем по упражнениям
            {
                "$group": {
                    "_id": {
                        "exerciseId": "$exercises.exerciseId",
                        "exerciseName": "$exercises.exerciseName"
                    },
                    "count": {"$sum": 1},
                    "totalSets": {"$sum": {"$size": "$exercises.sets"}},
                    "totalReps": {"$sum": {
                        "$sum": "$exercises.sets.reps"
                    }}
                }
            },
            # Сортируем по популярности
            {"$sort": {"count": -1}},
            # Ограничиваем результат
            {"$limit": 10},
            # Проекция
            {
                "$project": {
                    "_id": 0,
                    "exerciseName": "$_id.exerciseName",
                    "workoutCount": "$count",
                    "totalSets": 1,
                    "totalReps": 1
                }
            }
        ]
        
        return list(self.db.workouts.aggregate(pipeline))
    
    def get_user_progress(self, user_login):
        """
        Получение прогресса пользователя по неделям
        Использует stages: $match, $addFields, $group, $sort
        """
        user = self.db.users.find_one({"login": user_login})
        if not user:
            return None
        
        pipeline = [
            {"$match": {"userId": user["_id"]}},
            # Добавляем поле с номером недели
            {
                "$addFields": {
                    "week": {
                        "$week": "$workoutDate"
                    },
                    "year": {
                        "$year": "$workoutDate"
                    }
                }
            },
            # Группировка по неделям
            {
                "$group": {
                    "_id": {
                        "year": "$year",
                        "week": "$week"
                    },
                    "workouts": {"$sum": 1},
                    "totalDuration": {"$sum": "$duration"},
                    "totalCalories": {"$sum": "$caloriesBurned"},
                    "avgRating": {"$avg": "$rating"}
                }
            },
            {"$sort": {"_id.year": 1, "_id.week": 1}}
        ]
        
        return list(self.db.workouts.aggregate(pipeline))
    
    def get_user_detailed_stats(self, user_login):
        """
        Детальная статистика с детализацией по упражнениям
        Использует: $match, $unwind, $group, $sort, $project
        """
        user = self.db.users.find_one({"login": user_login})
        if not user:
            return None
        
        pipeline = [
            {"$match": {"userId": user["_id"]}},
            {"$unwind": "$exercises"},
            {"$unwind": "$exercises.sets"},
            {
                "$group": {
                    "_id": {
                        "exerciseId": "$exercises.exerciseId",
                        "exerciseName": "$exercises.exerciseName"
                    },
                    "totalWorkouts": {"$sum": 1},
                    "totalSets": {"$sum": 1},
                    "totalReps": {"$sum": "$exercises.sets.reps"},
                    "maxWeight": {"$max": "$exercises.sets.weight"},
                    "avgWeight": {"$avg": "$exercises.sets.weight"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "exerciseName": "$_id.exerciseName",
                    "totalWorkouts": 1,
                    "totalSets": 1,
                    "totalReps": 1,
                    "maxWeight": {"$ifNull": ["$maxWeight", 0]},
                    "avgWeight": {"$round": [{"$ifNull": ["$avgWeight", 0]}, 1]}
                }
            },
            {"$sort": {"totalSets": -1}}
        ]
        
        return list(self.db.workouts.aggregate(pipeline))
    
    def get_weekly_trends(self):
        """
        Тренды тренировок по неделям для всех пользователей
        Использует: $group, $project, $sort
        """
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "week": {"$week": "$workoutDate"},
                        "year": {"$year": "$workoutDate"}
                    },
                    "totalWorkouts": {"$sum": 1},
                    "avgDuration": {"$avg": "$duration"},
                    "avgCalories": {"$avg": "$caloriesBurned"},
                    "uniqueUsers": {"$addToSet": "$userId"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "year": "$_id.year",
                    "week": "$_id.week",
                    "totalWorkouts": 1,
                    "avgDuration": {"$round": ["$avgDuration", 0]},
                    "avgCalories": {"$round": ["$avgCalories", 0]},
                    "activeUsers": {"$size": "$uniqueUsers"}
                }
            },
            {"$sort": {"year": -1, "week": -1}},
            {"$limit": 10}
        ]
        
        return list(self.db.workouts.aggregate(pipeline))

def demo_aggregations():
    """Демонстрация агрегаций"""
    agg = FitnessAggregations()
    
    print("="*60)
    print("Демонстрация агрегационных запросов")
    print("="*60)
    
    # Статистика за период
    print("\n--- Статистика тренировок за период ---")
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 31)
    stats = agg.get_workout_statistics_for_period("john_doe", start, end)
    if stats:
        print(f"Всего тренировок: {stats['totalWorkouts']}")
        print(f"Общая длительность: {stats['totalDuration']} мин")
        print(f"Общее кол-во калорий: {stats['totalCalories']}")
        print(f"Средняя длительность: {stats['avgDuration']} мин")
        print(f"Средний рейтинг: {stats['avgRating']}")
    
    # Популярность упражнений
    print("\n--- Популярность упражнений ---")
    popular = agg.get_exercise_popularity()
    for i, ex in enumerate(popular[:5], 1):
        print(f"{i}. {ex['exerciseName']} - {ex['workoutCount']} тренировок, {ex['totalSets']} подходов")
    
    # Прогресс пользователя
    print("\n--- Прогресс пользователя (по неделям) ---")
    progress = agg.get_user_progress("john_doe")
    if progress:
        for week in progress[:5]:
            print(f"Неделя {week['_id']['week']}: {week['workouts']} тренировок, {week['totalDuration']} мин")
    
    # Детальная статистика
    print("\n--- Детальная статистика по упражнениям ---")
    detailed = agg.get_user_detailed_stats("john_doe")
    if detailed:
        for ex in detailed[:5]:
            print(f"{ex['exerciseName']}: {ex['totalSets']} подходов, макс вес {ex['maxWeight']}кг")
    
    # Тренды
    print("\n--- Недельные тренды ---")
    trends = agg.get_weekly_trends()
    for trend in trends[:5]:
        print(f"{trend['year']}-W{trend['week']}: {trend['totalWorkouts']} тренировок, {trend['activeUsers']} активных пользователей")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    demo_aggregations()
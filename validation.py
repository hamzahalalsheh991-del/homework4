#!/usr/bin/env python3
"""
Скрипт для создания валидации схемы коллекции users
"""

from pymongo import MongoClient, errors
from datetime import datetime

def create_user_validation():
    """Создание валидации для коллекции users"""
    client = MongoClient('mongodb://localhost:27017')
    db = client['fitness_tracker']
    
    # Команда для создания/обновления коллекции с валидацией
    validation_command = {
        "collMod": "users",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["login", "firstName", "lastName", "email", "dateOfBirth"],
                "properties": {
                    "login": {
                        "bsonType": "string",
                        "description": "Логин - обязательное строковое поле",
                        "pattern": "^[a-zA-Z0-9_]{3,30}$"
                    },
                    "firstName": {
                        "bsonType": "string",
                        "description": "Имя - обязательное строковое поле",
                        "minLength": 1,
                        "maxLength": 50
                    },
                    "lastName": {
                        "bsonType": "string",
                        "description": "Фамилия - обязательное строковое поле",
                        "minLength": 1,
                        "maxLength": 50
                    },
                    "email": {
                        "bsonType": "string",
                        "description": "Email - обязательное поле с корректным форматом",
                        "pattern": "^[^@\\s]+@([^@\\s]+\\.)+[^@\\s]+$"
                    },
                    "dateOfBirth": {
                        "bsonType": "date",
                        "description": "Дата рождения - обязательное поле типа date"
                    },
                    "weight": {
                        "bsonType": "double",
                        "description": "Вес в кг",
                        "minimum": 20,
                        "maximum": 300
                    },
                    "height": {
                        "bsonType": "double",
                        "description": "Рост в см",
                        "minimum": 100,
                        "maximum": 250
                    },
                    "createdAt": {
                        "bsonType": "date",
                        "description": "Дата создания"
                    }
                },
                "additionalProperties": True
            }
        },
        "validationLevel": "strict",
        "validationAction": "error"
    }
    
    try:
        # Проверяем, существует ли коллекция
        if "users" in db.list_collection_names():
            # Обновляем валидацию существующей коллекции
            db.command(validation_command)
            print("Validation updated for existing 'users' collection")
        else:
            # Создаем новую коллекцию с валидацией
            db.create_collection("users", validator=validation_command["validator"])
            print("Created new 'users' collection with validation")
        
        print("JSON Schema validation successfully applied to 'users' collection")
        
    except errors.PyMongoError as e:
        print(f"Error creating validation: {e}")

def test_validation():
    """Тестирование валидации - попытка вставить невалидные данные"""
    client = MongoClient('mongodb://localhost:27017')
    db = client['fitness_tracker']
    
    print("\n" + "="*60)
    print("Тестирование валидации схемы")
    print("="*60)
    
    # Тест 1: Валидный пользователь
    print("\n1. Вставка валидного пользователя:")
    valid_user = {
        "login": "valid_user",
        "firstName": "Test",
        "lastName": "User",
        "email": "test@example.com",
        "dateOfBirth": datetime(1990, 1, 1),
        "weight": 75.5,
        "height": 180
    }
    try:
        result = db.users.insert_one(valid_user)
        print(f"   ✓ Успешно: {result.inserted_id}")
    except errors.WriteError as e:
        print(f"   ✗ Ошибка: {e.details}")
    
    # Тест 2: Отсутствует обязательное поле (firstName)
    print("\n2. Вставка без обязательного поля firstName:")
    no_firstname = {
        "login": "no_firstname",
        "lastName": "User",
        "email": "test@example.com",
        "dateOfBirth": datetime(1990, 1, 1)
    }
    try:
        result = db.users.insert_one(no_firstname)
        print(f"   ✓ Успешно: {result.inserted_id} (ОШИБКА: должно было быть отклонено)")
    except errors.WriteError as e:
        print(f"   ✗ Отклонено (корректно): {str(e.details)[:100]}...")
    
    # Тест 3: Невалидный email
    print("\n3. Вставка с невалидным email:")
    invalid_email = {
        "login": "invalid_email",
        "firstName": "Test",
        "lastName": "User",
        "email": "not-an-email",
        "dateOfBirth": datetime(1990, 1, 1)
    }
    try:
        result = db.users.insert_one(invalid_email)
        print(f"   ✓ Успешно: {result.inserted_id} (ОШИБКА: должно было быть отклонено)")
    except errors.WriteError as e:
        print(f"   ✗ Отклонено (корректно): {str(e.details)[:100]}...")
    
    # Тест 4: Невалидный вес (слишком маленький)
    print("\n4. Вставка с весом 15 кг (ниже минимума):")
    invalid_weight = {
        "login": "invalid_weight",
        "firstName": "Test",
        "lastName": "User",
        "email": "test@example.com",
        "dateOfBirth": datetime(1990, 1, 1),
        "weight": 15.0
    }
    try:
        result = db.users.insert_one(invalid_weight)
        print(f"   ✓ Успешно: {result.inserted_id} (ОШИБКА: должно было быть отклонено)")
    except errors.WriteError as e:
        print(f"   ✗ Отклонено (корректно): {str(e.details)[:100]}...")
    
    # Тест 5: Невалидный логин (спецсимволы)
    print("\n5. Вставка с логином 'bad@login' (не соответствует pattern):")
    invalid_login = {
        "login": "bad@login",
        "firstName": "Test",
        "lastName": "User",
        "email": "test@example.com",
        "dateOfBirth": datetime(1990, 1, 1)
    }
    try:
        result = db.users.insert_one(invalid_login)
        print(f"   ✓ Успешно: {result.inserted_id} (ОШИБКА: должно было быть отклонено)")
    except errors.WriteError as e:
        print(f"   ✗ Отклонено (корректно): {str(e.details)[:100]}...")
    
    print("\n" + "="*60)
    print("Тестирование завершено")
    print("="*60)

if __name__ == "__main__":
    create_user_validation()
    test_validation()
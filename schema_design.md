# Проектирование документной модели для Фитнес-трекера

## Обзор сущностей

Система содержит 3 основные сущности:
- **Пользователь (User)** - информация о пользователе
- **Упражнение (Exercise)** - справочник упражнений
- **Тренировка (Workout)** - запись о выполненной тренировке

## Выбор между Embedded и References

### Пользователь (User) - отдельная коллекция
```json
{
  "_id": ObjectId,
  "login": "john_doe",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "dateOfBirth": ISODate("1990-01-15"),
  "weight": 75.5,
  "height": 180,
  "createdAt": ISODate()
}
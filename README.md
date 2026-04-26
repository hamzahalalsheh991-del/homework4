# Fitness Tracker - MongoDB Project

## Описание проекта

Фитнес-трекер для отслеживания тренировок, упражнений и прогресса пользователей. Реализован на Python + FastAPI + MongoDB.

## Функциональность

-  CRUD операции с пользователями, упражнениями, тренировками
-  Поиск по логину и маске имени/фамилии
-  Фильтрация упражнений по категории и сложности
- История тренировок пользователя
-  Статистика за период
-  Агрегационные запросы для аналитики
-  Валидация схемы MongoDB

## Технологии

- Python 3.11
- FastAPI
- MongoDB 6.0
- PyMongo
- Docker & Docker Compose

## Установка и запуск

### 1. Запуск с Docker Compose

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/fitness-tracker-mongodb.git
cd fitness-tracker-mongodb

# Запуск контейнеров
docker-compose up -d

# Просмотр логов
docker-compose logs -f
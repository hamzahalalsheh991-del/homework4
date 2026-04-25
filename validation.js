// validation.js
const { MongoClient } = require('mongodb');

const uri = 'mongodb://localhost:27017';
const dbName = 'fitness_tracker';

async function createValidatedCollection() {
  const client = new MongoClient(uri);
  try {
    await client.connect();
    const db = client.db(dbName);

    // Удаляем старую коллекцию, если существует (чтобы применить новую валидацию)
    await db.collection('users').drop().catch(() => {});

    // Создаём коллекцию с валидацией JSON Schema
    await db.createCollection('users', {
      validator: {
        $jsonSchema: {
          bsonType: 'object',
          required: ['login', 'firstName', 'lastName', 'email', 'age'],
          properties: {
            login: {
              bsonType: 'string',
              description: 'Логин – обязательная уникальная строка',
              pattern: '^[a-zA-Z0-9_]{3,20}$'
            },
            firstName: {
              bsonType: 'string',
              description: 'Имя обязательно',
              minLength: 1,
              maxLength: 50
            },
            lastName: {
              bsonType: 'string',
              description: 'Фамилия обязательна'
            },
            email: {
              bsonType: 'string',
              pattern: '^\\S+@\\S+\\.\\S+$',
              description: 'Должен быть корректный email'
            },
            age: {
              bsonType: 'int',
              minimum: 18,
              maximum: 100,
              description: 'Возраст от 18 до 100 лет'
            },
            createdAt: { bsonType: 'date' },
            updatedAt: { bsonType: 'date' }
          },
          additionalProperties: false
        }
      },
      validationLevel: 'strict',
      validationAction: 'error'
    });

    console.log('Коллекция users создана с валидацией JSON Schema');

    // Тест: вставка валидного документа
    const validUser = {
      login: 'valid_user',
      firstName: 'Иван',
      lastName: 'Петров',
      email: 'ivan@example.com',
      age: 25,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    await db.collection('users').insertOne(validUser);
    console.log('Валидный пользователь добавлен');

    // Тест: попытка вставить невалидный документ (возраст 17)
    const invalidUser = {
      login: 'invalid',
      firstName: 'Анна',
      lastName: 'Сидорова',
      email: 'anna@example.com',
      age: 17, // не проходит min
      createdAt: new Date(),
      updatedAt: new Date()
    };
    try {
      await db.collection('users').insertOne(invalidUser);
      console.log('Ошибка: невалидный документ был вставлен (этого не должно быть)');
    } catch (err) {
      console.log('Валидация сработала корректно, ошибка:', err.message);
    }

    // Дополнительный тест: отсутствие обязательного поля firstName
    const missingField = {
      login: 'missing_first',
      lastName: 'Тестов',
      email: 'test@test.com',
      age: 30
    };
    try {
      await db.collection('users').insertOne(missingField);
    } catch (err) {
      console.log('Отсутствие firstName поймано:', err.message);
    }

  } finally {
    await client.close();
  }
}

createValidatedCollection();
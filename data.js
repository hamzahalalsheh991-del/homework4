const { MongoClient } = require('mongodb');

const uri = 'mongodb://localhost:27017';
const dbName = 'fitness_tracker';

const client = new MongoClient(uri);

async function seed() {
  try {
    await client.connect();
    const db = client.db(dbName);

    // Очистка коллекций (опционально)
    await db.collection('users').deleteMany({});
    await db.collection('exercises').deleteMany({});
    await db.collection('workouts').deleteMany({});

    // ----- Пользователи (10 шт) -----
    const users = [];
    for (let i = 1; i <= 10; i++) {
      users.push({
        login: `user${i}`,
        firstName: `FirstName${i}`,
        lastName: `LastName${i}`,
        email: `user${i}@example.com`,
        age: 20 + i,
        createdAt: new Date(),
        updatedAt: new Date()
      });
    }
    const userResult = await db.collection('users').insertMany(users);
    const userIds = Object.values(userResult.insertedIds);

    // ----- Упражнения (10 шт) -----
    const exercises = [
      { name: 'Жим лёжа', description: 'Классический жим штанги', muscleGroup: 'грудь', difficulty: 'intermediate', createdBy: userIds[0], createdAt: new Date() },
      { name: 'Приседания', description: 'Со штангой на плечах', muscleGroup: 'ноги', difficulty: 'intermediate', createdBy: userIds[1], createdAt: new Date() },
      { name: 'Становая тяга', description: 'Классическая тяга', muscleGroup: 'спина', difficulty: 'advanced', createdBy: userIds[2], createdAt: new Date() },
      { name: 'Отжимания', description: 'От груди', muscleGroup: 'грудь', difficulty: 'beginner', createdBy: userIds[0], createdAt: new Date() },
      { name: 'Подтягивания', description: 'Широким хватом', muscleGroup: 'спина', difficulty: 'intermediate', createdBy: userIds[1], createdAt: new Date() },
      { name: 'Тяга гантели', description: 'В наклоне', muscleGroup: 'спина', difficulty: 'beginner', createdBy: userIds[2], createdAt: new Date() },
      { name: 'Жим гантелей', description: 'Сидя', muscleGroup: 'плечи', difficulty: 'intermediate', createdBy: userIds[3], createdAt: new Date() },
      { name: 'Скручивания', description: 'На пресс', muscleGroup: 'пресс', difficulty: 'beginner', createdBy: userIds[4], createdAt: new Date() },
      { name: 'Выпады', description: 'С гантелями', muscleGroup: 'ноги', difficulty: 'beginner', createdBy: userIds[5], createdAt: new Date() },
      { name: 'Французский жим', description: 'На трицепс', muscleGroup: 'руки', difficulty: 'intermediate', createdBy: userIds[6], createdAt: new Date() }
    ];
    const exerciseResult = await db.collection('exercises').insertMany(exercises);
    const exerciseIds = Object.values(exerciseResult.insertedIds);

    // ----- Тренировки (минимум 10, каждая принадлежит случайному пользователю) -----
    const workouts = [];
    for (let i = 0; i < 10; i++) {
      const userId = userIds[i % userIds.length];
      const date = new Date(2025, 2, 15 + i); // март 2025
      const exercisesInWorkout = [];
      // добавляем от 2 до 4 упражнений в тренировку
      const numEx = 2 + (i % 3);
      for (let j = 0; j < numEx; j++) {
        const exId = exerciseIds[(i + j) % exerciseIds.length];
        exercisesInWorkout.push({
          exerciseId: exId,
          sets: 3 + j,
          reps: 8 + j * 2,
          weight: 50 + j * 10,
          restTimeSec: 60
        });
      }
      workouts.push({
        userId: userId,
        date: date,
        duration: 45 + i,
        notes: `Тренировка ${i+1}`,
        exercises: exercisesInWorkout,
        createdAt: new Date(),
        updatedAt: new Date()
      });
    }
    await db.collection('workouts').insertMany(workouts);

    console.log('Тестовые данные успешно вставлены!');
    await client.close();
  } catch (err) {
    console.error('Ошибка:', err);
    await client.close();
  }
}

seed();
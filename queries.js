// queries.js (примеры запросов, можно запускать в среде Node.js)
const { MongoClient, ObjectId } = require('mongodb');

const uri = 'mongodb://localhost:27017';
const dbName = 'fitness_tracker';

async function runQueries() {
  const client = new MongoClient(uri);
  try {
    await client.connect();
    const db = client.db(dbName);

    // 1. Create – создание нового пользователя
    const newUser = {
      login: 'johndoe',
      firstName: 'John',
      lastName: 'Doe',
      email: 'john@example.com',
      age: 30,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    const insertResult = await db.collection('users').insertOne(newUser);
    console.log('Создан пользователь:', insertResult.insertedId);

    // 2. Read – поиск пользователя по логину
    const userByLogin = await db.collection('users').findOne({ login: 'johndoe' });
    console.log('Поиск по логину:', userByLogin);

    // 3. Read – поиск пользователя по маске имени и фамилии (регулярное выражение, частичное совпадение)
    const mask = 'Jo'; // ищем firstName или lastName, начинающиеся с "Jo"
    const usersByMask = await db.collection('users').find({
      $or: [
        { firstName: { $regex: `^${mask}`, $options: 'i' } },
        { lastName: { $regex: `^${mask}`, $options: 'i' } }
      ]
    }).toArray();
    console.log('По маске имени/фамилии:', usersByMask);

    // 4. Create – создание упражнения
    const newExercise = {
      name: 'Бёрпи',
      description: 'Интенсивное кардио',
      muscleGroup: 'всё тело',
      difficulty: 'advanced',
      createdBy: userByLogin._id,
      createdAt: new Date()
    };
    const exResult = await db.collection('exercises').insertOne(newExercise);
    console.log('Создано упражнение:', exResult.insertedId);

    // 5. Read – получение списка упражнений (с фильтрацией по группе мышц)
    const chestExercises = await db.collection('exercises').find({ muscleGroup: 'грудь' }).toArray();
    console.log('Упражнения на грудь:', chestExercises);

    // 6. Create – создание тренировки
    const workout = {
      userId: userByLogin._id,
      date: new Date(),
      duration: 60,
      notes: 'Вечерняя тренировка',
      exercises: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    const workoutResult = await db.collection('workouts').insertOne(workout);
    console.log('Создана тренировка:', workoutResult.insertedId);

    // 7. Update – добавление упражнения в тренировку (используем $push)
    const exerciseToAdd = {
      exerciseId: exResult.insertedId,
      sets: 4,
      reps: 15,
      weight: 0,
      restTimeSec: 30
    };
    await db.collection('workouts').updateOne(
      { _id: workoutResult.insertedId },
      { $push: { exercises: exerciseToAdd }, $set: { updatedAt: new Date() } }
    );
    console.log('Упражнение добавлено в тренировку');

    // 8. Read – получение истории тренировок пользователя (сортировка по дате)
    const history = await db.collection('workouts')
      .find({ userId: userByLogin._id })
      .sort({ date: -1 })
      .toArray();
    console.log('История тренировок:', history);

    // 9. Read – статистика тренировок за период (используем $and, $gte, $lte)
    const startDate = new Date(2025, 2, 1);
    const endDate = new Date(2025, 2, 31);
    const stats = await db.collection('workouts').aggregate([
      { $match: { userId: userByLogin._id, date: { $gte: startDate, $lte: endDate } } },
      { $group: { _id: null, totalDuration: { $sum: '$duration' }, count: { $sum: 1 } } },
      { $project: { _id: 0, totalDuration: 1, count: 1, avgDuration: { $divide: ['$totalDuration', '$count'] } } }
    ]).toArray();
    console.log('Статистика за период:', stats);

    // Дополнительные примеры с операторами:
    // $ne, $in, $pull, $addToSet

    // Поиск пользователей, возраст которых не равен 30
    const not30 = await db.collection('users').find({ age: { $ne: 30 } }).toArray();
    console.log('Пользователи не 30 лет:', not30.length);

    // Поиск тренировок с длительностью > 50 минут И с заметками не пустыми
    const longWorkouts = await db.collection('workouts').find({
      $and: [
        { duration: { $gt: 50 } },
        { notes: { $ne: null, $ne: '' } }
      ]
    }).toArray();
    console.log('Длинные тренировки:', longWorkouts.length);

    // Удаление упражнения из тренировки ($pull)
    await db.collection('workouts').updateOne(
      { _id: workoutResult.insertedId },
      { $pull: { exercises: { exerciseId: exResult.insertedId } } }
    );
    console.log('Упражнение удалено из тренировки');

    // 10. Delete – удаление тренировки (по _id)
    await db.collection('workouts').deleteOne({ _id: workoutResult.insertedId });
    console.log('Тренировка удалена');
  } finally {
    await client.close();
  }
}

runQueries().catch(console.error);
require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const User = require('./models/User');
const Exercise = require('./models/Exercise');
const Workout = require('./models/Workout');

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;
require('dotenv').config();

const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/fitness_tracker';

mongoose.connect(MONGO_URI)
  .then(() => console.log('MongoDB connected'))
  .catch(err => console.error(err));

// --- API endpoints ---
app.get('/users', async (req, res) => {
  try {
    const users = await User.find();
    res.json(users);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});
// 1. Создание нового пользователя
app.post('/users', async (req, res) => {
  try {
    const user = new User(req.body);
    await user.save();
    res.status(201).json(user);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// 2. Поиск пользователя по логину
app.get('/users/login/:login', async (req, res) => {
  try {
    const user = await User.findOne({ login: req.params.login });
    if (!user) return res.status(404).json({ error: 'User not found' });
    res.json(user);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 3. Поиск пользователя по маске имени и фамилии (query параметры ?firstName=...&lastName=...)
app.get('/users/search', async (req, res) => {
  try {
    const { firstName, lastName } = req.query;
    const filter = {};
    if (firstName) filter.firstName = { $regex: firstName, $options: 'i' };
    if (lastName) filter.lastName = { $regex: lastName, $options: 'i' };
    const users = await User.find(filter);
    res.json(users);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 4. Создание упражнения
app.post('/exercises', async (req, res) => {
  try {
    const exercise = new Exercise(req.body);
    await exercise.save();
    res.status(201).json(exercise);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// 5. Получение списка упражнений (с возможной фильтрацией по muscleGroup)
app.get('/exercises', async (req, res) => {
  try {
    const { muscleGroup } = req.query;
    const filter = muscleGroup ? { muscleGroup } : {};
    const exercises = await Exercise.find(filter);
    res.json(exercises);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 6. Создание тренировки
app.post('/workouts', async (req, res) => {
  try {
    const workout = new Workout(req.body);
    await workout.save();
    res.status(201).json(workout);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// 7. Добавление упражнения в тренировку (по ID тренировки)
app.post('/workouts/:workoutId/exercises', async (req, res) => {
  try {
    const { workoutId } = req.params;
    const { exerciseId, sets, reps, weight, restTimeSec } = req.body;
    const workout = await Workout.findById(workoutId);
    if (!workout) return res.status(404).json({ error: 'Workout not found' });
    workout.exercises.push({ exerciseId, sets, reps, weight, restTimeSec });
    workout.updatedAt = new Date();
    await workout.save();
    res.json(workout);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// 8. Получение истории тренировок пользователя (по userId)
app.get('/workouts/user/:userId/history', async (req, res) => {
  try {
    const { userId } = req.params;
    const workouts = await Workout.find({ userId }).sort({ date: -1 });
    res.json(workouts);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 9. Получение статистики тренировок за период (query: startDate, endDate, userId)
app.get('/workouts/statistics', async (req, res) => {
  try {
    const { userId, startDate, endDate } = req.query;
    const match = { userId };
    if (startDate || endDate) {
      match.date = {};
      if (startDate) match.date.$gte = new Date(startDate);
      if (endDate) match.date.$lte = new Date(endDate);
    }
    const stats = await Workout.aggregate([
      { $match: match },
      { $group: { _id: null, totalDuration: { $sum: '$duration' }, count: { $sum: 1 } } },
      { $project: { _id: 0, totalDuration: 1, count: 1, avgDuration: { $divide: ['$totalDuration', '$count'] } } }
    ]);
    res.json(stats[0] || { totalDuration: 0, count: 0, avgDuration: 0 });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => console.log(`API running on port ${PORT}`));
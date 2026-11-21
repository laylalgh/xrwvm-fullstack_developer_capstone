const express = require('express');
const mongoose = require('mongoose');
const { dealerships } = require('./data/dealerships.json');
const { reviews } = require('./data/reviews.json');
const Review = require('./review');
const Dealership = require('./dealership');

const app = express();
app.use(express.json({ limit: '64kb' }));

const useFixtures = process.env.DEALERSHIP_DEMO === '1';

const handle = action => (req, res, next) => action(req, res).catch(next);

function read(model, fixtures, filterBy = () => ({})) {
  return handle(async (req, res) => {
    const filter = filterBy(req.params);
    const rows = useFixtures
      ? fixtures.filter(row => Object.entries(filter).every(([key, value]) => row[key] === value))
      : await model.find(filter).lean();
    res.json(rows);
  });
}

app.get('/fetchReviews', read(Review, reviews));
app.get('/fetchReviews/dealer/:id', read(Review, reviews, ({ id }) => ({ dealership: Number(id) })));
app.get('/fetchDealers', read(Dealership, dealerships));
app.get('/fetchDealers/:state', read(Dealership, dealerships, ({ state }) => ({ state })));
app.get('/fetchDealer/:id', read(Dealership, dealerships, ({ id }) => ({ id: Number(id) })));
app.post('/insert_review', handle(async (req, res) => {
  const review = new Review(req.body);
  if (useFixtures) {
    review.id = Math.max(0, ...reviews.map(row => row.id)) + 1;
    await review.validate();
    const data = review.toObject();
    reviews.push(data);
    return res.status(201).json(data);
  }
  const counters = mongoose.connection.collection('counters');
  const counter = await counters.findOneAndUpdate(
    { _id: 'review' }, { $inc: { sequence: 1 } }, { returnDocument: 'after' }
  );
  review.id = (counter.value || counter).sequence;
  res.status(201).json(await review.save());
}));
app.use((err, req, res, next) => {
  res.status(err.name === 'ValidationError' ? 400 : 500).json({ error: 'Request could not be completed' });
});

async function start() {
  if (!useFixtures) {
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://mongo_db:27017/dealershipsDB');
    for (const [model, fixtures] of [[Review, reviews], [Dealership, dealerships]]) {
      if (!(await model.exists({}))) await model.insertMany(fixtures);
    }
    const latest = await Review.findOne().sort({ id: -1 }).lean();
    await mongoose.connection.collection('counters').updateOne(
      { _id: 'review' }, { $max: { sequence: latest ? latest.id : 0 } }, { upsert: true }
    );
  }
  app.listen(3030, () => console.log('Dealership API listening on http://localhost:3030'));
}

start().catch(error => {
  console.error(error);
  process.exitCode = 1;
});

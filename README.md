# Cars Dealership

Cars Dealership is a full-stack directory of U.S. dealership branches. Visitors can browse dealers, filter by state and read reviews. Registered customers can submit reviews, and the Flask service analyzes review sentiment.

Django serves the React application and manages user accounts and the SQLite car catalog. Express serves dealer and review data from MongoDB.

## Run locally

From `server`:

1. Install the Python dependencies with `pip install -r requirements.txt`.
2. Run `npm ci --prefix frontend` and `npm run build --prefix frontend`.
3. Start MongoDB and run `npm install --prefix database` followed by `node database/app.js`. Set `MONGODB_URI` if MongoDB is hosted elsewhere.
4. Install `djangoapp/microservices/requirements.txt`, extract the included VADER lexicon ZIP into an NLTK data directory under `sentiment/`, then run `python -m flask --app djangoapp/microservices/app run --port 5050`.
5. Run `python manage.py migrate`, then `python manage.py shell -c "from djangoapp.populate import initiate; initiate()"` and `python manage.py runserver`.

Set `backend_url` and `sentiment_analyzer_url` to your service URLs when running them remotely.

For an isolated local container stack, run `docker compose up --build` and open http://localhost:8000.
The Express service also supports `DEALERSHIP_DEMO=1` for local verification with the course's JSON fixtures. Reviews created in that mode last until the service restarts.

# Network Route Optimizer

A Django REST Framework service that models a network as a directed graph of
nodes (servers) and edges (links with latency). It finds the lowest-latency
route between two nodes and keeps a history of route queries.

## Setup

Requires Python 3.12+.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # then set DJANGO_SECRET_KEY
python manage.py migrate
python manage.py runserver
```

Run the tests, linter and formatter:

```bash
python manage.py test
ruff check .
black --check .
```

## Configuration

All settings come from environment variables, which can also be placed in a
`.env` file (see `.env.example`).

| Variable               | Required | Default                    |
|------------------------|----------|----------------------------|
| `DJANGO_SECRET_KEY`    | yes      | none                       |
| `DJANGO_DEBUG`         | no       | `False`                    |
| `DJANGO_ALLOWED_HOSTS` | no       | `localhost,127.0.0.1`      |
| `DB_ENGINE`            | no       | `django.db.backends.sqlite3` |
| `DB_NAME`              | no       | `db.sqlite3` in the project directory |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | no | empty |

## API

| Method   | Path               | Description                          | Success |
|----------|--------------------|--------------------------------------|---------|
| `POST`   | `/nodes`           | Create a node `{"name"}`             | 201     |
| `GET`    | `/nodes`           | List nodes                           | 200     |
| `DELETE` | `/nodes/{id}`      | Delete a node and its edges          | 204     |
| `POST`   | `/edges`           | Create an edge `{"source", "destination", "latency"}` | 201 |
| `GET`    | `/edges`           | List edges                           | 200     |
| `DELETE` | `/edges/{id}`      | Delete an edge                       | 204     |
| `POST`   | `/routes/shortest` | Find the shortest route `{"source", "destination"}` | 200 / 404 |
| `GET`    | `/routes/history`  | List past route queries              | 200     |

`/routes/history` accepts these optional query parameters: `source`,
`destination`, `limit`, and `date_from` / `date_to` (ISO 8601 datetimes,
inclusive).

### Example

```bash
curl -X POST localhost:8000/nodes -H "Content-Type: application/json" -d '{"name": "ServerA"}'
curl -X POST localhost:8000/nodes -H "Content-Type: application/json" -d '{"name": "ServerB"}'
curl -X POST localhost:8000/nodes -H "Content-Type: application/json" -d '{"name": "ServerD"}'
curl -X POST localhost:8000/edges -H "Content-Type: application/json" \
     -d '{"source": "ServerA", "destination": "ServerB", "latency": 12.5}'
curl -X POST localhost:8000/edges -H "Content-Type: application/json" \
     -d '{"source": "ServerB", "destination": "ServerD", "latency": 10.9}'

curl -X POST localhost:8000/routes/shortest -H "Content-Type: application/json" \
     -d '{"source": "ServerA", "destination": "ServerD"}'
# {"total_latency": 23.4, "path": ["ServerA", "ServerB", "ServerD"]}
```

### Errors

Every error has the shape `{"error": ...}`. For validation errors (400) the
value is the per-field messages:

```json
{"error": {"latency": ["Latency must be greater than 0."]}}
```

## Project layout

- `routing/services/route_finder.py` contains the shortest-path algorithm
  (Dijkstra with a binary heap). It is plain Python with no Django or HTTP
  code, so it can be unit-tested without a database.
- `routing/views.py` stays thin. Each view validates input with a serializer,
  calls the service, and returns the response.
- `routing/exceptions.py` has the DRF exception handler that wraps every error
  in the `{"error": ...}` shape.

## Assumptions

- **Edges are directed.** `A → B` does not imply `B → A`. To model a
  bidirectional link, add both edges. `A → B` and `B → A` are separate edges,
  so adding one does not make the other a duplicate.
- **A route from a node to itself** returns `{"total_latency": 0, "path": ["A"]}`.
- **Only successful lookups are recorded in history.** A 404 (no path) or a 400
  (invalid input) is not recorded.
- **History is a snapshot.** It stores node names and the path as values, not
  foreign keys, so deleting nodes or edges later does not change or remove
  past records.
- **History is ordered newest first**, so `limit=N` returns the N most recent
  queries.
- **Deleting a node deletes its edges** (cascade).
- **Node names are case-sensitive.**
- **There is at most one edge per direction.** Adding a second `A → B` edge
  returns 400; delete the existing edge to change its latency.
- **Latency must be greater than 0.** Dijkstra's algorithm needs non-negative
  weights, and a zero-latency link is treated as a data error.

## Trade-offs

- **Decimal instead of float for latency.** Latency is stored as
  `DECIMAL(12, 3)`, so sums are exact: `12.5 + 10.9` is `23.4`, not
  `23.400000000000002`. The cost is that latency has at most 3 decimal places.
  The API still sends and receives latency as a JSON number.
- **The graph is loaded for each request.** `/routes/shortest` reads all edges
  in one query (`values_list`, so no model objects are built) and runs
  Dijkstra in memory in O((V + E) log V). This is simple, always up to date,
  and fast enough for thousands of edges. For much larger graphs, the next
  steps would be to cache the adjacency list and invalidate it when edges
  change, or to use a graph database.
- **No authentication or pagination**, because the brief does not ask for
  them.

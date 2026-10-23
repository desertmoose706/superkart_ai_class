# SuperKart Sales Prediction

A two-container app that predicts product sales for SuperKart stores.

| Component | Folder | Port | Description |
|-----------|--------|------|-------------|
| Backend (Flask) | [flask/](flask/) | 7860 | REST API that loads `superkart_model.joblib` (scikit-learn pipeline + XGBoost regressor) and serves predictions |
| Frontend (Streamlit) | [streamlit/](streamlit/) | 8501 | Web form that sends inputs to the backend and shows the predicted sales |

## Project layout

```
flask/
  app.py                  # Flask API
  superkart_model.joblib  # trained model
  requirements.txt
  Dockerfile
streamlit/
  frontend.py             # Streamlit UI
  requirements.txt
  Dockerfile
```

## Authentication

The API is protected by a shared API key sent in an `X-API-Key` header. The key is never stored in the code or the repo. Both containers read it from an `API_KEY` environment variable, and the backend refuses to start without it. Requests with a missing or wrong key get `401 Unauthorized`.

**In a GitHub Codespace:** add the key as a Codespaces secret so it is injected into your terminal as an environment variable.

1. GitHub → **Settings → Codespaces → Secrets → New secret** (user-level), or the repo's **Settings → Secrets and variables → Codespaces**.
2. Name it `API_KEY`, set a long random value (for example the output of `openssl rand -hex 32`), and grant it access to this repository.
3. Create (or rebuild) the Codespace. Check with `echo ${API_KEY:+set}`, which should print `set`.

**On a local machine:** export it in your shell first, for example `export API_KEY=$(openssl rand -hex 32)`.

## Run with Docker (local machine or GitHub Codespace)

The frontend reaches the backend by container name, so both containers must share a Docker network and the backend container must be named `backend`. `-e API_KEY` (no value) passes your shell's `API_KEY` into the container.

```bash
# 1. Create a shared network
docker network create superkart-net

# 2. Build and start the backend
cd flask
docker build -t superkart-backend .
docker run -d --name backend --network superkart-net -e API_KEY -p 7860:7860 superkart-backend

# 3. Build and start the frontend
cd ../streamlit
docker build -t superkart-frontend .
docker run -d --name frontend --network superkart-net -e API_KEY -p 8501:8501 superkart-frontend
```

- API: http://localhost:7860
- UI: http://localhost:8501

To stop and clean up:

```bash
docker rm -f frontend backend
docker network rm superkart-net
```

### In a GitHub Codespace

1. On the repo page, choose **Code → Codespaces → Create codespace on main**.
2. Run the commands above in the Codespace terminal.
3. Open the **Ports** tab. To call the API from outside the Codespace (for example from a Colab notebook), right-click port **7860 → Port Visibility → Public**. Do the same for **8501** to open the UI from a browser outside your GitHub session.
4. Copy the forwarded address for port 7860 (`https://<codespace-name>-7860.app.github.dev`). Use it without a trailing slash as the API root, for example `model_root_url` in a notebook.
5. In Colab, store the key in **Secrets** (the key icon in the sidebar) and read it with `from google.colab import userdata; api_key = userdata.get("API_KEY")`, then send `headers={"X-API-Key": api_key}` with each request. Never paste the key into a notebook cell.

The Streamlit UI has no login of its own. Anyone with the port 8501 URL can use the form (the key is added server-side), so keep 8501 Private unless you want to share the UI.

## API

Base URL: `http://localhost:7860`. Every request must include the `X-API-Key` header (see [Authentication](#authentication)).

### `POST /v1/predict`

Predicts sales for a single record. Send JSON with **all** of the fields below.

| Field | Type |
|-------|------|
| `Product_Weight` | number |
| `Product_Sugar_Content` | string (`Low Sugar`, `No Sugar`, `Regular`) |
| `Product_Allocated_Area` | number |
| `Product_Type` | string (`Baking Goods`, `Breads`, `Breakfast`, `Canned`, `Dairy`, `Frozen Foods`, `Fruits and Vegetables`, `Hard Drinks`, `Health and Hygiene`, `Household`, `Meat`, `Others`, `Seafood`, `Snack Foods`, `Soft Drinks`, `Starchy Foods`) |
| `Product_MRP` | number |
| `Store_Establishment_Year` | integer |
| `Store_Size` | string (`Small`, `Medium`, `High`) |
| `Store_Location_City_Type` | string (`Tier 1`, `Tier 2`, `Tier 3`) |
| `Store_Type` | string (`Supermarket Type1`, `Supermarket Type2`, `Food Mart`, `Departmental Store`) |

```bash
curl -X POST http://localhost:7860/v1/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "Product_Weight": 12.66,
    "Product_Sugar_Content": "Low Sugar",
    "Product_Allocated_Area": 0.027,
    "Product_Type": "Dairy",
    "Product_MRP": 117.08,
    "Store_Establishment_Year": 2009,
    "Store_Size": "Medium",
    "Store_Location_City_Type": "Tier 2",
    "Store_Type": "Supermarket Type2"
  }'
```

Response:

```json
{"predicted_sales": 1234.56}
```

### `POST /v1/predictbatch`

Predicts sales for many records. Upload a CSV as multipart form data under the field name `file`. The CSV needs the same columns as above.

```bash
curl -X POST http://localhost:7860/v1/predictbatch -H "X-API-Key: $API_KEY" -F "file=@records.csv"
```

Response: a JSON object keyed by row index.

```json
{"0": 1234.56, "1": 987.65}
```

A request without the correct key returns `401 {"error": "Unauthorized"}`. A request without a `file` field returns `400 {"error": "No file uploaded"}`.

## Configuration

- The backend URL in the Streamlit UI defaults to `http://backend:7860/v1/predict` and can be edited in the form. To point the UI at a different backend, replace it with that backend's `/v1/predict` URL.
- The model depends on pinned library versions (`scikit-learn==1.6.1`, `xgboost==2.1.4`, `pandas==2.2.2`, `joblib==1.4.2`). Keep them in sync with the versions used to train and save the model.
- The Flask app uses its built-in development server, which is fine for a class project but not for production.

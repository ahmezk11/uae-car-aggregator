# UAE Car Aggregator

AutoTempest-style aggregator backend for the UAE used-car market. FastAPI REST API over a SQLAlchemy/SQLite store, with Pydantic models for listings (make, model, year, price, mileage, location, source).

## Run

```bash
pip install fastapi uvicorn sqlalchemy pydantic
uvicorn car_aggregator_backend:app --reload
```

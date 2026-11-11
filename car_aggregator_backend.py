# car_aggregator_backend/main.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy model
class CarModel(Base):
    __tablename__ = "cars"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    price = Column(Integer)
    mileage = Column(Integer)
    location = Column(String)
    image_url = Column(String, nullable=True)
    source_url = Column(String)
    date_posted = Column(DateTime)

Base.metadata.create_all(bind=engine)

# FastAPI app setup
app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class CarBase(BaseModel):
    title: str
    make: str
    model: str
    year: int
    price: int
    mileage: int
    location: str
    image_url: Optional[str] = None
    source_url: str

class CarCreate(CarBase):
    pass

class Car(CarBase):
    id: str
    date_posted: datetime.datetime

    class Config:
        orm_mode = True

# Add a new car listing
@app.post("/cars/", response_model=Car)
def add_car(car: CarCreate, db: Session = Depends(get_db)):
    db_car = CarModel(
        id=str(uuid4()),
        date_posted=datetime.datetime.now(),
        **car.dict()
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

# Get all car listings
@app.get("/cars/", response_model=List[Car])
def list_cars(db: Session = Depends(get_db)):
    return db.query(CarModel).all()

# Get a specific car listing by ID
@app.get("/cars/{car_id}", response_model=Car)
def get_car(car_id: str, db: Session = Depends(get_db)):
    car = db.query(CarModel).filter(CarModel.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

# Search cars by filters
@app.get("/search/", response_model=List[Car])
def search_cars(
    make: Optional[str] = None,
    model: Optional[str] = None,
    year: Optional[int] = None,
    max_price: Optional[int] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CarModel)
    if make:
        query = query.filter(CarModel.make.ilike(make))
    if model:
        query = query.filter(CarModel.model.ilike(model))
    if year:
        query = query.filter(CarModel.year == year)
    if max_price:
        query = query.filter(CarModel.price <= max_price)
    if location:
        query = query.filter(CarModel.location.ilike(location))
    return query.all()

# Seed the database with sample listings (for testing purposes only)
@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    if not db.query(CarModel).first():
        sample_cars = [
            CarModel(
                id=str(uuid4()),
                title="2018 Toyota Land Cruiser VXR",
                make="Toyota",
                model="Land Cruiser",
                year=2018,
                price=180000,
                mileage=75000,
                location="Dubai",
                image_url="https://example.com/toyota1.jpg",
                source_url="https://dubicars.com/listing/toyota1",
                date_posted=datetime.datetime.now()
            ),
            CarModel(
                id=str(uuid4()),
                title="2020 Nissan Patrol Platinum",
                make="Nissan",
                model="Patrol",
                year=2020,
                price=210000,
                mileage=40000,
                location="Sharjah",
                image_url="https://example.com/nissan1.jpg",
                source_url="https://dubicars.com/listing/nissan1",
                date_posted=datetime.datetime.now()
            ),
            CarModel(
                id=str(uuid4()),
                title="2017 Mercedes-Benz G63 AMG",
                make="Mercedes-Benz",
                model="G63",
                year=2017,
                price=320000,
                mileage=60000,
                location="Abu Dhabi",
                image_url="https://example.com/merc1.jpg",
                source_url="https://dubicars.com/listing/merc1",
                date_posted=datetime.datetime.now()
            )
        ]
        db.bulk_save_objects(sample_cars)
        db.commit()
    db.close()

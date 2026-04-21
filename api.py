from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine
from auth import verify_password
import schemas

# This creates database.db and all tables within it
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="UVT Branding App API")

app.mount("/static", StaticFiles(directory="html/static"), name="static")

@app.get("/")
def serve_home():
    return FileResponse("html/login.html")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.post("/inventory/", response_model=schemas.Inventory)
def add_item(item: schemas.InventoryCreate, db: Session = Depends(get_db)):
    return crud.create_inventory(db, item)

@app.get("/inventory/", response_model=list[schemas.Inventory])
def list_items(db: Session = Depends(get_db)):
    return crud.get_all_inventory(db)

@app.post("/loans/", response_model=schemas.Loan)
def checkout_item(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    return crud.create_loan(db, loan)

@app.post("/login/")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    # Find the user by their email
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    
    # If user doesn't exist OR password doesn't match the hash
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return {"message": "Login successful", "role": user.role}

@app.get("/home")
def serve_home():
    # Make sure you have a home.html inside your html/ folder!
    return FileResponse("html/home.html")
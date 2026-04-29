from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, get_db
from .auth import (
    verify_password,
    get_current_user,
    require_superadmin,
    require_admin_or_above,
    require_coordinator_or_above,
    create_session,
    delete_session,
    get_session_user_id,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="UVT Branding App API")

app.mount("/static", StaticFiles(directory="frontend/html/static"), name="static")


# --- Page Routes ---

@app.get("/")
def serve_login():
    return FileResponse("frontend/html/login.html")


@app.get("/home")
def serve_home(request: Request):
    if get_session_user_id(request) is None:
        return RedirectResponse(url="/", status_code=302)
    return FileResponse("frontend/html/home.html")


@app.get("/inventory")
def serve_inventory(request: Request):
    if get_session_user_id(request) is None:
        return RedirectResponse(url="/", status_code=302)
    return FileResponse("frontend/html/InventoryManagement.html")


@app.get("/admin")
def serve_admin(request: Request, db: Session = Depends(get_db)):
    from .auth import _sessions
    token = request.cookies.get("session_token")
    if not token or token not in _sessions:
        return RedirectResponse(url="/", status_code=302)
    user_id = _sessions[token]
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.role != "SuperAdmin":
        return RedirectResponse(url="/home", status_code=302)
    return FileResponse("frontend/html/superadmin.html")


# --- Auth API ---

@app.post("/login/")
def login(user_credentials: schemas.UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_session(user.id)
    response.set_cookie(key="session_token", value=token, httponly=True, samesite="lax")
    return {"message": "Login successful", "role": user.role, "full_name": user.full_name}


@app.post("/logout/")
def logout(request: Request, response: Response):
    token = request.cookies.get("session_token")
    if token:
        delete_session(token)
    response.delete_cookie("session_token")
    return {"message": "Logged out"}


@app.get("/me", response_model=schemas.User)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


# --- Inventory API ---

@app.post("/inventory/", response_model=schemas.Inventory)
def add_item(
    item: schemas.InventoryCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin_or_above),
):
    return crud.create_inventory(db, item)


@app.get("/inventory/", response_model=list[schemas.Inventory])
def list_items(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    return crud.get_all_inventory(db)


@app.get("/inventory/{item_id}", response_model=schemas.Inventory)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    item = crud.get_inventory_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/inventory/{item_id}", response_model=schemas.Inventory)
def update_item(
    item_id: int,
    update: schemas.InventoryUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_coordinator_or_above),
):
    return crud.update_inventory(db, item_id, update)


@app.delete("/inventory/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin_or_above),
):
    crud.delete_inventory(db, item_id)
    return {"message": "Item deleted"}


# --- Stats API ---

@app.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    return crud.get_stats(db)


# --- Loan API ---

@app.post("/loans/", response_model=schemas.Loan)
def checkout_item(
    loan: schemas.LoanCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    return crud.create_loan(db, loan)


# --- Superadmin: User Management API ---

@app.get("/admin/users/", response_model=list[schemas.User])
def list_users(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_superadmin),
):
    return crud.get_all_users(db)


@app.post("/admin/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_superadmin),
):
    return crud.create_user(db, user)


@app.get("/admin/users/{user_id}", response_model=schemas.User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_superadmin),
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/admin/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_superadmin),
):
    return crud.update_user(db, user_id, user_update)


@app.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_superadmin),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    crud.delete_user(db, user_id)
    return {"message": "User deleted"}

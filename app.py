from fastapi import FastAPI,Depends, HTTPException
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy  import URL,create_engine
from typing import List
from models import *


# Create Engine for PostgreSQL
url_object = URL.create(
    "postgresql+psycopg2",
    username="postgres",
    password="123456",  # plain (unescaped) text
    host="localhost",
    database="googleplay",
    port=5432
    )

engine = create_engine(url_object,execution_options={"schema_translate_map": {None: "public"}})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
#db = engine.connect()

app = FastAPI()

@app.get('/')
async def home():
    return dict({"msg":"Hello,World!!!"})

@app.get("/developers", response_model=List[DeveloperSchema])
def read_developers(skip= 0 , limit = 100 , db:Session=Depends(get_db)):

    developers = db.query(Developer).offset(skip).limit(limit).all()
    return developers

@app.get("/developers/{developer_id}", response_model=DeveloperSchema)
def get_developer(developer_id: str, db:Session=Depends (get_db)):

    developer = db.query(Developer).filter(Developer.developer_id == developer_id).first()

    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    return developer

@app.post("/developers/", response_model=DeveloperSchema)
def create_developer(developer: DeveloperSchema, db: Session = Depends(get_db)):
    new_developer = Developer(**developer.model_dump())
    db.add(new_developer)
    db.commit()
    db.refresh(new_developer)
    return new_developer


@app.put("/developers/{developer_id}", response_model=DeveloperSchema)
def update_developer(developer_id: str, updated_data: DeveloperSchema, db: Session = Depends(get_db)):
    
    developer_query = db.query(Developer).filter(Developer.developer_id == developer_id).first()
    
    if not developer_query:
        raise HTTPException(status_code=404, detail="Developer not found")
    
    validated_data = updated_data.model_dump(exclude_unset=True)

    for k,v in validated_data.items():
        setattr(developer_query,k,v)
    
    db.commit()
    db.refresh(developer_query)
    return developer_query

@app.delete("/developers/{developer_id}",response_model=DeveloperSchema)
def delete_developer(developer_id:str, db: Session = Depends(get_db)):
    db_developer = db.query(Developer).filter(Developer.developer_id == developer_id).first()
    if db_developer is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    db.delete(db_developer)
    db.commit()
    return db_developer


#Category Endpoints

# GET all categories
@app.get("/categories/", response_model=List[CategorySchema])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

# GET a specific category
@app.get("/categories/{category_id}", response_model=CategorySchema)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
    
# POST a new category
@app.post("/categories/", response_model=CategorySchema)
def create_category(category: CategorySchema, db: Session = Depends(get_db)):
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# PUT (update) a category
@app.put("/categories/{category_id}", response_model=CategorySchema)
def update_category(category_id: int, category: CategorySchema, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.category_id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.model_dump(exclude_unset=True).items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category
    
# DELETE a category
@app.delete("/categories/{category_id}", response_model=CategorySchema)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.category_id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return db_category
    
#App Endpoints

# GET all apps
@app.get("/apps/", response_model=List[AppSchema])
def read_apps(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    apps = db.query(App).offset(skip).limit(limit).all()
    return apps

# GET a specific app
@app.get("/apps/{app_id}", response_model=AppSchema)
def read_app(app_id: str, db: Session = Depends(get_db)):
    app = db.query(App).filter(App.app_id == app_id).first()
    if app is None:
        raise HTTPException(status_code=404, detail="App not found")
    return app


# POST a new app
@app.post("/apps/", response_model=AppSchema)
def create_app(app: AppSchema, db: Session = Depends(get_db)):
    db_app = App(**app.dict())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

# PUT (update) an app
@app.put("/apps/{app_id}", response_model=AppSchema)
def update_app(app_id: str, app: AppSchema, db: Session = Depends(get_db)):
    db_app = db.query(App).filter(App.app_id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    for key, value in app.dict(exclude_unset=True).items():
        setattr(db_app, key, value)
    db.commit()
    db.refresh(db_app)
    return db_app

# DELETE an app
@app.delete("/apps/{app_id}", response_model=AppSchema)
def delete_app(app_id: str, db: Session = Depends(get_db)):
    db_app = db.query(App).filter(App.app_id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    db.delete(db_app)
    db.commit()
    return db_app
from fastapi import FastAPI, Request
from sqlalchemy.orm import Session
from fds_service.fds_db.database import engine, init_db
from fds_service.fds_core import detector

from .blocklist_endpoints import router as blocklist_router
from .rule_endpoints import router as rule_router
from .chargeback_endpoints import router as chargeback_router

app = FastAPI(title="FDS API", description="Fraud Detection System API", version="1.0")
app.include_router(blocklist_router, prefix="/blocklist", tags=["Blocklist"])
app.include_router(rule_router, prefix="/rules", tags=["Rules"])
app.include_router(chargeback_router, prefix="/chargeback", tags=["Chargeback"])

'''
uvicorn fds_service.fds_api.app:app --reload --port 5000
uvicorn customer_server.main:app --reload --port 5001

http://localhost:5000/docs/
http://localhost:5001/docs/

백그라운드 실행
uvicorn fds_service.fds_api.app:app --reload --port 8000 &
uvicorn customer_server.main:app --reload --port 8001 &

아이피 중복
lsof -i :5001
kill -9 62267
'''
@app.on_event("startup")
async def startup():
    init_db()
    print("Database initialized")

@app.get("/")
def root():
    return {"message": "FDS API is running"}

@app.post("/check-block")
async def fds_check_block(request: Request):
    order_data = await request.json()
    print(order_data)
    with Session(engine) as db:
        return detector.check_block(order_data, db)
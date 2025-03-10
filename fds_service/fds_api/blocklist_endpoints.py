from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/check-block")
async def fds_check_block(request: Request):
        return
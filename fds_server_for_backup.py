import json

from fastapi import FastAPI, Request
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, DateTime, text, Integer
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

# fds app으로 모듈화함.
# 이 코드는 sqlalchemy orm과 직접 sql 작성하는 것을 비교하기 위해 보존한다.

app = FastAPI()

# Database setup
engine = create_engine("sqlite:///fds.db", echo=True)
metadata = MetaData()

blacklist = Table(
    "blacklist", metadata,
    Column("user_id", String, primary_key=True),
    Column("reason", String),
    Column("created_at", DateTime, default=datetime.now),
)

orders = Table(
    "orders", metadata,
    Column("order_id", String, primary_key=True),
    Column("user_id", String),
    Column("order_time", DateTime),
    Column("amount", Float),
    Column("order_status", String),
)

rules = Table(
    "rules", metadata,
    Column("rule_id", String, primary_key=True),   # 룰 ID
    Column("rule_sql", String),                   # SQL 조건
    Column("rule_reason", String),                # 룰 사유
)

@app.on_event("startup")
async def startup():
    # 애플리케이션 시작 시 테이블 생성
    metadata.create_all(engine)
    print("Tables created!")

@app.post("/fds/check-block")
async def check_block(request: Request):
    # 요청 데이터 파싱
    order_data = await request.json()

    with engine.begin() as conn:  # 자동으로 트랜잭션 관리 (commit/rollback)
        # collecting order data
        conn.execute(orders.insert().values(
            order_id=order_data["order_id"],
            user_id=order_data["user_id"],
            amount=order_data["amount"],
            order_time=datetime.fromisoformat(order_data["order_time"]),
            # order_status=order_data["order_status"]
        ))

        # registering the user on the blacklist for a test.
        conn.execute(blacklist.insert().values(
            user_id=order_data["user_id"],
            reason="test"
        ))

        # getting rule list
        rule_fetch_query = text("SELECT rule_sql, rule_reason FROM rules ORDER BY rule_id ASC")
        rule_list = conn.execute(rule_fetch_query).fetchall()

        for rule in rule_list:
            # SQL 조건 실행: 주문 ID를 기반으로 확인
            rule_condition_query = text(rule[0])
            print(f"Executing rule: {rule_condition_query}")

            rule_condition_result = conn.execute(rule_condition_query, {"order_id": order_data["order_id"]}).fetchone()

            if rule_condition_result:  # 조건을 만족하면 차단
                return {"block": True, "reason": rule[1]}

        # 모든 룰을 통과하면 차단되지 않음
    return {"block": False}

@app.post("/fds/add-rules")
async def add_rules():
    with open("fds_service/data/fds_rules.json", "r") as json_file:
        loaded_rules = json.load(json_file)
    try:
        with engine.begin() as conn:
            cnt=0
            # 데이터 삽입
            for rule in loaded_rules:
                conn.execute(rules.insert().values(
                    rule_id=rule["rule_id"],
                    rule_sql=rule["rule_sql"],
                    rule_reason=rule["rule_reason"]
                ))
                cnt += 1
        return {"message": f"{cnt} rules added successfully"}
    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
from fastapi import FastAPI
import requests
from random import randint
from datetime import datetime

app = FastAPI()

'''
cd customer_server
uvicorn customer_server.main:app --reload
'''

@app.get("/generate-order")
def generate_order():
    order_data = {
        "order_id": f"ORD{randint(1000, 9999)}",
        # "user_id": f"USER{randint(100, 999)}",
        "user_id": "USER999",
        "order_time": datetime.now().isoformat(),
        "amount": randint(10, 100),
        "payment_status": "success"
    }
    response = requests.post("http://127.0.0.1:5000/check-block", json=order_data)
    return {"order": order_data, "fds_response": response.json()}
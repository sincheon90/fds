

def check_block(order_data, db):
    response = {
        "isBlock": isBlock(order_data),
    }
    return response

def isBlock(order_data):
    """
    주문 데이터를 검사하여 차단 여부를 반환합니다.
    """

    # 블록리스트 등록을 여기서 안한다면 유저아이디 안받아도 될듯
    order_id = order_data.get("order_id")

    # collecting order data
    conn.execute(orders.insert().values(
        order_id=order_data["order_id"],
        user_id=order_data["user_id"],
        amount=order_data["amount"],

# order id로 탐지, 주문 기준 탐지이기때문에 유저 보다는 order로
# 반환 값은 탐지를 리스트, 블록 여부, 블록리스트 등록 여부 필요? 일단 룰 종류를 반환 받고 에러 메시지 알림에 띄우는 것은 나중에
 order_time=datetime.fromisoformat(order_data["order_time"]),
        # order_status=order_data["order_status"]
    ))


# dectectd_rules : rule_id list
# flag: 탐지된 룰중에 블록이 있는지 반환
    rule_id, flag = rule_manager.check_rule(order_id) # 차단이 아닌 경우는 rule_id null 반환

    if rule_id:
        if rule_manager.isBlocklist and order_id:
            add_to_blocklist(order_id, rule_id)
            return True  # 차단 규칙이 있으면 즉시 True 반환
    else:
        return False

def add_to_blocklist(order_id):
    """
    주문 ID를 블랙리스트에 추가합니다.
    """
    blocklist = get_blocklist()
    if order_id not in blocklist:
        blocklist.add(order_id)
        update_blocklist(blocklist)
    return
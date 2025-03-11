from concurrent.futures import ThreadPoolExecutor
import threading

# ✅ 비동기 탐지: 스레드 풀
executor = ThreadPoolExecutor(max_workers=2)  # 최대 2개의 스레드로 비동기 처리

# ✅ 룰을 메모리에 올려 캐싱
RULES = []  # 프로그램 시작 시 한 번만 DB에서 불러옴

def load_rules_from_db(db):
    """
    프로그램 시작 시 DB에서 룰을 불러와 메모리에 캐싱
    """
    global RULES
    sql = """
    SELECT id, sql_query, type FROM rules
    ORDER BY id ASC, type ASC;
    """
    RULES = db.execute(sql).fetchall()
    print(f"Loaded {len(RULES)} rules into memory.")

def check_block(order_data, db):
    """
    주문 데이터를 검사하여 차단 여부를 결정.
    - 메모리에 캐싱된 룰을 사용하여 빠르게 탐지
    - 차단 룰이 탐지되면 즉시 반환
    """
    detected_rules, is_blocked, block_rule_id = isBlock(order_data)

    response = {
        "isBlock": is_blocked,
        "blockRuleId": block_rule_id if is_blocked else None,
    }

    return response

def isBlock(order_data):
    """
    1차 실시간 탐지:
    - 메모리에 있는 룰 리스트에서 탐색 수행
    - 차단 룰이 처음 발견되면 즉시 반환
    """
    order_id = order_data["order_id"]
    detected_rules = []  # 탐지된 룰 리스트
    block_rule_id = None  # 차단된 룰 ID

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

    # 🚀 메모리에서 룰 리스트 탐색
    for rule_id, rule_sql, rule_type, is_blocklist, table_type in RULES:
        if detect_with_sql(order_id, rule_sql):
            detected_rules.append(rule_id)
            # 🚨 차단 룰이 발견되면 즉시 종료하고 반환
            if rule_type == "Block":
                if is_blocklist:
                    add_to_blocklist(order_id, block_rule_id, db)
                executor.submit(process_remaining_rules, order_data, detected_rules, db)  # 🚀 비동기 탐색 실행
                return True

    # 모든 룰 탐지 후 차단된 룰이 없으면 False 반환
    save_detection_history(order_id, detected_rules, db)
    return False


################### 이하 코드 확인 필요 ###################

def detect_with_sql(order_id, rule_sql, db):
    """
    주어진 SQL을 실행하여 특정 주문(order_id)이 탐지되는지 확인.
    """
    detection_sql = f"""
    SELECT 1 FROM ({rule_sql}) AS subquery
    WHERE order_id = :order_id
    LIMIT 1;
    """
    result = db.execute(detection_sql, {"order_id": order_id}).fetchone()
    return bool(result)  # 데이터가 존재하면 탐지됨 (True)

def process_remaining_rules(order_id, detected_rules, db):
    """
    차단된 룰이 아니면 나머지 룰들을 비동기로 처리하고 기록합니다.
    """
    remaining_rules = RULES[RULES.index(rule) + 1:]  # 이후 룰 저장

    # 나머지 룰들에 대해서 비동기 탐지하고 기록하는 작업
    for rule_id in RULES:
        if rule_id not in detected_rules:
            # 남은 룰에 대한 탐지 및 기록 작업을 비동기로 처리
            if detect_with_sql(order_id, rule_id[1], db):
                detected_rules.append(rule_id)

    # 룰 탐지 히스토리 기록
    save_detection_history(order_id, detected_rules, db)

def save_detection_history(order_id, detected_rules, db):
    """
    탐지된 룰을 DB에 기록합니다.
    """
    for rule_id in detected_rules:
        sql = """
        INSERT INTO detection_history (order_id, rule_id, detected_at)
        VALUES (:order_id, :rule_id, NOW());
        """
        db.execute(sql, {"order_id": order_id, "rule_id": rule_id})
        db.commit()


def add_to_blocklist(user_id):
    """
    주문 ID를 블랙리스트에 추가합니다.
    """
    blocklist = get_blocklist()
    if user_id not in blocklist:
        blocklist.add(user_id)
        update_blocklist(blocklist)
    return
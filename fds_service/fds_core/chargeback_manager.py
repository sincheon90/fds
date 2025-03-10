from fds_service.fds_db import crud
import blocklist_manager

def register_chargeback(orderId):

    userId = crud.getUserId(orderId)

    change_status(orderId, "chargeback")

    blocklist_manager.add_to_blocklist(userId, "chargeback")
    return

def change_status(orderId, status: str):
    return


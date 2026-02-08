import random
import uuid


def process_payment(amount: int) -> dict:
    """
    Dummy payment processor.
    Simulates a real payment gateway.
    """

    success = random.random() > 0.1  # 90% success rate

    if success:
        return {
            "payment_status": "SUCCESS",
            "transaction_id": str(uuid.uuid4()),
            "amount": amount
        }
    else:
        return {
            "payment_status": "FAILED",
            "transaction_id": None,
            "amount": amount
        }

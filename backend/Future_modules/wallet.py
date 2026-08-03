from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"]
)

WALLETS = {}
TRANSACTIONS = {}
WITHDRAWALS = {}
PAYMENT_REQUESTS = {}

class WalletCreate(BaseModel):
    user_id: str

class AddMoneyRequest(BaseModel):
    user_id: str
    amount: float

class TransferRequest(BaseModel):
    sender_id: str
    receiver_id: str
    amount: float

class WithdrawRequest(BaseModel):
    user_id: str
    amount: float

@router.post("/create")
def create_wallet(
    payload: WalletCreate
):

    if payload.user_id in WALLETS:

        return {
            "success": False,
            "message": "Wallet exists"
        }

    wallet_id = str(uuid4())

    WALLETS[payload.user_id] = {
        "wallet_id": wallet_id,
        "balance": 0,
        "created_at":
            datetime.utcnow().isoformat()
    }

    return {
        "success": True,
        "wallet_id": wallet_id
    }

@router.get("/balance/{user_id}")
def get_balance(user_id: str):

    wallet = WALLETS.get(user_id)

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    return {
        "user_id": user_id,
        "balance": wallet["balance"]
    }

@router.post("/add-money")
def add_money(
    payload: AddMoneyRequest
):

    wallet = WALLETS.get(
        payload.user_id
    )

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    wallet["balance"] += payload.amount

    txn_id = str(uuid4())

    TRANSACTIONS[txn_id] = {
        "txn_id": txn_id,
        "type": "credit",
        "user_id": payload.user_id,
        "amount": payload.amount,
        "created_at":
            datetime.utcnow().isoformat()
    }

    return {
        "success": True,
        "transaction_id": txn_id,
        "new_balance":
            wallet["balance"]
    }

@router.post("/transfer")
def transfer_money(
    payload: TransferRequest
):

    sender = WALLETS.get(
        payload.sender_id
    )

    receiver = WALLETS.get(
        payload.receiver_id
    )

    if not sender:
        raise HTTPException(
            status_code=404,
            detail="Sender wallet not found"
        )

    if not receiver:
        raise HTTPException(
            status_code=404,
            detail="Receiver wallet not found"
        )

    if sender["balance"] < payload.amount:

        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    sender["balance"] -= payload.amount
    receiver["balance"] += payload.amount

    txn_id = str(uuid4())

    TRANSACTIONS[txn_id] = {
        "txn_id": txn_id,
        "type": "transfer",
        "sender":
            payload.sender_id,
        "receiver":
            payload.receiver_id,
        "amount":
            payload.amount,
        "created_at":
            datetime.utcnow().isoformat()
    }

    return {
        "success": True,
        "transaction_id": txn_id
    }

@router.post("/withdraw")
def withdraw_money(
    payload: WithdrawRequest
):

    wallet = WALLETS.get(
        payload.user_id
    )

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    if wallet["balance"] < payload.amount:

        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    wallet["balance"] -= payload.amount

    withdrawal_id = str(uuid4())

    WITHDRAWALS[
        withdrawal_id
    ] = {
        "withdrawal_id":
            withdrawal_id,
        "user_id":
            payload.user_id,
        "amount":
            payload.amount,
        "status":
            "completed",
        "created_at":
            datetime.utcnow().isoformat()
    }

    return {
        "success": True,
        "withdrawal_id":
            withdrawal_id
    }

@router.get("/transactions/{user_id}")
def transaction_history(
    user_id: str
):

    result = []

    for txn in (
        TRANSACTIONS.values()
    ):

        if (
            txn.get("user_id")
            == user_id
        ):
            result.append(txn)

        elif (
            txn.get("sender")
            == user_id
        ):
            result.append(txn)

        elif (
            txn.get("receiver")
            == user_id
        ):
            result.append(txn)

    return {
        "count": len(result),
        "transactions":
            result
    }

@router.get("/stats")
def wallet_stats():

    total_wallets = len(
        WALLETS
    )

    total_balance = sum(
        wallet["balance"]
        for wallet
        in WALLETS.values()
    )

    return {
        "wallets":
            total_wallets,
        "total_balance":
            total_balance,
        "transactions":
            len(
                TRANSACTIONS
            )
    }

CASHBACK_HISTORY = {}

@router.post("/cashback/apply")
def apply_cashback(
    user_id: str,
    amount: float
):

    wallet = WALLETS.get(user_id)

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    cashback = round(
        amount * 0.05,
        2
    )

    wallet["balance"] += cashback

    cashback_id = str(uuid4())

    CASHBACK_HISTORY[
        cashback_id
    ] = {
        "cashback_id":
            cashback_id,
        "user_id":
            user_id,
        "amount":
            cashback,
        "created_at":
            datetime.utcnow().isoformat()
    }

    return {
        "cashback":
            cashback,
        "balance":
            wallet["balance"]
    }

REWARD_POINTS = {}

@router.post("/rewards/add")
def add_rewards(
    user_id: str,
    points: int
):

    REWARD_POINTS[user_id] = (
        REWARD_POINTS.get(
            user_id,
            0
        ) + points
    )

    return {
        "user_id":
            user_id,
        "points":
            REWARD_POINTS[user_id]
    }

@router.get("/rewards/{user_id}")
def get_rewards(
    user_id: str
):

    return {
        "points":
            REWARD_POINTS.get(
                user_id,
                0
            )
    }

COUPONS = {
    "WELCOME50": 50,
    "NAV100": 100,
    "FIRST20": 20
}

@router.post("/coupon/apply")
def apply_coupon(
    user_id: str,
    coupon: str
):

    if coupon not in COUPONS:

        raise HTTPException(
            status_code=400,
            detail="Invalid coupon"
        )

    discount = COUPONS[coupon]

    return {
        "success": True,
        "coupon": coupon,
        "discount": discount
    }

REFERRALS = {}

@router.post("/referral/create")
def create_referral(
    user_id: str
):

    code = (
        "NAV-" +
        user_id[:4].upper()
    )

    REFERRALS[user_id] = code

    return {
        "referral_code":
            code
    }

@router.get("/referral/{user_id}")
def get_referral(
    user_id: str
):

    return {
        "code":
            REFERRALS.get(
                user_id
            )
    }

RAZORPAY_ORDERS = {}

@router.post("/razorpay/create-order")
def create_order(
    user_id: str,
    amount: float
):

    order_id = (
        "order_" +
        str(uuid4())[:10]
    )

    RAZORPAY_ORDERS[
        order_id
    ] = {
        "user_id":
            user_id,
        "amount":
            amount,
        "status":
            "created"
    }

    return {
        "order_id":
            order_id,
        "amount":
            amount,
        "currency":
            "INR"
    }

@router.post("/razorpay/verify")
def verify_payment(
    order_id: str
):

    order = (
        RAZORPAY_ORDERS.get(
            order_id
        )
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    order["status"] = "paid"

    wallet = WALLETS.get(
        order["user_id"]
    )

    if wallet:

        wallet["balance"] += (
            order["amount"]
        )

    return {
        "success": True,
        "status": "paid"
    }

@router.get("/leaderboard")
def wallet_leaderboard():

    ranking = []

    for user_id, wallet in (
        WALLETS.items()
    ):

        ranking.append({
            "user_id":
                user_id,
            "balance":
                wallet["balance"]
        })

    ranking.sort(
        key=lambda x: x["balance"],
        reverse=True
    )

    return {
        "leaderboard":
            ranking[:20]
    }

@router.get("/admin/dashboard")
def admin_dashboard():

    total_wallets = len(
        WALLETS
    )

    total_transactions = len(
        TRANSACTIONS
    )

    total_withdrawals = len(
        WITHDRAWALS
    )

    total_rewards = sum(
        REWARD_POINTS.values()
    ) if REWARD_POINTS else 0

    return {
        "wallets":
            total_wallets,
        "transactions":
            total_transactions,
        "withdrawals":
            total_withdrawals,
        "reward_points":
            total_rewards
    }

@router.get("/health")
def health():

    return {
        "status":
            "healthy",
        "module":
            "wallet",
        "time":
            datetime.utcnow().isoformat()
    }
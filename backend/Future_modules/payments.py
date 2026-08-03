from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

class PaymentRequest(BaseModel):
    user_id: str
    amount: float
    currency: str = "INR"
    description: Optional[str] = None


class WalletRecharge(BaseModel):
    user_id: str
    amount: float


class RefundRequest(BaseModel):
    payment_id: str
    reason: str


payments_db = []
wallet_db = []
refunds_db = []


def generate_id():
    return str(uuid.uuid4())


def now():
    return datetime.utcnow()


@router.post("/wallet/create")
def create_wallet(user_id: str):

    existing = next(
        (
            w
            for w in wallet_db
            if w["user_id"] == user_id
        ),
        None
    )

    if existing:
        return existing

    wallet = {
        "wallet_id": generate_id(),
        "user_id": user_id,
        "balance": 0,
        "created_at": now()
    }

    wallet_db.append(wallet)

    return wallet


@router.get("/wallet/{user_id}")
def get_wallet(user_id: str):

    wallet = next(
        (
            w
            for w in wallet_db
            if w["user_id"] == user_id
        ),
        None
    )

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    return wallet


@router.post("/wallet/recharge")
def recharge_wallet(
    data: WalletRecharge
):

    wallet = next(
        (
            w
            for w in wallet_db
            if w["user_id"] == data.user_id
        ),
        None
    )

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    wallet["balance"] += data.amount

    return {
        "success": True,
        "balance":
        wallet["balance"]
    }


@router.post("/create")
def create_payment(
    payment: PaymentRequest
):

    transaction = {
        "payment_id":
        generate_id(),

        "user_id":
        payment.user_id,

        "amount":
        payment.amount,

        "currency":
        payment.currency,

        "description":
        payment.description,

        "status":
        "pending",

        "created_at":
        now()
    }

    payments_db.append(
        transaction
    )

    return transaction


@router.post("/verify/{payment_id}")
def verify_payment(
    payment_id: str
):

    payment = next(
        (
            p
            for p in payments_db
            if p["payment_id"]
            == payment_id
        ),
        None
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    payment["status"] = "success"

    return {
        "success": True,
        "payment": payment
    }

@router.get("/{payment_id}")
def payment_status(
    payment_id: str
):

    payment = next(
        (
            p
            for p in payments_db
            if p["payment_id"]
            == payment_id
        ),
        None
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    return payment


@router.get("/history/{user_id}")
def payment_history(
    user_id: str
):

    history = [
        p
        for p in payments_db
        if p["user_id"] == user_id
    ]

    return {
        "count":
        len(history),

        "payments":
        history
    }



@router.post("/refund")
def refund_payment(
    data: RefundRequest
):

    payment = next(
        (
            p
            for p in payments_db
            if p["payment_id"]
            == data.payment_id
        ),
        None
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    refund = {
        "refund_id":
        generate_id(),

        "payment_id":
        payment["payment_id"],

        "amount":
        payment["amount"],

        "reason":
        data.reason,

        "status":
        "processed",

        "created_at":
        now()
    }

    refunds_db.append(
        refund
    )

    return refund



@router.get("/refunds/all")
def all_refunds():

    return {
        "count":
        len(refunds_db),

        "refunds":
        refunds_db
    }



@router.post("/wallet/pay")
def pay_using_wallet(
    user_id: str,
    amount: float
):

    wallet = next(
        (
            w
            for w in wallet_db
            if w["user_id"] == user_id
        ),
        None
    )

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    if wallet["balance"] < amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    wallet["balance"] -= amount

    transaction = {
        "payment_id":
        generate_id(),

        "user_id":
        user_id,

        "amount":
        amount,

        "status":
        "success",

        "method":
        "wallet",

        "created_at":
        now()
    }

    payments_db.append(
        transaction
    )

    return {
        "success": True,
        "balance":
        wallet["balance"],
        "payment":
        transaction
    }

coupons_db = []


class CouponCreate(BaseModel):
    code: str
    discount_percent: float
    max_discount: float


@router.post("/coupon/create")
def create_coupon(
    coupon: CouponCreate
):

    data = {
        "coupon_id": generate_id(),
        "code": coupon.code.upper(),
        "discount_percent":
        coupon.discount_percent,
        "max_discount":
        coupon.max_discount,
        "active": True,
        "created_at": now()
    }

    coupons_db.append(data)

    return data


@router.post("/coupon/apply")
def apply_coupon(
    code: str,
    amount: float
):

    coupon = next(
        (
            c
            for c in coupons_db
            if c["code"] == code.upper()
            and c["active"]
        ),
        None
    )

    if not coupon:
        raise HTTPException(
            status_code=404,
            detail="Invalid coupon"
        )

    discount = (
        amount *
        coupon["discount_percent"]
    ) / 100

    discount = min(
        discount,
        coupon["max_discount"]
    )

    final_amount = amount - discount

    return {
        "discount":
        round(discount, 2),

        "final_amount":
        round(final_amount, 2)
    }


@router.get("/gst")
def calculate_gst(
    amount: float,
    gst_percent: float = 18
):

    gst = (
        amount *
        gst_percent
    ) / 100

    return {
        "base_amount":
        amount,

        "gst":
        round(gst, 2),

        "total":
        round(
            amount + gst,
            2
        )
    }


subscriptions_db = []


class SubscriptionPlan(
    BaseModel
):
    user_id: str
    plan_name: str
    amount: float


@router.post("/subscription")
def create_subscription(
    data: SubscriptionPlan
):

    plan = {
        "subscription_id":
        generate_id(),

        "user_id":
        data.user_id,

        "plan_name":
        data.plan_name,

        "amount":
        data.amount,

        "status":
        "active",

        "created_at":
        now()
    }

    subscriptions_db.append(
        plan
    )

    return plan


@router.get(
    "/subscription/{user_id}"
)
def get_subscription(
    user_id: str
):

    return [
        s
        for s in subscriptions_db
        if s["user_id"] == user_id
    ]



invoices_db = []


@router.post(
    "/invoice/{payment_id}"
)
def generate_invoice(
    payment_id: str
):

    payment = next(
        (
            p
            for p in payments_db
            if p["payment_id"]
            == payment_id
        ),
        None
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    invoice = {
        "invoice_id":
        generate_id(),

        "payment_id":
        payment_id,

        "amount":
        payment["amount"],

        "generated_at":
        now()
    }

    invoices_db.append(
        invoice
    )

    return invoice


@router.get("/analytics")
def payment_analytics():

    total_amount = sum(
        p["amount"]
        for p in payments_db
        if p["status"]
        == "success"
    )

    total_transactions = len(
        payments_db
    )

    success_count = len(
        [
            p
            for p in payments_db
            if p["status"]
            == "success"
        ]
    )

    failed_count = len(
        [
            p
            for p in payments_db
            if p["status"]
            == "failed"
        ]
    )

    return {
        "total_transactions":
        total_transactions,

        "successful":
        success_count,

        "failed":
        failed_count,

        "revenue":
        round(total_amount, 2)
    }


@router.get("/admin/stats")
def admin_stats():

    return {

        "users_with_wallet":
        len(wallet_db),

        "payments":
        len(payments_db),

        "refunds":
        len(refunds_db),

        "subscriptions":
        len(subscriptions_db),

        "invoices":
        len(invoices_db),

        "coupons":
        len(coupons_db)
    }


@router.post("/razorpay/order")
def create_razorpay_order(
    amount: float
):

    return {
        "order_id":
        "order_" +
        generate_id()[:10],

        "amount":
        amount,

        "currency":
        "INR",

        "status":
        "created"
    }


@router.post(
    "/razorpay/verify"
)
def verify_razorpay_payment(
    order_id: str,
    payment_id: str
):

    return {
        "verified": True,
        "order_id":
        order_id,

        "payment_id":
        payment_id
    }


@router.post("/upi/pay")
def upi_payment(
    user_id: str,
    amount: float,
    upi_id: str
):

    transaction = {
        "payment_id":
        generate_id(),

        "user_id":
        user_id,

        "upi_id":
        upi_id,

        "amount":
        amount,

        "status":
        "success",

        "created_at":
        now()
    }

    payments_db.append(
        transaction
    )

    return transaction
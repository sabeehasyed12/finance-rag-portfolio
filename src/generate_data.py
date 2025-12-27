import uuid
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_customers(n_customers: int) -> pd.DataFrame:
    customers = []

    shared_addresses = [fake.address() for _ in range(int(n_customers * 0.2))]
    shared_devices = [fake.uuid4() for _ in range(int(n_customers * 0.15))]

    for _ in range(n_customers):
        customer_id = str(uuid.uuid4())

        created_at = fake.date_time_between(start_date="-2y", end_date="now")
        ingestion_delay_days = random.randint(0, 3)
        ingestion_date = (created_at + timedelta(days=ingestion_delay_days)).date()

        email_base = fake.user_name()
        email_variation = random.choice(
            [
                f"{email_base}@gmail.com",
                f"{email_base.replace('.', '')}@gmail.com",
                f"{email_base}+promo@gmail.com",
            ]
        )

        address = random.choice(shared_addresses) if random.random() < 0.2 else fake.address()
        device_id = random.choice(shared_devices) if random.random() < 0.15 else str(uuid.uuid4())

        customers.append(
            {
                "customer_id": customer_id,
                "full_name": fake.name(),
                "email": email_variation,
                "phone": fake.phone_number(),
                "address": address,
                "device_id": device_id,
                "created_at": created_at,
                "ingestion_date": ingestion_date,
            }
        )

    return pd.DataFrame(customers)



def generate_accounts(customers: pd.DataFrame) -> pd.DataFrame:
    accounts = []

    for _, customer in customers.iterrows():
        num_accounts = random.randint(1, 3)

        for _ in range(num_accounts):
            account_id = str(uuid.uuid4())
            account_type = random.choice(["checking", "savings", "credit"])
            status = random.choices(
                ["active", "closed", "suspended"],
                weights=[0.7, 0.2, 0.1],
            )[0]

            opened_at = customer["created_at"] + timedelta(days=random.randint(0, 30))

            closed_at = None
            if status == "closed":
                closed_at = opened_at + timedelta(days=random.randint(30, 600))

            ingestion_delay_days = random.randint(0, 2)
            ingestion_date = (opened_at + timedelta(days=ingestion_delay_days)).date()

            accounts.append(
                {
                    "account_id": account_id,
                    "customer_id": customer["customer_id"],
                    "account_type": account_type,
                    "status": status,
                    "opened_at": opened_at.date(),
                    "closed_at": closed_at.date() if closed_at else None,
                    "ingestion_date": ingestion_date,
                }
            )

    return pd.DataFrame(accounts)



def generate_transactions(accounts: pd.DataFrame) -> pd.DataFrame:
    transactions = []

    for _, account in accounts.iterrows():
        if account["account_type"] == "credit":
            num_transactions = random.randint(200, 600)
        elif account["account_type"] == "checking":
            num_transactions = random.randint(100, 300)
        else:
            num_transactions = random.randint(20, 80)

        for _ in range(num_transactions):
            transaction_id = str(uuid.uuid4())

            created_at = fake.date_time_between(
                start_date=account["opened_at"],
                end_date="now",
            )

            status = random.choices(
                ["success", "failed", "pending"],
                weights=[0.85, 0.1, 0.05],
            )[0]

            settled_at = None
            if status == "success":
                settled_at = created_at + timedelta(days=random.randint(0, 2))

            ingestion_delay_days = random.randint(0, 5)
            ingestion_date = (created_at + timedelta(days=ingestion_delay_days)).date()

            amount = round(
                random.choice(
                    [
                        random.uniform(1, 20),
                        random.uniform(20, 100),
                        random.uniform(100, 500),
                        random.uniform(500, 2000),
                    ]
                ),
                2,
            )

            transactions.append(
                {
                    "transaction_id": transaction_id,
                    "account_id": account["account_id"],
                    "customer_id": account["customer_id"],
                    "amount": amount,
                    "currency": "USD",
                    "merchant_name": fake.company(),
                    "status": status,
                    "created_at": created_at,
                    "settled_at": settled_at,
                    "ingestion_date": ingestion_date,
                    "card_last_four": str(random.randint(1000, 9999)),
                    "device_id": fake.uuid4(),
                }
            )

            if random.random() < 0.02:
                duplicate = transactions[-1].copy()
                duplicate["ingestion_date"] = (
                    created_at + timedelta(days=random.randint(1, 7))
                ).date()
                transactions.append(duplicate)

    return pd.DataFrame(transactions)



def generate_payments(transactions: pd.DataFrame) -> pd.DataFrame:
    payments = []

    for _, txn in transactions.iterrows():
        if txn["status"] == "failed":
            max_attempts = random.randint(1, 2)
        elif txn["status"] == "pending":
            max_attempts = random.randint(1, 3)
        else:
            max_attempts = random.randint(1, 2)

        attempt_number = 1
        success = False

        for _ in range(max_attempts):
            payment_id = str(uuid.uuid4())
            attempted_at = txn["created_at"] + timedelta(
                hours=random.randint(1, 72)
            )

            if not success and random.random() < 0.75:
                status = "success"
                success = True
            else:
                status = "failed"

            ingestion_delay_days = random.randint(0, 2)
            ingestion_date = (attempted_at + timedelta(days=ingestion_delay_days)).date()

            payments.append(
                {
                    "payment_id": payment_id,
                    "transaction_id": txn["transaction_id"],
                    "payment_method": random.choice(["card", "bank"]),
                    "status": status,
                    "attempt_number": attempt_number,
                    "attempted_at": attempted_at,
                    "ingestion_date": ingestion_date,
                }
            )

            attempt_number += 1

            if success:
                break

    return pd.DataFrame(payments)



def generate_subscriptions(customers: pd.DataFrame) -> pd.DataFrame:
    subscriptions = []

    plans = ["basic", "pro", "enterprise"]
    statuses = ["active", "paused", "canceled"]

    for _, customer in customers.iterrows():
        has_subscription = random.random() < 0.7
        if not has_subscription:
            continue

        num_changes = random.randint(1, 4)
        start_date = customer["created_at"].date() + timedelta(days=random.randint(0, 30))

        for _ in range(num_changes):
            subscription_id = str(uuid.uuid4())
            plan_name = random.choice(plans)
            status = random.choice(statuses)

            end_date = None
            if status in ["paused", "canceled"]:
                end_date = start_date + timedelta(days=random.randint(30, 180))

            ingestion_delay_days = random.randint(0, 2)
            ingestion_date = start_date + timedelta(days=ingestion_delay_days)

            subscriptions.append(
                {
                    "subscription_id": subscription_id,
                    "customer_id": customer["customer_id"],
                    "plan_name": plan_name,
                    "status": status,
                    "start_date": start_date,
                    "end_date": end_date,
                    "ingestion_date": ingestion_date,
                }
            )

            if end_date:
                start_date = end_date - timedelta(days=random.randint(0, 15))
            else:
                start_date = start_date + timedelta(days=random.randint(30, 120))

    return pd.DataFrame(subscriptions)



def generate_refunds(transactions: pd.DataFrame) -> pd.DataFrame:
    refunds = []

    refundable_txns = transactions[
        transactions["status"] == "success"
    ].sample(frac=0.1, random_state=42)

    for _, txn in refundable_txns.iterrows():
        refund_id = str(uuid.uuid4())

        refunded_at = txn["created_at"] + timedelta(days=random.randint(2, 14))

        amount = txn["amount"]
        if random.random() < 0.3:
            amount = round(txn["amount"] * random.uniform(0.3, 0.9), 2)

        ingestion_delay_days = random.randint(0, 3)
        ingestion_date = (refunded_at + timedelta(days=ingestion_delay_days)).date()

        refunds.append(
            {
                "refund_id": refund_id,
                "transaction_id": txn["transaction_id"],
                "amount": amount,
                "refund_reason": random.choice(
                    ["customer_dispute", "merchant_error", "duplicate_charge"]
                ),
                "refunded_at": refunded_at.date(),
                "ingestion_date": ingestion_date,
            }
        )

        if random.random() < 0.1:
            duplicate = refunds[-1].copy()
            duplicate["refund_id"] = str(uuid.uuid4())
            duplicate["ingestion_date"] = (
                refunded_at + timedelta(days=random.randint(1, 5))
            ).date()
            refunds.append(duplicate)

    return pd.DataFrame(refunds)



def main():
    customers = generate_customers(n_customers=1000)
    accounts = generate_accounts(customers)
    transactions = generate_transactions(accounts)
    payments = generate_payments(transactions)
    subscriptions = generate_subscriptions(customers)
    refunds = generate_refunds(transactions)

    customers.to_csv(RAW_DATA_DIR / "customers.csv", index=False)
    accounts.to_csv(RAW_DATA_DIR / "accounts.csv", index=False)
    transactions.to_csv(RAW_DATA_DIR / "transactions.csv", index=False)
    payments.to_csv(RAW_DATA_DIR / "payments.csv", index=False)
    subscriptions.to_csv(RAW_DATA_DIR / "subscriptions.csv", index=False)
    refunds.to_csv(RAW_DATA_DIR / "refunds.csv", index=False)


if __name__ == "__main__":
    main()





# Data Dictionary

## 1. customers

**Description**  
Represents an individual customer. Contains intentional PII for masking demos.

**Purpose**  
Represents an individual customer with personal and device level attributes used for analytics and privacy demonstrations.

**Fields**

* customer_id  
  Type: UUID  
  Description: Primary key

* full_name  
  Type: STRING  
  Description: PII

* email  
  Type: STRING  
  Description: PII

* phone  
  Type: STRING  
  Description: PII

* address  
  Type: STRING  
  Description: PII

* device_id  
  Type: STRING  
  Description: Device identifier

* created_at  
  Type: TIMESTAMP  
  Description: Time customer was created in source system

* ingestion_date  
  Type: DATE  
  Description: Date record was ingested into the warehouse

**Notes**

* device_id is not guaranteed to be unique  
* multiple customers may share the same address  
* ingestion_date may lag created_at  

---

## 2. accounts

**Purpose**  
Represents financial accounts owned by customers.

**Fields**

* account_id  
  Type: UUID  
  Description: Primary key

* customer_id  
  Type: UUID  
  Description: Foreign key to customers

* account_type  
  Type: STRING  
  Description: checking, savings, credit

* status  
  Type: STRING  
  Description: active, closed, suspended

* opened_at  
  Type: DATE  
  Description: Account open date

* closed_at  
  Type: DATE  
  Description: Nullable close date

* ingestion_date  
  Type: DATE  
  Description: Date record was ingested

**Notes**

* closed accounts may still receive late transactions  
* one customer can have multiple accounts  

---

## 3. transactions

**Purpose**  
Atomic financial events. This is the messy truth.

**Fields**

* transaction_id  
  Type: UUID  
  Description: Primary key

* account_id  
  Type: UUID  
  Description: Account reference

* customer_id  
  Type: UUID  
  Description: Customer reference

* amount  
  Type: DECIMAL  
  Description: Transaction amount

* currency  
  Type: STRING  
  Description: ISO currency code

* merchant_name  
  Type: STRING  
  Description: Merchant label

* status  
  Type: STRING  
  Description: success, failed, pending

* created_at  
  Type: TIMESTAMP  
  Description: Event creation time

* settled_at  
  Type: TIMESTAMP  
  Description: Nullable settlement time

* ingestion_date  
  Type: DATE  
  Description: Warehouse ingestion date

* card_last_four  
  Type: STRING  
  Description: PII

* device_id  
  Type: STRING  
  Description: Device identifier

**Notes**

* duplicate transactions are allowed  
* ingestion_date can be days after created_at  
* failed transactions never have settled_at  

---

## 4. payments

**Purpose**  
Represents attempts to settle transactions.

**Fields**

* payment_id  
  Type: UUID  
  Description: Primary key

* transaction_id  
  Type: UUID  
  Description: Related transaction

* payment_method  
  Type: STRING  
  Description: card, bank

* status  
  Type: STRING  
  Description: success, failed

* attempt_number  
  Type: INTEGER  
  Description: Retry count

* attempted_at  
  Type: TIMESTAMP  
  Description: Attempt timestamp

* ingestion_date  
  Type: DATE  
  Description: Warehouse ingestion date

**Notes**

* one transaction can have multiple payment attempts  
* failed payments may later succeed  

---

## 5. subscriptions

**Purpose**  
Tracks recurring billing relationships.

**Fields**

* subscription_id  
  Type: UUID  
  Description: Primary key

* customer_id  
  Type: UUID  
  Description: Customer reference

* plan_name  
  Type: STRING  
  Description: basic, pro, enterprise

* status  
  Type: STRING  
  Description: active, paused, canceled

* start_date  
  Type: DATE  
  Description: Subscription start

* end_date  
  Type: DATE  
  Description: Nullable end date

* ingestion_date  
  Type: DATE  
  Description: Warehouse ingestion date

**Notes**

* upgrades and downgrades create multiple rows  
* overlapping subscriptions are allowed  

---

## 6. refunds

**Purpose**  
Represents refunds issued for prior transactions.

**Fields**

* refund_id  
  Type: UUID  
  Description: Primary key

* transaction_id  
  Type: UUID  
  Description: Related transaction

* amount  
  Type: DECIMAL  
  Description: Refund amount

* refund_reason  
  Type: STRING  
  Description: Reason code or description

* refunded_at  
  Type: DATE  
  Description: Refund date

* ingestion_date  
  Type: DATE  
  Description: Warehouse ingestion date

**Notes**

* refunds often occur days after the original transaction  
* partial refunds are allowed  
* duplicate refunds are possible  

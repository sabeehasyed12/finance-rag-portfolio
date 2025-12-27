# Data Generation Rules

## Global Rules

* All IDs are UUIDs
* ingestion_date is independent of event time
* Late arriving data is expected and common
* Duplicates are allowed in raw data
* All timestamps are in UTC
* Row order is not guaranteed

## Customers

* Each customer has one primary identity
* PII fields are intentionally included for masking demos
* Multiple customers may share:
  * address
  * device_id
* Email addresses may vary by:
  * dots
  * plus addressing
* created_at represents signup time
* ingestion_date may lag created_at by 0 to 3 days

## Accounts

* Each customer can have 1 to 3 accounts
* Account types include:
  * checking
  * savings
  * credit
* Account status transitions are not always clean
* Closed accounts may still:
  * receive late transactions
  * receive refunds
* ingestion_date may lag opened_at by 0 to 2 days

## Transactions

* Transactions are generated per account
* Daily transaction volume varies by account type
* Amount distribution:
  * many small transactions
  * few large transactions
* Supported statuses:
  * success
  * failed
  * pending
* Failed transactions:
  * never have settled_at
* Pending transactions:
  * may later succeed or fail
* Duplicate transactions:
  * 1 to 3 percent of rows
  * duplicates share all fields except ingestion_date
* ingestion_date may lag created_at by 0 to 5 days

## Payments

* Payments attempt to settle transactions
* One transaction may have multiple payment attempts
* attempt_number increments sequentially
* Failed payments:
  * may retry
  * may never succeed
* Successful payment:
  * ends retry chain
* ingestion_date may lag attempted_at by 0 to 2 days

## Subscriptions

* Subscriptions represent recurring billing
* Plans include:
  * basic
  * pro
  * enterprise
* Customers may:
  * upgrade
  * downgrade
  * cancel
  * pause
* Plan changes create new rows
* Overlapping subscription periods are allowed
* ingestion_date may lag start_date by 0 to 2 days

## Refunds

* Refunds always reference a prior transaction
* Refund amount may be:
  * full
  * partial
* Refunds occur 2 to 14 days after original transaction
* Duplicate refunds are possible
* ingestion_date may lag refunded_at by 0 to 3 days

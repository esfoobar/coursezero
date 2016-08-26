from mongoengine import CASCADE

from application import db
from user.models import User

PERCENT = 1
AMOUNT = 2

DISCOUNT_TYPE = (
    (PERCENT, 'Percent'),
    (AMOUNT, 'Amount'),
)

class Coupon(db.Document):
    title = db.StringField(db_field="t")
    description = db.StringField(db_field="d")
    discount_type = db.IntField(db_field="dt", choices=DISCOUNT_TYPE)
    discount_quantity = db.IntField(db_field="dq")
    expires = db.DateTimeField(db_field="e", default=None)
    live = db.BooleanField(db_field="l", default=True)

class Transaction(db.Document):
    user = db.ReferenceField(User, db_field="u", reverse_delete_rule=CASCADE)
    payment_id = db.StringField(db_field="pi") # whatever id I get from BT
    coupon = db.ReferenceField(Coupon, db_field="c")
    price_dollars = db.IntField(db_field="pd")
    price_cents = db.IntField(db_field="pc")
    transaction_date = db.DateTimeField(db_field="td", default=None)

MONTHLY = 1
YEARLY = 2

SUBSCRIPTION_PLAN_TYPE = (
    (MONTHLY, 'Monthly'),
    (YEARLY, 'Yearly'),
)

class SubscriptionPlans(db.Document):
    title = db.StringField(db_field="t")
    length_type = db.IntField(db_field="lt", choices=SUBSCRIPTION_PLAN_TYPE)
    price = db.IntField(db_field="p")
    expires = db.DateTimeField(db_field="e", default=None)
    live = db.BooleanField(db_field="l", default=True)

class Subscription(db.Document):
    title = db.StringField(db_field="t")
    length_type = db.IntField(db_field="lt", choices=SUBSCRIPTION_PLAN_TYPE)
    price = db.IntField(db_field="p")
    expires = db.DateTimeField(db_field="e", default=None)
    live = db.BooleanField(db_field="l", default=True)

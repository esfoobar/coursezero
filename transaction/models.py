from application import db
from user.models import User

class Transaction(db.Document):
    payment_id = db.StringField(db_field="pi") # whatever id I get from BT
    coupon = db.ReferenceField(Coupon, db_field="c")

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

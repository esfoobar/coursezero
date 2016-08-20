
from application import db
from user.models import User
from transaction.models import Transaction

class Track(db.Document):
    course_list = db.ListField(db_field="cl") # objects with course id and position

class Course(db.Document):
    title = db.StringField(db_field="t")
    subtitle = db.StringField(db_field="st")
    categories = db.StringField(db_field="c")
    summary = db.StringField(db_field="s")
    price_dollars = db.IntField(db_field="pd")
    price_cents = db.IntField(db_field="pc")
    goals = db.StringField(db_field="d")
    requirements = db.StringField(db_field="r")
    image = db.StringField(db_field="i", default=None)
    live = db.BooleanField(db_field="l", default=True)

    def imgsrc(self, image_ts, size):
        if AWS_BUCKET:
            return os.path.join(AWS_CONTENT_URL, AWS_BUCKET, 'courses', '%s.%s.%s.png' % (self.id, image_ts, size))
        else:
            return url_for('static', filename=os.path.join(STATIC_IMAGE_URL, 'courses', '%s.%s.%s.png' % (self.id, image_ts, size)))

class Lesson(db.Document):
    course = db.ReferenceField(Course, db_field="c", reverse_delete_rule=CASCADE)
    title = db.StringField(db_field="t")
    summary = db.StringField(db_field="s")
    preview_enabled = db.BooleanField(db_field="pe", default=False)
    video_file_path = db.StringField(db_field="v")

class Enrollment(db.Document):
    course = db.ReferenceField(Course, db_field="c", reverse_delete_rule=CASCADE)
    user = db.ReferenceField(User, db_field="u", reverse_delete_rule=CASCADE)
    coupon_code = db.StringField(db_field="cc")
    transaction = db.ReferenceField(Transaction, db_field="t")

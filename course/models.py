from mongoengine import CASCADE

from application import db
from user.models import User
from transaction.models import Transaction, Subscription

class Track(db.Document):
    title = db.StringField(db_field="t")
    subtitle = db.StringField(db_field="st")
    course_list = db.ListField(db_field="cl") # objects with course id and position
    image = db.StringField(db_field="i", default=None)
    live = db.BooleanField(db_field="l", default=True)

class Course(db.Document):
    track = db.ReferenceField(Track, db_field="tr", reverse_delete_rule=CASCADE)
    title = db.StringField(db_field="t")
    slug = db.StringField(db_field="sl", unique=True)
    subtitle = db.StringField(db_field="st")
    section_list = db.ListField(db_field="cl") # objects with section id and position
    categories = db.StringField(db_field="c")
    summary = db.StringField(db_field="s")
    goals = db.StringField(db_field="d")
    prereqs = db.ListField(db_field="r")
    price = db.IntField(db_field="pd")
    image = db.StringField(db_field="i", default=None)
    live = db.BooleanField(db_field="l", default=True)

    def imgsrc(self, image_ts, size):
        if AWS_BUCKET:
            return os.path.join(AWS_CONTENT_URL, AWS_BUCKET, 'courses', '%s.%s.%s.png' % (self.id, image_ts, size))
        else:
            return url_for('static', filename=os.path.join(STATIC_IMAGE_URL, 'courses', '%s.%s.%s.png' % (self.id, image_ts, size)))

class Category(db.Document):
    title = db.StringField(db_field="t")

class Section(db.Document):
    course = db.ReferenceField(Course, db_field="c", reverse_delete_rule=CASCADE)
    title = db.StringField(db_field="t")
    subtitle = db.StringField(db_field="st")
    lesson_list = db.ListField(db_field="cl") # objects with lesson id and position
    live = db.BooleanField(db_field="l", default=True)

class Lesson(db.Document):
    course = db.ReferenceField(Course, db_field="c", reverse_delete_rule=CASCADE)
    section = db.ReferenceField(Section, db_field="s", reverse_delete_rule=CASCADE)
    title = db.StringField(db_field="t")
    summary = db.StringField(db_field="sm")
    preview_enabled = db.BooleanField(db_field="pe", default=False)
    video_file_path = db.StringField(db_field="v")

class Enrollment(db.Document):
    course = db.ReferenceField(Course, db_field="c", reverse_delete_rule=CASCADE)
    user = db.ReferenceField(User, db_field="u", reverse_delete_rule=CASCADE)
    coupon_code = db.StringField(db_field="cc")
    transaction = db.ReferenceField(Transaction, db_field="t")
    subscription = db.ReferenceField(Subscription, db_field="s")
    live = db.BooleanField(db_field="l", default=True)

class Progress(db.Document):
    course = db.ReferenceField(Course, db_field="c", reverse_delete_rule=CASCADE)
    user = db.ReferenceField(User, db_field="u", reverse_delete_rule=CASCADE)
    lesson = db.ReferenceField(Lesson, db_field="l", reverse_delete_rule=CASCADE)
    started = db.DateTimeField(db_field="s")

from flask_wtf import Form
from wtforms import validators, StringField, IntegerField, BooleanField, SelectMultipleField
from wtforms.widgets import TextArea
from flask_wtf.file import FileField, FileAllowed

from course.models import Course

prereq_courses = []
for item in Course.objects.only('id', 'title').filter(live=True):
    prereq_courses.append((str(item['id']), item['title']))

class CourseForm(Form):
    title = StringField('Title', [validators.DataRequired()])
    slug = StringField('Slug', [validators.DataRequired()])
    subtitle = StringField('Subtitle', [validators.DataRequired()])
    summary = StringField('Summary',
            widget=TextArea(),
            validators=[validators.Length(max=2048)]
        )
    goals = StringField('Goals',
            widget=TextArea(),
            validators=[validators.Length(max=2048)]
        )
    prereqs = SelectMultipleField('Required Courses',
            choices=prereq_courses
        )
    price = IntegerField('Price', [validators.DataRequired()])
    live = BooleanField('Live')
    image = FileField('Course image (2048x1172)', validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only JPEG, PNG and GIFs allowed')
        ])

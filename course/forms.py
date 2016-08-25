from flask_wtf import Form
from wtforms import validators, StringField
from wtforms.widgets import TextArea

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
    requirements = StringField('Requirements',
            widget=TextArea(),
            validators=[validators.Length(max=2048)]
        )
    price = StringField('Price', [validators.DataRequired()])

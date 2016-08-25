from flask import Blueprint, render_template

from user.decorators import admin_required
from course.forms import CourseForm

course_app = Blueprint('course_app', __name__)

@course_app.route('/courses')
@admin_required
def home():
    return "Courses Home"

@course_app.route('/admin/courses', methods=('GET', 'POST'))
@admin_required
def admin():
    mkd = "```markdown```"
    return render_template('course/admin.html', mkd=mkd)

@course_app.route('/admin/courses/new', methods=('GET', 'POST'))
@admin_required
def admin_new():
    form = CourseForm()
    # form = EditForm(obj=user)
    return render_template('course/admin_new.html', form=form)

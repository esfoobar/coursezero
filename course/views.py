from flask import Blueprint, render_template

from user.decorators import admin_required

course_app = Blueprint('course_app', __name__)

@course_app.route('/courses')
@admin_required
def courses_home():
    return "Courses Home"

@course_app.route('/admin/courses', methods=('GET', 'POST'))
@admin_required
def courses_admin():
    return render_template('course/admin.html')

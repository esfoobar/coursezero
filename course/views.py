from flask import Blueprint, render_template, request
from werkzeug import secure_filename
import os

from user.decorators import admin_required
from course.models import Course
from course.forms import CourseForm
from utilities.imaging import thumbnail_process
from settings import UPLOAD_FOLDER

course_app = Blueprint('course_app', __name__)

@course_app.route('/courses')
@admin_required
def home():
    # make courses thumbs 350px wide
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
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            subtitle=form.subtitle.data,
            slug=form.slug.data,
            summary=form.summary.data,
            goals=form.goals.data,
            prereqs=form.prereqs.data,
            price=form.price.data,
            live=form.live.data
        ).save()

        if course.id:
            image_ts = None
            if request.files.get('image'):
                filename = secure_filename(form.image.data.filename)
                file_path = os.path.join(UPLOAD_FOLDER, 'videos', filename)
                form.image.data.save(file_path)
                image_ts = str(thumbnail_process(
                    file_path,
                    'videos',
                    str(course.id),
                    sizes=[("sm", 200), ("lg", 300), ("xlg", 400)],
                    square=False
                ))
            if image_ts:
                course.image = image_ts
                course.save()
    return render_template('course/admin_new.html', form=form)

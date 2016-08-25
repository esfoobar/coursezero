from flask import Blueprint, render_template, request, redirect, session, url_for, abort
import bcrypt
import uuid
import os
from werkzeug import secure_filename
from mongoengine import Q
import bson

from user.models import User
from user.forms import RegisterForm, LoginForm, EditForm, ForgotForm, PasswordResetForm
from utilities.common import email
from settings import UPLOAD_FOLDER
from utilities.imaging import thumbnail_process
from relationship.models import Relationship
from user.decorators import login_required
from feed.forms import FeedPostForm
from feed.models import Message, POST

user_app = Blueprint('user_app', __name__)

@user_app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    error = None

    if request.method == 'GET' and request.args.get('next'):
        session['next'] = request.args.get('next', None)

    if form.validate_on_submit():
        user = User.objects.filter(
            email=form.email.data,
            ).first()
        if user:
            if bcrypt.hashpw(form.password.data, user.password) == user.password:
                session['id'] = str(user.id)
                session['first_name'] = user.first_name
                session['is_admin'] = user.is_admin
                if 'next' in session:
                    next = session.get('next')
                    session.pop('next')
                    return redirect(next)
                else:
                    return redirect(url_for('home_app.home'))
            else:
                user = None
        if not user:
            error = "Incorrect credentials"
    return render_template('user/login.html', form=form, error=error)

@user_app.route('/join', methods=('GET', 'POST'))
def join():
    form = RegisterForm()
    if form.validate_on_submit():
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(form.password.data, salt)
        code = str(uuid.uuid4())
        user = User(
            email=form.email.data,
            password=hashed_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            change_configuration={
                "new_email": form.email.data,
                "confirmation_code": code
                }
        )
        user.save()

        if user:
            # email the user
            body_html = render_template('mail/user/register.html', user=user)
            body_text = render_template('mail/user/register.txt', user=user)
            email(user.email, "Welcome to Flaskbook", body_html, body_text)

        return redirect(url_for('user_app.login'))
    return render_template('user/join.html', form=form)

@user_app.route('/logout')
def logout():
    session.pop('id')
    session.pop('first_name')
    session.pop('is_admin')
    return redirect(url_for('user_app.login'))

@user_app.route('/<id>/friends/<int:friends_page>', endpoint='profile-friends-page')
@user_app.route('/<id>/friends', endpoint='profile-friends')
@user_app.route('/<id>')
def profile(id, page=1):
    # is id a valid ObjectId
    if not bson.objectid.ObjectId.is_valid(id):
        abort(404)

    logged_user = None
    rel = None
    friends_page = False
    user = User.objects.filter(id=id).first()
    profile_messages = []

    if user:
        if session.get('id'):
            logged_user = User.objects.filter(
                id=session.get('id')
                ).first()
            rel = Relationship.get_relationship(logged_user, user)

        # get friends
        friends = Relationship.objects.filter(
            from_user=user,
            rel_type=Relationship.FRIENDS,
            status=Relationship.APPROVED
            )
        friends_total = friends.count()

        if 'friends' in request.url:
            friends_page = True
            friends = friends.paginate(page=friends_page, per_page=8)
        else:
            friends = friends[:5]

        form = FeedPostForm()

        # get user messages if friends
        if logged_user and (rel == "SAME" or rel == "FRIENDS_APPROVED"):
            profile_messages = Message.objects.filter(
                Q(from_user=user) | Q(to_user=user),
                message_type=POST,
                ).order_by('-create_date')[:10]

        return render_template('user/profile.html',
            user=user,
            logged_user=logged_user,
            rel=rel,
            friends=friends,
            friends_total=friends_total,
            friends_page=friends_page,
            form=form,
            profile_messages=profile_messages
            )
    else:
        abort(404)

@user_app.route('/edit', methods=('GET', 'POST'))
@login_required
def edit():
    error = None
    message = None
    user = User.objects.filter(id=session.get('id')).first()
    if user:
        form = EditForm(obj=user)

        if form.validate_on_submit():
            # check if image
            image_ts = None
            if request.files.get('image'):
                filename = secure_filename(form.image.data.filename)
                file_path = os.path.join(UPLOAD_FOLDER, 'user', filename)
                form.image.data.save(file_path)
                image_ts = str(thumbnail_process(file_path, 'user', str(user.id)))

            # check if new email
            if user.email != form.email.data.lower():
                if User.objects.filter(email=form.email.data.lower()).first():
                    error = 'Email already exists'
                else:
                    code = str(uuid.uuid4())
                    user.change_configuration = {
                        "new_email": form.email.data.lower(),
                        "confirmation_code": code
                        }
                    user.email_confirmed = False
                    form.email.data = user.email
                    message = "You will need to confirm the new email to complete this change"

                    # email the user
                    body_html = render_template('mail/user/change_email.html', user=user)
                    body_text = render_template('mail/user/change_email.txt', user=user)
                    email(user.change_configuration['new_email'], "Confirm your new email", body_html, body_text)

            if not error:
                form.populate_obj(user)
                if image_ts:
                    user.profile_image = image_ts
                user.save()
                if not message:
                    message = "Profile updated"
        return render_template('user/edit.html', form=form, error=error, message=message, user=user)
    else:
        abort(404)

@user_app.route('/confirm/<id>/<code>')
def confirm(id, code):
    edit_profile = False
    user = User.objects.filter(id=id).first()
    if user and user.change_configuration and user.change_configuration.get('confirmation_code'):
        if code == user.change_configuration.get('confirmation_code'):
            user.email = user.change_configuration.get('new_email')
            user.change_configuration = {}
            user.email_confirmed = True
            user.save()
            return render_template('user/email_confirmed.html')
    abort(404)

@user_app.route('/forgot', methods=('GET', 'POST'))
def forgot():
    error = None
    message = None
    form = ForgotForm()
    if form.validate_on_submit():
        user = User.objects.filter(email=form.email.data).first()
        if user:
            code = str(uuid.uuid4())
            user.change_configuration={
                "password_reset_code": code
            }
            user.save()
            # email the user
            body_html = render_template('mail/user/password_reset.html', user=user)
            body_text = render_template('mail/user/password_reset.txt', user=user)
            email(user.email, "Password reset request", body_html, body_text)

        message = "You will receive a password reset email if we find that email in our system"
    return render_template('user/forgot.html', form=form, error=error, message=message)

@user_app.route('/password_reset/<id>/<code>', methods=('GET','POST'))
def password_reset(id, code):
    require_current = False

    form = PasswordResetForm()

    user = User.objects.filter(id=id).first()
    if not user or code != user.change_configuration.get('password_reset_code'):
        abort(404)

    if request.method == 'POST':
        del form.current_password
        if form.validate_on_submit():
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(form.password.data, salt)
            user.password = hashed_password
            user.change_configuration = {}
            user.save()
            # if user is logged in, log him out
            if session.get('id'):
                session.pop('id')
                session.pop('first_name')
                session.pop('is_admin')
            return redirect(url_for('user_app.password_reset_complete'))

    return render_template('user/password_reset.html',
        form=form,
        require_current=require_current,
        username=username,
        code=code
        )

@user_app.route('/password_reset_complete')
def password_reset_complete():
    return render_template('user/password_change_confirmed.html')

@user_app.route('/change_password', methods=('GET','POST'))
def change_password():
    require_current = True
    error = None
    form = PasswordResetForm()

    user = User.objects.filter(id=session.get('id')).first()
    if not user:
        abort(404)

    if request.method == 'POST':
        if form.validate_on_submit():
            if bcrypt.hashpw(form.current_password.data, user.password) == user.password:
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(form.password.data, salt)
                user.password = hashed_password
                user.save()
                # if user is logged in, log him out
                if session.get('id'):
                    session.pop('id')
                    session.pop('first_name')
                    session.pop('is_admin')
                return redirect(url_for('user_app.password_reset_complete'))
            else:
                error = "Incorrect password"

    return render_template('user/password_reset.html',
        form=form,
        require_current=require_current,
        error=error
        )

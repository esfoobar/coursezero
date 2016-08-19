from flask import Blueprint, abort, session, redirect, url_for, request, render_template

from user.models import User
from relationship.models import Relationship
from user.decorators import login_required
from utilities.common import email

relationship_app = Blueprint('relationship_app', __name__)

@relationship_app.route('/add_friend/<id>')
@login_required
def add_friend(id):
    ref = request.referrer
    logged_user = User.objects.filter(id=session.get('id')).first()
    to_user = User.objects.filter(id=id).first()
    if to_user:
        rel = Relationship.get_relationship(logged_user, to_user)
        if rel == "REVERSE_FRIENDS_PENDING":
            # Check if there's a pending invitation to_user -> from_user
            # so then we confirm the friendship
            Relationship(
                from_user=logged_user,
                to_user=to_user,
                rel_type=Relationship.FRIENDS,
                status=Relationship.APPROVED
                ).save()
            reverse_rel = Relationship.objects.get(
                from_user=to_user,
                to_user=logged_user)
            reverse_rel.status=Relationship.APPROVED
            reverse_rel.save()

        elif rel == None and rel != "REVERSE_BLOCKED":
            # Otherwise, just do the initial request
            Relationship(
                from_user=logged_user,
                to_user=to_user,
                rel_type=Relationship.FRIENDS,
                status=Relationship.PENDING
                ).save()

            # email the user
            body_html = render_template('mail/relationship/added_friend.html', from_user=logged_user, to_user=to_user)
            body_text = render_template('mail/relationship/added_friend.txt', from_user=logged_user, to_user=to_user)
            email(to_user.email, ("%s has requested to be friends") % logged_user.first_name, body_html, body_text)
        if ref:
            return redirect(ref)
        else:
            return redirect(url_for('user_app.profile', id=to_user.id))
    else:
        abort(404)

@relationship_app.route('/remove_friend/<id>')
@login_required
def remove_friend(id):
    ref = request.referrer
    logged_user = User.objects.filter(id=session.get('id')).first()
    to_user = User.objects.filter(id=id).first()
    if to_user:
        rel = Relationship.get_relationship(logged_user, to_user)
        if rel == "FRIENDS_PENDING" or rel == "FRIENDS_APPROVED" or rel == "REVERSE_FRIENDS_PENDING":
            rel = Relationship.objects.filter(
                from_user=logged_user,
                to_user=to_user).delete()
            reverse_rel = Relationship.objects.filter(
                from_user=to_user,
                to_user=logged_user).delete()
        if ref:
            return redirect(ref)
        else:
            return redirect(url_for('user_app.profile', id=to_user.id))
    else:
        abort(404)

@relationship_app.route('/block/<id>')
@login_required
def block(id):
    ref = request.referrer
    logged_user = User.objects.filter(id=session.get('id')).first()
    to_user = User.objects.filter(id=id).first()
    if to_user:
        rel = Relationship.get_relationship(logged_user, to_user)
        if rel == "FRIENDS_PENDING" or rel == "FRIENDS_APPROVED" or rel == "REVERSE_FRIENDS_PENDING":
            rel = Relationship.objects.filter(
                from_user=logged_user,
                to_user=to_user).delete()
            reverse_rel = Relationship.objects.filter(
                from_user=to_user,
                to_user=logged_user).delete()
        Relationship(
            from_user=logged_user,
            to_user=to_user,
            rel_type=Relationship.BLOCKED,
            status=Relationship.APPROVED
            ).save()
        if ref:
            return redirect(ref)
        else:
            return redirect(url_for('user_app.profile', id=to_user.id))
    else:
        abort(404)

@relationship_app.route('/unblock/<id>')
@login_required
def unblock(id):
    ref = request.referrer
    logged_user = User.objects.filter(id=session.get('id')).first()
    to_user = User.objects.filter(id=id).first()
    if to_user:
        rel = Relationship.get_relationship(logged_user, to_user)
        if rel == "BLOCKED":
            rel = Relationship.objects.filter(
                from_user=logged_user,
                to_user=to_user).delete()
        if ref:
            return redirect(ref)
        else:
            return redirect(url_for('user_app.profile', id=to_user.id))
    else:
        abort(404)

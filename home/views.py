from flask import Blueprint, session, render_template

from user.models import User
from feed.models import Feed
from feed.forms import FeedPostForm
from utilities.imaging import get_signed_url

home_app = Blueprint('home_app', __name__)

@home_app.route('/')
def home():
    home_video_url = get_signed_url('home/the_from_zero_approach.mp4', 5)
    return render_template('home/home.html', home_video_url=home_video_url)

@home_app.route('/about')
def about():
    return render_template('home/about.html')

from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
from flask import session

from user.models import User
from relationship.models import Relationship
from settings import MONGODB_HOST

class FeedTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'flaskbook_test'
        return create_app_base(
            MONGODB_SETTINGS={'DB': self.db_name,
                'HOST': MONGODB_HOST},
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY = 'mySecret!',
        )

    def setUp(self):
        self.app_factory = self.create_app()
        self.app = self.app_factory.test_client()

    def tearDown(self):
        db = _get_db()
        db.client.drop_database(db)

    def user1_dict(self):
        return dict(
                first_name="Jorge",
                last_name="Escobar",
                email="jorge@example.com",
                password="test123",
                confirm="test123"
                )

    def user2_dict(self):
        return dict(
                first_name="Javier",
                last_name="Escobar",
                email="javier@example.com",
                password="test123",
                confirm="test123"
                )

    def user3_dict(self):
        return dict(
                first_name="Luis",
                last_name="Escobar",
                email="luiti@example.com",
                password="test123",
                confirm="test123"
                )

    def test_feed_posts(self):
        # register user
        rv = self.app.post('/join', data=self.user1_dict(),
            follow_redirects=True)

        # login the first user
        rv = self.app.post('/login', data=dict(
            email=self.user1_dict()['email'],
            password=self.user1_dict()['password']
            ))

        # get user
        self.db_user1 = User.objects.get(email=self.user1_dict()['email'])

        # post a message
        rv = self.app.post('/message/add', data=dict(
            post="Test Post #1 User 1",
            to_user=str(self.db_user1.id),
            ), follow_redirects=True)
        assert "Test Post #1 User 1" in str(rv.data)

        # register user 2
        rv = self.app.post('/join', data=self.user2_dict(),
            follow_redirects=True)

        # get user
        self.db_user2 = User.objects.get(email=self.user2_dict()['email'])

        # make friends with user2
        rv = self.app.get('/add_friend/' + str(self.db_user2.id),
            follow_redirects=True)

        # login user 2 and confirm friend user 1
        rv = self.app.post('/login', data=dict(
            email=self.user2_dict()['email'],
            password=self.user2_dict()['password']
            ))
        rv = self.app.get('/add_friend/' + str(self.db_user1.id),
            follow_redirects=True)

        # login the first user again
        rv = self.app.post('/login', data=dict(
            email=self.user1_dict()['email'],
            password=self.user1_dict()['password']
            ))

        # post a message
        rv = self.app.post('/message/add', data=dict(
            post="Test Post #2 User 1",
            to_user=str(self.db_user1.id),
            ), follow_redirects=True)
        assert "Test Post #2 User 1" in str(rv.data)

        # post a message to user 2
        rv = self.app.post('/message/add', data=dict(
            post="Test Post User 1 to User 2",
            to_user=str(self.db_user1.id),
            ), follow_redirects=True)

        # login the second user
        # check that the two messages are on the second user's home
        self.app.post('/login', data=dict(
            email=self.user2_dict()['email'],
            password=self.user2_dict()['password']
            ))
        rv = self.app.get('/')
        assert "Test Post #2 User 1" in str(rv.data)
        assert "Test Post User 1 to User 2" in str(rv.data)

        # register user 3
        rv = self.app.post('/join', data=self.user3_dict(),
            follow_redirects=True)

        # get user
        self.db_user3 = User.objects.get(email=self.user3_dict()['email'])

        # make friends with user3
        rv = self.app.get('/add_friend/' + str(self.db_user2.id),
            follow_redirects=True)

        # login the first user
        rv = self.app.post('/login', data=dict(
            email=self.user1_dict()['email'],
            password=self.user1_dict()['password']
            ))

        # block user 3
        rv = self.app.get('/block/' + str(self.db_user3.id),
            follow_redirects=True)

        # login the second user
        rv = self.app.post('/login', data=dict(
            email=self.user2_dict()['email'],
            password=self.user2_dict()['password']
            ))

        # user 2 confirm friend user 3
        rv = self.app.get('/add_friend/' + str(self.db_user3.id),
            follow_redirects=True)

        # post a message to user 3
        rv = self.app.post('/message/add', data=dict(
            post="Test Post User 2 to User 3",
            to_user=str(self.db_user3.id),
            ), follow_redirects=True)


        # login the first user
        rv = self.app.post('/login', data=dict(
            email=self.user1_dict()['email'],
            password=self.user1_dict()['password']
            ))

        # check he doesn't see user 2's post to user 3 (blocked)
        rv = self.app.get('/')
        assert "Test Post User 2 to User 3" not in str(rv.data)

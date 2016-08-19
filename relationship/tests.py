from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
from flask import session

from user.models import User
from relationship.models import Relationship
from settings import MONGODB_HOST

class RelationshipTest(unittest.TestCase):
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

    def test_friends_operations(self):
        # register users
        rv = self.app.post('/join', data=self.user1_dict(),
            follow_redirects=True)
        assert User.objects.filter(email=self.user1_dict()['email']).count() == 1
        rv = self.app.post('/join', data=self.user2_dict(),
            follow_redirects=True)
        assert User.objects.filter(email=self.user2_dict()['email']).count() == 1

        # get users
        self.db_user1 = User.objects.get(email=self.user1_dict()['email'])
        self.db_user2 = User.objects.get(email=self.user2_dict()['email'])

        # login the first user
        rv = self.app.post('/login', data=dict(
            email=self.user1_dict()['email'],
            password=self.user1_dict()['password']
            ))

        # add second user as a friend
        rv = self.app.get('/add_friend/' + str(self.db_user2.id),
            follow_redirects=True)
        assert "relationship-friends-requested" in str(rv.data)

        # check that only one records exists at this point
        relcount = Relationship.objects.count()
        assert relcount == 1

        # login the second user
        rv = self.app.post('/login', data=dict(
            email=self.user2_dict()['email'],
            password=self.user2_dict()['password']
            ))

        # check the friend request is pending
        rv = self.app.get('/' + str(self.db_user1.id))
        assert "relationship-reverse-friends-requested" in str(rv.data)

        # confirm first user as a friend
        rv = self.app.get('/add_friend/' + str(self.db_user1.id),
            follow_redirects=True)
        assert "relationship-friends" in str(rv.data)

        # check that two records exists at this point
        relcount = Relationship.objects.count()
        assert relcount == 2

        # user2 now unfriends user1
        rv = self.app.get('/remove_friend/' + str(self.db_user1.id),
            follow_redirects=True)
        assert "relationship-add-friend" in str(rv.data)

        # check that no records exists at this point
        relcount = Relationship.objects.count()
        assert relcount == 0

        # login the first user
        rv = self.app.post('/login', data=dict(
            email=self.user1_dict()['email'],
            password=self.user1_dict()['password']
            ))

        # check no longer friends
        rv = self.app.get('/' + str(self.db_user2.id))
        assert "relationship-add-friend" in str(rv.data)

    def test_block_operations(self):
        # register users
        rv = self.app.post('/join', data=self.user1_dict(),
            follow_redirects=True)
        assert User.objects.filter(email=self.user1_dict()['email']).count() == 1
        rv = self.app.post('/join', data=self.user2_dict(),
            follow_redirects=True)
        assert User.objects.filter(email=self.user2_dict()['email']).count() == 1

        # get users
        self.db_user1 = User.objects.get(email=self.user1_dict()['email'])
        self.db_user2 = User.objects.get(email=self.user2_dict()['email'])

        # login the first user
        rv = self.app.post('/login', data=dict(
            email=self.user1_dict()['email'],
            password=self.user1_dict()['password']
            ))

        # user1 blocks the second user
        rv = self.app.get('/block/' + str(self.db_user2.id),
            follow_redirects=True)
        assert "relationship-blocked" in str(rv.data)

        # login the second user
        rv = self.app.post('/login', data=dict(
            email=self.user2_dict()['email'],
            password=self.user2_dict()['password']
            ))

        # check user1's profile reflects it's blocked
        rv = self.app.get('/' + str(self.db_user1.id))
        assert "relationship-reverse-blocked" in str(rv.data)

        # try to become friends with user1
        rv = self.app.get('/add_friend/' + str(self.db_user1.id),
            follow_redirects=True)
        assert "relationship-reverse-blocked" in str(rv.data)

        # user1 unblocks user2
        # login the first user
        rv = self.app.post('/login', data=dict(
            email=self.user1_dict()['email'],
            password=self.user1_dict()['password']
            ))

        # user1 blocks the second user
        rv = self.app.get('/unblock/' + str(self.db_user2.id),
            follow_redirects=True)
        assert "relationship-add-friend" in str(rv.data)

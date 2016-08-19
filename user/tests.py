from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
from flask import session

from user.models import User
from settings import MONGODB_HOST

class UserTest(unittest.TestCase):
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

    def user_dict(self):
        return dict(
                first_name="Jorge",
                last_name="Escobar",
                email="jorge@example.com",
                password="test123",
                confirm="test123"
                )

    def test_register_user(self):
        # basic registration
        rv = self.app.post('/register', data=self.user_dict(),
            follow_redirects=True)
        assert User.objects.filter(email=self.user_dict()['email']).count() == 1

        # confirm the user
        user = User.objects.get(email=self.user_dict()['email'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + str(user.id) + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)

        # try again to confirm
        rv = self.app.get('/confirm/' + str(user.id) + '/' + code)
        assert rv.status_code == 404

        # check change configuration is empty
        user = User.objects.get(email=self.user_dict()['email'])
        assert user.change_configuration == {}

    def test_login_user(self):
        # create a user
        self.app.post('/register', data=self.user_dict())
        # login the user
        rv = self.app.post('/login', data=dict(
            email=self.user_dict()['email'],
            password=self.user_dict()['password']
            ))
        # check the session is set
        with self.app as c:
            user = User.objects.get(email=self.user_dict()['email'])
            rv = c.get('/')
            assert session.get("id") == str(user.id)

    def test_edit_profile(self):
        # create a user
        self.app.post('/register', data=self.user_dict())

        # confirm the user
        user = User.objects.get(email=self.user_dict()['email'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + str(user.id) + '/' + code)

        # login the user
        rv = self.app.post('/login', data=dict(
            email=self.user_dict()['email'],
            password=self.user_dict()['password']
            ))

        # check that user has edit button on his own profile
        rv = self.app.get('/' + str(user.id))
        assert "Edit profile" in str(rv.data)

        # edit fields
        user = self.user_dict()
        user['first_name'] = "Test First"
        user['last_name'] = "Test Last"

        # edit the user
        rv = self.app.post('/edit', data=user)
        assert "Profile updated" in str(rv.data)
        edited_user = User.objects.first()
        assert edited_user.first_name == "Test First"
        assert edited_user.last_name == "Test Last"

        # check new email is in change configuration
        user['email'] = "test@example.com"
        rv = self.app.post('/edit', data=user)
        assert "You will need to confirm the new email to complete this change" in str(rv.data)

        db_user = User.objects.first()
        code = db_user.change_configuration.get('confirmation_code')
        new_email = db_user.change_configuration.get('new_email')
        assert new_email == user['email']

        # now confirm
        rv = self.app.get('/confirm/' + str(db_user.id) + '/' + code)
        db_user = User.objects.filter().first()
        assert db_user.email == user['email']
        assert db_user.change_configuration == {}

        # create a second user
        self.app.post('/register', data=self.user_dict())
        # login the user
        rv = self.app.post('/login', data=dict(
            email=self.user_dict()['email'],
            password=self.user_dict()['password']
            ))

        # try to save same email
        user = self.user_dict()
        user['email'] = "test@example.com"
        rv = self.app.post('/edit', data=user)
        assert "Email already exists" in str(rv.data)

    def test_get_profile(self):
        # create a user
        self.app.post('/register', data=self.user_dict())

        # get the user's profile
        db_user = User.objects.filter().first()
        rv = self.app.get('/' + str(db_user.id))
        assert self.user_dict()['first_name'] in str(rv.data)

    def test_forgot_password(self):
        # create a user
        self.app.post('/register', data=self.user_dict())

        # confirm the user
        user = User.objects.get(email=self.user_dict()['email'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + str(user.id) + '/' + code)

        # enter user forgot email
        rv = self.app.post('/forgot', data=dict(email=self.user_dict().get('email')))
        user = User.objects.first()
        password_reset_code = user.change_configuration.get('password_reset_code')
        assert password_reset_code is not None

        # try wrong password reset code
        rv = self.app.get('/password_reset/' + str(user.id) + '/bad-code')
        assert rv.status_code == 404

        # do right password reset code
        rv = self.app.post('/password_reset/' + str(user.id) + '/' + password_reset_code,
            data=dict(password='newpassword', confirm='newpassword'),
            follow_redirects=True)
        assert "Your password has been updated" in str(rv.data)
        user = User.objects.first()
        assert user.change_configuration == {}

        # try logging in with new password
        rv = self.app.post('/login', data=dict(
            email=self.user_dict()['email'],
            password='newpassword'
            ))
        # check the session is set
        with self.app as c:
            rv = c.get('/')
            assert session.get("id") == str(user.id)

    def test_change_password(self):
        # create a user
        self.app.post('/register', data=self.user_dict())

        # confirm the user
        user = User.objects.get(email=self.user_dict()['email'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + str(user.id) + '/' + code)

        # login the user
        rv = self.app.post('/login', data=dict(
            email=self.user_dict()['email'],
            password=self.user_dict()['password']
            ))

        # change the password
        rv = self.app.post('/change_password', data=dict(
            current_password=self.user_dict()['password'],
            password="newpassword",
            confirm="newpassword"),
            follow_redirects=True)
        assert "Your password has been updated" in str(rv.data)

        # try logging in with new password
        rv = self.app.post('/login', data=dict(
            email=self.user_dict()['email'],
            password='newpassword'
            ))
        # check the session is set
        with self.app as c:
            rv = c.get('/')
            assert session.get("id") == str(user.id)

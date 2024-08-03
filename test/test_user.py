import unittest
from models import Users, Organizations, UserSession
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import timedelta, datetime
from app_config import create_app, db


class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()

        db.create_all()

        # Setup initial data
        first_name = "John"
        organization_name = "test_org"
        organization_desc = "test_org_desc"
        last_name = "bush"
        username = "john_bush"
        email = "atmme1992@gmail.com"
        password = sha256.hash("Password@123")
        org = Organizations(
            name=organization_name,
            description=organization_desc
        )
        user = Users(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
            organization=org,
            email_verified=False
        )
        user_session = UserSession(otp="123456",
                                   otp_expiry=datetime.now() + timedelta(minutes=10), user=user)
        # db.session.add_all([org, user, user_session])
        db.session.add(org)
        db.session.add(user)
        db.session.add(user_session)
        db.session.commit()

    def tearDown(self):
        # db.session.remove()
        # db.drop_all()
        self.appctx.pop()
        self.app = None
        self.client = None

    def test_auser_reg(self):
        payload = {
            "first_name": "John",
            "last_name": "bush",
            "username": "john_bush2",
            "email": "atmme1993@gmail.com",
            "password": "Password@123",
            "organization_name": "test_org2",
            "organization_description": "test_org_desc2"
        }

        response = self.client.post('/api/v1/auth/register', json=payload)
        self.assertEqual(response.status_code, 201)
        user = Users.query.filter_by(email="atmme1993@gmail.com").first()
        self.assertEqual(user.email, payload["email"])

    def test_email_verify(self):
        payload = {
            "email": "atmme1992@gmail.com",
            "otp": "123456",
        }
        response = self.client.patch('/api/v1/auth/verify-email', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_login_user(self):
        payload = {
            "email": "atmme1992@gmail.com",
            "password": "Password@123"
        }
        user = Users.query.filter_by(email="atmme1992@gmail.com").first()
        user.email_verified = True
        db.session.commit()
        response = self.client.post('/api/v1/auth/login', json=payload)
        self.assertEqual(response.status_code, 200)

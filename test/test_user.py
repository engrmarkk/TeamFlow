import unittest
from models import Users, Organizations, UserSession
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import timedelta, datetime
from app_config import create_app, db

"""
You have to comment out any celery import (send_mail function) in the code before running the test
"""


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
        email = "john_bush@me.com"
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
        )
        user_session = UserSession(otp="123456",
                                   otp_expiry=datetime.now() + timedelta(minutes=10), user=user)
        db.session.add_all([org, user, user_session])
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
            "email": "john_bush2@me.com",
            "password": "Password@123",
            "organization_name": "test_org2",
            "organization_description": "test_org_desc2"
        }

        response = self.client.post('/api/v1/auth/register', json=payload)
        self.assertEqual(response.status_code, 201)
        user = Users.query.filter_by(email="john_bush2@me.com").first()
        self.assertEqual(user.email, payload["email"])

    def test_email_verify(self):
        payload = {
            "email": "john_bush@me.com",
            "otp": "123456",
        }
        response = self.client.patch('/api/v1/auth/verify-email', json=payload)
        self.assertEqual(response.status_code, 200)

        payload = {
            "email": "john_bush@me.com",
            "password": "Password@123"
        }
        response2 = self.client.post('/api/v1/auth/login', json=payload)
        print(response2, "login response")
        self.assertEqual(response2.status_code, 200)
        self.assertTrue(response2.json["access_token"].startswith("ey"))

    def test_login_user(self):
        payload = {
            "email": "john_bush@me.com",
            "password": "Password@123"
        }
        user = Users.query.filter_by(email="john_bush@me.com").first()
        user.email_verified = True
        db.session.commit()
        response = self.client.post('/api/v1/auth/login', json=payload)
        self.assertEqual(response.status_code, 200)

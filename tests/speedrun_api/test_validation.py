import json
import unittest

from pydantic_core._pydantic_core import ValidationError

from src.app.verified_runs.api.schemas import User

from tests.settings import settings


class TestUserSchema(unittest.TestCase):
    def test_valid_users(self):
        valid_users_path = settings.speedrun_api.validation.user.valid_users
        with open(valid_users_path) as valid_users_file:
            valid_users = json.load(valid_users_file)

        for user in valid_users:
            try:
                User(**user)
            except ValidationError:
                self.fail("Valid user raised a ValidationError!")

    def test_invalid_users(self):
        invalid_users_path = settings.speedrun_api.validation.user.invalid_users
        with open(invalid_users_path) as invalid_users_file:
            invalid_users = json.load(invalid_users_file)

        for user in invalid_users:
            with self.assertRaises(ValidationError):
                User(**user)

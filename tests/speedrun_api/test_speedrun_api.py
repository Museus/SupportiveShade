import datetime
import unittest
from string import Template

from pydantic_core._pydantic_core import ValidationError

from src.app.verified_runs.api.api import src_api
from tests.settings import settings


class TestSpeedrunApi(unittest.TestCase):
    def test_get_username(self):
        user_id = settings.speedrun_api.test_user.id
        user_name = src_api.get_user_name_from_id(user_id)

        self.assertEqual(user_name, "Museus")

    def test_get_latest_verified_run(self):
        game_id = settings.speedrun_api.test_game.id

        try:
            _ = src_api.get_latest_run(game_id)
        except ValidationError:
            self.fail("Parsing latest run raised a ValidationError!")
        except Exception:
            self.fail("Unknown error when getting latest verified run!")

    def test_get_runs_in_last_week(self):
        game_id = settings.speedrun_api.test_game.id
        since_timestamp = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(weeks=1)

        verify_date_template = Template("${verify_date}+00:00")

        try:
            for run in src_api.get_verified_runs(game_id, since=since_timestamp):
                run_verified_date = datetime.datetime.fromisoformat(
                    verify_date_template.substitute(verify_date=run.status.verify_date)
                )

                self.assertGreater(run_verified_date, since_timestamp)
        except ValidationError as exc:
            self.fail("Parsing a verified run raised a ValidationError:\n%s!" % exc)


if __name__ == "__main__":
    unittest.main()
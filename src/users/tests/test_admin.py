from test_plus.test import TestCase

from src.users.admin import MyUserCreationForm


class TestMyUserCreationForm(TestCase):
    def setUp(self):
        self.user = self.make_user("watermelon", "watermelon_password")

    def test_clean_username_success(self):
        form = MyUserCreationForm(
            {
                "username": "oak",
                "password1": "3@FY$GeWrVasH#@$JL",
                "password2": "3@FY$GeWrVasH#@$JL",
            }
        )
        # Run is_valid() to trigger the validation
        valid = form.is_valid()
        self.assertTrue(valid)

        # Run the actual clean_username method
        username = form.clean_username()
        self.assertEqual("oak", username)

    def test_clean_username_false(self):
        form = MyUserCreationForm(
            {
                "username": self.user.username,
                "password1": "watermelon_password",
                "password2": "watermelon_password",
            }
        )
        # Run is_valid() to trigger the validation, which is going to fail
        # because the username is already taken
        valid = form.is_valid()
        self.assertFalse(valid)

        # The form.errors dict should contain a single error called 'username'
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue("username" in form.errors)

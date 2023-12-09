default_app_config = 'account.apps.AccountsConfig'

class ACCOUNT:
    common_timezones = {
        'New York': 'America/New_York',
        "Los Angeles": "America/Los_Angeles",
        'London': 'Europe/London',
        'Paris': 'Europe/Paris',
    }
    TYPE_CHOICES = [
        ("partner", "Partner"),
        ("staff", "Staff"),
        ("user", "User")
    ]

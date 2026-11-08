
# StockTrack Login Authentication

USERNAME = "admin"
PASSWORD = "admin123"


def verify_login(username, password):
    if username == USERNAME and password == PASSWORD:
        return True

    return False

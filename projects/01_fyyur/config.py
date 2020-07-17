import os

# configurable 
database_url = 'postgresql://postgres:root@localhost:5432/fyyurapp'

# development configuration
class config(object):
    SECRET_KEY = os.urandom(32)
    # Enable debug mode.
    DEBUG = True
    # Connect to the database
    SQLALCHEMY_DATABASE_URI = database_url
    # Track modification
    SQLALCHEMY_TRACK_MODIFICATIONS = 'False'

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ma_cle_secrete_qui_devrait_etre_changee')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

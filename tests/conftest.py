from datetime import datetime

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from main.models import Client, Client_parking, Parking


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db = SQLAlchemy(app)

    with app.app_context():
        db.create_all()

        client = Client(
            name="John", surname="Doe", credit_card="1234567890", car_number="ABC123"
        )
        parking = Parking(
            address="Test Parking",
            opened=True,
            count_places=10,
            count_available_places=10,
        )
        time_in = datetime.now()
        time_out = datetime.now()
        client_parking = Client_parking(
            client_id=client.id,
            parking_id=parking.id,
            time_in=time_in,
            time_out=time_out,
        )

        db.session.add(client)
        db.session.add(parking)
        db.session.add(client_parking)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        db = SQLAlchemy(app)
        yield db

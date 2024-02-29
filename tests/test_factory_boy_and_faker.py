import factory
from faker import Faker
from main.models import Client, Parking

fake = Faker()


class ClientFactory(factory.Factory):
    class Meta:
        model = Client

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = factory.LazyFunction(
        lambda: fake.credit_card_number() if fake.boolean() else None
    )
    car_number = factory.Faker("text")


class ParkingFactory(factory.Factory):
    class Meta:
        model = Parking

    address = factory.Faker("address")
    opened = factory.Faker("boolean")
    count_places = factory.Faker("random_int")
    count_available_places = factory.LazyAttribute(lambda obj: obj.count_places)


def test_create_client_with_factory(client):
    client_data = ClientFactory.build()
    response = client.post("/clients", data=client_data.__dict__)
    assert response.status_code == 201

    created_client = Client.query.filter_by(
        name=client_data.name, surname=client_data.surname
    ).first()
    assert created_client is not None
    assert created_client.name == client_data.name
    assert created_client.surname == client_data.surname
    assert created_client.credit_card == client_data.credit_card
    assert created_client.car_number == client_data.car_number


def test_create_parking_with_factory(client):
    parking_data = ParkingFactory.build()
    response = client.post("/parkings", data=parking_data.__dict__)
    assert response.status_code == 201

    created_parking = Parking.query.filter_by(address=parking_data.address).first()
    assert created_parking is not None
    assert created_parking.address == parking_data.address
    assert created_parking.opened == parking_data.opened
    assert created_parking.count_places == parking_data.count_places
    assert created_parking.count_available_places == parking_data.count_available_places

import pytest
from module_29_testing.hw.main.models import Client, Client_parking, Parking


@pytest.mark.parametrize("endpoint", ["/clients", "/clients/1", "/parkings"])
def test_get_endpoints_return_200(client, endpoint):
    response = client.get(endpoint)
    assert response.status_code == 200


def test_create_client(client):
    data = {
        "name": "John",
        "surname": "Doe",
        "credit_card": "1234567890",
        "car_number": "ABC123",
    }
    response = client.post("/clients", data=data)
    assert response.status_code == 201


def test_create_parking(client):
    data = {
        "address": "Test Parking",
        "opened": True,
        "count_places": 10,
        "count_available_places": 10,
    }
    response = client.post("/parkings", data=data)
    assert response.status_code == 201


@pytest.mark.parking
def test_check_in(client):
    client_id = 1
    parking_id = 1
    initial_available_places = 10

    response = client.post(
        "/client_parkings", data={"client_id": client_id, "parking_id": parking_id}
    )
    assert response.status_code == 200

    client_parking = Client_parking.query.filter_by(
        client_id=client_id, parking_id=parking_id
    ).first()
    parking = Parking.query.get(parking_id)
    assert parking.count_available_places == initial_available_places - 1
    assert client_parking.time_in is not None


@pytest.mark.parking
def test_departure(client):
    client_id = 1
    parking_id = 1
    initial_available_places = 10

    response = client.delete(
        "/client_parkings", data={"client_id": client_id, "parking_id": parking_id}
    )
    assert response.status_code == 200

    client_parking = Client_parking.query.filter_by(
        client_id=client_id, parking_id=parking_id
    ).first()
    parking = Parking.query.get(parking_id)
    assert parking.count_available_places == initial_available_places
    assert client_parking.time_out is not None
    assert client_parking.time_out >= client_parking.time_in

    client = Client.query.get(client_id)
    assert client.credit_card is not None

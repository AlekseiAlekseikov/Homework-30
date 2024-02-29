from datetime import datetime
from typing import List

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    from .models import Client, Client_parking, Parking

    @app.before_request
    def before_request_func():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route("/clients", methods=["GET"])
    def get_clients_handler():
        """
            Получить список всех клиентов.

            Returns:
            JSON: Список клиентов.
        """
        clients: List[Client] = db.session.query(Client).all()
        clients_list = [u.to_json() for u in clients]
        return jsonify(clients_list), 200

    @app.route("/clients/<int:client_id>", methods=["GET"])
    def get_client_handler(client_id: int):
        """
        Получить информацию о конкретном клиенте.

        Args:
            client_id (int): Идентификатор клиента.

        Returns:
            JSON: Информация о клиенте.
        """
        client: Client = db.session.query(Client).get(client_id)
        return jsonify(client.to_json()), 200

    @app.route("/clients", methods=["POST"])
    def create_client_handler():
        """
        Создать нового клиента.

        Returns:
            str: Сообщение о создании нового клиента.
        """
        name = request.form.get("name", type=str)
        surname = request.form.get("surname", type=str)
        credit_card = request.form.get("credit_card", type=str)
        car_number = request.form.get("car_number", type=str)

        new_client = Client(
            name=name, surname=surname, credit_card=credit_card, car_number=car_number
        )

        db.session.add(new_client)
        db.session.commit()

        return "Новый клиент создан", 201

    @app.route("/parkings", methods=["POST"])
    def create_parking_handler():
        """
        Создать новую парковочную зону.

        Returns:
            str: Сообщение о создании новой парковочной зоны.
        """
        address = request.form.get("address", type=str)
        opened = request.form.get("opened", type=bool, default=True)
        count_places = request.form.get("count_places", type=int)
        count_available_places = request.form.get("count_available_places", type=int)

        new_parking = Parking(
            address=address,
            opened=opened,
            count_places=count_places,
            count_available_places=count_available_places,
        )

        db.session.add(new_parking)
        db.session.commit()

        return "Новая парковочная зона создана", 201

    @app.route("/client_parkings", methods=["POST"])
    def check_in():
        """
        Заезд на парковку.

        Returns:
            str: Сообщение о успешной регистрации заезда.
        """
        parking_id = request.form.get("parking_id", type=int)
        client_id = request.form.get("client_id", type=int)

        parking = db.session.query(Parking).get(parking_id)

        if parking:
            if parking.opened:
                if parking.count_available_places > 0:
                    parking.count_available_places -= 1

                    client_parking = Client_parking(
                        client_id=client_id, parking_id=parking_id
                    )
                    client_parking.time_in = datetime.now()

                    try:
                        db.session.add(client_parking)
                        db.session.commit()
                        return "Регистрация прошла успешно"
                    except Exception as e:
                        db.session.rollback()
                        return str(e), 500
                else:
                    return "Нет свободных мест для парковки", 400
            else:
                return "Парковка закрыта", 400
        else:
            return "Парковка не найдена", 404

    @app.route("/client_parkings", methods=["DELETE"])
    def departure():
        """
        Выезд с парковки.

        Returns:
            str: Сообщение о успешном выезде.
        """
        parking_id = request.form.get("parking_id", type=int)
        client_id = request.form.get("client_id", type=int)

        parking = db.session.query(Parking).get(parking_id)
        client = db.session.query(Client).get(client_id)

        if parking:
            if client.credit_card:
                client_parking = (
                    db.session.query(Client_parking)
                    .filter_by(client_id=client_id, parking_id=parking_id)
                    .first()
                )

                if client_parking:
                    parking.count_available_places += 1
                    client_parking.time_out = datetime.now()

                    try:
                        db.session.delete(client_parking)
                        db.session.commit()
                        return "Выезд прошёл успешно"
                    except Exception as e:
                        db.session.rollback()
                        return str(e), 500
                else:
                    return "Запись о парковке клиента не найдена", 404
            else:
                return "У клиента нет привязанной кредитной карты", 400
        else:
            return "Парковка не найдена", 404

    return app

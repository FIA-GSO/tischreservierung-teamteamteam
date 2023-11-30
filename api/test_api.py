import pytest
from api import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True

    # yield app.test_client()
    return app


@pytest.fixture
def reservierungen_data():
    return [
        [
            1,
            "2022-02-02 17:30:00",
            1,
            1331,
            "False"
        ],
        [
            2,
            "2022-02-02 18:30:00",
            1,
            1332,
            "False"
        ],
        [
            3,
            "2022-02-02 19:30:00",
            1,
            1333,
            "False"
        ],
        [
            4,
            "2022-02-02 18:30:00",
            3,
            1334,
            "True"
        ],
        [
            5,
            "2022-02-02 19:30:00",
            3,
            1335,
            "False"
        ],
        [
            6,
            "2022-02-02 20:30:00",
            3,
            1336,
            "False"
        ],
        [
            7,
            "2022-02-02 18:30:00",
            4,
            3002,
            "True"
        ],
        [
            8,
            "2022-02-02 18:30:00",
            4,
            9033,
            "True"
        ],
        [
            9,
            "2022-02-02 18:30:00",
            4,
            9087,
            "False"
        ],
        [
            10,
            "2023-02-02 18:15:00",
            1,
            1447,
            "False"
        ]
    ]


@pytest.fixture
def reservierungen_mit_datum_data():
    return [[2], [3], [4]]


@pytest.fixture
def reservieren_bereits_reserviert_data():
    return b"Error: Tisch ist bereits reserviert."


def test_reservierungen(app, reservierungen_data):
    with app.app_context():
        route = "/v1/reservierungen"

        response = app.test_client().get(route)

        assert response.status_code == 200
        assert reservierungen_data == response.get_json()


def test_reservierungen_get_mit_datum(app, reservierungen_mit_datum_data):
    with app.app_context():
        route = "/v1/reservierungen"
        parameters = "?datum=2023-02-02T18:15:00Z"

        response = app.test_client().get(route + parameters)

        assert response.status_code == 200
        assert reservierungen_mit_datum_data == response.get_json()


def test_reservieren(app, reservieren_bereits_reserviert_data):
    with app.app_context():
        route = "/v1/reservierungen"
        parameters = "?tischnummer=1&datum=2023-02-02T18:15:00Z"

        response = app.test_client().post(route + parameters)

        assert response.status_code == 200
        assert reservieren_bereits_reserviert_data == response.data

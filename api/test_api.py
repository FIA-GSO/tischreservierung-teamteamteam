import pytest
from api import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True

    # yield app.test_client()
    return app


@pytest.fixture
def reservierung_get_data():
    return [[2], [3], [4]]


def test_reservierung_get(app, reservierung_get_data):
    with app.app_context():
        route = "/v1/reservierungen"
        parameters = "?datum=2023-02-02T18:15:00Z"

        response = app.test_client().get(route + parameters)

        assert response.status_code == 200
        assert reservierung_get_data == response.get_json()


def test_123(app, reservierung_get_data):
    with app.app_context():
        route = "/v1/reservierungen"
        parameters = "?datum=2023-02-02T18:15:00Z"

        response = app.test_client().get(route + parameters)

        assert response.status_code == 200
        assert reservierung_get_data == response.get_json()

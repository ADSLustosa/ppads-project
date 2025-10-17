
from app import create_app
from config import TestConfig

def test_health():
    app = create_app(TestConfig)
    client = app.test_client()
    r = client.get('/health')
    assert r.json['status']=='ok'

from app import app
import json
import pytest
from app import PurchaseOrderException


@pytest.fixture
def mock_data():
    data = {
        "po_date": "2022-12-02",
        "po_currency": "USD",
        "vendor_name": "IKAE",
        "vendor_email": "wellbert@ikae.com",
        "created_by": "procurement-agent-02",
        "po_lines": [
            {
                "item_name": "Plywood",
                "quantity": 200,
                "unit_price": 10,
                "notes": "Fine sanding"
            },
            {
                "item_name": "Top Table",
                "quantity": 40,
                "unit_price": 10,
                "notes": "Less glued particle"
            }
        ]
    }
    return data


def test_submit_purchase_order_success():
    data = {
        "po_date": "2022-12-01",
        "po_currency": "USD",
        "vendor_name": "WallMark",
        "vendor_email": "alice@wallmark.com",
        "created_by": "procurement-agent-01",
        "po_lines": [
            {
                "item_name": "Apple",
                "quantity": 280,
                "unit_price": 1,
                "notes": "Sweet red apple"
            },
            {
                "item_name": "Avocado",
                "quantity": 137,
                "unit_price": 3,
                "notes": "Australian avocado"
            }
        ]
    }
    response = app.test_client().post('/api/purchase_order', json=data)
    assert response.status_code == 201
    assert response.json['po_header_id']
    assert response.json['po_header_id'] is not None


@pytest.mark.parametrize("po_date, vendor_name, quantity, expected_status", [
    pytest.param("2022-12-01", "Wallmark Wallmark Wallmark Wallmark Wallmark Wallmark", 280, 400,
                 id="Long vendor name"),
    pytest.param("2022-12-01", "Wallmark", "280A", 400, id="Alphabet in quantity"),
    pytest.param("12-01-2022", "Wallmark", 280, 500, id="Wrong date format")
])
def test_submit_purchase_order_failed(po_date, vendor_name, quantity, expected_status):
    data = {
        "po_date": po_date,
        "po_currency": "USD",
        "vendor_name": vendor_name,
        "vendor_email": "alice@wallmark.com",
        "created_by": "procurement-agent-01",
        "po_lines": [
            {
                "item_name": "Apple",
                "quantity": quantity,
                "unit_price": 1,
                "notes": "Sweet red apple"
            },
            {
                "item_name": "Avocado",
                "quantity": 137,
                "unit_price": 3,
                "notes": "Australian avocado"
            }
        ]
    }
    response = app.test_client().post('/api/purchase_order', json=data)
    assert response.status_code == expected_status


def test_find_purchase_order_success_po_header(mock_data):
    post_response = app.test_client().post('/api/purchase_order', json=mock_data)
    get_response = app.test_client().get('/api/purchase_order?po_header_id=' + post_response.json['po_header_id'])

    assert get_response.status_code == 200
    assert len(json.loads(get_response.data)) > 0
    assert post_response.json['po_header_id'] in str(get_response.data)
    assert mock_data['po_lines'][0]['item_name'] in str(get_response.json[0]['po_lines'])
    assert mock_data['po_lines'][0]['notes'] in str(get_response.json[0]['po_lines'])
    assert mock_data['po_lines'][1]['item_name'] in str(get_response.json[0]['po_lines'])
    assert mock_data['po_lines'][1]['notes'] in str(get_response.json[0]['po_lines'])


def test_find_purchase_order_success_created_by(mock_data):
    post_response = app.test_client().post('/api/purchase_order', json=mock_data)
    get_response = app.test_client().get('/api/purchase_order?created_by=' + mock_data['created_by'])

    assert get_response.status_code == 200
    assert len(json.loads(get_response.data)) > 0
    assert post_response.json['po_header_id'] in str(get_response.data)
    assert mock_data['po_lines'][0]['item_name'] in str(get_response.json[0]['po_lines'])
    assert mock_data['po_lines'][0]['notes'] in str(get_response.json[0]['po_lines'])
    assert mock_data['po_lines'][1]['item_name'] in str(get_response.json[0]['po_lines'])
    assert mock_data['po_lines'][1]['notes'] in str(get_response.json[0]['po_lines'])


def test_find_purchase_order_success_all(mock_data):
    data2 = {
        "po_date": "2022-12-01",
        "po_currency": "USD",
        "vendor_name": "WallMark",
        "vendor_email": "alice@wallmark.com",
        "created_by": "procurement-agent-01",
        "po_lines": [
            {
                "item_name": "Apple",
                "quantity": 280,
                "unit_price": 1,
                "notes": "Sweet red apple"
            },
            {
                "item_name": "Avocado",
                "quantity": 137,
                "unit_price": 3,
                "notes": "Australian avocado"
            }
        ]
    }

    post_response = app.test_client().post('/api/purchase_order', json=mock_data)
    post_response2 = app.test_client().post('/api/purchase_order', json=data2)
    get_response = app.test_client().get('/api/purchase_order')

    assert get_response.status_code == 200
    assert len(json.loads(get_response.data)) > 1
    assert post_response.json['po_header_id'] in str(get_response.data)
    assert post_response2.json['po_header_id'] in str(get_response.data)
    assert mock_data['po_lines'][0]['item_name'] in str(get_response.data)
    assert mock_data['po_lines'][0]['notes'] in str(get_response.data)
    assert mock_data['po_lines'][1]['item_name'] in str(get_response.data)
    assert mock_data['po_lines'][1]['notes'] in str(get_response.data)
    assert data2['po_lines'][0]['item_name'] in str(get_response.data)
    assert data2['po_lines'][0]['notes'] in str(get_response.data)
    assert data2['po_lines'][1]['item_name'] in str(get_response.data)
    assert data2['po_lines'][1]['notes'] in str(get_response.data)


@pytest.mark.parametrize("param_name, param_value, expected_response, expected_length", [
    pytest.param("po_header_id", "nonexistpoheader", 200, 0, id="Test non-exist po_header_id"),
    pytest.param("created_by", "nonexistcreatedby", 200, 0, id="Test non-exist created_by"),
])
def test_find_purchase_order_failed(param_name, param_value, expected_response, expected_length):
    get_response = app.test_client().get('/api/purchase_order?' + str(param_name) + '=' + str(param_value))

    assert get_response.status_code == expected_response
    assert len(json.loads(get_response.data)) == expected_length


def test_index():
    get_response = app.test_client().get('/')

    assert get_response.status_code == 200
    assert f'Hello, World' in str(get_response.data)


def test_redirect():
    get_response = app.test_client().get('/redirect/')
    assert get_response.status_code == 302


def test_exception():
    with pytest.raises(PurchaseOrderException) as exc_info:
        raise PurchaseOrderException('error message', 'error detail', None)


def test_exception_dict():
    mock_dict = {'error_message': 'error message', 'detail': 'error detail'}
    assert mock_dict == PurchaseOrderException('error message', 'error detail', None).to_dict()

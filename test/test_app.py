from app import app
import json


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


def test_submit_purchase_order_failed_string_qty():
    data = {
        "po_date": "2022-12-01",
        "po_currency": "USD",
        "vendor_name": "WallMark",
        "vendor_email": "alice@wallmark.com",
        "created_by": "procurement-agent-01",
        "po_lines": [
            {
                "item_name": "Apple",
                "quantity": "280A",
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
    assert response.status_code == 400


def test_submit_purchase_order_failed_vendor_too_long():
    data = {
        "po_date": "2022-12-01",
        "po_currency": "USD",
        "vendor_name": "WallMark WallMark WallMark WallMark WallMark WallMark",
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
    assert response.status_code == 400


def test_submit_purchase_order_failed_wrong_date_format():
    data = {
        "po_date": "12-01-2022",
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
    assert response.status_code == 500


def test_find_purchase_order_success_po_header():
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

    post_response = app.test_client().post('/api/purchase_order', json=data)
    get_response = app.test_client().get('/api/purchase_order?po_header_id=' + post_response.json['po_header_id'])

    assert get_response.status_code == 200
    assert len(json.loads(get_response.data)) > 0
    assert post_response.json['po_header_id'] in str(get_response.data)
    assert data['po_lines'][0]['item_name'] in str(get_response.json[0]['po_lines'])
    assert data['po_lines'][0]['notes'] in str(get_response.json[0]['po_lines'])
    assert data['po_lines'][1]['item_name'] in str(get_response.json[0]['po_lines'])
    assert data['po_lines'][1]['notes'] in str(get_response.json[0]['po_lines'])


def test_find_purchase_order_success_created_by():
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

    post_response = app.test_client().post('/api/purchase_order', json=data)
    get_response = app.test_client().get('/api/purchase_order?created_by=' + data['created_by'])

    assert get_response.status_code == 200
    assert len(json.loads(get_response.data)) > 0
    assert post_response.json['po_header_id'] in str(get_response.data)
    assert data['po_lines'][0]['item_name'] in str(get_response.json[0]['po_lines'])
    assert data['po_lines'][0]['notes'] in str(get_response.json[0]['po_lines'])
    assert data['po_lines'][1]['item_name'] in str(get_response.json[0]['po_lines'])
    assert data['po_lines'][1]['notes'] in str(get_response.json[0]['po_lines'])


def test_find_purchase_order_success_all():
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

    post_response = app.test_client().post('/api/purchase_order', json=data)
    post_response2 = app.test_client().post('/api/purchase_order', json=data2)
    get_response = app.test_client().get('/api/purchase_order')

    assert get_response.status_code == 200
    assert len(json.loads(get_response.data)) > 1
    assert post_response.json['po_header_id'] in str(get_response.data)
    assert post_response2.json['po_header_id'] in str(get_response.data)
    assert data['po_lines'][0]['item_name'] in str(get_response.data)
    assert data['po_lines'][0]['notes'] in str(get_response.data)
    assert data['po_lines'][1]['item_name'] in str(get_response.data)
    assert data['po_lines'][1]['notes'] in str(get_response.data)
    assert data2['po_lines'][0]['item_name'] in str(get_response.data)
    assert data2['po_lines'][0]['notes'] in str(get_response.data)
    assert data2['po_lines'][1]['item_name'] in str(get_response.data)
    assert data2['po_lines'][1]['notes'] in str(get_response.data)


def test_find_purchase_order_failed_nonexist_po_header():
    get_response = app.test_client().get('/api/purchase_order?po_header_id=nonexistpoheader')

    assert get_response.status_code == 200
    assert len(json.loads(get_response.data)) == 0


def test_find_purchase_order_failed_nonexist_created_by():
    get_response = app.test_client().get('/api/purchase_order?created_by=nonexistcreatedby')

    assert get_response.status_code == 200
    assert len(json.loads(get_response.data)) == 0

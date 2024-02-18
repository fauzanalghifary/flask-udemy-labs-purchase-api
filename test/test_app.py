from app import app


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

from flask import Flask, render_template, redirect, request, url_for, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from marshmallow import Schema, fields, validate, ValidationError
import datetime, uuid, math, werkzeug, random, string

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///retail.db"
db = SQLAlchemy(app)

# The lab is behind a http proxy, so it's not aware of the fact that it should use https.
# We use ProxyFix to enable it: https://flask.palletsprojects.com/en/2.0.x/deploying/wsgi-standalone/#proxy-setups
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


# Used for any other security related needs by extensions or application, i.e. csrf token
app.config['SECRET_KEY'] = 'mysecretkey'

# Required for cookies set by Flask to work in the preview window that's integrated in the lab IDE
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True

# Required to render urls with https when not in a request context. Urls within Udemy labs must use https
app.config['PREFERRED_URL_SCHEME'] = 'https'


@app.route("/")
def index():
    print('Received headers', request.headers)
    return render_template('index.html')


@app.route("/redirect/")
def redirect_to_index():
    return redirect(url_for('index'))


class PurchaseOrderHeader(db.Model):
    __tablename__ = 'header'
    
    po_header_id = db.Column(db.String(36), primary_key=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    po_date = db.Column(db.DateTime, nullable=False)
    po_currency = db.Column(db.String(5), nullable=False)
    vendor_name = db.Column(db.String(50), nullable=False)
    vendor_email = db.Column(db.String(50), nullable=False)
    created_by = db.Column(db.String(50), nullable=False)
    po_lines = db.relationship('PurchaseOrderLine', backref='header')

    def to_dict(self):
        return {
            'po_header_id': self.po_header_id,
            'po_number': self.po_number,
            'po_date': datetime.datetime.strftime(self.po_date, '%Y-%m-%d'),
            'po_currency': self.po_currency,
            'vendor_name': self.vendor_name,
            'vendor_email': self.vendor_email,
            'created_by': self.created_by,
            'po_lines': [line.to_dict() for line in self.po_lines]
        }


class PurchaseOrderLine(db.Model):
    __tablename__ = 'line'
    
    po_line_id = db.Column(db.String(36), primary_key=True)
    item_name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(50))
    po_header_id = db.Column(db.String, db.ForeignKey('header.po_header_id'))


    def to_dict(self):
        return {
            'po_line_id': self.po_line_id,
            'item_name': self.item_name, 
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'notes': self.notes
        }


class PurchaseOrderLineSchema(Schema):
    item_name = fields.String(required=True)
    quantity = fields.Integer(
        required=True, validate=validate.Range(min=1, max=999999)
        )
    unit_price = fields.Integer(
        required=True, validate=validate.Range(min=1)
        )
    notes = fields.String(
        validate=validate.Length(max=50)
        )


class PurchaseOrderHeaderSchema(Schema):
    po_date = fields.String(required=True)
    po_currency = fields.String(
        required=True, validate=validate.Length(min=3, max=5)
        )
    vendor_name = fields.String(
        required=True, validate=validate.Length(min=3, max=50)
        )
    vendor_email = fields.String(
        required=True, validate=validate.Email()
        )
    created_by = fields.String(
        required=True, validate=validate.Length(min=3, max=50)
        )
    po_lines = fields.List( fields.Nested(PurchaseOrderLineSchema) )


with app.app_context():
    db.drop_all()
    db.create_all()


def save_purchase_order_to_database(purchase_order):
    random_po_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    parsed_po_date = datetime.datetime.strptime(purchase_order['po_date'], '%Y-%m-%d')
    
    po_header = PurchaseOrderHeader(
            po_header_id = str(uuid.uuid4()),
            po_number = 'PO-' + random_po_number,
            po_date = parsed_po_date,
            po_currency = purchase_order['po_currency'],
            vendor_name = purchase_order['vendor_name'],
            vendor_email = purchase_order['vendor_email'],
            created_by = purchase_order['created_by']
        )

    db.session.add(po_header)

    for line in purchase_order['po_lines']:
        po_line = PurchaseOrderLine(
                po_line_id = str(uuid.uuid4()),
                item_name = line['item_name'],
                quantity = line['quantity'],
                unit_price = line['unit_price'],
                po_header_id = po_header.po_header_id,
                notes = line.get('notes', '')
            )
        
        db.session.add(po_line)

    db.session.commit()

    return po_header
    
    
po_header_schema = PurchaseOrderHeaderSchema()
    

@app.route('/api/purchase_order', methods=['POST'])
def submit_purchase_order():
    errors = po_header_schema.validate(request.json)
    
    if errors:
        raise PurchaseOrderException(
                error_message = "Validation failed",
                status_code = 400,
                detail = errors
            ) 
    
    saved_po = save_purchase_order_to_database(request.json)
    
    return jsonify(
        po_header_id = saved_po.po_header_id,
        po_number = saved_po.po_number
        ), 201
        

@app.route('/api/purchase_order', methods=['GET'])
def find_purchase_order():
    po_header_id = request.args.get('po_header_id', '%')
    created_by = request.args.get('created_by', '%')
    
    filter_po = PurchaseOrderHeader.query.filter( \
        and_(\
            PurchaseOrderHeader.po_header_id.ilike(po_header_id), \
            PurchaseOrderHeader.created_by.ilike(created_by)
        )
    )
    
    existing_po = filter_po.all()
    
    return jsonify(
        [po_header.to_dict() for po_header in existing_po]
    ), 200
    
    
class PurchaseOrderException(Exception):
    def __init__(self, error_message, detail, status_code=None):
        self.error_message = error_message
        self.detail = detail
        
        if status_code is not None:
            self.status_code = status_code
        else:
            self.status_code = 500
        
    def to_dict(self):
        return {
            'error_message' : self.error_message,
            'detail' : self.detail
        }
    

@app.errorhandler(Exception)
def handle_any_uncaught_exception(ex):
    return jsonify(
        error_message = 'Server cannot process request.',
        detail = str(ex)
    ), 500
    
    
@app.errorhandler(PurchaseOrderException)
def handle_loan_business_exception(ex):
    return jsonify(
        error_message = ex.error_message,
        detail = ex.detail
    ), ex.status_code
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from datetime import datetime
import json
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/order'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)


class Order(db.Model):
    __tablename__ = 'order'

    oid = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    cid = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    oStatus = db.Column(db.Integer, nullable=False)
    dStatus = db.Column(db.String(128), nullable=False)
    pResponse = db.Column(db.String(128), nullable=False)

    def json(self):

        return {
            "oid": self.oid,
            "pid": self.pid,
            "quantity": self.quantity,
            "cid": self.cid,
            "datetime": self.datetime,
            "oStatus": self.oStatus,
            "dStatus": self.dStatus,
            "pResponse": self.pResponse
        }


@app.route("/order")
def get_all():
    orderlist = Order.query.all()
    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "order": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404


@app.route("/order/<string:oid>")
def find_by_oid(oid):
    order = Order.query.filter_by(oid=oid).first()
    if order:
        return jsonify(
            {
                "code": 200,
                "data": order.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "order not found."
        }
    ), 404


@app.route("/order/product/<string:pid>")
def find_by_pid(pid):
    orderlist = Order.query.filter_by(pid=pid).all()
    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "order": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404

@app.route("/order", methods=['POST'])
def create_order():
    # oid = request.json.get('oid', None)
    quantity = request.json.get('quantity', None)
    datetime = request.json.get('datetime', None)
    pid = request.json.get('pid', None)
    cid = request.json.get('cid', None)
    oStatus = 0
    dStatus = "Undelivered"
    pResponse = request.json.get('pResponse', None)


    order = Order(quantity=quantity, datetime=datetime, pid=pid, cid=cid, oStatus=oStatus, dStatus=dStatus, pResponse=pResponse)

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the order. " + str(e)
            }
        ), 500

    # print(json.dumps(product.json(), default=str)) # convert a JSON object to a string and print
    # print()

    return jsonify(
        {
            "code": 201,
            "data": order.json()
        }
    ), 201


@app.route("/product/<string:pid>", methods=['PUT'])
def update_product(pid):
    product = Order.query.filter_by(pid=pid).first()
    if product:
        data = request.get_json()
        if data['pname']:
            product.pname = data['pname']
        if data['price']:
            product.price = data['price']
        if data['pdescription']:
            product.pdescription = data['pdescription']
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": product.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "pid": pid
            },
            "message": "Product not found."
        }
    ), 404


@app.route("/order/<string:oid>", methods=['DELETE'])
def delete_product(oid):
    order = Order.query.filter_by(oid=oid).first()
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "oid": oid
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "oid": oid
            },
            "message": "Order not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(port=5002, debug=True)

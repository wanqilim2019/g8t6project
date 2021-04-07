from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests
from invokes import invoke_http

import json

app = Flask(__name__)
CORS(app)


order_URL = environ.get('order_URL') or "http://localhost:5002/order" 
product_URL = environ.get('product_URL') or "http://localhost:5001/product" 
customer_URL = environ.get('customer_URL') or "http://localhost:5003/customer" 

@app.route("/check_order_biz/<string:bid>", methods=['GET'])
def check_order_biz(bid):
    # Simple check of input format and data of the request are JSON
    # do the actual work
    # 1. Send get order info
    result = processCheckOrderBiz(bid)
    print('\n------------------------')
    print('\nresult: ', result)
    return jsonify(result), result["code"]

def processCheckOrderBiz(bid):

    print('\n\n-----Invoking product microservice-----')
    # 2. get pid based on bid

    product_result = invoke_http(
        (product_URL + '/business/' + bid), method="GET" )
    print("product:", product_result, '\n')

    # Check the shipping result;
    # if a failure, send it to the error microservice.
    code = product_result["code"]

    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as shipping fails-----')
        print('\n\n-----Publishing the (product error)')
        
        # 7. Return error
        return {
            "code": 500,
            "data": {
                "product_result": product_result
            },
            "message": "Product retrival fail."
        }

    # 3. Get the order info base on pid
    # Invoke the order microservice
    product_result_list = product_result['data']['products']
    #print(product_result_list)
    print('\n-----Invoking order microservice-----')
    

    order_result_list=list()
    
    for product in product_result_list:
        pid=product['pid']
        print('pid')
        print(pid)
        order_result = invoke_http(order_URL + '/product/' + str(pid))
        print('order_result:', order_result)
        order_result_list.append(order_result)
    
        # Check the order result; if a failure, print error.
        code = order_result["code"]
        message = json.dumps(order_result)

        if code not in range(200, 300):

            #  Return error
            print('-----No order-----')

        else:
            # 4. Confirm success
            print('\n\n-----Publishing the (order info) message-----')



        # 5. Send PID order to product
        # Invoke the product microservice


    print('\n\n-----Invoking customer microservice-----')
    
    customer_result_list=list()
    print(order_result_list)

    for order in order_result_list:
        cid=order
        customer_result = invoke_http(
            (customer_URL + '/' + str(cid)), method="GET")
        print("customer:", customer_result, '\n')
        customer_result_list.append(customer_result)

        # Check the customer result;
        # if a failure, send it to the error microservice.
        code = customer_result["code"]
        if code not in range(200, 300):
            # Inform the error microservice
            #print('\n\n-----Invoking error microservice as shipping fails-----')
            print('\n\n-----Publishing the (customer error)')
            
            # 7. Return error
            return {
                "code": 400,
                "data": {
                    "order_result": order_result,
                    "shipping_result": product_result,
                    "customer_result":customer_result
                },
                "message": "Customer retrival fail."
            }



    # 7. Return created order, shipping record
    return {
        "code": 201,
        "data": {
            "order_result": product_result,
            "shipping_result": order_result_list,
            "customer_result":customer_result_list
        }
    }






# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for checking order by business...")
    app.run(host="0.0.0.0", port=5100, debug=True)
    # Notes for the parameters: 
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program, and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.

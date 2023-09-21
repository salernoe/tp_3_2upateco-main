"""from flask import Flask, jsonify, request
from config import Config
from app.database import DatabaseConnection

def init_app():
    app = Flask(__name__, static_folder=Config.STATIC_FOLDER, template_folder=Config.TEMPLATE_FOLDER)
    app.config.from_object(Config)
"""
from flask import Flask, jsonify, request
from config import Config
from app.database import DatabaseConnection  # Asegúrate de que la importación sea correcta

def init_app():
    app = Flask(__name__, static_folder=Config.STATIC_FOLDER, template_folder=Config.TEMPLATE_FOLDER)
    app.config.from_object(Config)
    
    # 1.1. Obtener un cliente
    # GET /customers/<int:customer_id>

    @app.route('/customers/<int:customer_id>', methods=['GET'])
    def get_customer(customer_id):
        sql = "SELECT customer_id, first_name, last_name, email, phone, street, city, state, zip_code FROM sail.customer WHERE customer_id = %s;"
        params = (customer_id,)
        result = DatabaseConnection.fetch_one(sql, params)

        if result is None:
            return jsonify({'error': 'Customer not found'}), 404

        customer_data = {
            'customer_id': result[0],
            'first_name': result[1],
            'last_name': result[2],
            'email': result[3],
            'phone': result[4],
            'street': result[5],
            'city': result[6],
            'state': result[7],
            'zip_code': result[8]
        }

        return jsonify(customer_data)

    # 1.2. Obtener el listado de clientes
    # GET /customers

    @app.route('/customers', methods=['GET'])
    def get_customers():
        state = request.args.get('state', default=None, type=str)
        sql = "SELECT customer_id, first_name, last_name, email, phone, street, city, state, zip_code FROM sales.customer"
        params = ()

        if state:
            sql += " WHERE state = %s"
            params = (state,)

        results = DatabaseConnection.fetch_all(sql, params)
        total = len(results)

        customers = []
        for result in results:
            customer_data = {
                'customer_id': result[0],
                'first_name': result[1],
                'last_name': result[2],
                'email': result[3],
                'phone': result[4],
                'street': result[5],
                'city': result[6],
                'state': result[7],
                'zip_code': result[8]
            }
            customers.append(customer_data)

        response = {
            'customers': customers,
            'total': total
        }

        return jsonify(response)

    # 1.3. Registrar un cliente
    # POST /customers
    @app.route('/customers', methods=['POST'])
    def create_customer():
        data = request.get_json()

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        street = data.get('street')
        city = data.get('city')
        state = data.get('state')
        zip_code = data.get('zip_code')

        if not first_name or not last_name or not email:
            return jsonify({'error': 'Missing required fields'}), 400

        sql = "INSERT INTO sales.customer (first_name, last_name, email, phone, street, city, state, zip_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        params = (first_name, last_name, email, phone, street, city, state, zip_code)

        DatabaseConnection.execute(sql, params)

        return jsonify({}), 201

    # 1.4. Modificar un cliente
    # PUT /customers/<int:customer_id>
    @app.route('/customers/<int:customer_id>', methods=['PUT'])
    def update_customer(customer_id):
        data = request.get_json()

        email = data.get('email')
        phone = data.get('phone')
        street = data.get('street')
        city = data.get('city')
        state = data.get('state')
        zip_code = data.get('zip_code')

        sql = "UPDATE sales.customer SET email = %s, phone = %s, street = %s, city = %s, state = %s, zip_code = %s WHERE customer_id = %s"
        params = (email, phone, street, city, state, zip_code, customer_id)

        DatabaseConnection.execute(sql, params)

        return jsonify({}), 200

    # 1.5. Eliminar un cliente
    # DELETE /customers/<int:customer_id>
    @app.route('/customers/<int:customer_id>', methods=['DELETE'])
    def delete_customer(customer_id):
        sql = "DELETE FROM sales.customer WHERE customer_id = %s"
        params = (customer_id,)

        DatabaseConnection.execute(sql, params)

        return jsonify({}), 204

    # 2.1. Obtener un producto
    # GET /products/<int:product_id>

    products = [
        {
            "product_id": 10,
            "product_name": "Surly Straggler - 2016",
            "brand": {
                "brand_id": 8,
                "brand_name": "Surly"
            },
            "category": {
                "category_id": 4,
                "category_name": "Cyclocross Bicycles"
            },
            "model_year": 2016,
            "list_price": 1549.00
        },
        # Add more products here
    ]

    @app.route('/products/<int:product_id>', methods=['GET'])
    def get_product(product_id):
        product = None
        for p in products:
            if p["product_id"] == product_id:
                product = p
                break

        if product is None:
            return jsonify({'error': 'Product not found'}), 404

        return jsonify(product), 200

    # 2.2. Obtener un listado de productos
    # GET /products

    @app.route('/products', methods=['GET'])
    def get_products():
        brand_id = request.args.get('brand_id')
        category_id = request.args.get('category_id')

        filtered_products = []
        for p in products:
            if (brand_id is None or p["brand"]["brand_id"] == int(brand_id)) and \
               (category_id is None or p["category"]["category_id"] == int(category_id)):
                filtered_products.append(p)

        response_data = {
            "products": filtered_products,
            "total": len(filtered_products)
        }

        return jsonify(response_data), 200

    # 2.3. Registrar un producto
    # POST /products
    @app.route('/products', methods=['POST'])
    def create_product():
        data = request.json

        new_product = {
            "product_id": len(products) + 1,
            "product_name": data["product_name"],
            "brand": {
                "brand_id": data["brand_id"],
                "brand_name": ""
            },
            "category": {
                "category_id": data["category_id"],
                "category_name": ""
            },
             "model_year": data["model_year"],
            "list_price": data["list_price"]
        }

        products.append(new_product)

        return jsonify({}), 201

    # 2.4. Modificar un producto
    # PUT /products/<int:product_id>
    @app.route('/products/<int:product_id>', methods=['PUT'])
    def update_product(product_id):
        data = request.json

        product_to_update = None
        for p in products:
            if p["product_id"] == product_id:
                product_to_update = p
                break

        if product_to_update is None:
            return jsonify({"error": "Product not found"}), 404

        if "product_name" in data:
            product_to_update["product_name"] = data["product_name"]
        if "brand_id" in data:
            product_to_update["brand"]["brand_id"] = data["brand_id"]
        if "category_id" in data:
            product_to_update["category"]["category_id"] = data["category_id"]
        if "model_year" in data:
            product_to_update["model_year"] = data["model_year"]
        if "list_price" in data:
            product_to_update["list_price"] = data["list_price"]

        return jsonify({}), 200

    # 2.5. Eliminar un producto
    # DELETE /products/<int:product_id>
    @app.route('/products/<int:product_id>', methods=['DELETE'])
    def delete_product(product_id):
        global products
        products = [p for p in products if p["product_id"] != product_id]
        return jsonify({}), 204

    return app           
from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from elasticsearch import Elasticsearch

app = Flask(__name__, template_folder='templates')

es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200}])
app.config["MONGO_URI"] = "mongodb://mongo:27017/myDatabase"
mongo = PyMongo(app)
db = mongo.db
products = db.products

# Create a new dictionary with the fields in the desired order
def create_doc(data):
    doc = {
        'id': data['id'],
        'ProductName': data['ProductName'],
        'ProductCategory': data['ProductCategory'],
        'Price': data['Price'],
        'AvailableQuantity': data['AvailableQuantity']
    }
    return doc

# Create index 'products' and add alias 'product_alias'
try:
    if not es.indices.exists(index='products'):
        es.indices.create(index='products', ignore=400)
        es.indices.put_alias(index='products', name='product_alias')
except Exception as e:
    print("Error while configuring Elasticsearch:", e)


# Index products in Elasticsearch, if any exist
def index_products():
    try:
        if products.count_documents({}) > 0:
            for product in products.find():
                product['id'] = str(product.pop('_id'))
                doc = create_doc(product)
                es.index(index='product_alias', id=str(product['_id']), body=doc)
    except Exception as e:
        print("Exception occurred during indexing:", e)

index_products()

# Displays the home page
@app.route('/', methods=['GET'])
def home():
    print('home route accessed')
    return render_template('home.html')

# Displays the gettingstarted page
@app.route('/gettingstarted', methods=['GET'])
def gettingstarted():
    return render_template('gettingstarted.html')

# Displays the search page
@app.route('/search', methods=['GET'])
def search():
    return render_template('search.html')

# Displays the update product page
@app.route('/updateproduct', methods=['GET'])
def updateproduct():
    products_list = list(products.find())
    return render_template('updateproduct.html', products=products_list)

# Displays the list products page
@app.route('/listproducts', methods=['GET'])
def list_products():
    products_list = list(products.find())
    return render_template('listproducts.html', products=products_list)

# Displays the products page or returns a JSON list of products
@app.route('/products', methods=['GET'])
def get_products():
    if request.accept_mimetypes.accept_html:
        products_list = list(products.find())
        print('products accessed')
        return render_template('products.html', products=products_list)
    else:
        products_list = []
        for product in products.find():
            product['_id'] = str(product['_id'])
            products_list.append(product)
        return jsonify(products_list)

# Searches for products using elasticsearch and returns a JSON list of search results
@app.route('/products/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    print(f"Search query: {query}")
    search_query = {
        'query': {
            'multi_match': {
                'query': query,
                'fields': ['ProductName', 'ProductCategory', 'Price', 'AvailableQuantity']
            }
        }
    }
    print(f"Elasticsearch search query: {search_query}")
    search_result = es.search(index='product_alias', body=search_query)
    print(f"Elasticsearch search result: {search_result}")
    products_list = [hit['_source'] for hit in search_result['hits']['hits']]
    return jsonify(products_list)

# Returns a specific product by ID 
@app.route('/products/<id>', methods=['GET'])
def get_product(id):
    product = products.find_one({'_id': ObjectId(id)})
    if product:
        product['_id'] = str(product['_id'])
        return jsonify(product)
    else:
        return jsonify({'error': 'Product not found'}), 404

# Adds a new product to the database
@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    if 'ProductName' in data and 'ProductCategory' in data and 'Price' in data and 'AvailableQuantity' in data:
        product_id = products.insert_one(data).inserted_id
        # Convert the ObjectId field to a string
        data['id'] = str(data.pop('_id'))
        # Create a new dictionary with the fields in the desired order
        doc = create_doc(data)
        # Index the new product in Elasticsearch
        es.index(index='product_alias', id=str(product_id), body=doc)
        return jsonify({'result': str(product_id)})
    else:
        return jsonify({'error': 'Missing required fields'}), 400

# Updates an existing product by ID
@app.route('/products/<id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    if 'ProductName' in data or 'ProductCategory' in data or 'Price' in data or 'AvailableQuantity' in data:
        update_result = products.update_one({'_id': ObjectId(id)}, {'$set': data})
        if update_result.modified_count > 0:
            return jsonify({'result': 'Product updated'})
        else:
            return jsonify({'error': 'Product not found'}), 404
    else:
        return jsonify({'error': 'Missing required fields'}), 400

# Deletes a specific product by ID
@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    delete_result = products.delete_one({'_id': ObjectId(id)})
    if delete_result.deleted_count > 0:
        return jsonify({'result': 'Product deleted'})
    else:
        return jsonify({'error': 'Product not found'}), 404

# Displays the product analytics page
@app.route('/analytics', methods=['GET'])
def show_product_analytics():
    return render_template('analytics.html')

# Returns aggregated product data, most popular category, average price, and total count of products as JSON
@app.route('/products/analytics', methods=['GET'])
def get_product_analytics():
    # Get the total count of products
    total_count = products.count_documents({})
    
    # Get the most popular product category
    pipeline = [
        {'$group': {'_id': '$ProductCategory', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 1}
    ]
    most_popular_category = list(products.aggregate(pipeline))[0]['_id']
    
    # Get the average price of products
    pipeline = [
            {
            '$project': {
                'Price': {
                    '$convert': {
                        'input': '$Price',
                        'to': 'double',
                        'onError': 0.0,
                        'onNull': 0.0
                    }
                }
            }
        },
        {
            '$group': {
                '_id': None,
                'average_price': {'$avg': '$Price'}
            }
        }
    ]
    average_price = list(products.aggregate(pipeline))[0]['average_price']
    
    # Round the average price to round to the nearest hundredth
    rounded_average_price = round(average_price, 2)

    # Return the aggregated data as a JSON object
    return jsonify({
        'total_count': total_count,
        'most_popular_category': most_popular_category,
        'average_price': rounded_average_price
    })


# Flask Inventory Manager

This is a web appication and RESTful API that enables managing and agrigating products. This app is hosted in minikube via the include docker image, deployment and service .yaml files. 

### Requirements
The following both need to be installed on your computer in order to use this app.

docker

minikube

## Getting Started
Follow the steps below to get this app running:

1. Download the project from github from this directory run the following commands.

2. Start Minikube in either powershell or terminal:
   ```sh
   minikube start
   ```

2. Check Minikube status:
   ```sh
   minikube status
   ```

3. Set up Docker environment for Minikube:
   ```sh
   minikube docker-env | Invoke-Expression
   ```
   or using curl:
   ```sh
   eval $(minikube docker-env)
   ```

4. Build your Docker image:
   ```sh
   docker build -t salsproject/flask-inventory-app .
   ```

5. Apply Kubernetes service configuration:
   ```sh
   kubectl apply -f service.yaml
   ```

6. Apply Kubernetes deployment configuration:
   ```sh
   kubectl apply -f deployment.yaml
   ```

This setup process should take around 2 minutes and 40 seconds.

7. Check your pods are running:
   ```sh
   kubectl get pods
   ```

8. Access the application:
   ```sh
   minikube service flask-inventory --url
   ```

This will provide you with a URL to access the app. Put this url in your browser of choice to access the site. There will be additional troubleshooting at the bottom of this red me as well as some example products for testing. 

## Using the App

Inventory Manager provides various HTML pages to interact with the app:

- **Manage Products:** Add, update, and delete products using the `/products` endpoint through the web interface.
- **Update Product:** Update product details using the `/updateproduct` endpoint.
- **List Products:** View a list of all products using the `/listproducts` endpoint.
- **Search Products:** Search for products using Elasticsearch through the `/search` endpoint.
- **Product Analytics:** Access aggregated product data using the `/analytics` endpoint.

## Using the API

The Inventory Manager API allows programmatic interaction. Here are the API endpoints:

- **Add Products:** POST `/products` to add a new product.
- **Get Products:** GET `/products` to retrieve a list of all products.
- **Fetch a Specific Product:** GET `/products/{id}` to retrieve a specific product.
- **Update an Existing Product:** PUT `/products/{id}` to update a product.
- **Delete a Product:** DELETE `/products/{id}` to delete a product.
- **Elasticsearch:** GET `/products/search?query={query}` to search using Elasticsearch.
- **Analytics:** GET `/products/analytics` for aggregated product data.

Please replace placeholders like `{query}`, `{id}`, and `http://<use the url and port recived from Access the application>/products` with actual values from your application. There are some examples below. Also, ensure that the directory structure of your project matches the locations mentioned in the commands.


## Conclusion

This README covers the basics setting up the Flask Inventory Manager and using it's API. Below are some example API request as well as a bit of troubleshooting if you run into any issues launching the app.

# Examples
Make sure to use the correct URL provide in the console instead of the placeholders below. Also Remembering to replace the example {id} and {query} with actual IDs and search queries for your products.
## powershell
To add products to the app, use the following commands:
```
Invoke-WebRequest -Method POST -ContentType "application/json" -Body '{"ProductName": "Mystical Unicorn Plushie", "ProductCategory": "Toys", "Price": 14.99, "AvailableQuantity": 20}' -Uri http://URL:PORT/products
Invoke-WebRequest -Method POST -ContentType "application/json" -Body '{"ProductName": "Galactic Spaceship Model", "ProductCategory": "Collectibles", "Price": 24.99, "AvailableQuantity": 15}' -Uri http://URL:PORT/products
Invoke-WebRequest -Method POST -ContentType "application/json" -Body '{"ProductName": "Enchanted Fairy Garden Kit", "ProductCategory": "Gardening", "Price": 19.99, "AvailableQuantity": 25}' -Uri http://URL:PORT/products
```
To retrive a list of all products
```
Invoke-WebRequest -Method GET -Uri http://URL:PORT/products | Select-Object -ExpandProperty Content
```
Request a specific product by id
```
Invoke-WebRequest -Method GET -Uri http://URL:PORT/products/{id} | Select-Object -ExpandProperty Content
```
Updating a product by id
```
Invoke-WebRequest -Method PUT -ContentType "application/json" -Body '{"ProductName": "Mystical Plushie", "ProductCategory": "Toys", "Price": 14.99, "AvailableQuantity": 20}' -Uri http://URL:PORT/products/64d00dedc7cd8547e8824502
```
Deleting a product by id
```
Invoke-WebRequest -Method DELETE -Uri http://URL:PORT/products/{id}
```
Using Elasticsearch
```
Invoke-WebRequest -Method GET -Uri "http://localhost:5000/products/search?query=Plushie" | Select-Object -ExpandProperty Content
```

## cURL
To add products to the app, use the following commands:
```
curl -X POST -H "Content-Type: application/json" -d '{"ProductName": "Mystical Unicorn Plushie", "ProductCategory": "Toys", "Price": 14.99, "AvailableQuantity": 20}' http://URL:PORT/products
curl -X POST -H "Content-Type: application/json" -d '{"ProductName": "Galactic Spaceship Model", "ProductCategory": "Collectibles", "Price": 24.99, "AvailableQuantity": 15}' http://URL:PORT/products
curl -X POST -H "Content-Type: application/json" -d '{"ProductName": "Enchanted Fairy Garden Kit", "ProductCategory": "Gardening", "Price": 19.99, "AvailableQuantity": 25}' http://URL:PORT/products

```
To retrive a list of all products
```
curl -X GET http://URL:PORT/products
```
Request a specific product by id
```
curl -X GET http://URL:PORT/products/{id}
```
Updating a product by id
```
curl -X GET http://URL:PORT/products/64d00dedc7cd8547e8824502
```
Deleting a product by id
```
curl -X DELETE http://URL:PORT/products/{id}
```
Using Elasticsearch
```
curl -X GET "http://URL:PORT/products/search?query=Plushie"
```

## Troubleshooting
If you encounter any issues during the setup or running of the Inventory Manager app, here are some troubleshooting steps you can follow to diagnose and resolve potential problems:

Tthe following command will check the status of the pods in your Kubernetes cluster.
```
kubectl get pods
```
Check Dependencies Initialization: If you suspect that the Flask app is having trouble initializing due to dependency issues, you can check the logs of the pod using the following command.
```
kubectl logs flask-inventory-<pod-ID> -c wait-for-dependencies
```
Run the following to gain shell access to the pod's wait-for-dependencies container to perform manual checks.
```
kubectl exec -it flask-inventory-<pod-ID> -c wait-for-dependencies -- /bin/sh
```
Inside the shell of the wait-for-dependencies container, run the following command to check the connectivity to the Elasticsearch service. If everything is set up correctly, this command should not return anything.
```
curl --output /dev/null --silent --head --fail http://elasticsearch:9200
```
This command if successful, indicates that the Flask app's dependency on Elasticsearch is satisfied.

Exit the Shell: Once you've performed your checks, you can exit the shell:
```
exit
```
These troubleshooting steps can help you identify potential issues in your setup and provide insights into what might be causing problems.

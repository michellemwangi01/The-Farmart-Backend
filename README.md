# Farmart Backend

This is the backend repository for the Farmart project, a platform aimed at supporting and empowering farmers by streamlining sales, increasing profits, and delivering high-quality, farm-fresh products to customers' convenience. The backend is built using Flask and interacts with the ReactJs frontend.
![Alt text](image.png)

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [API Endpoints](#api-endpoints)
- [Running the Backend](#running-the-backend)
  - [Development Mode](#development-mode)
  - [Production Build](#production-build)
- [Contributing](#contributing)
- [Authors](#authors)
- [License](#license)

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- Python 3.10
- Flask
- Pip
- Virtualenv (optional but recommended)

## Installation

1. Clone the repository:

   bash
   git clone https://github.com/michellemwangi01/farmart.git
   cd farmart/backend

2. Create a virtual environment and activate it:

   bash
   python -m venv venv
   source venv/bin/activate # On Windows, use 'venv\Scripts\activate'

3. Install Python dependencies:

   bash
   pip install -r requirements.txt

## Database Setup

Farmart uses a database to store information about farmers, products, transactions, and users. Follow these steps to set up the database:

1. Create a PostgreSQL database.
2. Update the `config.py` file with your database credentials.

## API Endpoints

Farmart's backend provides the following API endpoints:

- `/api/products`: Get a list of all products.
- `/api/products/<product_id>`: Get details about a specific product.
- `/api/users`: Get a list of all users.
- `/api/users/<user_id>`: Get details about a specific user.
- `/api/transactions`: Get a list of all transactions.
- `/api/transactions/<transaction_id>`: Get details about a specific transaction.

Refer to the API documentation for more details on request and response formats.

## Running the Backend

### Development Mode

To run the backend server in development mode:

1. Activate the virtual environment (if not already activated):

   bash
   source venv/bin/activate # On Windows, use 'venv\Scripts\activate'

2. Set the Flask app and run the server:

   bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   flask run

   The backend server will run on `http://localhost:5500`.

### Production Build

For production deployment, consider using a WSGI server like Gunicorn. Update the `gunicorn_config.py` file with your desired configurations, and run:

bash
gunicorn -c gunicorn_config.py app:app

## Contributing

If you'd like to contribute to Farmart's backend, please follow our [contribution guidelines](CONTRIBUTING.md).

## Authors

Authored by:

- MICHELLE MWANGI
- ENOCK SANG
- GLORY GWETH
- DONELL WAMBUA
- SHADRACK KIBET

## License

Licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

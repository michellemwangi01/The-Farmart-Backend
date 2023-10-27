# Installation & Setup of server

1. Clone repo onto local machine.
2. Create a new branch and checkout to it so you can continue to work from it. `git checkout -b ft-newbranchname`
3. cd into the server folder and enter virtual environment by typing `source venv/bin/activate`
4. Install requirements `pip install -r requirements.txt`
5. Run app: `python app.py`

# Database setup & upgrade

1. ````export FLASK_APP=app.py
         export FLASK_RUN_PORT=5555
         flask db init```
   ````
   2.flask db revision --autogenerate -m'Create tables owners, pets'
2. flask db upgrade

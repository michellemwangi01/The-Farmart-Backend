# Installation & Setup of server

1. Clone repo onto local machine.
2. Create a new branch and checkout to it so you can continue to work from it. `git checkout -b ft-newbranchname`
3. cd into the server folder and enter virtual environment by typing `source venv/bin/activate`
4. Install requirements `pip install -r requirements.txt`
5. Run app: `python app.py`

## SETUP STEPS

As a reminder, here are the steps we will follow: 0. Clone the repo to your local machine -> git clone repolink

1. Create your branch -> git branch yournewbranchname

- The format of the branch names should be ft-nameoffeature

2. Checkout or switch to your branch. DO NOT work on the main branch -> git checkout yournewbranchname
3. Pull the data from the development branch -> git pull origin development
4. start working work on your branch.
5. regularly push to your branch as you make progress -> git push origin yournewbranchname
6. Tell me when you are done with a feature so we can review it together and confirm it is okay.
7. If it is okay I merge your changes to the development branch.
8. Once I merge, everyone pulls the latest to their local -> git pull origin development
9. The cycle continues...

## Database setup & upgrade

1. ````export FLASK_APP=app.py
         export FLASK_RUN_PORT=5555
         flask db init```
   ````
   2.flask db revision --autogenerate -m'Create tables owners, pets'
2. flask db upgrade

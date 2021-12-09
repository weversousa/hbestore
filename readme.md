C:\programas\Python\Python310\python.exe -m venv env
env\Scripts\activate
pip install gunicorn Flask Flask-SQLAlchemy Flask-Migrate psycopg2-binary
pip freeze > requirements.txt

Procfile
web: gunicorn "app:create_app()"
<qualquer_coisa>: gunicorn "<pasta>:create_app()"

git init

heroku login
heroku create nome_projeto
heroku buildpacks:add heroku/python

heroku addons:create heroku-postgresql:hobby-dev
heroku pg:info
heroku pg:credentials:url

flask db init
flask db migrate
flask db upgrade

git add .
git commit -m ""
git push heroku main




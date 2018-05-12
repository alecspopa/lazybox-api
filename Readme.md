LazyBox API
===

#### Local setup

    pip install --dev pipenv

https://robots.thoughtbot.com/how-to-manage-your-python-projects-with-pipenv

    pipenv install
    pipenv shell
    
Run Flask API

    FLASK_APP=api.py FLASK_DEBUG=1 python -m flask run
    
## Deploy to Heroku

#####  Initial deploy

Set env vars:

    heroku config:set GOOGLE_APPLICATION_CREDENTIALS="$(< ../LazyBox-2582172d95b7.json)" --app lazybox-api
    heroku config:set FIREBASE_DATABASE_URL="https://lazybox-5fc02.firebaseio.com/" --app lazybox-api

All other deployments are done automatically on git push
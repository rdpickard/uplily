# UpLily

UpLily is a web service for uploading and downloading files over HTTP for situations where transferring files between
hosts is hindered by network policy or accessibility.

The service can run locally on a personal computer or 'serverless' cloud services such as AWS Elastic Beanstalk and
Heroku Dynamos.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Example use cases

#### Two users in different, non-publicly accessible networks

When two users are in networks that don't allow incoming connections from the Internet, set up a UpLily instance
in as a Heroku application as a 'drop off location'

#### User on corporate network that has constrained files leaving the network

#### Hosts on a LAN with no Internet access

### Recipes

#### Running on a free tier Heroku Dyno in the cloud

This method requires that you have [Git installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) (free), a Heroku [account](https://signup.heroku.com/) (free tier account works fine) and the Heroku command line tools [installed](https://devcenter.heroku.com/articles/heroku-cli) (free).
```
git clone https://github.com/rdpickard/uplily
cd uplily/
heroku create
git push heroku master
heroku ps:scale web=1
heroku open
```

After you're finished, stop and erase the Dyno
```
heroku destroy
```

#### Running on a locally on your machine

This method requires that you have Python 3.4 or greater [installed](https://realpython.com/installing-python/).

```
git clone https://github.com/rdpickard/uplily
cd uplily/
pip3 install -r requirements.txt
python3 application.py
```

This recipe works fine with a [python virtual environment](https://docs.python-guide.org/dev/virtualenvs/).

The output of running application.py will tell you the URL to access the web app.
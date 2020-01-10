# UpLily

UpLily is a web service for uploading and downloading files over HTTP in situations where transferring files between
hosts is hindered by network policy or accessibility.

The service can run locally on a personal computer or 'serverless' cloud services such as AWS Elastic Beanstalk and
Heroku Dynamos.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Example use cases

#### Two users in different, non-publicly accessible networks

When two users are in networks that don't allow incoming connections from the Internet, set up a UpLily instance
in as a Heroku application as a 'drop off location'

#### User on corporate network that has constrained files leaving the network

It isn't uncommon for corporate IT to put restrictions on network file transfers. Email size is often capped, filesharing sites such as AWS S3, box.com & PasteBin are often blocked by web proxies, protocols such as scp and ftp blocked at edge firewalls.

#### Hosts on a LAN with no Internet access

"Barebones" smart devices or appliances don't often have the capability to run file sharing protocols that are common on personal computers or full servers. HTTP is an almost universally supported protocol by even the most basic systems.

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

#### Running on a AWS Elastic-Beanstalk

This method requires you have an existing AWS [account](https://console.aws.amazon.com/?nc2=h_m_mc), the AWS command line tools [installed](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html).

_This method has a monetary cost billed by Amazon._ It is probably low, but it isn't free to run on AWS.

```
git clone https://github.com/rdpickard/uplily
cd uplily/
eb init -p python-3.6 uplily --region us-east-2
eb create uplily-env
eb open
```

After you're finished, stop and release all of the AWS resources
```
eb terminate
```
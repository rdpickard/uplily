# UpLily

UpLily is a web service for uploading and downloading files over HTTP for situations where transferring files between
hosts is hindered by network policy or accessibility.

The service can run locally on a personal computer or 'serverless' cloud services such as AWS Elastic Beanstalk and
Heroku Dynamos.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
##### Example use cases

###### Two users in different, non-publicly accessible networks
When two users are in networks that don't allow incoming connections from the Internet, set up a UpLily instance
in as a Heroku application as a 'drop off location'

###### User on corporate network that has constrained files leaving the network

###### Hosts on a LAN with no Internet access

##### Recipes

###### Running on a free tier Heroku Dyno in the cloud
```
git clone github.com:/rdpickard/uplily
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
[![Build Status](https://travis-ci.com/jorge-3/zerotribe.svg?token=CpgTPHGMFe4PoRnkeQqo&branch=master)](https://travis-ci.com/jorge-3/zerotribe)

# Running the application

- Checkout code on /opt/zerotribe on local computer
- Build the containers: ```docker-compose build```
- Copy settings.py.bak to settings.py and add 'mongodb' as MONGODB_HOST
- Start the application: ```docker-compose up```
- To start the application with pdb enabled: ```docker-compose run --rm --name zerotribe_web_1 --service-ports web python3 manage.py runserver```
- Run ```bower install``` for JS dependencies
- Create a ```~/.aws/credentials``` file with:
```
[default]
aws_access_key_id = xxx
aws_secret_access_key = xxx
```

# To access mongodb
- Find the docker web container name and run: ```docker exec -it zerotribe_web_1 mongo --host mongodb```

# To run tests
- Find the docker web container name and run: ```docker exec -it zerotribe_web_1 python tests.py```

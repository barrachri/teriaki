# Teriaki App
A `tasty` event driven api

## Vars to set inside worker/worker.py

```python
SMTP_SERVER = "" # SMTP server
SMTP_PORT = 0 # SMTP port
EMAIL_USER = "" # SMTP user
EMAIL_PASSWORD = "" # SMTP password
EMAIL_SENDER = ""  # Email sender
EMAIL_RECEIVER = "" # Email receiver
```

## RUN
```
pip install requirements.txt
docker run -d -p 5672:5672 --hostname my-rabbit --name some-rabbit rabbitmq:3.6.12
python app.py
```

## RUN TESTS
```
make test
```

## TODO
* add CI
* add more tests
* add docker compose
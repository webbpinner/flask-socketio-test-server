flask-socketio-test-server

#### To install server: ####
pip install ./requirements.txt

Also requires installing rabbitmq, sqlite3

#### To install client: ####
```
cd ./client
npm install
```

#### Starting server/client: #####
Start server via: `python app.py`.  Server runs on port 5000
Start client via: `npm start`.  Client runs on port 3000


#### Where I'm having an issue using rabbitmq as the flask-socketio message queue: ####
To change flask-socketio to use rabbitmq:
  - uncomment line 13 AND comment out line 14 on ./server/__init__.py
  - restart server


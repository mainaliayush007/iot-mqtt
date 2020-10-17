"""

A small Test application to show how to use Flask-MQTT.

"""

import eventlet
import json
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
import sqlite3
from flask_mail import Mail, Message



eventlet.monkey_patch()


app = Flask(__name__)
app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_CLIENT_ID'] = 'flask_mqtt'
app.config['MQTT_CLEAN_SESSION'] = True
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_LAST_WILL_TOPIC'] = 'home/lastwill'
app.config['MQTT_LAST_WILL_MESSAGE'] = 'bye'
app.config['MQTT_LAST_WILL_QOS'] = 2

# Parameters for SSL enabled
# app.config['MQTT_BROKER_PORT'] = 8883
# app.config['MQTT_TLS_ENABLED'] = True
# app.config['MQTT_TLS_INSECURE'] = True
# app.config['MQTT_TLS_CA_CERTS'] = 'ca.crt'

#For EMail

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "iotmqttipr@gmail.com"
app.config['MAIL_PASSWORD'] = "L@trobe2020"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

app.config.from_object(__name__)

mqtt = Mqtt(app)
mail =  Mail(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)
connection = sqlite3.connect("CpuInfo.db", check_same_thread=False)
c= connection.cursor()

subscribe = None
publish = None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return '<h1> This is the test page!</h1>'

@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    publish = data['topic']
    print("Publish is "+publish)
    print("Subscribe is "+subscribe)
    if(publish=="topic/cpu_request" and subscribe=="topic/cpu_reply"):
        sendEmail = False
        print("Inside")
        query = "Select * from CpuInfo Where Key = 'CPU_Usage' Order by id DESC LIMIT 10"
        datas = c.execute(query)
        myList = []
        for d in datas:
            myList.append(d[3])
            if(d[3]>50.00):
                sendEmail =  True
        print(myList)
        data['message'] = str(myList)
        data['topic'] = subscribe
        mqtt.publish(data['topic'], data['message'], data['qos'])
        if(sendEmail):
            send_email("Warning! CPU Usage is more than 50%" )

    elif(publish=="topic/mem_request" and subscribe=="topic/mem_reply"):
        print("Inside")
        query = "Select * from CpuInfo Where Key = 'Virtual_Memory' Order by id DESC LIMIT 10"
        sendEmail = False
        datas = c.execute(query)
        myList = []
        for d in datas:
            myList.append(d[3])
            if(d[3]>80.0):
                sendEmail = True
        print(myList)
        if(sendEmail):
            send_email("Warning! Memory Usage is more than 80% ")
        data['message'] = str(myList)
        data['topic'] = subscribe
        mqtt.publish(data['topic'], data['message'], data['qos'])



@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    global publish
    global subscribe
    subscribe = data['topic']
    print("Subscribe is "+subscribe)
    mqtt.subscribe(data['topic'], data['qos'])


    




@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode(),
        qos=message.qos,
    )
    socketio.emit('mqtt_message', data=data)


def send_email(message):
    
    try:
        with app.app_context():
            msg = Message("Sending email",
                sender="iotmqttipr@gmail.com",
                recipients=['mainaliayush2007@gmail.com'])
            msg.body= message
            print(msg)
            mail.send(msg)
            print("Bhayo holla")
    except Exception as ex:
            print("Bhayeana holla")
            print(str(ex))

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    # print(level, buf)
    pass


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)
    



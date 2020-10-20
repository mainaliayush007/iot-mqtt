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
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
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

subscribe = None
publish = None
isCpuRequest = False
isMemRequest = False


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return '<h1> This is the test page!</h1>'


def on_publish(client,userdata,result): #create function for callback
  print("published data is : ")
  pass

@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    global isCpuRequest
    global isMemRequest
    print("Publish is "+data['topic'])
    if(data['topic']=="topic/cpu_request"):
        mqtt.on_publish = on_publish
        mqtt.publish(data['topic'],'nothing')
        isCpuRequest = True
        isMemRequest = False
        
        
        mqtt.subscribe('topic/cpu_reply')
    elif(data['topic']=="topic/mem_request"):
        mqtt.on_publish = on_publish
        mqtt.publish(data['topic'],'nothing')
        
        
        mqtt.subscribe('topic/mem_reply')
        isCpuRequest = False
        isMemRequest = True
    




@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
   
    print(data)
   
    if(data['topic'=='topic/cpu_reply']):
         mqtt.subscribe(data['topic'])
         
         print('Subscribing in '+data['topic'])
    elif(data['topic'=='topic/mem_reply']):
         mqtt.subscribe(data['topic'])
         print('Subscribing in '+data['topic'])
         


    




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
    # for ele in data['payload']:
    #     print(ele)
    socketio.emit('mqtt_message', data=data)
    items = data['payload']
    if(isCpuRequest):
        print("CPU REQUEST ",items)
        items = items[1:-1]
        items = items.split(',')
        print(items)
        for item in items:
            print(item)
            if(float(item)>50.00):
                sendEmail = True
                
    
            
    elif(isMemRequest):
        print("MEM REQUEST ",items)
        items = items[1:-1]
        items = items.split(',')
        print(items)
        for item in items:
            print(item)
            if(float(item)>80.00):
                sendEmail = True
                
    if(sendEmail):
        
        msg =""
        if(isCpuRequest):
            message="Warning!  CPU Usage more than 50 percent!"
        elif(isMemRequest):
            message = "Warning!  Memory Usage more than 80 percent!"
        print("Inside send email: ",msg)
        try:
            with app.app_context():
                msg = Message("Warning!",
                    sender="iotmqttipr@gmail.com",
                    recipients=['mainaliayush2007@gmail.com'])
                msg.body= message
                print(msg)
                mail.send(msg)
        except Exception as ex:
            print(str(ex))
            
                

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
    



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 18:14:04 2020

@author: mainaliayush2007
"""


import socket 
from threading import Thread 
import sqlite3
import datetime
import paho.mqtt.client as paho
import time

thread_process_list=list()
connection = sqlite3.connect("CpuInfo.db", check_same_thread=False)
threads = [] 
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ip_port = ("127.0.0.1",8080)
c= connection.cursor()
broker = "broker.hivemq.com"
topic_subscribe1="topic/cpu_request"
topic_subscribe2='topic/mem_request'


#Multithread
class ClientThread(Thread): 
 
    def __init__(self,ip,port): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
 
    def run(self): 
       server.listen(4) 
       (conn, (ip,port)) = server.accept() 
       
       while True : 
            data = conn.recv(2048)
            msg = data.decode()
            dt = eval(msg) 
            process_storeData(dt,ip,port)


            if not data: 
                break
            conn.send(data) 
 
class PubSubThread(Thread):
    def __init__(self,topic):
        Thread.__init__(self)
        self.topic = topic
    def run(self):
        client = paho.Client('User')
        client.on_message = on_message  
        print("Connecting to the broker host ",broker)
        client.connect(broker)
        print("Subscribing begins here")
        client.subscribe(topic_subscribe1)
        client.subscribe(topic_subscribe2)
        client.on_publish = on_publish
        client.loop_forever() 
        
def on_message(client,userdata,message):
     
    
    if(str(message.topic)==topic_subscribe1 and str(message.payload.decode("utf-8"))=="nothing"):
        recentData= str(get10RecentData("CPU_Usage"))
        print(recentData)
        client.publish("topic/cpu_reply",recentData)
        
    elif(str(message.topic)==topic_subscribe2 and str(message.payload.decode("utf-8"))=="nothing"):
        recentData= str(get10RecentData("Virtual_Memory"))
        print(recentData)
        client.publish("topic/mem_reply",recentData)
    
def on_publish(client,userdata,result): #create function for callback
  print("published data is : ",userdata)
  
  

def main():
    createDb()
    server.bind(ip_port)
    server.listen(4) 
    (conn, (ip,port)) = server.accept() 
    threads.append(PubSubThread("topic/cpu_request").start())
    
   
    
   

    while True: 
        message_recv = conn.recv(1024)
        dt = eval(message_recv)
        process_storeData(dt,ip,port)

        newthread = ClientThread(ip,port)
        newthread.start() 
        threads.append(newthread) 
     
    for t in threads: 
        t.join()
    


def get10RecentData(data):
    print("get 10 recent data ",data)
   
    try:
        query = "Select * from CpuInfo Where Key = '"+data+"' Order by id DESC LIMIT 10"
        
        datas = c.execute(query)
    except sqlite3.Error as error:
                    print(error)
   
    myList = []
    for d in datas:
        myList.append(d[3])
    print(data+" "+str(myList))
    
    return myList
   


def createDb():
    
    c.execute("CREATE TABLE IF NOT EXISTS CpuInfo (id INTEGER PRIMARY KEY AUTOINCREMENT ,DateTime TEXT, Key TEXT ,Value REAL)")
   
def process_storeData(dt,ip,port):
    # print(dt)
    if(dt['Key']=='CPU_Usage'):
            if(float(dt['Value']>30.0)):
                valueList = list()
                valueList.append(str(datetime.datetime.now()))
                valueList.append(dt['Key'])
                valueList.append(dt['Value'])
                print("CPU Usage more than 30%")
                try:
                    c.execute("Insert into CpuInfo (DateTime, Key, Value ) VALUES (?,?,?)",tuple(valueList))
                    valueList.clear()
                    connection.commit()
                    print("Inserted CPU Usage")
                except sqlite3.Error as error:
                    print(error)
    elif(dt['Key']=='Virtual_Memory'):
        if(float(dt['Value']>80.0)):
            valueList = list()
            valueList.append(str(datetime.datetime.now()))
            valueList.append(dt['Key'])
            valueList.append(dt['Value'])
            print("Memory Usage more than 40%")
            try:
                c.execute("Insert into CpuInfo (DateTime, Key, Value ) VALUES (?,?,?)",tuple(valueList))
                valueList.clear()
                connection.commit()
                print("Inserted Memory Usage")
            except sqlite3.Error as error:
                print(error)
            
    

if __name__ =="__main__":
         main()

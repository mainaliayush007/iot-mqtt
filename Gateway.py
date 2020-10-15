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

thread_process_list=list()
connection = sqlite3.connect("MyDb.db", check_same_thread=False)
threads = [] 
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ip_port = ("127.0.0.1",8080)
c= connection.cursor()

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
            # if(dt['Key']=='CPUUsage'):
            #     if(float(dt['Value']>10.0) and float(dt['Value']<30.0) ):
            #         print("CPU Usage from the node "+str((ip,port)) +" is "+dt['Value'])
            #         print("CPU Usage between 10 and 30%")
            #     elif(float(dt['Value']>30.0)):
            #         valueList = list()
            #         valueList.append(datetime.now())
            #         valueList.append("CPU_Usage")
            #         valueList.append(dt['Value'])
            #         print("CPU Usage more than 30%")
            #         try:
            #             c.execute("Insert into CpuInfo (DateTime, Key, Value ) VALUES (?,?,?)",tuple(valueList))
            #             valueList.clear()
            #             connection.commit()
            #             print("Inserted")
            #         except sqlite3.Error as error:
            #             print(error)
            
                    
                
           
            # if(msg.contains("CPUUsage")):
                
            #     pass
            # elif(msg.contains("VirtualMemory")):
            #     pass
                
            
            # print(data.decode() + " From the node "+ str((ip,port)))
            # if(len(thread_process_list)==0 or port not in thread_process_list):
            #     print(str((ip,port)),"Joined!")
            #     thread_process_list.append(port)

            if not data: 
                break
            conn.send(data) 
 

def main():
 
    createDb()
    server.bind(ip_port)
    server.listen(4) 
    (conn, (ip,port)) = server.accept() 

    while True: 
        message_recv = conn.recv(1024)
        dt = eval(message_recv)
        # process_storeData(dt,ip,port)

        if(dt['Key']=='CPU_Usage'):
            if(float(dt['Value']>30.0)):
                valueList = list()
                valueList.append(str(datetime.datetime.now()))
                valueList.append("CPU_Usage")
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
            if(float(dt['Value']>40.0)):
                valueList = list()
                valueList.append(str(datetime.datetime.now()))
                valueList.append("Virtual_Memory")
                valueList.append(dt['Value'])
                print("Memory Usage more than 40%")
                try:
                    c.execute("Insert into CpuInfo (DateTime, Key, Value ) VALUES (?,?,?)",tuple(valueList))
                    valueList.clear()
                    connection.commit()
                    print("Inserted Memory Usage")
                except sqlite3.Error as error:
                        print(error)
        newthread = ClientThread(ip,port)
        newthread.start() 
        threads.append(newthread) 
     
    for t in threads: 
        t.join()   

def createDb():
    
    c.execute("CREATE TABLE IF NOT EXISTS CpuInfo (DateTime TEXT, Key TEXT, Value REAL)")

def process_storeData(dt,ip,port):
    print(dt)
    if(dt['Key']=='CPU_Usage'):
            if(float(dt['Value']>30.0)):
                valueList = list()
                valueList.append(str(datetime.datetime.now()))
                valueList.append("CPU_Usage")
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
        if(float(dt['Value']>40.0)):
            valueList = list()
            valueList.append(str(datetime.datetime.now()))
            valueList.append("Virtual_Memory")
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
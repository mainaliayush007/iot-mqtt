#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 17:48:32 2020

@author: mainaliayush2007
"""


import socket
import psutil
import time


def process1():
    socket_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    ip_port = ("127.0.0.1",8080)
    socket_client.connect(ip_port) 
    socket_client.settimeout(60)
    while 1:    
        try:
            
            msg = "Virtual memory usage: "+ str(psutil.virtual_memory()[2]) 
            print(msg)
            socket_client.send(msg.encode())
            
            time.sleep(3)
        except BrokenPipeError as ex:
            print(ex)
            socket_client.close()
        
        
        
if __name__ == '__main__' :
    process1()
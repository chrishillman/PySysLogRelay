#!/usr/bin/env python
import socket
import logging
import SocketServer
import sqlite3
import datetime

content=""
LISTEN_HOST, LISTEN_PORT, SEND_HOST, SEND_PORT, LOG_FILE = "0.0.0.0", 514, "127.0.0.1", 515, 'syslogfile_proxy.log'

try:
    with open("syslog.ini") as file:
        content = file.readlines()
    for line in content:
        if (line.split("=")[0] == "LOG_FILE"):
            LOG_FILE = line.split("=")[1].strip()
        if (line.split("=")[0] == "LISTEN_HOST"):
            LISTEN_HOST = line.split("=")[1].strip()
        if (line.split("=")[0] == "LISTEN_PORT"):
            LISTEN_PORT = int(line.split("=")[1])
        if (line.split("=")[0] == "SEND_HOST"):
            SEND_HOST = line.split("=")[1].strip()
        if (line.split("=")[0] == "SEND_PORT"):
            SEND_PORT = int(line.split("=")[1])
except (IOError, SystemExit):
    file = open("syslog.ini", 'w')
    file.write("LOG_FILE="+LOG_FILE + '\n')
    file.write("LISTEN_HOST="+LISTEN_HOST+ '\n')
    file.write("LISTEN_PORT="+str(LISTEN_PORT)+ '\n')
    file.write("SEND_HOST="+SEND_HOST+ '\n')
    file.write("SEND_PORT="+str(SEND_PORT)+ '\n')

print("Configuration:" + '\n')
print("LOG_FILE="+LOG_FILE + '\n')
print("LISTEN_HOST="+LISTEN_HOST+ '\n')
print("LISTEN_PORT="+str(LISTEN_PORT)+ '\n')
print("SEND_HOST="+SEND_HOST+ '\n')
print("SEND_PORT="+str(SEND_PORT)+ '\n')
print('\n'+" Display Logged Data: "+'\n')

conn = sqlite3.connect('syslog.db')
cursor = conn.cursor()
try:
    cursor.execute('''CREATE TABLE syslog (time_stamp text, source text, message text)''')
except:
    print("error on table create")
    pass

class SyslogUDPHandler(SocketServer.BaseRequestHandler):
 
    def handle(self):
        data = bytes.decode(self.request[0].strip())
        print( "%s : " % self.client_address[0], str(data))
        try:
            cursor.execute('INSERT INTO syslog values (?,?,?)', (datetime.datetime.now().strftime("%y%m%d%H%M%S%f"), self.client_address[0], str(data)))
        except:
            print("error on insert")
            raise
            pass
        conn.commit()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (SEND_HOST, SEND_PORT))
 
if __name__ == "__main__":
        try:
                server = SocketServer.UDPServer((LISTEN_HOST,LISTEN_PORT), SyslogUDPHandler)
                server.serve_forever(poll_interval=0.25)
        except (IOError, SystemExit):
                raise
        except KeyboardInterrupt:
                print ("Crtl+C Pressed. Shutting down.")
                conn.close()

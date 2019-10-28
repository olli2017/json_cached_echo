#!/usr/bin/env python3
import os
import socket
import redis
import json

HOST = ""  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


def sendMsg(conn, message):
    conn.sendall(message.encode('utf-8'))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    cache = redis.Redis(host='rediska', port=6379)
    cache.ping()

    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)

            if not data:
                break

            response = {}
            parsed_json = {"action": 0}
            try:
                parsed_json = json.loads(data)
            except ValueError as e:
                response["status"] = "Bad Request"

            action = parsed_json["action"]
            if action == "put":
                if cache.exists(parsed_json["key"]):
                    response["status"] = "Ok"
                else:
                    response["status"] = "Created"
                cache.set(parsed_json["key"], parsed_json["message"])

            if action == "get":
                key = cache.get(parsed_json["key"])

                if key is None:
                    response["Status"] = "Not Found"
                else:
                    response["status"] = "Ok"
                    if type(key) is bytes:
                        response["message"] = key.decode('utf-8')
                    else:
                        response["message"] = key

            if action == "delete":
                if cache.exists(parsed_json["key"]):
                    cache.delete(parsed_json["key"])
                    response["status"] = "Ok"
                else:
                    response["status"] = "Not Found"

            json_string = json.dumps(response)
            sendMsg(conn, json_string + "\n")
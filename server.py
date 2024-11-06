import json
import socket
import threading
from random import randint


class SocketEncoder(json.JSONEncoder):

	def default(self, obj):
		if isinstance(obj, socket.socket):
			return str(obj)
	
		return super(SocketEncoder, self).default(obj)


next_client_id = 0
active_clients: list[tuple[str, str, socket.socket]] = [] # TODO: set in redis ???

def handle_client(client_socket, client_address):
	global active_clients
	
	try:
		while True:
			# Receive data from client
			data = client_socket.recv(1024)
			if not data:
				break

			
			data = data.decode('utf-8')
			print(data)
			data = data.split("||")
			message_type = data[0]
			if message_type == "MESSAGE":
				client_id, message = data[1], data[2]
				for client in active_clients:
					if client_id == client[0]:
						message = f"MESSAGE||{message}"
						client[2].send(message.encode("utf-8"))
	finally:
		for i, client in enumerate(active_clients):
			if client[2] == client_socket:
				if i == 0:
					active_clients = active_clients[1:]
				elif i == len(active_clients)-1:
					active_clients = active_clients[:-1]
				else:
					active_clients = active_clients[:i] + active_clients[i+1:]
		client_socket.close()

def start_server(host='localhost', port=5555):
	global active_clients
	global next_client_id

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind((host, port))
	server_socket.listen()

	print(f"Server listening on {host}:{port}")

	while True:
		client_socket, client_address = server_socket.accept()
		print(f"Client connected from {client_address}")

		data = client_socket.recv(1024).decode('utf-8')
	
		data = data.split("||")		
		message_type = data[0]
		
		if message_type == "PUB_KEY":
			pub_key = data[1]
			new_client = (f"{next_client_id}", pub_key, client_socket)
			active_clients.append(new_client)
			next_client_id += 1
		
		print(active_clients)
		
		# send updated active_clients to clients
		for client in active_clients:
			message = f"ACTIVE_CLIENTS||{json.dumps(active_clients, cls=SocketEncoder)}"
			print(f"Send list of clients to new client: {message}")
			client[2].send(message.encode("utf-8"))
			

		# Handle client communication in a new thread
		client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
		client_thread.start()

start_server()

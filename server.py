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
active_clients: list[tuple[str, str, socket.socket]] = []

def handle_client(client_socket, client_address):
	global active_clients
	
	try:
		while True:
			# Receive data from client
			data = client_socket.recv(1024)
			if not data:
				break

			
			socket_message = json.loads(data.decode('utf-8'))
			message_type = socket_message.get("type", "")

			if message_type == "MESSAGE":
				client_id = socket_message["data"]["client_id"]
				for client in active_clients:
					print(client_id, client[0])
					if client_id == client[0]:
						socket_message = json.dumps(socket_message)
						client[2].send(socket_message.encode("utf-8"))
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

		socket_message = client_socket.recv(1024).decode('utf-8')
	
		socket_message = json.loads(socket_message)
		message_type = socket_message.get("type", "")
		
		if message_type == "PUB_KEY":
			pub_key = socket_message["data"]
			new_client = (f"{next_client_id}", pub_key, client_socket)
			active_clients.append(new_client)
			next_client_id += 1
		
		print(active_clients)
		
		# send updated active_clients to clients
		for client in active_clients:
			socket_message = {"type": "ACTIVE_CLIENTS", "data": active_clients}
			socket_message = json.dumps(socket_message, cls=SocketEncoder)
			print(f"Send list of clients to new client: {socket_message}")
			client[2].send(socket_message.encode("utf-8"))
			

		# Handle client communication in a new thread
		client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
		client_thread.start()

start_server()

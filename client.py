import json
import socket
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext

from rsa_code import decrypt, encrypt, generate_keys


class ChatClient:
	def __init__(self):
		self.public_key, self.private_key = generate_keys()
		
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect(('localhost', 5555))
		self.running = True
		self.pub_keys: list[list[str, list, str]] = []  # (client_id, client_pub_key, client_socket)
		
		# Tkinter GUI
		self.root = tk.Tk()
		self.root.title("Encrypted Chat")
		self.root.geometry("800x600")
		self.root.columnconfigure(0, weight=1)
		self.root.columnconfigure(1, weight=1)
		self.root.columnconfigure(2, weight=1)
		self.root.columnconfigure(3, weight=1)
		self.root.columnconfigure(4, weight=1)
  
		self.root.rowconfigure(0, weight=1)
		self.root.rowconfigure(1, weight=1)
		self.root.rowconfigure(2, weight=1)
		self.root.rowconfigure(3, weight=1)
		self.root.rowconfigure(4, weight=1)

		self.join_button = tk.Button(self.root, text="Send", command=self.send_pub_key)
		self.join_button.grid(column=2, row=2)

	def send_pub_key(self):
		socket_message = {"type": "PUB_KEY", "data": self.public_key}
		socket_message = json.dumps(socket_message)
		self.sock.sendall(socket_message.encode("utf-8"))
		
		# Iterate through every widget inside the root
		for widget in self.root.winfo_children():
			widget.destroy()  # deleting widget
		
		self.main_window()
		
	def main_window(self):
		self.client_id = tk.Entry(self.root)
		self.client_id.grid(column=0, row=0, columnspan=2)
  
		self.messages_outgoing = scrolledtext.ScrolledText(self.root)
		self.messages_outgoing.grid(column=0, row=1, columnspan=2, rowspan=3)
		
		self.send_button = tk.Button(self.root, text="Send message", command=self.send_message)
		self.send_button.grid(column=0, row=4, columnspan=2)
 
		self.available_clients = scrolledtext.ScrolledText(self.root)
		self.available_clients.insert(tk.END, self.get_available_clients())
		self.available_clients.config(state='disabled')
		self.available_clients.grid(column=3, row=0, columnspan=2, rowspan=2)
  
		self.messages_incoming = scrolledtext.ScrolledText(self.root, state='disabled')
		self.messages_incoming.grid(column=3, row=3, columnspan=2, rowspan=2)
  
		self.thread = threading.Thread(target=self.receive_messages, daemon=True)
		self.thread.start()
 
	def get_available_clients(self) -> str:
		clients_str = ""
		for client in self.pub_keys:
			clients_str += f"{'Client' if self.public_key != tuple(client[1]) else 'My'} id: {client[0]}, client pub key: {client[1]}\n"
		return clients_str
 
	def send_message(self):
		client_id = self.client_id.get()
		message = self.messages_outgoing.get('1.0', tk.END)
  
		print(f"Send message to client: {client_id}, message: {message}")
		for client in self.pub_keys:
			if client[0] == client_id:
				pub_key = client[1]
				socket_message = {"type": "MESSAGE", "data": {"client_id": client_id, "message": encrypt(pub_key, message)}}
				socket_message = json.dumps(socket_message)

				self.sock.sendall(socket_message.encode("utf-8"))
		
	def receive_messages(self):
		while self.running:
			try:
				data = self.sock.recv(1024)
				if data:
					socket_message = json.loads(data.decode("utf-8"))
					message_type = socket_message.get("type", "")
					print(socket_message)
					if message_type == "MESSAGE":
						message = socket_message["data"]["message"]
						decrypted_message = decrypt(self.private_key, message)
						self.messages_incoming.config(state='normal')
						self.messages_incoming.insert(tk.END, decrypted_message + "\n")
						self.messages_incoming.config(state='disabled')
					elif message_type == "ACTIVE_CLIENTS":
						clients = socket_message["data"]
						print(clients)
						self.pub_keys = clients
						self.available_clients.config(state='normal')
						self.available_clients.delete("1.0", tk.END)
						self.available_clients.insert(tk.END, self.get_available_clients())
						self.available_clients.config(state='disabled')
			except OSError:
				break
	
	def quit(self):
		self.running = False  # Stop the receive loop
		self.sock.close()  # Close the socket connection
		self.root.quit()
		self.root.destroy()
 
	def run(self):
		self.root.protocol("WM_DELETE_WINDOW", self.quit)
		self.root.mainloop()
		

client = ChatClient()
client.run()
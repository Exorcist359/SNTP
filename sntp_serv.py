from socket import *
from datetime import datetime


SERV_IP = 'localhost'
SERV_PORT = 123
EPOCH_TIME = datetime(1900, 1, 1)

try:
    with open('DELTA.conf') as f:
        DELTA = int(f.read())
except Exception():
    DELTA = 0
            
def get_answer(inp, recv_time):
    n_prot = '{:08b}'.format(inp[0])[2:5]
    
    first_byte = chr(int('00'+n_prot+'100', 2)).encode()
    stratum = b'\x01'
    poll_interval = b'\x00'
    clock_precision = (-20).to_bytes(1, 'big', signed=True)
    root_delay = b'\x00' * 4
    root_despersion = b'\x00' * 4
    reference_id = b'LOCL'
    origin_timestamp = inp[40:48]
    
    return first_byte + stratum + poll_interval + clock_precision \
        + root_delay + root_despersion + reference_id \
        + get_currect_time() + origin_timestamp + recv_time
    
def get_time_in_bytes(time):
    integ, fract = str(time).split('.')
    return int(integ).to_bytes(4, 'big') + int(fract).to_bytes(4, 'big')
    
def get_currect_time():
    return get_time_in_bytes((datetime.utcnow() - EPOCH_TIME).total_seconds() + DELTA)
    
def start_server():
    srv_sock = socket(AF_INET, SOCK_DGRAM)
    
    try:
        srv_sock.bind((SERV_IP, SERV_PORT))
    except Exception:
        print('Something\'s wrong ... Check the port 123')
        srv_sock.close()
        exit(0)
    
    print('Wait for clients...')
    
    while True:
        data, addr = srv_sock.recvfrom(1024)
        try:
            if data:   
                print('{} connected'.format(addr))
                            
                recv_time = get_currect_time()
                
                answ = get_answer(data, recv_time)
                srv_sock.sendto(answ + get_currect_time(), addr)
        except Exception:
            print('Incorrect connection from {}'.format(addr))
            
if __name__ == '__main__':    
    start_server()
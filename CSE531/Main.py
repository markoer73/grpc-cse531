#
#   Main.py
#
# Marco Ermini - March 2021 for ASU CSE531 Course
# Do not leech!
# Built with python 3.8 with GRPC and GRPC-tools libraries; may work with other Python versions
'''Implementation of a banking's branches/customers RPC synchronisation using GRPC, multiprocessing and Python
Main spawner'''

import logging
import multiprocessing
import sys
import contextlib
import logging
import socket
import argparse
import json

from concurrent import futures
from Branch import Branch
from Customer import Customer

import grpc

import banking_pb2
import banking_pb2_grpc

# Global logger
LOGGER = logging.getLogger(__name__)

#
# Multiprocessing reused from https://github.com/grpc/grpc/tree/801c2fd832ec964d04a847c6542198db093ff81d/examples/python/multiprocessing
#

#ONE_DAY = datetime.timedelta(days=1)
# the number of branches and customers are setup as equal the number of CPUs enumerated by Python
THREAD_CONCURRENCY = multiprocessing.cpu_count()
SLEEP_SECONDS = 3
PROCESS_COUNT = 4
#STARTING_PORT = 50000

# Moved to Branch.py
#def Wait_Forever(server):
#    try:
#        while True:
#            time.sleep(ONE_DAY.total_seconds())
#    except KeyboardInterrupt:
#        server.stop(None)
#
#def Run_Branch(branch, bind_address):
#    """Start a server (branch) in a subprocess."""
#    LOGGER.info('Starting branch #{branch.ID] at {bind_address}')
#    options = (('grpc.so_reuseport', 1),)
#
#    server = grpc.server(futures.ThreadPoolExecutor(
#        max_workers=_THREAD_CONCURRENCY,),
#                         options=options)
# 
#    BankingRPC_pb2_grpc.add_BankingRPC_to_server(branch, server)
#
#    server.add_insecure_port(bind_address)
#    server.start()
#    Wait_Forever(server)

# First version
#def _run_branch(branch):
#    logger = logging.getLogger(LOG_NAME)
#    address = f'[::]:{50000 + branch.id_}'
#    options = (('grpc.so_reuseport', 1),)
#    logger.info(f'Starting branch {branch.id_} at {address}.')
#    server = grpc.server(futures.ThreadPoolExecutor(max_workers=THREAD_CONCURRENCY), options=options)
#    rpc_pb2_grpc.add_RPCServicer_to_server(branch, server)
#    server.add_insecure_port(address)
#    server.start()
#    _wait_forever(server)


def Process_Args():
    """Parse arguments."""
    all_args = argparse.ArgumentParser(description='Input and Output file names')
    all_args.add_argument('-i', '--Input', required=False, help='File name containing branches and customers, in JSON format (optional; defaults to input.json')
    all_args.add_argument('-o', '--Output', required=False, help='Output file name to use (optional; defaults to output.json)')
    args = all_args.parse_args()
    return args.Input.strip(), args.Output.strip()


def Load_Input_File(filename, branches, customers):
    """Load from input files."""
    try:
        file = open(filename)
    except OSError:
        raise RuntimeError(f'Failed to open {filename}.')
    
    items = json.load(file)
    # Retrieves:
    #   the branches' list and populate IDs and balances
    #   the customers' operations and populate events
    for item in items:
        if item['type'] == 'branch':
            branch = Branch(item['id'], item['balance'], list())
            branches.append(branch)
        if item['type'] == 'customer':
            events = list()
            for event in item['events']:
                events.append(event)
            customer = Customer(item['id'], events)
            customers.append(customer)

    # Append the list of all branches to every branch
    for b in branches:
        for b1 in branches:
            b.branches.append(b1.id)
        LOGGER.info(f'Branch #{b.id} initialised with Balance={b.balance}, Known Branches={b.branches}')
    # Append the list of all events to customers
    for c in customers:
        for e in c.events:
            LOGGER.info(f'Customer #{c.id} -> Event #{e["id"]}, {e["interface"]}, {e["money"]}')

    file.close()


@contextlib.contextmanager
def Reserve_Port():
    """Find and reserve a port for the subprocess to use."""
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    if  sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 0:
        raise RuntimeError("Failed to set SO_REUSEPORT.")
    sock.bind(('', 0))
    try:
        yield sock.getsockname()[1]
    finally:
        sock.close()

def main():
    """Main function."""
    input_file, output_file = Process_Args()
    if not input_file:
        input_file = 'input.json'
    if not output_file:
        output_file = 'output.json'
    branches = list()
    customers = list()
    Load_Input_File(input_file, branches, customers)
    workers = list()
    workers = []

    # Spawns processes for branches
    #
    # NOTE: It is imperative that the worker subprocesses be forked before
    # any gRPC servers start up. See
    # https://github.com/grpc/grpc/issues/16001 for more details.

    for curr_branch in branches:
        with Reserve_Port() as curr_port:
            bind_address = '[::]:{}'.format(curr_port)
        
            LOGGER.info(f'Reserved {bind_address} for Branch #{curr_branch.id}...')
            sys.stdout.flush()
        
            worker = multiprocessing.Process(name=f'Branch-{curr_branch.id}', target=Branch.Run_Branch,
                                                args=(Branch,bind_address,LOGGER,THREAD_CONCURRENCY))
            worker.start()
            workers.append(worker)
            
            LOGGER.info(f'Started branch \"{worker.name}\" with PID {worker.pid} at address {bind_address} successfully')
            sys.stdout.flush()
    
    for worker in workers:
        worker.join()


if __name__ == '__main__':
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[PID %(process)d %(asctime)s] %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)
    main()

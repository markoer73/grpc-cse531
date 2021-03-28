#
#   Customer.py
#
# Marco Ermini - March 2021 for ASU CSE531 Course
# Do not leech!
# Built with python 3.8 with GRPC and GRPC-tools libraries; may work with other Python versions
'''Implementation of a banking's branches/customers RPC synchronisation using GRPC, multiprocessing and Python
Customer Class'''

import time
import datetime
import sys
import multiprocessing
import array

from concurrent import futures

import grpc
import banking_pb2
import banking_pb2_grpc

class Customer:
    def __init__(self, ID, events):
        # unique ID of the Customer
        self.id = ID
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # pointer for the stub
        self.stub = None

    # Create stub for the customer, matching them with their own branch
    def createStub(self, LOGGER):
        """Start a client (customer) stub."""
        LOGGER.info(f'Running customer\'s stub...')
        sys.stdout.flush()



        branch_address = f'localhost:{50000 + self.id_}'
        logger.info(f'Initializing customer stub {self.id_} to branch stub at {branch_address}')
        self.stub = rpc_pb2_grpc.RPCStub(grpc.insecure_channel(branch_address))


    # TODO: students are expected to send out the events to the Bank
    def executeEvents(self):
        pass



    # Spawn the Customer process server
    #
    def Run_Customer(self, Branch_address, LOGGER, THREAD_CONCURRENCY):
        """Start a client (customer) in a subprocess."""
        LOGGER.info(f'Running customer connecting to server {Branch_address}...')
        sys.stdout.flush()

        #options = (('grpc.so_reuseport', 1),)

        server = grpc.server(futures.ThreadPoolExecutor(
            max_workers=THREAD_CONCURRENCY,),
                             )

        #banking_pb2_grpc.add_BankingServicer_to_server(Customer, server)

        #server.add_insecure_port(bind_address)
        server.start()

        # Wait one day until keypress
        #try:
        #    while True:
        #        time.sleep(ONE_DAY.total_seconds())
        #except KeyboardInterrupt:
        #    server.stop(None)
        server.stop(None)
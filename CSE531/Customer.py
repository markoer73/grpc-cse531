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
import multiprocessing
#import array
import json

from concurrent import futures
from Util import setup_logger, MyLog

import grpc
import banking_pb2
import banking_pb2_grpc

#from Main import get_operation, get_operation_name, get_result_name

ONE_DAY = datetime.timedelta(days=1)
logger = setup_logger("Customer")

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

    # Create stub for the customer, matching them with their respective branch
    #
    def createStub(self, Branch_address, THREAD_CONCURRENCY):
        """Start a client (customer) stub."""
        
        MyLog(logger, f'Initializing customer stub to branch stub at {Branch_address}')
        
        self.stub = banking_pb2_grpc.BankingStub(grpc.insecure_channel(Branch_address))

        client = grpc.server(futures.ThreadPoolExecutor(max_workers=THREAD_CONCURRENCY,),)
        #banking_pb2_grpc.add_BankingServicer_to_server(Customer, client)
        client.start()

    # Iterate through the list of the customer events, sends the messages,
    # and output to the JSON file
    #
    def executeEvents(self, output_file):
        """Execute customer events."""
        
        # DEBUG
        #MyLog(logger,f'Executing events for Customer #{self.id}')
                
        record = {'id': self.id, 'recv': []}
        for event in self.events:
            request_id = event['id']
            request_operation = get_operation(event['interface'])
            request_amount = event['money']
            response = self.stub.MsgDelivery(
                banking_pb2.MsgDeliveryRequest(
                    S_ID=request_id,
                    OP=request_operation,
                    Amount=request_amount,
                    D_ID=self.id,
                )
            )
            MyLog(logger,
                f'Customer {self.id} sent request {request_id} to Branch {response.ID} '
                f'interface {get_operation_name(request_operation)} result {get_result_name(response.RC)} '
                f'money {response.Amount}')
            values = {
                'interface': get_operation_name(request_operation),
                'result': get_result_name(response.RC),
            }
            if request_operation == banking_pb2.QUERY:
                values['money'] = response.Amount
            record['recv'].append(values)
        if record['recv']:
            # DEBUG
            #MyLog(logger,f'Writing JSON file on #{output_file}')
            with open(f'{output_file}', 'a') as outfile:
                json.dump(record, outfile)
                outfile.write('\n')

    # Spawn the Customer process client. No need to bind to a port here; rather, we are connecting to one.
    #
    def Run_Customer(self, Branch_address, output_file, THREAD_CONCURRENCY):
        """Start a client (customer) in a subprocess."""
        # DEBUG
        #MyLog(logger,f'Processing Customer #{self.id} with Events:' )
        #for e in self.events:
        #    MyLog(logger,f'    #{e["id"]} = {e["interface"]}, {e["money"]}' )
                
        MyLog(logger,f'Running client customer #{self.id} connecting to server {Branch_address}...')

        Customer.createStub(self, Branch_address, THREAD_CONCURRENCY)
        Customer.executeEvents(self, output_file)

        # Wait one day until keypress
        #try:
        #    while True:
        #        time.sleep(ONE_DAY.total_seconds())
        #except KeyboardInterrupt:
        #    server.stop(None)
        
        MyLog(logger,f'Client customer #{self.id} connecting to server {Branch_address} exiting successfully.')

# Utility functions, used for readability
#
def get_operation(operation):
    """Returns the message type from the operation described in the input file."""
    if operation == 'query':
        return banking_pb2.QUERY
    if operation == 'deposit':
        return banking_pb2.DEPOSIT
    if operation == 'withdraw':
        return banking_pb2.WITHDRAW

def get_operation_name(operation):
    """Returns the operation type from the message."""
    if operation == banking_pb2.QUERY:
        return 'QUERY'
    if operation == banking_pb2.DEPOSIT:
        return 'DEPOSIT'
    if operation == banking_pb2.WITHDRAW:
        return 'WITHDRAW'

def get_result_name(name):
    """Return state of a client's operation."""
    if name == banking_pb2.SUCCESS:
        return 'SUCCESS'
    if name == banking_pb2.FAILURE:
        return 'FAILURE'
    if name == banking_pb2.ERROR:
        return 'ERROR'
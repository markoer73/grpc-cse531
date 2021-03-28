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

ONE_DAY = datetime.timedelta(days=1)


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
    def createStub(self, Branch_address, LOGGER, THREAD_CONCURRENCY):
        """Start a client (customer) stub."""
        
        LOGGER.info(f'Initializing customer stub to branch stub at {Branch_address}')
        sys.stdout.flush()

        self.stub = banking_pb2_grpc.BankingStub(grpc.insecure_channel(Branch_address))

        client = grpc.server(futures.ThreadPoolExecutor(max_workers=THREAD_CONCURRENCY,),)
        #banking_pb2_grpc.add_BankingServicer_to_server(Customer, client)
        client.start()

    # Iterate through the list of the customer events, sends the messages,
    # and output to the JSON file
    #
    def executeEvents(self, LOGGER, output_file):
        """Execute customer events."""
        
        # DEBUG
        LOGGER.info(f'Executing events for Customer #{self.id}')
        sys.stdout.flush()
                
        record = {'id': self.id, 'recv': []}
        for event in self.events:
            request_id = event['id']
            request_interface = get_interface(event['interface'])
            request_money = event['money']
            response = self.stub.MsgDelivery(
                banking_pb2.MsgDeliveryRequest(
                    id_=request_id,
                    interface=request_interface,
                    money=request_money,
                    dest=self.id_,
                )
            )
            LOGGER.info(
                f'Customer {self.id_} sent request {request_id} to Branch {self.id_} '
                f'interface {get_interface_name(request_interface)} result {get_result_name(response.result)} '
                f'money {response.money}'
            )
            values = {
                'interface': get_interface_name(request_interface),
                'result': get_result_name(response.result),
            }
            if request_interface == rpc_pb2.QUERY:
                values['money'] = response.money
            record['recv'].append(values)
        if record['recv']:
            with open(f'output/{out_filename}', 'a') as outfile:
                json.dump(record, outfile)
                outfile.write('\n')

    # Spawn the Customer process client. No need to bind to a port here; rather, we are connecting to one.
    #
    def Run_Customer(self, Branch_address, LOGGER, output_file, THREAD_CONCURRENCY):
        """Start a client (customer) in a subprocess."""
        # DEBUG
        #LOGGER.info(f'Processing Customer #{self.id} with Events:' )
        #for e in self.events:
        #    LOGGER.info(f'    #{e["id"]} = {e["interface"]}, {e["money"]}' )
                
        LOGGER.info(f'Running client customer #{self.id} connecting to server {Branch_address}...')
        sys.stdout.flush()

        Customer.createStub(self, Branch_address, LOGGER, THREAD_CONCURRENCY)
        #Customer.executeEvents(self, LOGGER, output_file)

        # Wait one day until keypress
        #try:
        #    while True:
        #        time.sleep(ONE_DAY.total_seconds())
        #except KeyboardInterrupt:
        #    server.stop(None)
        
        LOGGER.info(f'Client customer #{self.id} connecting to server {Branch_address} exiting successfully.')
        
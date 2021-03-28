#
#   Branch.py
#
# Marco Ermini - March 2021 for ASU CSE531 Course
# Do not leech!
# Built with python 3.8 with GRPC and GRPC-tools libraries; may work with other Python versions
'''Implementation of a banking's branches/customers RPC synchronisation using GRPC, multiprocessing and Python
Branch Class'''

import time
import datetime
import sys
import multiprocessing

from concurrent import futures

import grpc
import banking_pb2
import banking_pb2_grpc

ONE_DAY = datetime.timedelta(days=1)

#from Main import THREAD_CONCURRENCY, LOGGER


class Branch(banking_pb2_grpc.BankingServicer):

    def __init__(self, ID, balance, branches):
        # unique ID of the Branch
        self.id = ID
        # replica of the Branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branches = branches
        # the list of Client stubs to communicate with the branches
        self.stubList = list()
        # a list of received messages used for debugging purpose
        self.recvMsg = list()

    def MsgDelivery(self, request, context):
       # logger = logging.getLogger(LOG_NAME)
        self.recvMsg.append(request)
        balance_result = None
        if request.OP == Banking_pb2.QUERY:
            time.sleep(SLEEP_TIME_IN_SECONDS)
            balance_result = self.query()
        if request.OP == Banking_pb2.DEPOSIT:
            balance_result = self.deposit(request.money)
        if request.OP == Banking_pb2.WITHDRAW:
            balance_result = self.withdraw(request.money)
        response_result = Banking_pb2.SUCCESS if balance_result else Banking_pb2.ERROR
#        logger.info(
#            f'Branch {self.id_} response to Customer request {request.id_} '
#            f'interface {get_interface_name(request.interface)} result {get_result_name(response_result)} '
#            f'balance {balance_result}'
#        )
        response = Banking_pb2.MsgDeliveryResponse(
            ID=request.S_ID,
            RC=response_result,
            Amount=balance_result,
        )
#        if request.dest != DONT_PROPAGATE and request.interface == rpc_pb2.DEPOSIT:
#            self.propagate_deposit(request.id_, request.money)
#        if request.dest != DONT_PROPAGATE and request.interface == rpc_pb2.WITHDRAW:
#            self.propagate_withdraw(request.id_, request.money)
        return response


    def Query(self):
        return self.balance

    def Deposit(self, amount):
        if amount <= 0:		        # invalid operation
            return BankingRPC.ERROR
        self_balance = self.balance + amount
        return self.balance

    def Withdraw(self, amount):
        if amount <= 0:		        # invalid operation
            return BankingRPC.ERROR
        new_balance = self.balance - amount
        if new_balance < 0:	        # not enough money! cannot widthdraw
            return BankingRPC.FAILURE
        self.balance = new_balance
        return self.balance


    # Spawn the Branch process server
    #
    def Run_Branch(self, bind_address, LOGGER, THREAD_CONCURRENCY):
        """Start a server (branch) in a subprocess."""
        LOGGER.info(f'Starting branch at {bind_address}...')
        sys.stdout.flush()

        options = (('grpc.so_reuseport', 1),)

        server = grpc.server(futures.ThreadPoolExecutor(
            max_workers=THREAD_CONCURRENCY,),
                             options=options)

        banking_pb2_grpc.add_BankingServicer_to_server(Branch, server)

        server.add_insecure_port(bind_address)
        server.start()

        # Wait one day until keypress
        try:
            while True:
                time.sleep(ONE_DAY.total_seconds())
        except KeyboardInterrupt:
            server.stop(None)


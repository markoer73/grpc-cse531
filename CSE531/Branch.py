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
from Util import setup_logger, MyLog

import grpc
import banking_pb2
import banking_pb2_grpc

ONE_DAY = datetime.timedelta(days=1)
logger = setup_logger("Branch")
SLEEP_SECONDS = 3

# A constant used to indicate that the Branch must not propagate an operation. This is because a Branch receiving a message
#   cannot distinguish between an operation is coming from a client or another branch or it has been received already.
#   Without this control, the branches would keep propagating operations in an infinite loop. By setting this value after
#   the first propagation, it is not spread further.
DO_NOT_PROPAGATE = -1       

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
        # Binded address
        self.bind_address = str

    def MsgDelivery(self, request, context):
        self.recvMsg.append(request)
        balance_result = None
        response_result = None
        if request.OP == banking_pb2.QUERY:
            time.sleep(SLEEP_SECONDS)
            balance_result = self.Query()
        if request.OP == banking_pb2.DEPOSIT:
            balance_result = self.Deposit(request.Amount)
        if request.OP == banking_pb2.WITHDRAW:
            response_result, balance_result = self.Withdraw(request.Amount)
        MyLog(logger,
            f'Branch {self.id} response to Customer request {request.S_ID} '
            f'interface {get_operation_name(request.OP)} result {get_result_name(response_result)} '
            f'balance {balance_result}' )
        response = banking_pb2.MsgDeliveryResponse(
            ID=request.S_ID,
            RC=response_result,
            Amount=balance_result,
        )
        
        # If DO_NOT_PROPAGATE it means it has come from another branch and it must not be
        # spread further.  Also, no need to propagate query operations.
        if request.D_ID != DO_NOT_PROPAGATE and request.OP == banking_pb2.DEPOSIT:
            self.Propagate_Deposit(request.D_ID, request.Amount)
        if request.D_ID != DO_NOT_PROPAGATE and request.OP == banking_pb2.WITHDRAW:
            if response_result == banking_pb2.SUCCESS:                              # only propagates if the change has been successful 
                self.Propagate_Withdraw(request.D_ID, request.Amount)
        
        return response

    def Query(self):
        return self.balance

    def Deposit(self, amount):
        if amount <= 0:		        # invalid operation
            return BankingRPC.ERROR
        self_balance = self.balance + amount
        return self.balance

    def Withdraw(self, amount):
        # Distinguish between error (cannot execute a certain operation) or failure (operation is valid, but for instance
        # there is not enough balance).
        # This distinction is currently unused but can be used for further expansions of functionalities, such as overdraft.
        if amount <= 0:		        # invalid operation
            return banking_pb2.ERROR, 0
        new_balance = self.balance - amount
        if new_balance < 0:	        # not enough money! cannot widthdraw
            return banking_pb2.FAILURE, amount
        self.balance = new_balance
        return banking_pb2.SUCCESS, new_balance

    def Propagate_Deposit(self, request_id, amount):
        MyLog(logger,f'Propagate {get_operation_name(banking_pb2.DEPOSIT)} id {request_id} amount {amount} to other branches')
        if not self.stubList:
            self.Populate_Stub_List()
        for stub in self.stubList:
            response = stub.MsgDelivery(
                banking_pb2.MsgDeliveryRequest(
                    S_ID=request_id,
                    OP=banking_pb2.DEPOSIT,
                    Amount=amount,
                    D_ID=DO_NOT_PROPAGATE,          # Sets DO_NOT_PROPAGATE for receiving branches
                )
            )
            MyLog(logger,
                f'Branch {self.id} sent request {request_id} to other Branches -'
                f'operation {get_operation_name(banking_pb2.DEPOSIT)} result {get_result_name(response.RC)} '
                f'money {response.Amount}')

    def Propagate_Withdraw(self, request_id, amount):
        MyLog(logger,f'Propagate {get_operation_name(banking_pb2.WITHDRAW)} id {request_id} amount {amount} to other branches')
        if not self.stubList:
            self.Populate_Stub_List()
        for stub in self.stubList:
            response = stub.MsgDelivery(
                banking_pb2.MsgDeliveryRequest(
                    S_ID=request_id,
                    OP=banking_pb2.WITHDRAW,
                    Amount=amount,
                    D_ID=DO_NOT_PROPAGATE,          # Sets DO_NOT_PROPAGATE for receiving branches
                )
            )
            MyLog(logger,
                f'Branch {self.id} sent request {request_id} to other Branches -'
                f'operation {get_operation_name(banking_pb2.WITHDRAW)} result {get_result_name(response.RC)} '
                f'money {response.Amount}')

    def Populate_Stub_List(self):
        if len(self.stubList) == len(self.branches):  # stub list already initialized
            return
        for b in self.branches:
            if b != self.id:
                branch_address = self.bind_address
                MyLog(logger,f'Initializing branch to branch stub at {branch_address}')
                self.stubList.append(banking_pb2_grpc.BankingStub(grpc.insecure_channel(branch_address)))


# Currently waits for a day unless a CTRL+C is pressed, but it can be improved
#
def Wait_Loop():
    try:
        while True:
            time.sleep(ONE_DAY.total_seconds())
    except KeyboardInterrupt:
        return


# Spawn the Branch process server
#
def Run_Branch(Branch, binding_address, THREAD_CONCURRENCY):
    """Start a server (branch) in a subprocess."""
    MyLog(logger,f'Initialising branch at {binding_address}...')

    options = (('grpc.so_reuseport', 1),)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=THREAD_CONCURRENCY,), options=options)

    Branch.bind_address = binding_address
    banking_pb2_grpc.add_BankingServicer_to_server(Branch, server)

    server.add_insecure_port(binding_address)
    server.start()

    MyLog(logger,'*** Press CTRL+C to exit the process when finished ***')
    Wait_Loop()

    server.stop(None)


# Utility functions, used for readability
#
def get_operation(operation):
    """Returns the message type from the operation described in the input file."""
    if operation == 'query':
        return banking_pb2.QUERY
    if interface == 'deposit':
        return banking_pb2.DEPOSIT
    if interface == 'withdraw':
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
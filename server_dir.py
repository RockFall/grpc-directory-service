import grpc
from concurrent import futures
import directory_pb2
import directory_pb2_grpc
import integration_pb2
import integration_pb2_grpc

class DirectoryServicer(directory_pb2_grpc.DirectoryServiceServicer):
    def __init__(self):
        self.directory = {}


    def Insert(self, request, context):
        key = request.key
        description = request.description
        value = request.value

        print("Inserting key: " + key + " with value: " + value)

        if key in self.directory:
            self.directory[key].description = description
            self.directory[key].value = value
            return directory_pb2.InsertResponse(status=1)
        else:
            entry = directory_pb2.DirectoryEntry(key=key, description=description, value=value)
            self.directory[key] = entry
            return directory_pb2.InsertResponse(status=0)


    def Lookup(self, request, context):
        key = request.key
        print("Looking up key: " + key)

        if key in self.directory:
            return self.directory[key]
        else:
            return directory_pb2.DirectoryEntry()


    def Register(self, request, context):
        server_info = request.server_info
        hostname = server_info.hostname
        port = server_info.port

        print("Registering server: " + hostname + ":" + str(port))

        channel = grpc.insecure_channel(f"{hostname}:{port}")
        stub = integration_pb2_grpc.IntegrationServiceStub(channel)
        
        integration_register_request = integration_pb2.I_RegisterRequest(hostname=hostname, port=port, keys=list(self.directory.keys()))
        integration_register_response = stub.I_RegisterResponse(integration_register_request)

        # TODO: Implement logic to register the server

        return integration_register_response.num_keys_received

    def Terminate(self, request, context):
        num_keys_stored  = len(self.directory)

        print("Terminating server. Keys stored: " + str(num_keys_stored))

        # Lógica para encerrar o servidor
        # ...

        return directory_pb2.TerminateResponse(num_keys_stored=num_keys_stored)
    
# Inicie o servidor gRPC
def run_server(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    directory_pb2_grpc.add_DirectoryServiceServicer_to_server(DirectoryServicer(), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    print("Server started. Listening on port " + str(port) + ".")
    server.wait_for_termination()

if __name__ == '__main__':
    port = int(input().strip())
    run_server(port)

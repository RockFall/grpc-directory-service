import grpc
from concurrent import futures
import directory_pb2
import directory_pb2_grpc
import integration_pb2
import integration_pb2_grpc

class IntegrationService(integration_pb2_grpc.IntegrationServiceServicer):
    def __init__(self):
        self.directories = []

    def Register(self, request, context):
        hostname = request.hostname
        port = request.port
        keys = request.keys

        directory_info = (hostname, port, keys)
        self.directories.append(directory_info)

        return integration_pb2.I_RegisterResponse(num_keys_received=len(keys))

    def Lookup(self, request, context):
        key = request.key

        for directory_info in self.directories:
            hostname, port, keys = directory_info
            return integration_pb2.I_LookupResponse(
                participant_name=hostname,
                participant_port=port
            )

        return integration_pb2.I_LookupResponse(
            participant_name="ND",
            participant_port=0
        )
    
    def Terminate(self, request, context):
        num_keys_registered = sum(len(keys) for _, _, keys in self.directories)
        return integration_pb2.TerminateResponse(num_keys_registered=num_keys_registered)


def run_server(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    integration_pb2_grpc.add_IntegrationServiceServicer_to_server(IntegrationService(), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    print("Server started. Listening on port " + str(port) + ".")
    server.wait_for_termination()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        # Porta via argumento (ex.: arg=5555)
        port = int(sys.argv[1])
    else:
        # Ou via input no terminal/entrada padrão
        port = int(input().strip())

    run_server(port)

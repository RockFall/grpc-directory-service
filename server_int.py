import grpc
from concurrent import futures
import threading
import integration_pb2
import integration_pb2_grpc


# Serviço de integração
# O servidor de integração mantém uma lista de servidores de diretório registrados
class IntegrationService(integration_pb2_grpc.IntegrationServiceServicer):
    def __init__(self, stop_event):
        self.directories = []
        self.stop_event = stop_event

    def Register(self, request, context):
        hostname = request.hostname
        port = request.port
        keys = request.keys

        # Adiciona o servidor de diretório à lista de servidores registrados
        directory_info = (hostname, port, keys)
        self.directories.append(directory_info)

        return integration_pb2.I_RegisterResponse(num_keys_received=len(keys))

    def Lookup(self, request, context):
        key = request.key

        # Busca o servidor de diretório no index da chave
        if len(self.directories) >= key+1:
            hostname, port, keys = self.directories[key]
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

        self.stop_event.set()

        return integration_pb2.TerminateResponse(num_keys_registered=num_keys_registered)


def run_server(port):
    stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    integration_pb2_grpc.add_IntegrationServiceServicer_to_server(IntegrationService(stop_event), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    stop_event.wait()
    server.stop(grace=0)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        # Porta via argumento (ex.: arg=5555)
        port = int(sys.argv[1])
    else:
        # Ou via input no terminal/entrada padrão
        port = int(input().strip())

    run_server(port)

import grpc
from concurrent import futures
import threading
import directory_pb2
import directory_pb2_grpc
import integration_pb2
import integration_pb2_grpc

# Serviço de diretório
# O servidor de diretório mantém um dicionário com os itens armazenados
class DirectoryServicer(directory_pb2_grpc.DirectoryServiceServicer):
    def __init__(self, stop_event, port):
        self.directory = {}
        self._stop_event = stop_event # Evento de parada
        self.port = port # Porta do servidor de diretório usado para registro na integração

    def Insert(self, request, context):
        key = request.key
        description = request.description
        value = request.value

        # Insere um item no armazenamento interno
        # -> Retorna 1 se o item foi sobrescrito e 0 se foi criado
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

        # Busca um item no armazenamento interno
        if key in self.directory:
            return self.directory[key]
        else:
            return directory_pb2.DirectoryEntry(key=-1, description="", value=0)


    def Register(self, request, context):
        server_info = request.server_info
        hostname = server_info.hostname
        port = server_info.port

        # Obtem o stub do servidor de integração
        channel = grpc.insecure_channel(f"{hostname}:{port}")
        stub = integration_pb2_grpc.IntegrationServiceStub(channel)
        
        # Envia a requisição de registro para o servidor de integração
        integration_register_request = integration_pb2.I_RegisterRequest(hostname=hostname, port=int(self.port), keys=list(self.directory.keys()))
        integration_register_response = stub.Register(integration_register_request)

        return directory_pb2.RegisterResponse(status=integration_register_response.num_keys_received)

    def Terminate(self, request, context):
        num_keys_stored  = len(self.directory)

        # Aciona o evento de parada da thread principal
        self._stop_event.set()

        return directory_pb2.TerminateResponse(num_keys_stored=num_keys_stored)
  

# Inicie o servidor gRPC
def run_server(port):
    stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    directory_pb2_grpc.add_DirectoryServiceServicer_to_server(DirectoryServicer(stop_event, str(port)), server)
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

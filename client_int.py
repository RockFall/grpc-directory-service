import grpc
import integration_pb2_grpc
import directory_pb2

# Inicia o cliente gRPC
def run_client(server_address):
    channel = grpc.insecure_channel(server_address)
    stub = integration_pb2_grpc.IntegrationServiceStub(channel)

    while True:
        command = input().strip()

        # Função de terminação
        if command == 'T':
            response = stub.Terminate(directory_pb2.Empty())
            print(response.num_keys_stored)
            break
        # Função de busca
        elif command.startswith('C'):
            _, key = command.split(',')
            key = int(key)

            # Envia a requisição de busca para o servidor e printa a resposta
            lookup_request = directory_pb2.LookupRequest(key=key)
            lookup_response = stub.Lookup(lookup_request)

            if lookup_response.participant_name == 'ND':
                print("ND")
            else:
                print(f'{lookup_response.participant_name}:{lookup_response.participant_port}')



if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        # Endereço via argumento (ex.: arg=localhost:5555)
        server_address = sys.argv[1]
    else:
        # Ou via input no terminal/entrada padrão
        server_address = input().strip()

    run_client(server_address)

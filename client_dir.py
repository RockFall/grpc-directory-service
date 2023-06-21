import grpc
import directory_pb2
import directory_pb2_grpc

# A partir de um comando, extrai seus dados nos tipos corretos
# Retorna None caso o comando seja inválido
def parse_command(command):
    command_parts = command.split(',')

    if command_parts[0] == 'I':
        if len(command_parts) != 4:
            return None
        key = int(command_parts[1])
        description = command_parts[2]
        value = float(command_parts[3])
        return ('insert', key, description, value)
    elif command_parts[0] == 'C':
        if len(command_parts) != 2:
            return None
        key = int(command_parts[1])
        return ('lookup', key)
    elif command_parts[0] == 'R':
        if len(command_parts) != 3:
            return None
        server_name = command_parts[1]
        port = int(command_parts[2])
        return ('register', server_name, port)
    elif command_parts[0] == 'T':
        return ('terminate',)
    else:
        return None

# Inicia o cliente gRPC
def run_client(server_address):
    channel = grpc.insecure_channel(server_address)
    stub = directory_pb2_grpc.DirectoryServiceStub(channel)

    while True:
        command = input().strip()
        parsed_command = parse_command(command)

        if parsed_command is None:
            continue

        if parsed_command[0] == 'insert':
            key = int(parsed_command[1])
            description = parsed_command[2]
            value = float(parsed_command[3])

            request = directory_pb2.DirectoryEntry(key=key, description=description, value=value)
            response = stub.Insert(request)
            print(response.status)

        elif parsed_command[0] == 'lookup':
            key = parsed_command[1]
            request = directory_pb2.LookupRequest(key=key)
            response = stub.Lookup(request)
            if response.key != -1:
                print(f"{response.description},{response.value}")
            else:
                print("-1")
                
        elif parsed_command[0] == 'register':
            server_name, port = parsed_command[1:]
            request = directory_pb2.RegisterRequest(server_info=directory_pb2.ServerInfo(hostname=server_name, port=port))
            response = stub.Register(request)
            print(response.status)
        elif parsed_command[0] == 'terminate':
            request = directory_pb2.TerminateRequest()
            response = stub.Terminate(request)
            print(response.num_keys_stored)
            break

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        # Endereço via argumento (ex.: arg=localhost:5555)
        server_address = sys.argv[1]
    else:
        # Ou via input no terminal/entrada padrão
        server_address = input().strip()

    run_client(server_address)
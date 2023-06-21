import grpc
import integration_pb2
import integration_pb2_grpc
import directory_pb2
import directory_pb2_grpc

def run_client(server_address):
    channel = grpc.insecure_channel(server_address)
    stub = integration_pb2_grpc.IntegrationServiceStub(channel)

    while True:
        command = input().strip()

        if command == 'T':
            response = stub.Terminate(directory_pb2.Empty())
            print(response.num_keys_stored)
            break
        elif command.startswith('C'):
            _, key = command.split(',')
            key = int(key)

            lookup_request = integration_pb2.LookupRequest(key=key)
            lookup_response = stub.Lookup(lookup_request)

            if lookup_response.server_name == 'ND':
                print("ND")
            else:
                participant_name = lookup_response.participant_name
                participant_port = lookup_response.participant_port

                directory_address = f"{participant_name}:{participant_port}"
                directory_channel = grpc.insecure_channel(directory_address)
                directory_stub = directory_pb2_grpc.DirectoryServiceStub(directory_channel)
                
                directory_lookup_request = directory_pb2.LookupRequest(key=key)
                directory_lookup_response = directory_stub.Lookup(directory_lookup_request)

                if directory_lookup_response.description:
                    print(f"{directory_lookup_response.description},{directory_lookup_response.value}")
                else:
                    print("-1")

if __name__ == '__main__':
    server_address = input("Enter server address (host:port): ")
    run_client(server_address)

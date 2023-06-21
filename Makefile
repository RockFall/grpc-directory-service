# Makefile para compilação e execução dos programas cliente e servidor

# Variáveis
PROTOC = python -m grpc_tools.protoc
PROTO_DIR = protos
PROTO_FILES = $(PROTO_DIR)/directory.proto $(PROTO_DIR)/integration.proto
PROTO_PY_FILES = directory_pb2.py directory_pb2_grpc.py integration_pb2.py integration_pb2_grpc.py

# Regras
clean:
	rm -f $(PROTO_PY_FILES) client server

stubs:
	$(PROTOC) -I $(PROTO_DIR) --python_out=. --grpc_python_out=. $(PROTO_FILES)

run_cli_dir: client_dir.py $(PROTO_PY_FILES)
	python client_dir.py $(ARGS)

run_serv_dir: server_dir.py $(PROTO_PY_FILES)
	python server_dir.py $(PORT)

run_serv_int: server_int.py $(PROTO_PY_FILES)
	python server_int.py $(PORT)

run_cli_int: client_int.py $(PROTO_PY_FILES)
	python client_int.py $(ARGS)

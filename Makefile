# Makefile para compilação e execução dos programas cliente e servidor
.PHONY: clean stubs run_cli_dir run_serv_dir run_serv_int run_cli_int

# Variáveis
PROTOC = python -m grpc_tools.protoc
PROTO_DIR = protos
PROTO_FILES = $(PROTO_DIR)/directory.proto $(PROTO_DIR)/integration.proto
PROTO_PY_FILES = directory_pb2.py directory_pb2_grpc.py integration_pb2.py integration_pb2_grpc.py

# Regras
clean:
	rm -rf $(PROTO_PY_FILES) __pycache__

stubs:
	$(PROTOC) -I $(PROTO_DIR) --python_out=. --grpc_python_out=. $(PROTO_FILES)

run_cli_dir:
	python3 client_dir.py $(arg)

run_serv_dir:
	python3 server_dir.py $(arg)

run_serv_int:
	python3 server_int.py $(arg)

run_cli_int:
	python3 client_int.py $(arg)

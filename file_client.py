"""
CLI app - CLI application to retrieve and print data
          from backends.

@author: Kristijan <kristijan.sarin@gmail.com>
"""

import click
import requests
import grpc
import logging
from pathlib import Path
import service_file_pb2
import service_file_pb2_grpc

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Error messages
ERROR_MESSAGES = {
    "not_found": "File not found. Please check the UUID and try again.",
    "server_unreachable": "Could not connect to the server. Please ensure the server address is correct and reachable.",
    "unexpected_error": "An unexpected error occurred. Please try again."
}

# REST API Client
def rest_stat(base_url, uuid):
    try:
        url = f"{base_url}/file/{uuid}/stat/"
        response = requests.get(url)
        if response.status_code == 404:
            click.echo(ERROR_MESSAGES["not_found"])
            return
        response.raise_for_status()
        data = response.json()
        click.echo(f"File Metadata:\n- Name: {data['name']}\n- Size: {data['size']} bytes\n"
                   f"- MIME Type: {data['mimetype']}\n- Created: {data['create_datetime']}")
    except requests.ConnectionError:
        click.echo(ERROR_MESSAGES["server_unreachable"])
    except Exception as e:
        logging.error(f"Error during REST stat request: {e}")
        click.echo(ERROR_MESSAGES["unexpected_error"])

def rest_read(base_url, uuid, output):
    try:
        url = f"{base_url}/file/{uuid}/read/"
        response = requests.get(url)
        if response.status_code == 404:
            click.echo(ERROR_MESSAGES["not_found"])
            return
        response.raise_for_status()
        content = response.content
        if output == '-':
            click.echo(content.decode(errors="replace"))
        else:
            with open(output, 'wb') as f:
                f.write(content)
            click.echo(f"Content saved to {output}")
    except requests.ConnectionError:
        click.echo(ERROR_MESSAGES["server_unreachable"])
    except Exception as e:
        logging.error(f"Error during REST read request: {e}")
        click.echo(ERROR_MESSAGES["unexpected_error"])

# gRPC Client
def grpc_stat(grpc_server, uuid):
    try:
        with grpc.insecure_channel(grpc_server) as channel:
            stub = service_file_pb2_grpc.FileServiceStub(channel)
            request = service_file_pb2.StatRequest(uuid=uuid)
            response = stub.Stat(request)
            click.echo(f"File Metadata:\n- Name: {response.name}\n- Size: {response.size} bytes\n"
                       f"- MIME Type: {response.mimetype}\n- Created: {response.create_datetime}")
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            click.echo(ERROR_MESSAGES["not_found"])
        else:
            click.echo(ERROR_MESSAGES["server_unreachable"])
        logging.error(f"gRPC Error during stat request: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during gRPC stat request: {e}")
        click.echo(ERROR_MESSAGES["unexpected_error"])

def grpc_read(grpc_server, uuid, output):
    try:
        with grpc.insecure_channel(grpc_server) as channel:
            stub = service_file_pb2_grpc.FileServiceStub(channel)
            request = service_file_pb2.ReadRequest(uuid=uuid)
            response = stub.Read(request)
            content = response.content
            if output == '-':
                click.echo(content.decode(errors="replace"))
            else:
                with open(output, 'wb') as f:
                    f.write(content)
                click.echo(f"Content saved to {output}")
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            click.echo(ERROR_MESSAGES["not_found"])
        else:
            click.echo(ERROR_MESSAGES["server_unreachable"])
        logging.error(f"gRPC Error during read request: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during gRPC read request: {e}")
        click.echo(ERROR_MESSAGES["unexpected_error"])

# CLI Command
@click.command()
@click.argument('command', type=click.Choice(['stat', 'read']))
@click.argument('uuid')
@click.option('--backend', default='grpc', type=click.Choice(['grpc', 'rest']), help='Set a backend to be used')
@click.option('--grpc-server', default='localhost:50051', help='gRPC server host:port')
@click.option('--base-url', default='http://localhost/', help='Base URL for REST API')
@click.option('--output', default='-', help='File to store output, default is stdout')
def file_client(command, uuid, backend, grpc_server, base_url, output):
    """CLI to retrieve file metadata and contents."""
    if backend == 'grpc':
        if command == 'stat':
            grpc_stat(grpc_server, uuid)
        elif command == 'read':
            grpc_read(grpc_server, uuid, output)
    elif backend == 'rest':
        if command == 'stat':
            rest_stat(base_url, uuid)
        elif command == 'read':
            rest_read(base_url, uuid, output)

if __name__ == '__main__':
    file_client()

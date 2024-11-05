"""
CLI app - CLI application to retrieve and print data
          from backends.

@author: Kristijan <kristijan.sarin@gmail.com>
"""

import click
import requests
import grpc
import logging
import sys
from pathlib import Path
from typing import Union
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

def output_metadata(name, size, mimetype, create_datetime, output):
    """Formats and outputs file metadata."""
    metadata = (f"File Metadata:\n- Name: {name}\n- Size: {size} bytes\n"
                f"- MIME Type: {mimetype}\n- Created: {create_datetime}")
    if output == '-':
        click.secho(metadata, fg='green')
    else:
        with open(output, 'w') as f:
            f.write(metadata)
        click.secho(f"Metadata saved to {output}", fg='cyan')

# REST API Client
def rest_stat(base_url, uuid, output):
    try:
        url = f"{base_url}/file/{uuid}/stat/"
        response = requests.get(url)
        if response.status_code == 404:
            click.secho(ERROR_MESSAGES["not_found"], fg='red')
            raise SystemExit(1)
        response.raise_for_status()
        data = response.json()
        output_metadata(data['name'], data['size'], data['mimetype'], data['create_datetime'], output)
    except requests.ConnectionError:
        click.secho(ERROR_MESSAGES["server_unreachable"], fg='red')
        raise SystemExit(1)
    except Exception as e:
        logging.error(f"Error during REST stat request: {e}")
        click.secho(ERROR_MESSAGES["unexpected_error"], fg='red')
        raise SystemExit(1)

def rest_read(base_url, uuid, output):
    try:
        url = f"{base_url}/file/{uuid}/read/"
        response = requests.get(url)
        if response.status_code == 404:
            click.secho(ERROR_MESSAGES["not_found"], fg='red')
            raise SystemExit(1)
        response.raise_for_status()
        content = response.content
        if output == '-':
            click.secho(content.decode(errors="replace"), fg='green')
        else:
            with open(output, 'wb') as f:
                f.write(content)
            click.secho(f"Content saved to {output}", fg='cyan')
    except requests.ConnectionError:
        click.secho(ERROR_MESSAGES["server_unreachable"], fg='red')
        raise SystemExit(1)
    except Exception as e:
        logging.error(f"Error during REST read request: {e}")
        click.secho(ERROR_MESSAGES["unexpected_error"], fg='red')
        raise SystemExit(1)

# gRPC Client
def grpc_stat(grpc_server, uuid, output):
    try:
        with grpc.insecure_channel(grpc_server) as channel:
            stub = service_file_pb2_grpc.FileServiceStub(channel)
            request = service_file_pb2.StatRequest(uuid=uuid)
            response = stub.Stat(request)
            output_metadata(response.name, response.size, response.mimetype, response.create_datetime, output)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            click.secho(ERROR_MESSAGES["not_found"], fg='red')
        else:
            click.secho(ERROR_MESSAGES["server_unreachable"], fg='red')
        logging.error(f"gRPC Error during stat request: {e}")
        raise SystemExit(1)
    except Exception as e:
        logging.error(f"Unexpected error during gRPC stat request: {e}")
        click.secho(ERROR_MESSAGES["unexpected_error"], fg='red')
        raise SystemExit(1)

def grpc_read(grpc_server, uuid, output):
    try:
        with grpc.insecure_channel(grpc_server) as channel:
            stub = service_file_pb2_grpc.FileServiceStub(channel)
            request = service_file_pb2.ReadRequest(uuid=uuid)
            response = stub.Read(request)
            content = response.content
            if output == '-':
                click.secho(content.decode(errors="replace"), fg='green')
            else:
                with open(output, 'wb') as f:
                    f.write(content)
                click.secho(f"Content saved to {output}", fg='cyan')
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            click.secho(ERROR_MESSAGES["not_found"], fg='red')
        else:
            click.secho(ERROR_MESSAGES["server_unreachable"], fg='red')
        logging.error(f"gRPC Error during read request: {e}")
        raise SystemExit(1)
    except Exception as e:
        logging.error(f"Unexpected error during gRPC read request: {e}")
        click.secho(ERROR_MESSAGES["unexpected_error"], fg='red')
        raise SystemExit(1)

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
    click.secho(f"Using {backend.upper()} backend...", fg='blue')
    if backend == 'grpc':
        if command == 'stat':
            grpc_stat(grpc_server, uuid, output)
        elif command == 'read':
            grpc_read(grpc_server, uuid, output)
    elif backend == 'rest':
        if command == 'stat':
            rest_stat(base_url, uuid, output)
        elif command == 'read':
            rest_read(base_url, uuid, output)

if __name__ == '__main__':
    file_client()

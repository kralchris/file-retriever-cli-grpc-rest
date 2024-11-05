# File Client CLI

A Python command-line application for retrieving file metadata and contents using either REST or gRPC backends. This tool supports metadata retrieval (`stat`) and file content retrieval (`read`) for files identified by UUIDs.

## Key Features

- **Flexible Backends**: Supports both REST and gRPC backends.
- **Metadata and Content Retrieval**: Retrieves file metadata with the `stat` command and file content with the `read` command.
- **Error Handling**: Provides descriptive error messages and returns non-zero exit codes for errors.
- **Output Customization**: Metadata or file content can be saved to a file with the `--output` option.

## Installation

Ensure you have Python 3.7–3.10 installed. Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python file_client.py <command> <UUID> [options]
```

### Commands

stat: Retrieves and displays metadata for a specified file UUID.
read: Retrieves and displays the file content for a specified file UUID.

### Options

--backend: Specifies the backend protocol. Choices are grpc or rest (default: grpc).
--grpc-server: Defines the gRPC server host and port (default: localhost:50051).
--base-url: Sets the base URL for REST API requests (default: http://localhost/).
--output: Specifies a file to save the output. When used with stat, metadata is written to this file; with read, the file content is saved.

### Exit Codes

0: Success
1: Error (e.g., file not found, server unreachable, or other unexpected issues).

### Example Commands

Retrieve metadata using REST and save to a file:

```bash
python file_client.py stat 1234-5678 --backend rest --output metadata.txt
```

Retrieve file content using gRPC and display it in the terminal:

```bash
python file_client.py read 1234-5678 --backend grpc
```

### REST API Reference

The REST backend provides the following endpoints, relative to the `base_url`:

1. **Metadata Retrieval**  
   **Endpoint**: `file/<uuid>/stat/`  
   **Method**: `GET`  
   **Response**: JSON with file metadata:
   - `create_datetime`: ISO format date and time of file creation
   - `size`: File size in bytes
   - `mimetype`: File MIME type
   - `name`: Display name of the file

   **Error**: Returns HTTP 404 if the file is not found.

2. **File Content Retrieval**  
   **Endpoint**: `file/<uuid>/read/`  
   **Method**: `GET`  
   **Response**: Returns file content with headers:
   - `Content-Disposition`: Display name of the file
   - `Content-Type`: MIME type of the file

   **Error**: Returns HTTP 404 if the file is not found.

## Testing

Unit tests are included in `test_cli_file_client.py` to verify the functionality and error handling of the CLI application. Tests cover:

- **Positive Cases**: Successful `stat` and `read` requests using both REST and gRPC.
- **Negative Cases**: Non-existent files and server connection issues, verifying that the CLI returns a non-zero exit code on failure.
- **File Output Testing**: Ensures that `--output` writes metadata or content to the specified file.

### Running Tests

To run the tests, use:

```bash
python -m unittest discover tests
```
## Project Structure

file-retriever-cli/<br>
├── file_client.py             # Main CLI application<br>
├── requirements.txt           # Dependencies<br>
├── README.md                  # Project documentation<br>
├── service_file.proto         # Protocol Buffer file for gRPC<br>
&ensp;&ensp;└── tests/<br>
&ensp;&ensp;└── test_cli_file_client.py  # Unit tests for the CLI application

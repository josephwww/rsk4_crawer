# Pending Order and Inspection Order Crawler

## Overview

This Python script is designed to query pending and inspection orders from RSK4, gather detailed information about each order, and upload associated PDF documents to MinIO storage. The process involves several steps, including querying for orders, fetching detailed entry and document information, and handling PDF uploads asynchronously.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Functions](#functions)


## Requirements

- Python 3.10
- `asyncio`
- `requests`
- `minio`
- `selenium`

## Installation

1. Clone this repository:
    ```bash
    git clone git@gitee.com:josephwww/rsk4_craw.git
    cd rsk4_craw
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Configure the constants and parameters in the `const.py` file to match your environment.

2. Run the script:
    ```bash
    python main.py
    ```

## Functions

### `craw_pending_order(check_form_list)`

Queries pending orders with hazardous package inspection certificates (`SJ1`) and adds them to the `check_form_list`.

### `craw_inspection_order(check_form_list)`

Queries manual inspection orders with hazardous package inspection certificates (`SJ1`) and adds them to the `check_form_list`.

### `get_entry_info(check_form_list)`

Fetches all entry item information for each order in the `check_form_list` and checks if the entry already exists in the database.

### `get_entry_ddate(check_form_list)`

Fetches the declaration date (`D_DATE`) for each valid customs declaration and adds it to the corresponding order in the `check_form_list`.

### `get_data_document_info(check_form_list)`

Fetches all document information for each entry in the `check_form_list`.

### `async get_document_pdf(check_form_list)`

Asynchronously downloads all PDFs associated with the entries in the `check_form_list` and uploads them to MinIO storage. Also saves the file metadata to a MySQL database.

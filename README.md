# Intel® Device Management Toolkit(DMT) MCP Server

## Prerequisite
- Python 3.10 or higher installed
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed
- DMT setup
    - Management Presence Server (MPS) is ready. Refer https://device-management-toolkit.github.io/docs/2.27/GetStarted/Enterprise/setup/ for more detail.
    - AMT Devices/Remote Provisioning Client (RPC) are ready. Refer https://device-management-toolkit.github.io/docs/2.27/GetStarted/Enterprise/activateDevice/ for more detail.

*** Instructions below need to be done on MPS.

## Install
```
git clone https://github.com/Desmond0804/Intel_DMT_MCP_Server.git
cd Intel_DMT_MCP_Server

# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# Install dependencies
uv sync
```

## Run Server
```
# set DMT_username & DMT_password environment variable for DMT authentication.

# run MCP server
uv --directory /ABSOLUTE/PATH/TO/PARENT/FOLDER/Intel_DMT_MCP_Server run app.py
```

## Use [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to test
- Requirement: Node.js ^22.7.5

```
# set DMT_username & DMT_password environment variable for DMT authentication.

# run MCP Inspector
npx @modelcontextprotocol/inspector uv --directory /ABSOLUTE/PATH/TO/PARENT/FOLDER/Intel_DMT_MCP_Server run app.py
```

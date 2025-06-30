import os
import asyncio
from dotenv import load_dotenv
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Intel_DMT")

# Constants
DMT_API_BASE = "http://localhost:8181/api/v1"
USER_AGENT = "DMT-app/1.0"

load_dotenv()
DMT_username = os.getenv("DMT_username")
DMT_password = os.getenv("DMT_password")

global token

async def get_token(username: str, password: str) -> str | None:
    """
    Generates a JWT token that can be used for authentication to both MPS and RPS APIs. 
    Refer https://device-management-toolkit.github.io/docs/2.27/GetStarted/Enterprise/setup/#configuration for more information.

    Args:
        username: Intel® DMT username.
        password: Intel® DMT password.
    """
    url = f"{DMT_API_BASE}/authorize"
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data["token"]
        except Exception:
            return None

async def authorize():
    global token
    token = await get_token(DMT_username, DMT_password)

asyncio.run(authorize())


async def make_dmt_get_request(url: str) -> dict[str, Any] | None:
    """Make a GET request to the Intel® DMT API with proper error handling."""
    global token
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

async def make_dmt_post_request(url: str, json: dict[str, Any]) -> dict[str, Any] | None:
    """Make a POST request to the Intel® DMT API with proper error handling."""
    global token
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=json, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


@mcp.tool()
async def get_devices(status: int = 1) -> str:
    """
    Lists all Intel® AMT devices/Remote Provisioning Client (RPC) known to Management Presence Server (MPS).

    Args:
        status: Status of the client. Specify '0' to query for disconnected devices. Specify '1' for connected devices. To return all devices, omit this query parameter.
    """
    url = f"{DMT_API_BASE}/devices?status={status}"
    data = await make_dmt_get_request(url)

    if not data:
        return "Unable to fetch devices."
    if isinstance(data, list) and len(data) < 1:
        return "No device."
    
    devices = []
    for item in data:
        device = f"""
Connection Status: {item["connectionStatus"]}
Hostname: {item["hostname"]}
GUID: {item["guid"]}
Friendly Name: {item["friendlyName"]}
"""
        devices.append(device)

    return "\n---\n".join(devices)

@mcp.tool()
async def get_power_state(guid: str) -> str:
    """ 
    Retrieve current power state of Intel® AMT device, returns a number that maps to a device power state. Possible power state values:
        2 = On - corresponding to ACPI state G0 or S0 or D0
        3 = Sleep - Light, corresponding to ACPI state G1, S1/S2, or D1
        4 = Sleep - Deep, corresponding to ACPI state G1, S3, or D2
        6 = Off - Hard, corresponding to ACPI state G3, S5, or D3
        7 = Hibernate (Off - Soft), corresponding to ACPI state S4, where the state of the managed element is preserved and will be recovered upon powering on
        8 = Off - Soft, corresponding to ACPI state G2, S5, or D3
        9 = Power Cycle (Off-Hard), corresponds to the managed element reaching the ACPI state G3 followed by ACPI state S0
        13 = Off - Hard Graceful, equivalent to Off Hard but preceded by a request to the managed element to perform an orderly shutdown

    Args:
        guid: GUID of Intel® AMT device.
    """
    url = f"{DMT_API_BASE}/amt/power/state/{guid}"
    data = await make_dmt_get_request(url)

    if not data:
        return "Unable to get power state of device."
    
    state = ""
    match data["powerstate"]:
        case 2: state = "On"
        case 3: state = "Sleep - Light"
        case 4: state = "Sleep - Deep"
        case 6: state = "Off - Hard"
        case 7: state = "Hibernate (Off - Soft)"
        case 8: state = "Off - Soft"
        case 9: state = "Power Cycle (Off-Hard)"
        case 13: state = "Off - Hard Graceful"
        case _: state = "Unknown"

    return f"Power State: {state}"

@mcp.tool()
async def do_power_action(guid: str, action: int, useSOL: str = "false") -> str:
    """ 
    Perform an Out-of-band (OOB) power actions numbered 1 thru 99.

    Args:
        guid: GUID of Intel® AMT device.
        action: Power action number. Possible power action values:
            2 = Power up/on
            5 = Power cycle
            8 = Power down/off
            10 = Reset
        useSOL: Use Serial Over LAN control. Serial over LAN is a feature that enables the input and output of the serial port of a managed system to be redirected over IP.
    """
    url = f"{DMT_API_BASE}/amt/power/action/{guid}"
    payload = {
        "action": action,
        "useSOL": useSOL
    }
    data = await make_dmt_post_request(url, json=payload)

    if (not data) or (data.get("ReturnValue") is None):
        return "Unable to perform power action on the device."
    
    if data["ReturnValue"] != 0:
        return "Failed to perform power action."
    else:
        return "Success to perform power action."


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

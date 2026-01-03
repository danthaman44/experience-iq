import requests
from .supabase import get_messages
from typing import List


def get_current_weather(latitude, longitude):
    # Format the URL with proper parameter substitution
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m&hourly=temperature_2m&daily=sunrise,sunset&timezone=auto"

    try:
        # Make the API call
        response = requests.get(url)

        # Raise an exception for bad status codes
        response.raise_for_status()

        # Return the JSON response
        return response.json()

    except requests.RequestException as e:
        # Handle any errors that occur during the request
        print(f"Error fetching weather data: {e}")
        return None


TOOL_DEFINITIONS = [{
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather at a location",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "The latitude of the location",
                },
                "longitude": {
                    "type": "number",
                    "description": "The longitude of the location",
                },
            },
            "required": ["latitude", "longitude"],
        },
    },
}]

# Define the function declaration for the model
get_message_history_function = {
    "name": "get_message_history",
    "description": "Gets the message history for a given thread.",
    "parameters": {
        "type": "object",
        "properties": {
            "thread_id": {
                "type": "string",
                "description": "The thread ID",
            },
        },
        "required": ["thread_id"],
    },
}

async def get_message_history(thread_id: str) -> List[str]:
    """Get the message history for a given thread."""
    data = await get_messages(thread_id)
    return [message["content"] for message in data]

AVAILABLE_TOOLS = {
    "get_message_history": get_message_history,
}

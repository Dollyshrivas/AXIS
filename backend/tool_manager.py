from tools import (
    get_time,
    get_status,
    say_hello,
    get_battery,
    get_location,
    open_chrome,
    open_youtube,
    open_whatsapp,
    open_item,
    open_file_explorer,
    search_web,
)

# Register all tools here
TOOLS = {
    "get_time": get_time,
    "get_status": get_status,
    "say_hello": say_hello,
    "get_battery": get_battery,
    "get_location": get_location,
    "open_chrome": open_chrome,
    "open_youtube": open_youtube,
    "open_whatsapp": open_whatsapp,
    "open_item": open_item,
    "open_file_explorer": open_file_explorer,
    "search_web": search_web,
}

def execute_tool(tool_name, args=None):
    if args is None:
        args = {}

    if tool_name not in TOOLS:
        return {
            "error": f"Tool '{tool_name}' not found"
        }

    try:
        tool_function = TOOLS[tool_name]

        if args:
            return tool_function(**args)

        return tool_function()

    except Exception as e:
        return {
            "error": str(e)
        }
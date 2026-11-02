from tool_manager import execute_tool


def extract_web_search_request(text):
    text = text.lower().strip().strip(" .?!")
    prefixes = (
        "could you find ",
        "can you find ",
        "can you show me ",
        "please find ",
        "please search for ",
        "find me ",
        "find ",
        "search for ",
        "search ",
        "look for ",
        "show me ",
        "give me ",
        "get me ",
        "recommend ",
        "suggest ",
        "browse for ",
    )
    query = text

    for prefix in prefixes:
        if text.startswith(prefix):
            query = text[len(prefix):].strip()
            break
    else:
        if not any(
            phrase in text
            for phrase in ("near me", "nearby", "website", "websites")
        ):
            return None

    for filler in ("some ", "a few ", "the "):
        if query.startswith(filler):
            query = query[len(filler):].strip()

    if not query:
        return None

    near_me = any(phrase in query for phrase in ("near me", "nearby"))
    return {"query": query, "maps": near_me}


def extract_open_request(text):
    text = text.lower().strip()
    file_prefixes = (
        "please open my file ", "open my file ", "open the file ",
        "open file ", "find my file ", "find file ", "show me my file ",
    )
    is_file_request = text.startswith(file_prefixes)
    prefixes = (
        *file_prefixes,
        "कृपया ओपन करो ", "ओपन करो ", "ओपन ",
        "please open ", "open ", "launch ", "start ", "go to ", "visit ",
        "खोलो ", "खोलिए ", "खोल ", "चालू करो ",
    )

    for prefix in prefixes:
        if text.startswith(prefix):
            target = text[len(prefix):].strip().strip(" .?!")
            if target.startswith("the "):
                target = target[4:].strip()
            if not target:
                return None

            item, separator, location = target.rpartition(" in ")
            if separator and item and location:
                request = {"target": item.strip(), "location": location.strip()}
            else:
                request = {"target": target}
            if is_file_request:
                request["file_only"] = True
            return request

    return None


def detect_tool(text):
    text = text.lower().strip()

    if any(
        phrase in text
        for phrase in (
            "open file explorer",
            "open the file explorer",
            "open my file explorer",
            "open my files",
            "open files",
            "show file explorer",
            "show me file explorer",
            "start file explorer",
            "launch file explorer",
            "open explorer",
            "फाइल एक्सप्लोरर खोलो",
            "फ़ाइल एक्सप्लोरर खोलो",
        )
    ):
        return "open_file_explorer"

    # Open YouTube
    if any(
        phrase in text
        for phrase in ("open youtube", "launch youtube", "start youtube", "go to youtube")
    ):
        return "open_youtube"

    # Open WhatsApp
    if any(
        phrase in text
        for phrase in (
            "open whatsapp",
            "open whats app",
            "launch whatsapp",
            "launch whats app",
            "start whatsapp",
            "start whats app",
            "go to whatsapp",
            "go to whats app",
        )
    ):
        return "open_whatsapp"

    # Open Chrome
    if any(
        phrase in text
        for phrase in (
            "open chrome",
            "open google chrome",
            "launch chrome",
            "launch google chrome",
            "start chrome",
            "start google chrome",
        )
    ):
        return "open_chrome"

    # Location
    if any(
        phrase in text
        for phrase in (
            "where am i",
            "where am i now",
            "what is my location",
            "what's my location",
            "my current location",
            "tell me my location",
            "find my location",
            "meri location",
            "meri current location",
            "main kahan hoon",
            "mujhe location batao",
            "मेरी लोकेशन",
            "मेरा स्थान",
            "मैं कहाँ हूँ",
        )
    ):
        return "get_location"

    # Time
    if (
        "what time" in text
        or "current time" in text
        or "time is it" in text
        or "what's the time" in text
        or "tell me the time" in text
        or "what's the time right now" in text
    ):
        return "get_time"

    # Status
    if (
        "system status" in text
        or "axis status" in text
        or "are you online" in text
    ):
        return "get_status"

    # Hello
    if (
        text == "hello"
        or text == "hi"
        or text == "say hello"
    ):
        return "say_hello"
    
    # Battery
    if (
    "battery" in text
    or "battery percentage" in text
    or "how much battery" in text
):
        return "get_battery"

    return None


def try_tool(text):

    tool_name = detect_tool(text)
    args = None

    if tool_name is None:
        args = extract_open_request(text)
        if args is not None:
            tool_name = "open_item"

    if tool_name is None:
        file_name = text.strip().strip(" .?!")
        if "." in file_name and not any(character.isspace() for character in file_name):
            args = {"target": file_name}
            tool_name = "open_item"

    if tool_name is None:
        args = extract_web_search_request(text)
        if args is None:
            return None
        tool_name = "search_web"

    print(f"🛠️ AXIS selected tool: {tool_name}")

    result = execute_tool(tool_name, args)

    print(f"✅ Tool result: {result}")

    return result
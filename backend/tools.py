def say_hello():
    return "Hello! AXIS tool system is working."


def get_status():
    return {
        "status": "online",
        "system": "AXIS",
        "message": "All systems operational"
    }


def get_time():
    from datetime import datetime
    return datetime.now().strftime("%I:%M:%S %p")
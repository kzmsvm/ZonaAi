def run(args: str) -> str:
    try:
        result = eval(args, {"__builtins__": {}})
        return f"\U0001F9EE Result: {result}"
    except Exception as e:
        return f"\u26A0\uFE0F Math error: {str(e)}"

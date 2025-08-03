from datetime import datetime

def run(args: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"\U0001F552 Current server time is {now}"

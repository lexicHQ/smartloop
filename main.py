from signal import signal, SIGINT

from rich.console import Console
from smartloop import app

console = Console()

def signal_handler (signal_received, frame):
    # Handle any cleanup here
	console.print(f"\n[blue]Bye![/blue]\n")
	exit(0)

def bootstrap():
	signal(SIGINT, signal_handler)
	app.bootstrap()

if __name__ == "__main__":	
	bootstrap()
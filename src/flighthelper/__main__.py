import argparse
from .ui import launch
from .agent import ask

def cli() -> None:
    p = argparse.ArgumentParser(description="Flight-Finder AI")
    p.add_argument("-q", "--question", help="Ask the agent from CLI")
    args = p.parse_args()

    if args.question:
        print(ask(args.question))
    else:
        launch()

if __name__ == "__main__":
    cli()

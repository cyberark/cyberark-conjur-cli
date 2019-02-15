import sys

class Cli(object):
    def __init__(self):
        print("String CLI...")

    def run(self, *args, **kwargs):
        print("Invoking CLI runner...")
        cli_args = sys.argv
        print("CLI args:", cli_args)
        print("Args:", args)
        print("Kwargs:", kwargs)

    @staticmethod
    def launch():
        print("Launching app")
        return Cli().run()

if __name__ == '__main__':
    Cli.launch()

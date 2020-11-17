# Python CLI UX Guidelines

1. The tool’s executable name should be “**conjur**” (regardless to its supported platform), so “conjur-py3-cli-darwin” is not a good experience.
2. Once the CLI tool is executed **without** **any** **commands**, we should show the help and usage.
3. Make sure to provide short-form options (e.g. -h) and long-form options (--help)
4. Provide helpful and **readable** **feedback** (output) at all times. E.g., when a command succeeds and doesn’t have output, it is ended (in new line) with: Command succeeded! Data set to variable: XYZ
5. Provide helpful and **readable** **errors** (we currently show exception and line code): E.g.,:  conjur exception cli_err01: command failed. No such file or directory: ‘/Users/sharonr/.conjurrc’
6. When a command is executed with **missing** **parts** (subcommand, argument), or the CLI is executed with unfamiliar syntax, show error and right after the help of the command:

conjur exception cli_err02: command not found. 

Conjur help text…

conjur exception cli_err03: argument not found. type conjur <command> -h for more information.



7. Exit codes: commands with no errors will return exit code 0, while errors will return exit code 1 exit code 2 is for ??

8. Keep a structured language and easy to type, so it will be efficient to use (especially for double word commands), e.g.:

conjur user update**-**password <arg>

Help command 



<img src="/Users/ssax/Desktop/images/help-screen.png" alt="help-screen" style="zoom:50%;" />

The structure of command in the CLI is below - for example: Conjur help on 'init' command

The texts for each command is written in the epic itself. This is the guidelines on how the UI of the help should.

<img src="/Users/ssax/Desktop/images/init-help.png" alt="init-help" style="zoom:50%;" />



## Nice to have:

1. Use terminal colors – nice to have but very cool. We can add colors for command and subcommands to better differentiate them

2. We should support **tab**-**completion**:
   - Typing the first few characters of the command name followed by <tab> <tab>, will auto-complete the command
   - Hit space after a command, then <tab> <tab> again, will shows a list of available sub-commands
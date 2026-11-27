# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR MIT

# The README demo: the installed version, the repository's own
# Standard 18 fixture, then the load-and-summarise example.
# Render with `make demo`.

Output .github/demo.gif

Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 600
Set Padding 20
Set Theme "Catppuccin Mocha"
Set TypingSpeed 35ms

Hide
Type "export PS1='$ ' && clear"
Enter
Show

Type "poetry run python -c 'import bankstatementparser_loader_bacs as b; print(b.__version__)'"
Enter
Wait /\$$/
Sleep 1s

Type "cut -c1-110 tests/fixtures/standard18.bacs"
Enter
Wait /\$$/
Sleep 3s

Type "clear && poetry run python examples/01_basic_usage.py"
Enter
Wait /\$$/
Sleep 5s

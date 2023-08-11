# jklmbot

<img align="right" src="picture.jpeg" height="140px">

***Win all of your JKLM.fun games!***

<br>
<br>

[![GitHub - License](https://img.shields.io/github/license/Animenosekai/jklmbot)](https://github.com/Animenosekai/jklmbot/blob/master/LICENSE)
[![GitHub top language](https://img.shields.io/github/languages/top/Animenosekai/jklmbot)](https://github.com/Animenosekai/jklmbot)
![Code Size](https://img.shields.io/github/languages/code-size/Animenosekai/jklmbot)
![Repo Size](https://img.shields.io/github/repo-size/Animenosekai/jklmbot)
![Issues](https://img.shields.io/github/issues/Animenosekai/jklmbot)

## Index

- [Index](#index)
- [Purpose](#purpose)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
- [Installing](#installing)
  - [From Git](#from-git)
- [Usage](#usage)
- [Contributing](#contributing)
- [Built With](#built-with)
- [Authors](#authors)
- [Licensing](#licensing)

## Purpose

`jklmbot` is a simple script to let your computer play "BombParty" on the website [*jklm.fun*](https://jklm.fun)

> **Warning**  
> The code for this script hasn't been updated for a long time and might not work as well as back when the code was written! Please [contribute](#contributing) and fix stuff if you spot any bug 🙇.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

You will need Python 3 to use this module

```bash
Minimum required versions: 3.8
```

Although the code itself is made compatible with Python >=3.6, the dependencies require at least Python 3.8.

Always check if your Python version works with `jklmbot` before using it in production.

## Installing

### From Git

```bash
pip install --upgrade git+https://github.com/Animenosekai/jklmbot.git
```

> This will install the latest development version from the git repository

You can check if you successfully installed it by printing out its version:

```bash
$ jklmbot --version
1.0
```

## Usage

Go create a "BombParty" room on [*jklm.fun*](https://jklm.fun) and run the script using:

```bash
jklmbot --room="<YOUR_ROOM_ID>"
```

But there are lots of stuff to customize so head over to your terminal and enter:

```bash
🧃❯ jklmbot --help
usage: jklmbot [-h] [--version] --room ROOM [--username USERNAME] [--picture PICTURE] [--browser BROWSER] [--headless] [--delay DELAY] [--key KEY] [--check CHECK]

Win all of your JKLM.fun games!

options:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --room ROOM, -r ROOM  The room to enter.
  --username USERNAME, -u USERNAME
                        The username to use.
  --picture PICTURE, -p PICTURE
                        The profile picture to use.
  --browser BROWSER, -b BROWSER
                        The browser to use (chromium|firefox|webkit).
  --headless            Wether to run the browser without a graphical interface.
  --delay DELAY, --max-delay DELAY, -d DELAY
                        The maximum delay before searching for answers to avoid being caught (in secs).
  --key KEY, --key-delay KEY, --keystroke-delay KEY, --keyboard-delay KEY, --keypress-delay KEY, -k KEY
                        The delay between each keypress for the input to appear more realistic (in ms).
  --check CHECK, --check-delay CHECK, -c CHECK
                        The delay before checking if the answer is right or not (in secs).
```

## Contributing

Pull requests are welcome. For major changes, please open a discussion first to discuss what you would like to change.

## Built With

- [playwright](https://github.com/microsoft/playwright) - to control a web browser

## Authors

- **Animenosekai** - *Initial work* - [Animenosekai](https://github.com/Animenosekai)

## Licensing

This software is licensed under the MIT License. See the [*LICENSE*](./LICENSE) file for more information.

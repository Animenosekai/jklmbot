"""the core of this script"""
import argparse
import base64
import pathlib
import random
import time
import typing

from playwright.sync_api import Page, Playwright, sync_playwright

from jklmbot import __version__
from jklmbot.data.english import DICTIONARY as ENGLISH_DICTIONARY
from jklmbot.data.french import DICTIONARY as FRENCH_DICTIONARY
from jklmbot.data.german import DICTIONARY as GERMAN_DICTIONARY
from jklmbot.data.italian import DICTIONARY as ITALIAN_DICTIONARY
from jklmbot.data.nahuatl import DICTIONARY as NAHUATL_DICTIONARY
from jklmbot.data.spanish import DICTIONARY as SPANISH_DICTIONARY


def generate_user_id() -> str:
    """
    Returns
    -------
    str
    """
    return "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-") for _ in range(16))


def is_jpeg(data: bytes) -> bool:
    """
    Determine if the given object is a JPEG file

    Parameters
    ----------
    data: bytes

    Returns
    -------
    bool
    """
    buf = data[:max(8192, len(data))]
    return (len(buf) > 2 and
            buf[0] == 0xFF and
            buf[1] == 0xD8 and
            buf[2] == 0xFF)


def get_browser_from_name(name: str):
    """
    Parameters
    ----------
    name: str
    """
    name = str(name).lower().replace(" ", "")
    if name in ("firefox", "gecko"):
        return "firefox"
    elif name in ("webkit", "safari", "mac", "macos", "ios"):
        return "webkit"
    else:
        return "chromium"


def get_syllable(page: Page):
    """
    Parameters
    ----------
    page: Page
    """
    print("Getting the syllable...")
    syllable = str(page.frame_locator("iframe").locator(".syllable").text_content()).lower()
    print(f"🧃 The syllable is '{syllable}'")
    return syllable


def get_dictionary(page: Page):
    """
    Parameters
    ----------
    page: Page
    """
    print("🌐 Searching for the right dictionary...")
    language = str(page.frame_locator("iframe").locator(".dictionary").text_content()).lower().replace(" ", "")
    # print(f"Debug: `.dictionary` seems to be {language}")
    if language == "french":
        print("🧃 Found the French dictionary")
        DICTIONARY = FRENCH_DICTIONARY
    elif language == "german":
        print("🧃 Found the German dictionary")
        DICTIONARY = GERMAN_DICTIONARY
    elif language == "spanish":
        print("🧃 Found the Spanish dictionary")
        DICTIONARY = SPANISH_DICTIONARY
    elif language == "italian":
        print("🧃 Found the Italian dictionary")
        DICTIONARY = ITALIAN_DICTIONARY
    elif language == "nahuatl":
        print("🧃 Found the Nahuatl dictionary")
        DICTIONARY = NAHUATL_DICTIONARY

    elif language == "breton":
        print("😥 We do not support Breton yet (using the English dictionary)")
        DICTIONARY = ENGLISH_DICTIONARY
    elif language.startswith("brazilian"):
        print("😥 We do not support Braizilian Portuguese yet (using the English dictionary)")
        DICTIONARY = ENGLISH_DICTIONARY
    elif "pokemon" in language:
        print("😥 We do not support Pokemon languages yet (using the English dictionary)")
        DICTIONARY = ENGLISH_DICTIONARY

    else:
        print("🧃 Found the English dictionary")
        DICTIONARY = ENGLISH_DICTIONARY

    return DICTIONARY


def join_game(page: Page):
    """
    Parameters
    ----------
    page: Page
    """
    # Click text=Join game
    print("Joining game")

    JOINED = False
    while not JOINED:
        try:
            page.frame_locator("iframe").locator(".joinRound").click(timeout=1000)
            JOINED = True
        except Exception:
            JOINED = page.frame_locator("iframe").locator(".selfTurn").is_visible()


def run(playwright: Playwright, room: str, max_delay: float = 3, username: str = None, picture: pathlib.Path = None, check_delay: float = 1, keypress_delay: float = 100, headless: bool = False, browser: str = "chromium") -> None:
    """
    Runs the bot to play jklm

    Parameters
    ----------
    playwright: Playwright | playwright.sync_api.Playwright
        The Playwright context to run the bot from
    room: str
        The room code to enter
    max_delay: float, default = 3
        The maximum delay to use after getting a word before searching anything
    username: str, default = None
        The username to use. When None, uses the default random username.
    check_delay: float, default = 1
        The time to wait before checking if the answer was correct.
    keypress_delay: float, default = 100
        The delay between each keypress.
    headless: bool, default = False
        If the browser should be ran in headless mode or not.
    browser: str, default = "chromium"
        The browser to use.

    Returns
    -------
    None
    """
    if picture is not None:
        if not isinstance(picture, bytes):
            with open(picture, "r+b") as f:
                picture = f.read()

        if not is_jpeg(picture):
            raise TypeError("❌ The given picture does not seem to be a JPEG image")

        picture = base64.b64encode(picture).decode("utf-8")
        picture_length = len(picture)
        if picture_length > 10000:
            raise TypeError(f"❌ The given picture is too big ({picture_length}/10000)")

    browser = get_browser_from_name(browser)
    if browser == "firefox":
        browser = playwright.firefox.launch(headless=headless)
    elif browser == "webkit":
        browser = playwright.webkit.launch(headless=headless)
    else:
        browser = playwright.chromium.launch(headless=headless)

    context = browser.new_context()
    # Open new page
    page = context.new_page()
    if picture:
        if not username:
            username = f"Guest{''.join(random.choice('0123456789') for _ in range(4))}"
        page.add_init_script(script=f"""
        window.localStorage.setItem("jklmSettings", '{{"version":2,"volume":0.5,"muted":false,"chatFilter":[],"nickname":"{username}", "picture": "{picture}"}}')
        """)

    # Go to https://jklm.fun/{room}
    print(f"Going to https://jklm.fun/{room}")
    page.goto(f"https://jklm.fun/{room}")
    # Click text=OK
    print("Entering username")
    JOINABLE = False

    while not JOINABLE:
        try:
            if username is not None:
                # Click [placeholder="Your name"]
                page.locator("input.nickname").click(timeout=1000)
                # Press a with modifiers
                page.locator("input.nickname").press("Meta+a")
                # Fill [placeholder="Your name"]
                page.locator("input.nickname").type(username)
                # Press Enter
                page.locator("input.nickname").press("Enter")
            else:
                page.locator("button.styled").click(timeout=1000)
        except Exception:
            # from rich.console import Console
            # Console().print_exception()
            JOINABLE = page.frame_locator("iframe").locator(".joinRound").is_visible(
            ) or page.frame_locator("iframe").locator(".selfTurn").is_visible()

    join_game(page)
    USED_WORDS = []
    while True:
        print("🍡 Waiting for the input to be visible...")

        VISIBLE = False
        while not VISIBLE:
            try:
                page.frame_locator("iframe").locator(".selfTurn").wait_for(state="visible", timeout=1000)
                VISIBLE = True
            except Exception:
                if page.frame_locator("iframe").locator(".joinRound").is_visible():
                    join_game(page)

        print("✅ Input visible")
        print("Waiting a bit to to not be caught")
        time.sleep(random.random() * max_delay)
        # Click .syllable
        syllable = get_syllable(page)
        page.frame_locator("iframe").locator(".selfTurn").click()
        for element in get_dictionary(page):
            if syllable in element and element not in USED_WORDS:
                try:
                    print(f"Found '{element}' which has '{syllable}'")
                    page.frame_locator("iframe").locator(".selfTurn").type(element, delay=keypress_delay)
                    print("Pressing [Enter]")
                    USED_WORDS.append(element)
                    page.frame_locator("iframe").locator(".selfTurn").press("Enter")
                    time.sleep(check_delay)
                    if not page.frame_locator("iframe").locator(".selfTurn").is_visible():
                        break
                    syllable = get_syllable(page)
                except Exception:
                    time.sleep(0.1)
    # ---------------------
    context.close()
    browser.close()


def entry():
    """the main entrypoint"""
    parser = argparse.ArgumentParser(prog='jklmbot', description='Win all of your JKLM.fun games!')
    parser.add_argument("--version", "-v", action="version", version=__version__)

    # parser.add_argument('--version', '-v', action='version', version=translatepy.__version__)
    parser.add_argument("--room", "-r", action="store", type=str, help="The room to enter.", required=True)
    parser.add_argument("--username", "-u", action="store", type=str, help="The username to use.", required=False, default=None)
    parser.add_argument("--picture", "-p", action="store", type=str, help="The profile picture to use.", required=False, default=None)
    parser.add_argument("--browser", "-b", action="store", type=str,
                        help="The browser to use (chromium|firefox|webkit).", required=False, default="chromium")
    parser.add_argument("--headless", action="store_true",
                        help="Wether to run the browser without a graphical interface.")
    parser.add_argument("--delay", "--max-delay", "-d", action="store", type=float,
                        help="The maximum delay before searching for answers to avoid being caught (in secs).", required=False, default=3)
    parser.add_argument("--key", "--key-delay", "--keystroke-delay", "--keyboard-delay", "--keypress-delay", "-k", action="store", type=float,
                        help="The delay between each keypress for the input to appear more realistic (in ms).", required=False, default=100)
    parser.add_argument("--check", "--check-delay", "-c", action="store", type=float,
                        help="The delay before checking if the answer is right or not (in secs).", required=False, default=1)

    args = parser.parse_args()

    with sync_playwright() as playwright:
        try:
            run(playwright, room=args.room, max_delay=args.delay, username=args.username, picture=args.picture,
                check_delay=args.check, keypress_delay=args.key, headless=args.headless, browser=args.browser)
        except Exception as err:
            # from rich.console import Console
            # Console().print_exception()
            print("")
            print(" ".join(err.args))
            print("")


if __name__ == "__main__":
    entry()

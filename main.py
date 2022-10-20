import argparse
import random
import sys
import time

from playwright.sync_api import Playwright, sync_playwright, Page

from data.english import DICTIONARY as ENGLISH_DICTIONARY
from data.french import DICTIONARY as FRENCH_DICTIONARY
from data.german import DICTIONARY as GERMAN_DICTIONARY
from data.italian import DICTIONARY as ITALIAN_DICTIONARY
from data.nahuatl import DICTIONARY as NAHUATL_DICTIONARY
from data.spanish import DICTIONARY as SPANISH_DICTIONARY


def join_game(page: Page):
    # Click text=Join game
    print("Joining game")
    page.frame_locator("iframe").locator("text=Join game").click()

    time.sleep(1)
    print("Searching for the right dictionary...")
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
        print("😥 We do not support Breton yet")
        sys.exit(1)
    elif language.startswith("brazilian"):
        print("😥 We do not support Braizilian Portuguese yet")
        sys.exit(1)
    else:
        print("🧃 Found the English dictionary")
        DICTIONARY = ENGLISH_DICTIONARY

    return DICTIONARY


def run(playwright: Playwright, room: str, max_delay: float = 3, username: str = None, check_delay: float = 1) -> None:
    """
    Runs the bot to play jklm

    Parameters
    ----------
    playwright: playwright.sync_api.Playwright
        The Playwright context to run the bot from
    room: str
        The room code to enter
    max_delay: float, default = 3
        The maximum delay to use after getting a word before searching anything
    username: str, default = None
        The username to use. When None, uses the default random username.
    check_delay: float, default = 1
        The time to wait before checking if the answer was correct.
    """
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    # Open new page
    page = context.new_page()
    # Go to https://jklm.fun/{room}
    print(f"Going to https://jklm.fun/{room}")
    page.goto(f"https://jklm.fun/{room}")
    # Click text=OK
    print("Entering username")
    if username is not None:
        # Click [placeholder="Your name"]
        page.locator("[placeholder=\"Your name\"]").click()
        # Press a with modifiers
        page.locator("[placeholder=\"Your name\"]").press("Meta+a")
        # Fill [placeholder="Your name"]
        page.locator("[placeholder=\"Your name\"]").type(username)
        # Press Enter
        page.locator("[placeholder=\"Your name\"]").press("Enter")
    else:
        page.locator("text=OK").click()

    DICTIONARY = join_game(page)

    while True:
        print("🍡 Waiting for the input to be visible...")
        # if page.frame_locator("iframe").locator("text=won the last round!").is_visible():
        #     DICTIONARY = join_game(page)
        page.frame_locator("iframe").locator("input[type=\"text\"]").wait_for(state="visible", timeout=0)
        print("✅ Input visible")
        print("Waiting a bit to to not be caught")
        time.sleep(random.random() * max_delay)
        # Click .syllable
        print("Getting the syllable...")
        syllable = str(page.frame_locator("iframe").locator(".syllable").text_content()).lower()
        print(f"🧃 The syllable is {syllable}")
        page.frame_locator("iframe").locator("input[type=\"text\"]").click()
        for element in DICTIONARY:
            if syllable in element:
                try:
                    print(f"Found {element} which has {syllable}")
                    page.frame_locator("iframe").locator("input[type=\"text\"]").type(element, delay=100)
                    print("Pressing [Enter]")
                    page.frame_locator("iframe").locator("input[type=\"text\"]").press("Enter")
                    time.sleep(check_delay)
                    if not page.frame_locator("iframe").locator("input[type=\"text\"]").is_visible():
                        break
                except Exception:
                    time.sleep(0.1)
    # ---------------------
    context.close()
    browser.close()


def main():
    parser = argparse.ArgumentParser(
        prog='jklmbot', description='Win all of your JKLM.fun games!')

    # parser.add_argument('--version', '-v', action='version', version=translatepy.__version__)
    parser.add_argument("--room", "-r", action="store", type=str, help="The room to enter.", required=True)
    parser.add_argument("--username", "-u", action="store", type=str, help="The username to use.", required=False, default=None)
    parser.add_argument("--delay", "--max-delay", "-d", action="store", type=float,
                        help="The maximum delay before searching for answers to avoid being caught.", required=False, default=3)
    parser.add_argument("--check", "--check-delay", "-c", action="store", type=float,
                        help="The delay before checking if the answer is right or not.", required=False, default=1)

    args = parser.parse_args()

    with sync_playwright() as playwright:
        run(playwright, room=args.room, max_delay=args.delay, username=args.username, check_delay=args.check)


if __name__ == "__main__":
    main()

import argparse
import random
import sys
import time

from playwright.sync_api import Page, Playwright, sync_playwright

from data.english import DICTIONARY as ENGLISH_DICTIONARY
from data.french import DICTIONARY as FRENCH_DICTIONARY
from data.german import DICTIONARY as GERMAN_DICTIONARY
from data.italian import DICTIONARY as ITALIAN_DICTIONARY
from data.nahuatl import DICTIONARY as NAHUATL_DICTIONARY
from data.spanish import DICTIONARY as SPANISH_DICTIONARY


def get_dictionary(page: Page):
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


def run(playwright: Playwright, room: str, max_delay: float = 3, username: str = None, check_delay: float = 1, headless: bool = False) -> None:
    """
    Runs the bot to play jklm

    Parameters
    ----------
    playwright: playwright.sync_api.Playwright | Playwright
        The Playwright context to run the bot from
    room: str
        The room code to enter
    max_delay: float, default = 3
        The maximum delay to use after getting a word before searching anything
    username: str, default = None
        The username to use. When None, uses the default random username.
    check_delay: float, default = 1
        The time to wait before checking if the answer was correct.
    headless: bool, default = False
        If the browser should be ran in headless mode or not.

    Returns
    -------
    None
    """
    browser = playwright.chromium.launch(headless=headless)
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
        print("Getting the syllable...")
        syllable = str(page.frame_locator("iframe").locator(".syllable").text_content()).lower()
        print(f"🧃 The syllable is {syllable}")
        page.frame_locator("iframe").locator(".selfTurn").click()
        for element in get_dictionary(page):
            if syllable in element and element not in USED_WORDS:
                try:
                    print(f"Found {element} which has {syllable}")
                    page.frame_locator("iframe").locator(".selfTurn").type(element, delay=100)
                    print("Pressing [Enter]")
                    USED_WORDS.append(element)
                    page.frame_locator("iframe").locator(".selfTurn").press("Enter")
                    time.sleep(check_delay)
                    if not page.frame_locator("iframe").locator(".selfTurn").is_visible():
                        break
                except Exception:
                    time.sleep(0.1)
    # ---------------------
    context.close()
    browser.close()


def main():
    """
    """
    parser = argparse.ArgumentParser(
        prog='jklmbot', description='Win all of your JKLM.fun games!')

    # parser.add_argument('--version', '-v', action='version', version=translatepy.__version__)
    parser.add_argument("--room", "-r", action="store", type=str, help="The room to enter.", required=True)
    parser.add_argument("--username", "-u", action="store", type=str, help="The username to use.", required=False, default=None)
    parser.add_argument("--headless", action="store_true",
                        help="Wether to run the browser without a graphical interface.")
    parser.add_argument("--delay", "--max-delay", "-d", action="store", type=float,
                        help="The maximum delay before searching for answers to avoid being caught.", required=False, default=3)
    parser.add_argument("--check", "--check-delay", "-c", action="store", type=float,
                        help="The delay before checking if the answer is right or not.", required=False, default=1)

    args = parser.parse_args()

    with sync_playwright() as playwright:
        run(playwright, room=args.room, max_delay=args.delay, username=args.username, check_delay=args.check, headless=args.headless)


if __name__ == "__main__":
    main()

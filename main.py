import argparse
import random
import time
from playwright.sync_api import Playwright, sync_playwright

from data.french import DICTIONARY


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

    # Click text=Join game
    print("Joining game")
    page.frame_locator("iframe").locator("text=Join game").click()

    while True:
        print("🍡 Waiting for the input to be visible...")
        page.frame_locator("iframe").locator("input[type=\"text\"]").wait_for(state="visible", timeout=0)
        print("✅ Input visible")
        print("Waiting a bit to to not be caught")
        time.sleep(random.random() * max_delay)
        # Click .syllable
        print("Getting the syllable...")
        syllable = page.frame_locator("iframe").locator(".syllable").text_content().lower()
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
        prog='translatepy', description='Translate, transliterate, get the language of texts in no time with the help of multiple APIs!')

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

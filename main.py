import contextlib
import os, sys
import queue
import random
import threading
import undetected_chromedriver as uc
import time, proxy
from tempfile import mkdtemp
from typing import Tuple, List
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from email_manager import get_kick_email, extract_urls
from selenium.webdriver.common.action_chains import ActionChains


def move_and_click(driver, element) -> None:
    ActionChains(driver).move_to_element(element).click().perform()


def make_account(
    email: str, password: str, proxy_addr: str, thread_no: int
) -> Tuple[str, str]:
    print(f"=> Making account {email}")
    endpoint_p, username_p, password_p, port_p = parse_auth_proxy(proxy_addr)
    proxies_extension = proxy.proxies(
        username_p, password_p, endpoint_p, port_p, str(thread_no)
    )
    options = uc.ChromeOptions()
    options.add_argument(
        f"--load-extension={proxies_extension}"
    )
    time.sleep(5)
    driver = uc.Chrome(
        user_data_dir=mkdtemp(),
        options=options,
    )
    try:
        with contextlib.suppress(Exception):
            if urls := verify_account(email, password):
                print("=> Account already exists")
                driver.get(urls)
                accept_cookies(driver)
                find_element_by_xpath_and_click(driver, 15, '//*[text() = "Accept"]', 5)
                time.sleep(10)
                driver.quit()
                return
        # print(e)

        time.sleep(3)
        driver.get("https://www.kick.com")
        focus_the_page(driver)
        find_element_by_xpath_and_click(driver, 35, '//span[text() = "Sign Up"]', 3)
        accept_cookies(driver)

        find_element_and_send_keys(driver, "email", email)
        find_element_and_send_keys(driver, "username", email.split("@")[0])
        find_element_and_send_keys(driver, "password", "Abracadabr@12")
        find_element_and_send_keys(driver, "password_confirmation", "Abracadabr@12")

        choose_date_of_birth(driver)
        time.sleep(5)

        with contextlib.suppress(Exception):
            if elements := driver.find_elements(
                By.XPATH, '//*[contains(@class, "error input")]'
            ):
                print(
                    f"=> Error in filling form Account {email} probably already exists."
                )
                return

        element = WebDriverWait(driver, 35).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text() = "Next "]'))
        )
        element = element.find_element(By.XPATH, "..")
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        move_and_click(driver, element)
        time.sleep(10)
        print(f"=> Form filled for {email}")

        try:
            url = verify_account(email, password)
            print(f"=> Verifying Account {email} using link {url}")
            driver.get(url)
            time.sleep(5)
            accept_cookies(driver=driver)
            find_element_by_xpath_and_click(driver, 15, '//*[text() = "Accept"]', 5)
        except Exception as e:
            print(f"=> Error Verifing account {email} Error: {e}")

    finally:
        print(f"Account made successfully Email {email}, Password Abracadabr@12")
        with contextlib.suppress(Exception):
            driver.quit()


def find_element_by_xpath_and_click(
    driver, delay_secs: int, xpath: str, sleep_time: int
):
    elem = WebDriverWait(driver, delay_secs).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    move_and_click(driver, elem)
    time.sleep(sleep_time)


def accept_cookies(driver):
    with contextlib.suppress(Exception):
        elem = WebDriverWait(driver, 7).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[contains(@class, "grow")]/button[text() = "Accept"]')
            )
        )
        move_and_click(driver, elem)
    time.sleep(3)


def choose_date_of_birth(driver):
    choose_random_list_field(driver, '//span[text() = "Month"]')
    choose_random_list_field(driver, '//span[text() = "Day"]')
    elem = WebDriverWait(driver, 35).until(
        EC.element_to_be_clickable((By.XPATH, '//span[text() = "Year"]'))
    )
    move_and_click(driver, elem)

    sleep_for_random_time()

    element = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//span[text() = "2001"]'))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    move_and_click(driver, element)


def choose_random_list_field(driver, list_xpath: str):
    elem = WebDriverWait(driver, 35).until(
        EC.element_to_be_clickable((By.XPATH, list_xpath))
    )
    move_and_click(driver, elem)

    time.sleep(2)
    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//li[@role = "option"]'))
    )
    element = random.choice(driver.find_elements(By.XPATH, '//li[@role = "option"]'))
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    move_and_click(driver, element)


def find_element_and_send_keys(driver: uc.Chrome, id: str, text_to_send: str) -> None:
    elem = WebDriverWait(driver, 35).until(EC.element_to_be_clickable((By.ID, id)))
    send_slow_keys(elem, text_to_send)
    time.sleep(2)


def read_email_file(file_name: str) -> List[Tuple[str, str]]:
    with open(file_name, "rt") as fp:
        text = fp.readlines()
    return [
        (email.split(":")[0].strip(), email.split(":")[1].strip()) for email in text
    ]


def verify_account(email: str, password: str) -> str:
    email_text = get_kick_email(email, password)
    urls = extract_urls(email_text)
    #    print(f"Urls found: {urls} Email Text: {email_text}")
    return next((url for url in urls if "verify" in url), "")


def parse_auth_proxy(url: str) -> Tuple[str, str, str, str]:
    split = url.split("@")
    port = split[1].split(":")[1]
    domain = split[1].split(":")[0]

    split2 = split[0].removeprefix("http://").removeprefix("https://").split(":")
    username = split2[0]
    password = split2[1]
    return domain, username, password, port


def focus_the_page(driver):
    """
    Focuses the page.
    """
    targets = driver.execute_cdp_cmd("Target.getTargets", {})["targetInfos"]
    wanted_target = next(
        (target for target in targets if "kick.com" in target["url"]), None
    )
    driver.execute_cdp_cmd(
        "Target.activateTarget", {"targetId": wanted_target["targetId"]}
    )


def get_proxies(filename: str):
    with open(filename, "rt") as fp:
        return fp.readlines()


def add_noise(element):
    element.send_keys(chr(65))
    sleep_for_random_time(0.15, 0.2)
    element.send_keys(Keys.BACKSPACE)
    sleep_for_random_time(0.15, 0.2)


def send_slow_keys(element, text: str) -> None:
    noise_count = 1
    for i, char in enumerate(text):
        if i % 2 == 0 and noise_count < 3:
            noise_count += 1
            add_noise(element)
        element.send_keys(char)
        sleep_for_random_time(0.15, 0.2)


def sleep_for_random_time(start: int = 3, end: int = 5) -> None:
    rand_time = random.uniform(start, end)
    time.sleep(rand_time)


def make_account_threaded(
    email_queue: queue.Queue, proxy_list: List[str], thread_no: int
):
    while not email_queue.empty():
        email = email_queue.get()
        try:
            make_account(email[0], email[1], random.choice(proxy_list), thread_no)
        except Exception as e:
            print(f"=> Error in making account. Error: {email[0]}")


if __name__ == "__main__":
    try:
        thread_no = int(sys.argv[1])
    except Exception:
        thread_no = int(input("ENTER THE NUMBER OF THREADS: RECOMMENDED[1-5] \n"))

    email_queue = queue.Queue()
    proxy_list = get_proxies("proxies.txt")
    for email in reversed(read_email_file("emails.txt")):
        email_queue.put(email)
        
    for i in range(thread_no):
        threading.Thread(
            target=make_account_threaded, args=(email_queue, proxy_list, i)
        ).start()

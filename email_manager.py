import poplib, email
import time
from urlextract import URLExtract
from typing import List

def get_kick_email(email_string: str, password: str, delay: int = 30) -> str:
    start_time = time.time()
    while time.time() - start_time < delay:
        mail = poplib.POP3_SSL('outlook.office365.com', 995)
        mail.user(email_string)
        mail.pass_(password)
        num_messages = len(mail.list()[1])
        for i in range(num_messages):
            response = mail.retr(i+1)
            raw_message = b'\n'.join(response[1])
            parsed_email = email.message_from_bytes(raw_message)
            if "kick.com" in parsed_email["From"]:
                if parsed_email.is_multipart():
                    for part in parsed_email.get_payload():
                        if part.get_content_type() == 'text/plain':
                            return part.get_payload(decode=True).decode()
                else:
                    return parsed_email.get_payload(decode=True).decode()
    mail.quit()
    return ""

def extract_urls(text: str) -> List[str]:
    extractor = URLExtract()
    return extractor.find_urls(text)



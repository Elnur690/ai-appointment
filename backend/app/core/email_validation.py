import re
import socket
from fastapi import HTTPException, status

KNOWN_TRUSTED_PROVIDERS = {
    "gmail.com",
    "googlemail.com",
    "outlook.com",
    "hotmail.com",
    "live.com",
    "msn.com",
    "yahoo.com",
    "yahoo.co.uk",
    "icloud.com",
    "me.com",
    "mac.com",
    "proton.me",
    "protonmail.com",
    "mail.ru",
    "inbox.ru",
    "list.ru",
    "bk.ru",
    "yandex.ru",
    "yandex.com",
    "ya.ru",
    "zoho.com",
    "zohomail.com",
    "aol.com",
    "gmx.com",
    "gmx.net",
    "fastmail.com",
    "tutanota.com",
    "tuta.io",
    "rambler.ru",
    "box.az",
    "mail.az",
}

DISPOSABLE_EMAIL_DOMAINS = {
    "tempmail.com",
    "temp-mail.org",
    "temp-mail.io",
    "tempmailo.com",
    "tempail.com",
    "tmpmail.org",
    "tmpmail.net",
    "10minutemail.com",
    "10minutemail.net",
    "guerrillamail.com",
    "guerrillamail.org",
    "guerrillamail.net",
    "guerrillamailblock.com",
    "sharklasers.com",
    "mailinator.com",
    "mailinator.net",
    "yopmail.com",
    "yopmail.fr",
    "throwawaymail.com",
    "trashmail.com",
    "trashmail.net",
    "getnada.com",
    "dispostable.com",
    "maildrop.cc",
    "fakeinbox.com",
    "mintemail.com",
    "mohmal.com",
    "emailondeck.com",
    "burnermail.io",
    "33mail.com",
    "inboxbear.com",
    "dropmail.me",
    "moakt.com",
    "mailnesia.com",
    "mytemp.email",
    "luxusmail.org",
    "crazymailing.com",
    "harakirimail.com",
    "spam4.me",
    "spambog.com",
    "getairmail.com",
    "discard.email",
    "mailcatch.com",
    "mailnull.com",
    "TempEMail.net",
}

DISPOSABLE_KEYWORDS = (
    "tempmail",
    "temp-mail",
    "tmpmail",
    "10minute",
    "throwaway",
    "guerrilla",
    "mailinator",
    "yopmail",
    "trashmail",
    "disposable",
    "burnermail",
    "fakeinbox",
)


def is_disposable_or_invalid_email(email: str, check_dns: bool = False) -> tuple[bool, str | None]:
    """
    Validate that an email belongs to a known trusted provider or a legitimate custom business domain,
    rejecting temporary/disposable email domains.
    Returns (is_allowed, error_reason).
    """
    clean = (email or "").strip().lower()
    if "@" not in clean:
        return False, "Invalid email address."

    domain = clean.split("@", 1)[1].strip()
    if not re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", domain):
        return False, "Invalid email domain."

    if domain in {d.lower() for d in DISPOSABLE_EMAIL_DOMAINS} or any(
        kw in domain for kw in DISPOSABLE_KEYWORDS
    ):
        return False, "Temporary or disposable email addresses are not allowed. Please use your business domain or a trusted email provider."

    if domain in KNOWN_TRUSTED_PROVIDERS:
        return True, None

    # Custom business domain: optionally verify domain resolves in DNS
    if check_dns:
        try:
            socket.getaddrinfo(domain, None)
        except OSError:
            return False, "Custom email domain could not be verified. Please use a valid business domain or trusted email provider."

    return True, None


def assert_allowed_registration_email(email: str, check_dns: bool = False) -> None:
    allowed, reason = is_disposable_or_invalid_email(email, check_dns=check_dns)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason or "Disposable email addresses are not permitted.",
        )

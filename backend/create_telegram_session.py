"""One-time script to create a Telegram session file.

Run this ONCE in an interactive terminal:
    python create_telegram_session.py

It will prompt for:
  1. Your phone number (with country code, e.g. +91XXXXXXXXXX)
  2. The OTP code sent to your Telegram app
  3. Your 2FA cloud password (ONLY if you have Two-Step Verification enabled)

After successful login, a session file (e.g. 'crowdpulse.session') is created
in the backend/ directory. The scraper will then work headlessly.

If you hit a rate limit error, wait 15-30 minutes and try again.
"""

import asyncio
from app.core.config import get_settings

settings = get_settings()


async def main():
    from telethon import TelegramClient
    from telethon.errors import (
        SessionPasswordNeededError,
        FloodWaitError,
    )

    print("=" * 60)
    print("  Telegram Session Creator for CrowdPulse")
    print("=" * 60)
    print(f"  API ID:       {settings.TELEGRAM_API_ID}")
    print(f"  Session name: {settings.TELEGRAM_SESSION_NAME}")
    print()

    client = TelegramClient(
        settings.TELEGRAM_SESSION_NAME,
        int(settings.TELEGRAM_API_ID),
        settings.TELEGRAM_API_HASH,
    )

    await client.connect()

    # Already authorized from a previous session
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Already logged in as: {me.first_name} (ID: {me.id})")
        print(f"Session file: {settings.TELEGRAM_SESSION_NAME}.session")
        await client.disconnect()
        return

    phone = input("Enter your phone number (e.g. +919XXXXXXXXX): ").strip()

    try:
        await client.send_code_request(phone)
    except FloodWaitError as e:
        print(f"\nRate limited! Telegram says wait {e.seconds} seconds.")
        print("Try again later.")
        await client.disconnect()
        return
    except Exception as e:
        print(f"\nError sending code: {e}")
        print("If you see 'SendCodeUnavailableError', wait 15-30 min and retry.")
        await client.disconnect()
        return

    code = input("Enter the OTP code from Telegram: ").strip()

    try:
        await client.sign_in(phone, code)
    except SessionPasswordNeededError:
        print()
        print("Your account has Two-Step Verification (2FA) enabled.")
        print("This is the cloud password you set in Telegram Settings > Privacy > Two-Step Verification.")
        password = input("Enter your 2FA password: ").strip()
        await client.sign_in(password=password)
    except Exception as e:
        print(f"\nSign-in failed: {e}")
        await client.disconnect()
        return

    me = await client.get_me()
    print(f"\nLogged in as: {me.first_name} (ID: {me.id})")
    print(f"Session file created: {settings.TELEGRAM_SESSION_NAME}.session")
    print("\nYou can now run the live pipeline — Telegram will work headlessly.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

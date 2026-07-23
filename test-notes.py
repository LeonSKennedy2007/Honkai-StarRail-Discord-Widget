import asyncio
import os
import sys
import genshin

HSR_UID = os.environ.get("HSR_UID", "")
HOYOLAB_LTUID = os.environ.get("HOYOLAB_LTUID", "")
HOYOLAB_LTOKEN = os.environ.get("HOYOLAB_LTOKEN", "")

if not HSR_UID or not HOYOLAB_LTUID or not HOYOLAB_LTOKEN:
    print("✗ Missing one or more required secrets (HSR_UID, HOYOLAB_LTUID, HOYOLAB_LTOKEN).")
    sys.exit(1)


async def main():
    cookies = {"ltuid_v2": HOYOLAB_LTUID, "ltoken_v2": HOYOLAB_LTOKEN}
    client = genshin.Client(cookies)

    print("→ Fetching get_starrail_notes()...")
    notes = await client.get_starrail_notes(HSR_UID)
    print("✓ Success! Fields returned:")
    print(notes.model_dump())


asyncio.run(main())

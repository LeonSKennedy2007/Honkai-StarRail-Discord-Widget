import asyncio
import os
import sys
import requests
import genshin

# =====================================================
# Read secrets from environment variables (GitHub Secrets)
# =====================================================

HSR_UID = os.environ.get("HSR_UID", "")
HOYOLAB_LTUID = os.environ.get("HOYOLAB_LTUID", "")
HOYOLAB_LTOKEN = os.environ.get("HOYOLAB_LTOKEN", "")
DISCORD_APP_ID = os.environ.get("APPLICATION_ID", "")
DISCORD_USER_ID = os.environ.get("DISCORD_USER_ID", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

REQUIRED_SECRETS = {
    "HSR_UID": HSR_UID,
    "HOYOLAB_LTUID": HOYOLAB_LTUID,
    "HOYOLAB_LTOKEN": HOYOLAB_LTOKEN,
    "APPLICATION_ID": DISCORD_APP_ID,
    "DISCORD_USER_ID": DISCORD_USER_ID,
    "BOT_TOKEN": BOT_TOKEN,
}


def validate_secrets():
    print("Validating required secrets...")
    missing = [name for name, value in REQUIRED_SECRETS.items() if not value]
    if missing:
        for name in missing:
            print(f"✗ Missing GitHub Secret: {name}")
        sys.exit(1)
    print("✓ All required secrets present.")


async def update_widget():
    validate_secrets()

    print("▶ Starting HSR -> Discord widget update...")

    # -------------------------------------------------
    # Step 1: Enka Network (public, no login needed)
    # -------------------------------------------------
    enka_url = f"https://enka.network/api/hsr/uid/{HSR_UID}"
    print(f"→ Fetching Enka data: {enka_url}")

    try:
        enka_headers = {"User-Agent": "DiscordHSRWidget/1.0"}
        response = requests.get(enka_url, headers=enka_headers, timeout=15)
        response.raise_for_status()
        enka_data = response.json()

        detail_info = enka_data.get('detailInfo', {})
        record_info = detail_info.get('recordInfo', {})

        trailblaze_level = str(detail_info.get('level', '0'))
        achievements = str(record_info.get('achievementCount', '0'))
        characters_obtained = str(record_info.get('avatarCount', '0'))
        light_cones = str(record_info.get('equipmentCount', '0'))

        print(f"  ✓ Trailblaze Level: {trailblaze_level}")
        print(f"  ✓ Achievements: {achievements}")
        print(f"  ✓ Characters: {characters_obtained}")
        print(f"  ✓ Light Cones: {light_cones}")

    except requests.exceptions.Timeout:
        print("✗ Enka API timed out.")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Failed to fetch Enka data: {e}")
        sys.exit(1)

    # -------------------------------------------------
    # Step 2: HoYoLAB (requires your own login cookies)
    # -------------------------------------------------
    days_logged_in = "Unknown"
    treasure_chests = "Unknown"

    print("→ Fetching HoYoLAB data...")
    try:
        cookies = {"ltuid_v2": HOYOLAB_LTUID, "ltoken_v2": HOYOLAB_LTOKEN}
        client = genshin.Client(cookies)
        hsr_data = await client.get_starrail_user(HSR_UID)
        days_logged_in = str(hsr_data.stats.active_days)
        treasure_chests = str(hsr_data.stats.chest_num)

        print(f"  ✓ Login Days: {days_logged_in}")
        print(f"  ✓ Treasure Chests: {treasure_chests}")

    except genshin.errors.DataNotPublic:
        print("✗ Your HoYoLAB Star Rail Battle Chronicle is set to PRIVATE.")
        print("  Fix: HoYoLAB app/site -> your profile -> Battle Chronicle -> Privacy Settings -> make Star Rail public.")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Failed to fetch HoYoLAB data: {e}")
        sys.exit(1)

    # -------------------------------------------------
    # Step 3: Build payload and send to Discord
    # -------------------------------------------------
    payload = {
        "data": {
            "dynamic": [
                {"type": 1, "name": "trailblaze_level", "value": trailblaze_level},
                {"type": 1, "name": "achievements", "value": achievements},
                {"type": 1, "name": "treasures_chests", "value": treasure_chests},
                {"type": 1, "name": "days_logged_in", "value": days_logged_in},
                {"type": 1, "name": "characters_obtained", "value": characters_obtained},
                {"type": 1, "name": "light_cones", "value": light_cones},
            ]
        }
    }

    print("Widget preview:")
    print(payload)

    discord_url = f"https://discord.com/api/v9/applications/{DISCORD_APP_ID}/users/{DISCORD_USER_ID}/identities/0/profile"
    discord_headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://github.com/discord/discord-api-docs, 1.0.0)"
    }

    try:
        resp = requests.patch(discord_url, json=payload, headers=discord_headers, timeout=10)
        if resp.status_code in [200, 204]:
            print(f"✓ Discord profile widget updated (status {resp.status_code}).")
        else:
            print(f"✗ Discord API error ({resp.status_code}): {resp.text}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Failed to connect to Discord: {e}")
        sys.exit(1)

    print("▶ All done!")


if __name__ == "__main__":
    asyncio.run(update_widget())

# Easy WoW Fishing Bot
This bot automates fishing in World of Warcraft, enabling you to fish without manual intervention. The bot is written in Python and uses image recognition to detect the bobber and reel in the fish.

## Features

- Automatically casts and reels in fish.
- Simple setup with customizable options.
- Supports WoW Retail and Classic versions.
- Can apply fishing lures automatically.


## Requirements

- Python 3.x
- opencv-python package for image processing
- World of Warcraft installed

## Installation

- Clone the repository
- Open your terminal and clone the repository:

```
git clone https://github.com/NiclaasMoldenhauer/easy-wow-fishing-bot.git
```

- Install dependencies
- Navigate into the project folder and install the required Python packages:

```
cd easy-wow-fishing-bot
pip install -r requirements.txt
```

## Set up WoW

- Bind your fishing skill to a key in the game (e.g., 1 on the action bar).
- Make sure the WoW client is running in windowed mode for proper pixel detection.
- Zoom in first person

- fishing_key: The key to cast the fishing line (e.g., 1).
- loot_key: The key to interact with the loot (e.g., F).
- Run the bot
- start the bot using the command:

```
python fishing.py
```

The bot will automatically detect the bobber and click to reel in when a fish is caught.

## Usage

Ensure the game is running in the primary monitor and use the default WoW interface for best results.
Position your character near water and cast the fishing line manually or use the bot's casting feature.

## Troubleshooting

If the bot fails to detect the bobber:
- Adjust the game’s brightness or gamma settings.
- Try different camera angles (first-person or third-person view).
- If the bot doesn’t cast, try running the bot as an administrator.
  
## Disclaimer
This bot is intended for educational purposes. Use at your own risk, and be mindful of the game's terms of service.

# CaYaHeatSeekerBot

![CaYaHeatSeekerBot](src/logo.png)

Heatseeker **training goalie** for [RLBot](https://rlbot.org).

Camps its own net, state-sets onto incoming shots, and counters with skewed forward-jump hits.

Offline practice only. Not for ranked, online, or RLBot tournaments.

## Install the bot (easiest)

1. Install [RLBotGUI](https://rlbot.org) if needed.
2. On this GitHub page click green **Code** → **Download ZIP**.
3. Extract the zip. Open the folder until you see `bot.cfg` in it  
   (often named `CaYaHeatSeekerBot-main`).
4. RLBotGUI → **+ Add** → pick that folder  
   (or **Manage bot folders** → add the same folder).  
   **CaYaHeatSeekerBot** should show up in the bot list.

Alternative if you use Git:
git clone https://github.com/cayatur/CaYaHeatSeekerBot.git

Then Add that cloned folder the same way.

## Play

1. RLBotGUI → **Extra** → tick **Enable State Setting**.  
   Required. Without it the bot cannot teleport.
2. Match settings → mode **Heatseeker**.
3. Drag **CaYaHeatSeekerBot** onto a team. Add yourself on the other team if you want to shoot on it.
4. Start match.

## Files

| File | Role |
|---|---|
| `bot.py` | Save and counter logic |
| `bot.cfg` | Name, tags, logo |
| `appearance.cfg` | Loadout |
| `logo.png` | GUI icon |

## Notes

- State setting is off in official RLBot tournaments.
- Do not use this in ranked Heatseeker.
- If the bot stands still, State Setting is off.

## Demo

- Video in this repo: [demo.mp4](https://github.com/CaYatur/CaYaHeatSeekerBot/blob/main/demo.mp4)
- Posted on X: [https://x.com/cayatur/status/2104243025136513428](https://x.com/cayatur/status/2104243025136513428)

## Author

ÇAĞAN TURGUT — CaYaDev
# CaYaHeatSeekerBot

<p align="center">
  <img src="src/logo.png" width="200" alt="CaYaHeatSeekerBot">
</p>

Heatseeker **training goalie** for [RLBot](https://rlbot.org).

Camps its own net, state-sets onto incoming shots, and counters with skewed forward-jump hits.

Offline practice only. Not for ranked, online, or RLBot tournaments.

## Features

- **Goalie only** — stays on its own half, waits near the net, does not roam midfield.
- **Teleport saves** — when the ball is coming in, the car is state-set onto the shot so contact is consistent.
- **Fast-shot wall** — on very high ball speed or a ball already in the crease, it sits *in front* of the ball instead of jumping through it.
- **Jump counters** — normal saves use a forward aerial-style smash with a locked-in skewed pitch / yaw / roll so the clearance is not a flat center tap.
- **Own-half leash** — will come out for mid-range shots on its half, then return to the net. It does not chase into the opponent half.
- **Graze recovery** — if it clips the ball but the ball is still going toward the net, it keeps locking instead of idling.
- **Heatseeker match** — built for homing-ball defense practice, not standard soccar.

State Setting must be enabled. Without it the bot cannot teleport and will look stuck.

## Install the bot (easiest)

1. Install [RLBotGUI](https://rlbot.org) if needed.
2. On this GitHub page click green **Code** → **Download ZIP**.
3. Extract the zip. Open folders until you see `bot.cfg`  
   (usually `CaYaHeatSeekerBot-main/src`).
4. RLBotGUI → **+ Add** → pick that folder  
   (or **Manage bot folders** → add the same folder).  
   **CaYaHeatSeekerBot** should show up in the bot list.

Git: git clone https://github.com/CaYatur/CaYaHeatSeekerBot.git

Then Add the `src` folder the same way.

## Play

1. RLBotGUI → **Extra** → tick **Enable State Setting**.
2. Match settings → mode **Heatseeker**.
3. Drag **CaYaHeatSeekerBot** onto a team. Put yourself on the other team to shoot on it.
4. Start match.

## Files

| File | Role |
|---|---|
| `src/bot.py` | Save and counter logic |
| `src/bot.cfg` | Name, tags, logo |
| `src/appearance.cfg` | Loadout |
| `src/logo.png` | GUI icon |
| `src/util/` | Vec / steer helpers |

## Notes

- State setting is off in official RLBot tournaments.
- Do not use this in ranked Heatseeker.
- If the bot stands still, State Setting is off.

## Demo

- Video in this repo: [demo.mp4](https://github.com/CaYatur/CaYaHeatSeekerBot/blob/main/demo.mp4)
- Posted on X: [https://x.com/cayatur/status/2104243025136513428](https://x.com/cayatur/status/2104243025136513428)

## Author

ÇAĞAN TURGUT — CaYaDev
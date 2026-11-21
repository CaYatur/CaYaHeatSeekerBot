# CaYaHeatSeekerBot

<p align="center">
  <img src="src/logo.png" width="200" alt="CaYaHeatSeekerBot">
</p>

Heatseeker **training goalie** for [RLBot](https://rlbot.org).

Camps its own net, state-sets onto incoming shots, and counters with skewed forward-jump hits.

Offline practice only. Not for ranked, online, or RLBot tournaments.

> **RLBot v5.** This branch targets [RLBot v5](https://rlbot.org) (python package `rlbot` 2.x, `bot.toml`).
> The original **RLBot v4** version (RLBotGUI, `bot.cfg`) lives on the [`v4` branch](https://github.com/CaYatur/CaYaHeatSeekerBot/tree/v4).

## Features

- **Goalie only** — stays on its own half, waits near the net, does not roam midfield.
- **Teleport saves** — when the ball is coming in, the car is state-set onto the shot so contact is consistent.
- **Fast-shot wall** — on very high ball speed or a ball already in the crease, it sits *in front* of the ball instead of jumping through it.
- **Jump counters** — normal saves use a forward aerial-style smash with a locked-in skewed pitch / yaw / roll so the clearance is not a flat center tap.
- **Own-half leash** — will come out for mid-range shots on its half, then return to the net. It does not chase into the opponent half.
- **Graze recovery** — if it clips the ball but the ball is still going toward the net, it keeps locking instead of idling.
- **Heatseeker match** — built for homing-ball defense practice, not standard soccar.

State Setting must be enabled. Without it the bot cannot teleport and will look stuck.

## Install the bot (RLBot v5 GUI)

1. Install the [RLBot v5 GUI](https://rlbot.org) and Python 3.11+.
2. Download this repo (green **Code** → **Download ZIP**, or `git clone https://github.com/CaYatur/CaYaHeatSeekerBot.git`) and extract it.
3. In the repo folder create the virtual environment the bot's `run_command` expects:
   ```
   python -m venv venv
   venv\Scripts\pip install -r requirements.txt        (Windows)
   venv/bin/pip install -r requirements.txt              (Linux)
   ```
4. In the RLBot GUI add the repo folder (or `src`) as a bot folder. It finds `src/bot.toml` and
   **CaYaHeatSeekerBot** shows up in the bot list.

## Play

1. Enable **State Setting** for the match (in the GUI's match/extra settings, or `enable_state_setting = true` in a match toml).
2. Game mode **Heatseeker**.
3. Put **CaYaHeatSeekerBot** on a team and yourself on the other team to shoot on it.
4. Start the match.

Without the GUI: activate the venv and run `python run.py`. It starts RLBotServer with `rlbot.toml`
(Heatseeker, state setting on, you on blue vs. the bot on orange).

## Example setups

### Redirect practice

You play the field. CaYaHeatSeekerBot sits in **your** net. A Heatseeker goalie sits in the **other** net.

| Team | Player |
|---|---|
| Your team | You + **CaYaHeatSeekerBot** |
| Other team | A second **CaYaHeatSeekerBot** (or any v5 botpack bot) |

Flow: the ball homes into your net → CaYa saves and punches out → you redirect. Repeat.

You can add the same bot twice in the RLBot v5 GUI, so both nets get a keeper.

### Shooting / beat-the-keeper practice

CaYaHeatSeekerBot only defends. It does not rush the kickoff: if nobody touches the ball, it starts the play itself after about 5–10 seconds.

| Team | Player |
|---|---|
| Your team | You |
| Other team | **CaYaHeatSeekerBot** (optionally + a v5 botpack bot for faster kickoffs) |

For a faster start, take the kickoff yourself or add any v5 botpack bot (Noob Black, Element, Wisp…) as a teammate. After that CaYa holds its net and you practice scoring on a keeper that almost does not concede.

Both setups: **State Setting** enabled, mode **Heatseeker**.

## Files

| File | Role |
|---|---|
| `src/bot.py` | Save and counter logic |
| `src/bot.toml` | Agent id, name, run command, details and tags |
| `src/loadout.toml` | Loadout |
| `src/logo.png` | GUI icon |
| `src/util/` | Vec / steer helpers |
| `rlbot.toml`, `run.py` | Local Heatseeker practice match |
| `bob.toml`, `bot.spec` | Build config for the RLBot v5 botpack ([bob](https://github.com/RLBot/bob) + PyInstaller) |

## Notes

- State setting is off in official RLBot tournaments.
- Do not use this in ranked Heatseeker.
- If the bot stands still, State Setting is off.

## Demo

- Video in this repo: [demo.mp4](https://github.com/CaYatur/CaYaHeatSeekerBot/blob/main/demo.mp4)
- Posted on X: [https://x.com/cayatur/status/2104243025136513428](https://x.com/cayatur/status/2104243025136513428)

## Author

ÇAĞAN TURGUT — CaYaDev
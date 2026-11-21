"""Offline smoke test: drives MyBot.get_output with fake RLBot v5 GamePackets (no game or RLBotServer needed).

Run: python tests/offline_harness.py
"""
import math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from rlbot import flat
import bot as botmod

sent = []

class FakeBot(botmod.MyBot):
    def __init__(self, index, team):
        self.index, self.team = index, team  # skip socket setup
        self.initialize()
    def set_game_state(self, gs):
        flat.DesiredGameState.unpack(gs.pack())  # must serialize
        sent.append(gs)
    def set_game_state_parts(self, balls={}, cars={}, match_info=None):
        from rlbot.utils import fill_desired_game_state
        self.set_game_state(fill_desired_game_state(balls, cars, match_info))

def phys(loc, vel=(0, 0, 0), rot=(0, 0, 0)):
    return flat.Physics(location=flat.Vector3(*loc), rotation=flat.Rotator(*rot),
                        velocity=flat.Vector3(*vel), angular_velocity=flat.Vector3(0, 0, 0))

def packet(t, ball_loc, ball_vel, cars, touch=None, demo=-1.0, no_ball=False):
    players = []
    for i, (team, loc) in enumerate(cars):
        lt = None
        if touch and touch[0] == i:
            lt = flat.Touch(game_seconds=touch[1], location=flat.Vector3(0, 0, 0), normal=flat.Vector3(0, 0, 1), ball_index=0)
        players.append(flat.PlayerInfo(physics=phys(loc), team=team, latest_touch=lt,
                                       demolished_timeout=demo if i == 1 else -1.0))
    balls = [] if no_ball else [flat.BallInfo(physics=phys(ball_loc, ball_vel))]
    return flat.GamePacket(players=players, balls=balls,
                           match_info=flat.MatchInfo(seconds_elapsed=t))

for team, idx in [(1, 1), (0, 0)]:
    sent.clear()
    b = FakeBot(idx, team)
    sign = -1 if team == 1 else 1  # direction toward our goal from mid
    own_y = 5120 if team == 1 else -5120
    cars = [(0, (0, -4000, 17)), (1, (0, 4000, 17))]
    # 1) idle, ball far & moving away -> home branch, state set because car far from home
    c = b.get_output(packet(1.0, (0, -own_y * 0.6, 93), (0, -sign * -500, 0), cars))
    assert isinstance(c, flat.ControllerState); n_home = len(sent)
    # 2) incoming slow shot -> _tp_hit (slow path)
    c = b.get_output(packet(2.0, (300, own_y * 0.5, 93), (0, (own_y / abs(own_y)) * 1200, 0), cars))
    assert c.jump and c.boost and c.pitch == -1.0 and c.throttle == 1.0
    # 3) incoming fast shot -> fast path
    c = b.get_output(packet(2.1, (-200, own_y * 0.7, 300), (100, (own_y / abs(own_y)) * 3000, 0), cars))
    assert c.jump
    # 4) our touch just happened -> skew flips, pose reset
    skew0 = b.skew
    b.get_output(packet(3.0, (0, own_y * 0.8, 93), (0, -(own_y / abs(own_y)) * 1500, 0), cars, touch=(idx, 2.95)))
    assert b.skew == -skew0 and b.last_touch_time == 2.95
    # same touch again -> no second flip
    b.get_output(packet(3.05, (0, own_y * 0.8, 93), (0, -(own_y / abs(own_y)) * 1500, 0), cars, touch=(idx, 2.95)))
    assert b.skew == -skew0
    # opponent touch -> no flip
    b.get_output(packet(4.0, (0, 0, 93), (0, 0, 0), cars, touch=(1 - idx, 3.99)))
    assert b.skew == -skew0
    # 5) no ball / demolished -> neutral controls, no exception
    assert repr(b.get_output(packet(5.0, (0, 0, 0), (0, 0, 0), cars, no_ball=True))) == repr(flat.ControllerState())
    if idx == 1:
        assert repr(b.get_output(packet(5.0, (0, 0, 93), (0, 0, 0), cars, demo=2.0))) == repr(flat.ControllerState())
    # random fuzz
    random.seed(team)
    for k in range(5000):
        bl = (random.uniform(-4000, 4000), random.uniform(-5100, 5100), random.uniform(93, 1900))
        bv = tuple(random.uniform(-3500, 3500) for _ in range(3))
        cl = (random.uniform(-4000, 4000), random.uniform(-5100, 5100), 17)
        cs = [(0, cl), (1, cl)]
        b.get_output(packet(10 + k / 120, bl, bv, cs, touch=(random.choice([0, 1]), 10 + k / 120 - 0.05) if k % 7 == 0 else None))
    # inspect one state set
    gs = sent[-1]
    cs = gs.car_states[idx]
    assert len(gs.car_states) == idx + 1 and cs.physics.location is not None and cs.boost_amount == 100.0
    if idx == 1: assert repr(gs.car_states[0]) == repr(flat.DesiredCarState())
    print(f"team {team} idx {idx}: OK, home-sets={n_home}, total state sets={len(sent)}, last={cs.physics.location}")
print("ALL OK")

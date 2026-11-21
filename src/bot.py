import math
import random

from rlbot.flat import (
    ControllerState,
    DesiredCarState,
    DesiredPhysics,
    GamePacket,
    RotatorPartial,
    Vector3Partial,
)
from rlbot.managers import Bot

from util.drive import steer_toward_target
from util.vec import Vec3


GOAL = 5120.0
POST = 893.0
REACH = 2400.0

AGENT_ID = "cayatur/cayaheatseekerbot/1.0.0"


class _Touch:
    """v4-style view of the ball's latest touch (v5 stores touches per player)."""

    __slots__ = ("time_seconds", "team")

    def __init__(self, time_seconds: float = 0.0, team: int = -1):
        self.time_seconds = time_seconds
        self.team = team


def _latest_ball_touch(packet: GamePacket, ball_index: int = 0) -> _Touch:
    # RLBot v4 exposed packet.game_ball.latest_touch (the most recent touch by any
    # player, with its team). In v5 every PlayerInfo carries its own latest_touch,
    # so pick the most recent one on this ball and take the toucher's team.
    best = _Touch()
    for player in packet.players:
        t = player.latest_touch
        if t is None or t.ball_index != ball_index:
            continue
        if t.game_seconds > best.time_seconds:
            best = _Touch(t.game_seconds, player.team)
    return best


class MyBot(Bot):
    skew = 1.0
    pose = None
    last_touch_time = -1.0

    def initialize(self):
        self.skew = 1.0
        self.pose = None
        self.last_touch_time = -1.0

    def get_output(self, packet: GamePacket) -> ControllerState:
        if len(packet.balls) == 0:
            # No ball (e.g. during goal replays) - nothing to do this tick.
            return ControllerState()

        me = packet.players[self.index]
        if me.demolished_timeout >= 0:  # -1 while not demolished
            return ControllerState()

        now = packet.match_info.seconds_elapsed
        ball = Vec3(packet.balls[0].physics.location)
        bvel = Vec3(packet.balls[0].physics.velocity)
        car = Vec3(me.physics.location)
        touch = _latest_ball_touch(packet)

        own_y = -GOAL if self.team == 0 else GOAL
        out = 1.0 if self.team == 0 else -1.0
        speed = bvel.length()

        toward_us = (bvel.y * own_y) > -80
        on_our = (ball.y * own_y) > -200
        we_touched = (
            touch.time_seconds > 0
            and touch.team == self.team
            and (now - touch.time_seconds) < 0.20
        )
        we_just_hit = we_touched and not toward_us
        if we_touched and touch.time_seconds != self.last_touch_time:
            self.last_touch_time = touch.time_seconds
            self.skew = -self.skew
            self.pose = None

        t_goal = 99.0
        if abs(bvel.y) > 5:
            t = (own_y - ball.y) / bvel.y
            if t > 0:
                t_goal = t

        dist_goal = abs(ball.y - own_y)
        incoming = (
            not we_just_hit
            and ball.z < 1300
            and dist_goal < 5000
            and abs(ball.x) < 2200
            and (
                toward_us
                or (on_our and dist_goal < 3200)
                or dist_goal < 1400
                or t_goal < 3.6
            )
        )

        if incoming:
            self._tp_hit(ball, bvel, own_y, out, speed, dist_goal)
            c = ControllerState()
            c.throttle = 1.0
            c.boost = True
            c.jump = True
            c.pitch = -1.0
            return c

        self.pose = None
        home = Vec3(max(-800.0, min(800.0, ball.x * 0.45)), own_y + out * 70.0, 17.0)
        if car.dist(home) > 500:
            self._set(home.x, home.y, 17.0, 0.0, math.atan2(out, 0.0), 0.0, 0.0, 0.0, 0.0)
        c = ControllerState()
        c.steer = steer_toward_target(me, home)
        c.throttle = 0.5 if car.dist(home) > 80 else 0.0
        return c

    def _tp_hit(self, ball, bvel, own_y, out, speed, dist_goal):
        fast = speed > 2100 or dist_goal < 550

        if fast:
            # Topun yolunun ÖNÜ — o geçer, araba bekler
            step = bvel.normalized() * 45.0 if speed > 1 else Vec3(0, -out * 45, 0)
            future = ball + step
            gap = 28.0
        else:
            future = ball + bvel * (0.04 if speed < 1300 else 0.055)
            gap = 40.0 if dist_goal < 900 or speed < 1100 else 52.0

        x = max(-POST, min(POST, future.x))
        y = future.y - out * gap
        z = max(17.0, ball.z) if ball.z < 140 else future.z
        if self.team == 0:
            y = max(own_y + 14.0, min(y, own_y + REACH))
        else:
            y = min(own_y - 14.0, max(y, own_y - REACH))
        z = max(17.0, min(z, 660.0))

        if self.pose is None:
            self.pose = (
                self.skew * random.uniform(0.25, 0.55),
                random.uniform(-1.05, -0.45),
                self.skew * random.uniform(0.25, 0.9),
                self.skew * random.uniform(200.0, 480.0),
                random.uniform(280.0, 650.0),
            )
        yaw_off, pitch, roll, vx, vz = self.pose
        yaw = math.atan2(out, self.skew * 0.55) + yaw_off
        if fast:
            vx, vy, vz = 0.0, out * 200.0, 40.0
            pitch = pitch * 0.4
        else:
            vy = out * (1100.0 + min(speed * 0.2, 500.0))
        self._set(x, y, z, pitch, yaw, roll, vx, vy, vz)

    def _set(self, x, y, z, pitch, yaw, roll, vx, vy, vz):
        # NOTE: v4's CarState(jumped=True, double_jumped=True) has no equivalent in
        # RLBot v5's DesiredCarState (only physics + boost_amount can be set).
        self.set_game_state_parts(cars={
            self.index: DesiredCarState(
                physics=DesiredPhysics(
                    location=Vector3Partial(x, y, z),
                    velocity=Vector3Partial(vx, vy, vz),
                    rotation=RotatorPartial(pitch, yaw, roll),
                    angular_velocity=Vector3Partial(-4.0, 0.0, self.skew * 1.5),
                ),
                boost_amount=100.0,
            )
        })


if __name__ == "__main__":
    # RLBOT_AGENT_ID (set by RLBot) takes precedence over this default.
    MyBot(AGENT_ID).run(wants_match_communications=False, wants_ball_predictions=False)

import math
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import GameState, CarState, Physics, Vector3, Rotator

from util.drive import steer_toward_target
from util.vec import Vec3


GOAL = 5120.0
POST = 893.0
REACH = 2400.0


class MyBot(BaseAgent):
    def initialize_agent(self):
        self.skew = 1.0
        self.pose = None
        self.last_touch_time = -1.0

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        me = packet.game_cars[self.index]
        if me.is_demolished:
            return SimpleControllerState()

        now = packet.game_info.seconds_elapsed
        ball = Vec3(packet.game_ball.physics.location)
        bvel = Vec3(packet.game_ball.physics.velocity)
        car = Vec3(me.physics.location)
        touch = packet.game_ball.latest_touch

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
            c = SimpleControllerState()
            c.throttle = 1.0
            c.boost = True
            c.jump = True
            c.pitch = -1.0
            return c

        self.pose = None
        home = Vec3(max(-800.0, min(800.0, ball.x * 0.45)), own_y + out * 70.0, 17.0)
        if car.dist(home) > 500:
            self._set(home.x, home.y, 17.0, 0.0, math.atan2(out, 0.0), 0.0, 0.0, 0.0, 0.0)
        c = SimpleControllerState()
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
        self.set_game_state(GameState(cars={
            self.index: CarState(
                physics=Physics(
                    location=Vector3(x, y, z),
                    velocity=Vector3(vx, vy, vz),
                    rotation=Rotator(pitch, yaw, roll),
                    angular_velocity=Vector3(-4.0, 0.0, self.skew * 1.5),
                ),
                boost_amount=100.0,
                jumped=True,
                double_jumped=True,
            )
        }))
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import override

from rlbot.flat import ControllerState, GamePacket


@dataclass(slots=True)
class StepResult:
    controls: ControllerState
    done: bool


class Step(ABC):
    @abstractmethod
    def tick(self, packet: GamePacket) -> StepResult:
        """
        Return appropriate controls for this step in the sequence. If the step is over, you should
        set done to True in the result, and we'll move on to the next step during the next frame.
        If you panic and can't return controls at all, you may return None and we will move on to
        the next step immediately.
        """
        raise NotImplementedError


@dataclass(slots=True)
class ControlStep(Step):
    """
    This allows you to repeat the same controls every frame for some specified duration. It's useful for
    scheduling the button presses needed for kickoffs / dodges / etc.
    """

    duration: float
    controls: ControllerState

    start_time: float | None = field(default=None, init=False)

    @override
    def tick(self, packet: GamePacket) -> StepResult:
        if self.start_time is None:
            self.start_time = packet.match_info.seconds_elapsed
        elapsed_time = packet.match_info.seconds_elapsed - self.start_time
        return StepResult(controls=self.controls, done=elapsed_time > self.duration)


@dataclass(slots=True)
class Sequence:
    steps: list[Step]

    index: int = field(default=0, init=False)
    done: bool = field(default=False, init=False)

    def tick(self, packet: GamePacket) -> ControllerState:
        while self.index < len(self.steps):
            step = self.steps[self.index]
            result = step.tick(packet)
            if result.done:
                self.index += 1
                if self.index >= len(self.steps):
                    # The bot will know not to use this sequence next frame, even though we may be giving it controls.
                    self.done = True
            # If the step was able to give us controls, return them to the bot.
            return result.controls
            # Otherwise we will loop to the next step in the sequence.

        # If we reach here, we ran out of steps to attempt.
        self.done = True
        return ControllerState()

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from qcodes_qick.instructions.delay import Delay
from qcodes_qick.protocol_base import HardwareSweep, SweepProgram, SweepProtocol
from qick.qick_asm import QickConfig

if TYPE_CHECKING:
    from qcodes_qick.instruction_base import QickInstruction
    from qcodes_qick.instructions.readout_pulse import ReadoutPulse
    from qcodes_qick.instruments import QickInstrument


class HahnEchoProtocol(SweepProtocol):
    def __init__(
        self,
        parent: QickInstrument,
        half_pi_pulse: QickInstruction,
        pi_pulse: QickInstruction,
        readout_pulse: ReadoutPulse,
        name="HahnEchoProtocol",
        **kwargs,
    ):
        super().__init__(parent, name, **kwargs)
        assert half_pi_pulse.dac is pi_pulse.dac
        self.half_pi_pulse = half_pi_pulse
        self.pi_pulse = pi_pulse
        self.readout_pulse = readout_pulse
        self.delay = Delay(parent, pi_pulse.dac)
        self.instructions = {half_pi_pulse, pi_pulse, readout_pulse, self.delay}

    def generate_program(
        self, soccfg: QickConfig, hardware_sweeps: Sequence[HardwareSweep] = ()
    ):
        return HahnEchoProgram(soccfg, self, hardware_sweeps)


class HahnEchoProgram(SweepProgram):
    protocol: HahnEchoProtocol

    def body(self):
        self.protocol.half_pi_pulse.play(self)
        self.protocol.delay.play(self)
        self.protocol.pi_pulse.play(self)
        self.protocol.delay.play(self)
        self.protocol.half_pi_pulse.play(self)
        self.protocol.readout_pulse.play(self, wait_for_adc=True)

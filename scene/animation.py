"""Sequência determinística em segundos, sem dependências de janela/OpenGL."""
from enum import Enum
from dataclasses import dataclass
import math


class State(Enum):
    ROVER_EXPLORING = 0
    ROVER_DETECTED_BLOCKAGE = 1
    EXCAVATOR_APPROACH = 2
    EXCAVATOR_WORKING = 3
    EXCAVATOR_CLEAR = 4
    ROVER_RESUMES = 5
    RESET = 6


DURATIONS = (6.0, 2.0, 4.0, 10.0, 4.0, 7.0, 2.0)
LABELS = ('Explorando a rota', 'Obstáculo detectado • pedido de apoio',
          'Escavadeira a caminho', 'Removendo a obstrução',
          'Área liberada • recolhendo braço', 'Rover retomando a exploração',
          'Missão concluída • novo ciclo')


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def mix(a, b, t):
    return a + (b - a) * t


@dataclass
class Pose:
    rover_x: float = -7.0
    excavator_z: float = -5.3
    turret: float = 0.0
    shoulder: float = 0.6
    elbow: float = -1.2
    bucket: float = 0.0
    signal: bool = False
    fade: float = 0.0


def pickup_angles():
    # Inverse kinematics for the rock centre. Coordinates are relative to
    # arm_base=(.38,1.79,z+.1); bucket load offset=(.12,.22).
    tool_angle=-.4
    lx=1.65+.12*math.cos(tool_angle)-.22*math.sin(tool_angle)
    ly=.12*math.sin(tool_angle)+.22*math.cos(tool_angle)
    length=math.hypot(lx,ly)
    x,y=2.65,-1.45
    bend=-math.acos((x*x+y*y-2.15**2-length**2)/(2*2.15*length))
    shoulder=math.atan2(y,x)-math.atan2(length*math.sin(bend),2.15+length*math.cos(bend))
    return shoulder,bend-math.atan2(ly,lx)


PICKUP_SHOULDER,PICKUP_ELBOW=pickup_angles()


class Mission:
    def __init__(self):
        self.paused = False
        self.reset()

    def reset(self):
        self.state = State.ROVER_EXPLORING
        self.elapsed = 0.0
        self.total = 0.0
        self.cycles = 0
        self.paused = False
        self.transitions = []

    def update(self, dt):
        if not math.isfinite(dt) or dt < 0:
            raise ValueError('dt deve ser finito e não negativo')
        if self.paused:
            return
        self.total += dt
        self.elapsed += dt
        # Preserva o excedente mesmo quando um quadro atravessa várias etapas.
        while self.elapsed + 1e-10 >= DURATIONS[self.state.value]:
            self.elapsed = max(0.0, self.elapsed - DURATIONS[self.state.value])
            previous = self.state
            self.state = State((self.state.value + 1) % len(State))
            if self.state == State.ROVER_EXPLORING:
                self.cycles += 1
            self.transitions.append((previous.name, self.state.name))
            self.transitions = self.transitions[-28:]

    @property
    def progress(self):
        return self.elapsed / DURATIONS[self.state.value]

    def pose(self):
        p, k = Pose(), self.state.value
        u = smooth(self.progress)
        if k == 0:
            p.rover_x = mix(-7.0, -2.2, u)
        else:
            p.rover_x = -2.2
        p.signal = 1 <= k <= 4
        if k == 2:
            p.excavator_z = mix(-5.3, -2.7, u)
        elif 3 <= k <= 4:
            p.excavator_z = -2.7
        if k == 3:
            # Planar arm reaches the rock in world space. It then carries it
            # sideways, attached to the bucket's actual world transform.
            q = self.progress
            reach = smooth(q / .3)
            lift = smooth((q - .3) / .2)
            swing = smooth((q - .5) / .3)
            lower = smooth((q - .8) / .15)
            p.shoulder = mix(.6, PICKUP_SHOULDER, reach) + .35 * lift - .37 * lower
            p.elbow = mix(-1.2, PICKUP_ELBOW, reach) + .35 * lift - .38 * lower
            p.bucket = -.4 * reach + .7 * smooth((q - .92) / .08)
            p.turret = 1.35 * swing  # descarga no lado afastado do rover
        elif k == 4:
            p.turret = mix(1.35, 0, u)
            p.shoulder = mix(PICKUP_SHOULDER-.02, .6, u)
            p.elbow = mix(PICKUP_ELBOW-.03, -1.2, u)
            p.bucket = mix(.3, 0, u)
            p.excavator_z = mix(-2.7, -5.3, u)
        elif k >= 5:
            p.rover_x = mix(-2.2, 8.0, u) if k == 5 else 8.0
        # Fade completes before reset; next cycle fades back in without a pop.
        if k == 6:
            p.fade = smooth((self.progress - .3) / .65)
        elif k == 0:
            p.fade = 1.0 - smooth(self.elapsed / .6)
        return p

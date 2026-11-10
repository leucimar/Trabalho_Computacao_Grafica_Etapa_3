import math
from core.object3D import Object3D
from models.common import transform
from models.rover import Rover
from models.excavator import Excavator
from scene.animation import State


class Environment(Object3D):
    def __init__(self,p):
        super().__init__()
        p.box(self,(0,-.5,0),(23,.9,15),(.23,.32,.33))
        ground=p.box(self,(0,-.025,0),(22.8,.1,14.8),(.9,.8,.6),texture='sand',uv=(18,12))
        ground.cast_shadow=False
        p.box(self,(0,.035,0),(20,.045,2.6),(.59,.61,.55),texture='sand',uv=(16,2))
        # Dashed margins, landing pads, survey equipment and low-poly hills.
        for x in range(-9,10,2):
            for z in (-1.48,1.48):
                p.box(self,(x,.055,z),(.85,.03,.07),(.94,.84,.49))
        for x,z in [(-8,-4.6),(7,4.4)]:
            p.box(self,(x,.05,z),(2.8,.12,2.3),(.4,.49,.48),texture='hazard',uv=(3,3))
        for x,z,s in [(-9,5,1.9),(-6,5.8,1.2),(-2,6,1.6),(2,6.2,1.3),(9,-5.5,2.2),(6,-6,1.6),(-9,-6,1.1),(9,5,1.2)]:
            p.part(self,'rock',(x,.45*s,z),(s*1.4,s,s),(.47,.48,.42))
        for x,z in [(-8,2.5),(-5,-2.5),(5,2.5),(8,-2.5)]:
            p.part(self,'cone',(x,.31,z),(.42,.62,.42),(.95,.46,.17))
            p.box(self,(x,.08,z),(.55,.12,.55),(.23,.3,.32))
        for x,z in [(4,-4.5),(-5,4.5)]:
            p.part(self,'cylinder',(x,.6,z),(.06,1.2,.06),(.64,.7,.66))
            p.box(self,(x,1.17,z),(.62,.27,.09),(.14,.44,.5))
        self.rover=Rover(p); self.add(self.rover)
        self.excavator=Excavator(p); self.add(self.excavator)
        self.rock=p.part(self,'rock',(.38,.52,.05),(.95,.95,1.05),(.62,.42,.29))
        self.rest_transform=transform((.38,.52,.05),scale=(.95,.95,1.05))
        self.deposit=None

    def animate(self,mission):
        pose=mission.pose()
        self.rover.animate(pose,mission.total)
        self.excavator.animate(pose)
        state=mission.state
        if state==State.EXCAVATOR_WORKING and .3 <= mission.progress < .95:
            # Keep the rock mesh under the scene and use the bucket's world
            # matrix, preserving its true hierarchical attachment during lift.
            self.rock.transform=self.excavator.load.getWorldMatrix() @ transform(scale=(.95,.95,1.05))
            self.deposit=self.rock.transform.copy()
        elif state.value>=State.EXCAVATOR_WORKING.value and (state.value>3 or mission.progress>=.95):
            # Derive final deposit from the endpoint pose even if dt skips
            # the entire pickup interval; no dependency on render frequency.
            from scene.animation import Mission, DURATIONS
            end=Mission(); end.state=State.EXCAVATOR_WORKING; end.elapsed=DURATIONS[3]*.95
            self.excavator.animate(end.pose())
            deposited=self.excavator.load.getWorldMatrix() @ transform(scale=(.95,.95,1.05))
            deposited[1,3]=.52
            self.rock.transform=deposited
            self.excavator.animate(pose)
        else:
            self.rock.transform=self.rest_transform.copy()
        return pose

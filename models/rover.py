import math
from core.object3D import Object3D
from models.common import transform


class Rover(Object3D):
    def __init__(self,p):
        super().__init__()
        white,blue=(.88,.92,.9),(.12,.39,.49)
        p.box(self,(0,.79,0),(1.85,.42,1.25),white)
        p.box(self,(-.15,1.13,0),(1.4,.3,1.02),blue)
        p.box(self,(-.2,1.32,0),(1.32,.05,.96),(.8,.9,1),texture='solar',uv=(2,1))
        p.box(self,(.9,.94,0),(.25,.32,.94),white)
        for z in (-.42,.42):
            p.box(self,(1.04,.99,z),(.04,.15,.2),(1,.88,.55),emission=.35)
        self.wheels=[]
        for x in (-.65,0,.65):
            for z in (-.76,.76):
                p.box(self,(x,.53,z*.7),(.12,.12,.4),(.32,.39,.41))
                self.wheels.append((p.wheel(self,(x,.43,z),.42,.24),(x,.43,z)))
        self.antenna=p.node(self,(-.6,1.35,0))
        p.part(self.antenna,'cylinder',(0,.48,0),(.045,.96,.045),(.65,.74,.76))
        p.box(self.antenna,(0,.96,0),(.55,.23,.26),white)
        for z in (-.138,.138):
            p.box(self.antenna,(.12,.98,z),(.13,.1,.02),(.1,.28,.34))
        self.beacon=p.part(self,'cylinder',(.45,1.42,0),(.18,.14,.18),(.32,.82,.68),emission=.4)

    def animate(self,pose,time):
        self.transform=transform((pose.rover_x,0,0))
        for wheel,pos in self.wheels:
            wheel.transform=transform(pos,(0,0,-(pose.rover_x+7)/.42))
        # Sensor scans towards the excavator during the request, and sweeps
        # during travel. Rotation is an actual child transform.
        yaw=-math.pi/2 if pose.signal else math.sin(time*1.4)*.8
        self.antenna.transform=transform((-.6,1.35,0),(0,yaw,0))
        pulse=.5+.5*math.sin(time*8)
        self.beacon.color=(1,.25+.4*pulse,.08) if pose.signal else (.2,.85,.68)

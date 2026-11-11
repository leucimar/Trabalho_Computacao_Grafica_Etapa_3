import math
from core.object3D import Object3D
from models.common import transform


class Excavator(Object3D):
    def __init__(self,p):
        super().__init__()
        yellow,dark=(1,.66,.12),(.15,.21,.24)
        p.box(self,(0,.56,0),(1.6,.36,2.12),dark)
        self.wheels=[]
        for x in (-.84,.84):
            p.box(self,(x,.36,0),(.4,.5,2.4),dark)
            for z in (-.78,0,.78):
                pivot=p.node(self,(x,.39,z),(0,math.pi/2,0))
                wheel=p.wheel(pivot,(0,0,0),.34,.36)
                self.wheels.append(wheel)
            # Repeated raised track shoes make the silhouette readable.
            for z in range(9):
                p.box(self,(x,.64,-1.08+z*.27),(.43,.06,.16),(.28,.34,.35))
        self.turret=p.node(self,(0,.86,0))
        p.part(self.turret,'cylinder',(0,0,0),(1.3,.24,1.3),(.31,.36,.35))
        p.box(self.turret,(0,.3,0),(1.7,.46,1.48),yellow)
        p.box(self.turret,(-.42,.9,-.16),(.78,.96,1.1),yellow)
        p.box(self.turret,(-.42,1.08,.403),(.61,.53,.03),(.15,.43,.51))
        p.box(self.turret,(-.823,1.08,-.16),(.03,.53,.84),(.15,.43,.51))
        p.box(self.turret,(-.42,1.43,-.16),(.9,.12,1.2),yellow)
        p.box(self.turret,(.58,.55,-.45),(.44,.17,.68),dark,texture='hazard',uv=(2,1))
        # The arm plane is XY; Y rotation points its +X axis along world +Z.
        self.arm_base=p.node(self.turret,(.38,.93,.1),(0,-math.pi/2,0))
        self.shoulder=p.node(self.arm_base)
        p.box(self.shoulder,(1.075,0,0),(2.15,.25,.3),yellow)
        p.part(self.shoulder,'cylinder',(0,0,0),(.38,.36,.38),dark,rotation=(math.pi/2,0,0))
        p.box(self.shoulder,(.9,-.16,.19),(1.45,.07,.07),(.8,.85,.84))
        self.elbow=p.node(self.shoulder,(2.15,0,0))
        p.box(self.elbow,(.825,0,0),(1.65,.21,.25),yellow)
        p.part(self.elbow,'cylinder',(0,0,0),(.32,.36,.32),dark,rotation=(math.pi/2,0,0))
        self.bucket=p.node(self.elbow,(1.65,0,0))
        # Open bucket, rather than a solid block: back, floor and side walls.
        p.box(self.bucket,(.12,-.22,0),(.82,.12,1.1),dark)
        p.box(self.bucket,(-.35,.01,0),(.12,.50,1.1),yellow)
        for z in (-.51,.51):
            p.box(self.bucket,(.10,-.06,z),(.84,.43,.08),yellow)
        for z in (-.35,0,.35):
            p.box(self.bucket,(.54,-.17,z),(.19,.09,.12),(.65,.71,.69))
        self.load=p.node(self.bucket,(.12,.22,0))

    def animate(self,pose):
        self.transform=transform((0,0,pose.excavator_z))
        self.turret.transform=transform((0,.86,0),(0,pose.turret,0))
        self.shoulder.transform=transform(rotation=(0,0,pose.shoulder))
        self.elbow.transform=transform((2.15,0,0),(0,0,pose.elbow))
        self.bucket.transform=transform((1.65,0,0),(0,0,pose.bucket))
        for wheel in self.wheels:
            wheel.transform=transform(rotation=(0,0,-(pose.excavator_z+5.3)/.34))

"""Composição de Mesh/Object3D do framework; escalas ficam só nas folhas."""
import math
import numpy as np
from core.object3D import Object3D
from core.matrix import Matrix
from core.mesh import Mesh
from geometry.primitives import LitBoxGeometry, CylinderGeometry, RockGeometry


def transform(position=(0,0,0), rotation=(0,0,0), scale=(1,1,1)):
    x,y,z=position
    rx,ry,rz=rotation
    return (Matrix.makeTranslation(x,y,z) @ Matrix.makeRotationY(ry)
            @ Matrix.makeRotationX(rx) @ Matrix.makeRotationZ(rz)
            @ np.diag([*scale,1]).astype(np.float32))


class Parts:
    def __init__(self, material):
        self.material=material
        self.geometries={'box':LitBoxGeometry(), 'cylinder':CylinderGeometry(),
                         'cone':CylinderGeometry(12,.08), 'rock':RockGeometry()}

    def node(self, parent, position=(0,0,0), rotation=(0,0,0)):
        obj=Object3D(); obj.transform=transform(position,rotation); parent.add(obj)
        return obj

    def part(self, parent, kind, position, scale, color, rotation=(0,0,0), texture='white', uv=(1,1), emission=0):
        obj=Mesh(self.geometries[kind],self.material)
        obj.transform=transform(position,rotation,scale)
        obj.color=color; obj.texture_name=texture; obj.uv_repeat=uv
        obj.emission=emission; obj.cast_shadow=True
        obj.bump_strength = .24 if kind=='rock' else (.18 if texture=='sand' else 0.0)
        parent.add(obj)
        return obj

    def box(self,parent,pos,size,color,**kw):
        return self.part(parent,'box',pos,size,color,**kw)

    def wheel(self,parent,pos,radius=.42,width=.25):
        pivot=self.node(parent,pos)
        self.part(pivot,'cylinder',(0,0,0),(radius*2,width,radius*2),(.12,.16,.19),rotation=(math.pi/2,0,0))
        for s in (-1,1):
            self.part(pivot,'cylinder',(0,0,s*(width/2+.01)),(radius*1.1,.035,radius*1.1),(.48,.58,.62),rotation=(math.pi/2,0,0))
            self.box(pivot,(0,0,s*(width/2+.035)),(.09,radius*1.35,.02),(.94,.65,.18))
        return pivot

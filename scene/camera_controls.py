import math
import numpy as np
from core.matrix import Matrix


def look_at(eye,target,up=(0,1,0)):
    eye,target=np.asarray(eye,dtype=float),np.asarray(target,dtype=float)
    back=eye-target; back/=np.linalg.norm(back)
    right=np.cross(up,back); right/=np.linalg.norm(right)
    vertical=np.cross(back,right)
    m=np.eye(4,dtype=np.float32)
    m[0,:3],m[1,:3],m[2,:3]=right,vertical,back
    m[:3,3]=-m[:3,:3]@eye
    return m


class Camera:
    def __init__(self):
        self.home()

    def home(self):
        self.position=np.array([14.,11.,17.])
        direction=np.array([0.,.4,-.4])-self.position
        direction/=np.linalg.norm(direction)
        self.yaw=math.atan2(direction[0],-direction[2])
        self.pitch=math.asin(direction[1])

    @property
    def forward(self):
        return np.array([math.sin(self.yaw)*math.cos(self.pitch),math.sin(self.pitch),-math.cos(self.yaw)*math.cos(self.pitch)])

    @property
    def view(self):
        return look_at(self.position,self.position+self.forward)

    def update(self,dt,keys,mouse=(0,0)):
        # String-key input keeps the controller testable without a display.
        self.yaw += (keys.get('right',0)-keys.get('left',0))*dt*1.2+mouse[0]*.003
        self.pitch += (keys.get('up',0)-keys.get('down',0))*dt*1.2-mouse[1]*.003
        self.pitch=max(-1.45,min(1.45,self.pitch))
        right=np.cross(self.forward,[0,1,0]); right/=np.linalg.norm(right)
        move=(self.forward*(keys.get('w',0)-keys.get('s',0))
              +right*(keys.get('d',0)-keys.get('a',0))
              +np.array([0,keys.get('e',0)-keys.get('q',0),0]))
        length=np.linalg.norm(move)
        if length:
            self.position+=move/length*dt*(10 if keys.get('shift') else 5)

    def projection(self,aspect):
        return Matrix.makePerspective(48,aspect,.1,120)

"""Extensões de primitivas da versão didática do framework do livro."""
import math
import numpy as np
from geometry.geometry import Geometry
from geometry.boxGeometry import BoxGeometry


def flat_normals(positions):
    normals = []
    for i in range(0, len(positions), 3):
        a, b, c = np.asarray(positions[i:i + 3], dtype=float)
        n = np.cross(b - a, c - a)
        n /= np.linalg.norm(n)
        normals.extend([n.tolist()] * 3)
    return normals


class LitBoxGeometry(BoxGeometry):
    def __init__(self):
        super().__init__()
        self.addAttribute('vec3', 'vertexNormal', flat_normals(self.attributes['vertexPosition'].data))


class CylinderGeometry(Geometry):
    """Cilindro unitário no eixo Y; tampas e lateral com normais distintas."""
    def __init__(self, sides=16, top_radius=.5):
        super().__init__()
        pos, uv, normals = [], [], []
        for i in range(sides):
            a, b = 2 * math.pi * i / sides, 2 * math.pi * (i + 1) / sides
            v = [(math.cos(a)*.5,-.5,math.sin(a)*.5),
                 (math.cos(a)*top_radius,.5,math.sin(a)*top_radius),
                 (math.cos(b)*top_radius,.5,math.sin(b)*top_radius),
                 (math.cos(b)*.5,-.5,math.sin(b)*.5)]
            slope = .5 - top_radius
            for j in (0,1,2,0,2,3):
                pos.append(v[j]); uv.append([(i+(j>=2))/sides, float(j in (1,2))])
                angle = a if j < 2 else b
                n = np.array([math.cos(angle), slope, math.sin(angle)])
                normals.append((n/np.linalg.norm(n)).tolist())
            # Top: viewed from +Y, winding must yield +Y.
            for j in (None,2,1):
                p = (0,.5,0) if j is None else v[j]
                pos.append(p); uv.append([p[0]+.5,p[2]+.5]); normals.append([0,1,0])
            for j in (None,0,3):
                p = (0,-.5,0) if j is None else v[j]
                pos.append(p); uv.append([p[0]+.5,p[2]+.5]); normals.append([0,-1,0])
        self.addAttribute('vec3','vertexPosition',pos)
        self.addAttribute('vec2','vertexUV',uv)
        self.addAttribute('vec3','vertexNormal',normals)
        self.countVertices()


class RockGeometry(Geometry):
    """Octaedro de faces planas, sem modelo externo."""
    def __init__(self):
        super().__init__()
        top, bottom = (0,.65,.06), (.12,-.5,-.05)
        ring = [(.7,0,0),(0,.04,.55),(-.58,-.02,0),(0,.08,-.6)]
        pos=[]
        for i in range(4):
            a,b=ring[i],ring[(i+1)%4]
            pos.extend([top,b,a,bottom,a,b])
        self.addAttribute('vec3','vertexPosition',pos)
        self.addAttribute('vec2','vertexUV',[[0,1],[0,0],[1,0]]*8)
        self.addAttribute('vec3','vertexNormal',flat_normals(pos))
        self.countVertices()

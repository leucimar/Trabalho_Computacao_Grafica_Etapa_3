"""Integração gráfica real. Execute em contexto SDL/OpenGL válido."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import numpy as np
import pygame
from OpenGL.GL import *
from rendering.renderer import Renderer
from rendering.hud import Hud
from models.common import Parts
from scene.environment import Environment
from scene.animation import Mission, State
from scene.camera_controls import Camera


def main():
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION,3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION,3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.set_mode((960,540),pygame.OPENGL|pygame.DOUBLEBUF)
    renderer=Renderer(1024); scene=Environment(Parts(renderer.material)); camera=Camera(); hud=Hud()
    out=Path(sys.argv[1]) if len(sys.argv)>1 else Path('capturas/verificacao')
    out.mkdir(parents=True,exist_ok=True)
    report={'opengl':glGetString(GL_VERSION).decode(),'renderer':glGetString(GL_RENDERER).decode()}
    changed=[]; last=None
    # Two full cycles rendered, including the state boundaries.
    m=Mission()
    for i in range(142):
        scene.animate(m); renderer.draw(scene,camera,960,540)
        depth=renderer.depth_pixels().copy()
        assert np.isfinite(depth).all() and depth.min()<.99
        if last is not None: changed.append(int(np.count_nonzero(np.abs(depth-last)>1e-6)))
        last=depth
        assert glGetError()==GL_NO_ERROR
        pygame.display.flip(); m.update(.5)
    assert m.cycles==2
    report.update(rendered_frames=142,completed_cycles=m.cycles,depth_min=float(depth.min()),depth_max=float(depth.max()),max_changed_depth_pixels=max(changed))
    # Pickup: the bucket transform meets the original rock centre, then the
    # loaded rock moves with the bucket. Check actual scene graph matrices.
    m=Mission();m.update(15);scene.animate(m)
    np.testing.assert_allclose(scene.rock.getWorldPosition(),[.38,.34,.05],atol=1e-5)
    carried=scene.rock.getWorldMatrix().copy();m.update(2);scene.animate(m)
    assert np.linalg.norm(scene.rock.getWorldMatrix()[:3,3]-carried[:3,3])>.2
    report['bucket_pickup_alignment']=True
    # Depósito à direita, afastado do corredor (largura z=+-1.3) e do rover.
    m=Mission();m.update(21.6);scene.animate(m)
    deposit=np.array(scene.rock.getWorldPosition())
    rover=np.array(scene.rover.getWorldPosition())
    assert deposit[0]>2.0 and deposit[2]<-1.9, deposit
    assert np.linalg.norm(deposit-rover)>3.0
    assert .29<=deposit[1]<=.39
    report['deposit_world_position']=deposit.tolist()
    # Verifica continuidade nos trechos de transporte e descarte.
    samples=[]
    for t in np.linspace(15.02,21.49,130):
        m=Mission();m.update(float(t));scene.animate(m)
        samples.append(scene.rock.getWorldPosition())
    lengths=np.linalg.norm(np.diff(np.array(samples),axis=0),axis=1)
    assert lengths.max()<.4, lengths.max()
    report['max_rock_displacement_per_sample']=float(lengths.max())

    for seconds,name in [(4,'01_exploracao'),(15,'02_coleta'),(19.5,'03_transporte'),(29,'04_passagem')]:
        m=Mission();m.update(seconds);pose=scene.animate(m)
        renderer.shadows=True; renderer.draw(scene,camera,960,540)
        if seconds==4:
            glPixelStorei(GL_PACK_ALIGNMENT,1)
            with_shadow=np.frombuffer(glReadPixels(0,0,960,540,GL_RGB,GL_UNSIGNED_BYTE),dtype=np.uint8).astype(int)
            renderer.shadows=False;renderer.draw(scene,camera,960,540)
            without_shadow=np.frombuffer(glReadPixels(0,0,960,540,GL_RGB,GL_UNSIGNED_BYTE),dtype=np.uint8).astype(int)
            difference=np.abs(with_shadow-without_shadow)
            report['pixels_changed_by_shadow']=int(np.count_nonzero(difference.reshape(-1,3).max(axis=1)>5))
            assert report['pixels_changed_by_shadow']>100
            renderer.shadows=True;renderer.draw(scene,camera,960,540)
        hud.draw(m,60,True,False,True,pose.fade,960,540)
        renderer.screenshot(out/(name+'.png'),960,540)
        assert glGetError()==GL_NO_ERROR
    # Invalid values, inconsistent transforms or dark fake shadow decals would
    # not produce these changing depth values and the second-pass difference.
    report['gl_error']=int(glGetError())
    (out/'resultado.json').write_text(json.dumps(report,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps(report,indent=2));pygame.quit()

if __name__=='__main__':main()

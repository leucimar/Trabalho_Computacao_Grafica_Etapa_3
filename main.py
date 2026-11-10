"""Operação Rover — Python/Pygame/OpenGL, framework da disciplina."""
import argparse
import json
from pathlib import Path
import sys
import time
import pygame
from OpenGL.GL import *
from models.common import Parts
from rendering.renderer import Renderer
from rendering.hud import Hud
from scene.environment import Environment
from scene.animation import Mission
from scene.camera_controls import Camera

def run(args):
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION,3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION,3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE,24)
    width,height=1280,720
    pygame.display.set_mode((width,height),pygame.OPENGL|pygame.DOUBLEBUF)
    pygame.display.set_caption('Operação Rover | Computação Gráfica — Etapa 3')
    renderer=Renderer(args.shadow_size)
    print('OpenGL:',glGetString(GL_VERSION).decode(),flush=True)
    print('Renderer:',glGetString(GL_RENDERER).decode(),flush=True)
    scene=Environment(Parts(renderer.material))
    mission=Mission(); camera=Camera(); hud=Hud()
    clock=pygame.time.Clock()
    running=True; help_visible=True; mouse_active=False
    frames=0; capture_count=0
    if args.at is not None:
        mission.update(args.at)
    while running:
        dt=clock.tick(args.fps)/1000.0
        capture=None
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: running=False
                elif event.key==pygame.K_SPACE: mission.paused=not mission.paused
                elif event.key==pygame.K_r: mission.reset()
                elif event.key==pygame.K_c: camera.home()
                elif event.key==pygame.K_h: help_visible=not help_visible
                elif event.key==pygame.K_l: renderer.shadows=not renderer.shadows
                elif event.key==pygame.K_F12:
                    capture_count+=1; capture=Path('capturas')/f'rover_{time.time_ns()}_{capture_count}.png'
            elif event.type in (pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP) and event.button==3:
                mouse_active=event.type==pygame.MOUSEBUTTONDOWN
                pygame.event.set_grab(mouse_active); pygame.mouse.set_visible(not mouse_active)
                pygame.mouse.get_rel()
            elif event.type==pygame.WINDOWFOCUSLOST:
                mouse_active=False; pygame.event.set_grab(False); pygame.mouse.set_visible(True)
        keys=pygame.key.get_pressed()
        controls={key:keys[getattr(pygame,'K_'+(key.upper() if len(key)>1 else key))] for key in ('w','a','s','d','q','e','left','right','up','down')}
        controls['shift']=keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        camera.update(dt,controls,pygame.mouse.get_rel() if mouse_active else (0,0))
        if args.at is None:
            mission.update(args.fixed_dt if args.fixed_dt else dt)
        pose=scene.animate(mission)
        renderer.draw(scene,camera,width,height)
        hud.draw(mission,clock.get_fps(),renderer.shadows,mouse_active,help_visible,pose.fade,width,height)
        frames+=1
        if args.frames and frames>=args.frames:
            running=False
            if args.capture: capture=args.capture
        if capture:
            renderer.screenshot(capture,width,height)
            print('Captura:',capture,flush=True)
        error=glGetError()
        if error!=GL_NO_ERROR: raise RuntimeError(f'OpenGL error: {error}')
        pygame.display.flip()
    print(json.dumps({'frames':frames,'state':mission.state.name,'cycles':mission.cycles,'simulation_seconds':mission.total,'gl_error':int(glGetError())}),flush=True)
    pygame.quit()

def parse_args():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fps',type=int,default=60,choices=range(15,241),metavar='15..240')
    p.add_argument('--shadow-size',type=int,default=2048,choices=(512,1024,2048,4096))
    p.add_argument('--frames',type=int,default=0,help='Encerra após N quadros para teste')
    p.add_argument('--fixed-dt',type=float,help='Avanço simulado por quadro, somente para testes')
    p.add_argument('--at',type=float,help='Congela no segundo indicado; câmera continua livre')
    p.add_argument('--capture',type=Path,help='Salva último quadro antes de trocar buffers')
    return p.parse_args()

if __name__=='__main__':
    try: run(parse_args())
    except Exception as exc:
        pygame.quit(); print(f'Falha: {exc}',file=sys.stderr); raise

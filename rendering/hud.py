"""HUD OpenGL: estado da missão, ajuda, FPS/CPU/GPU e efeitos gráficos."""
import ctypes
import numpy as np
import pygame
from OpenGL.GL import *
from rendering.renderer import program
from scene.animation import LABELS

class Hud:
    def __init__(self):
        self.program=program('hud')
        self.tex=glGenTextures(1)
        self.vao=glGenVertexArrays(1); glBindVertexArray(self.vao)
        self.buffer=glGenBuffers(1);glBindBuffer(GL_ARRAY_BUFFER,self.buffer)
        vertices=np.array([[-1,-1,0,0],[1,-1,1,0],[1,1,1,1],
                           [-1,-1,0,0],[1,1,1,1],[-1,1,0,1]],dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER,vertices.nbytes,vertices,GL_STATIC_DRAW)
        for loc,offset in ((0,0),(1,8)):
            glEnableVertexAttribArray(loc)
            glVertexAttribPointer(loc,2,GL_FLOAT,False,16,ctypes.c_void_p(offset))
        self.fonts={s:pygame.font.Font(None,s) for s in (18,20,24,32,46)}
        self.last=None

    def draw(self,mission,fps,shadows,mouse,help_visible,fade,width,height,
             telemetry=None,show_stats=True,effects=(True,True,True)):
        telemetry=telemetry or {}
        def percent(value):
            return 'N/D' if value is None else f'{value:.0f}%'
        cpu=percent(telemetry.get('cpu'))
        gpu=percent(telemetry.get('gpu'))
        source=telemetry.get('gpu_kind','GPU')
        state=(mission.state,mission.paused,int(mission.progress*80),int(fps),
               shadows,mouse,help_visible,mission.cycles,show_stats,
               cpu,gpu,source,tuple(effects))
        if state!=self.last:
            self.last=state
            s=pygame.Surface((1280,720),pygame.SRCALPHA)
            def text(content,x,y,size=24,color=(229,237,230)):
                s.blit(self.fonts[size].render(content,True,color),(x,y))
            pygame.draw.rect(s,(8,22,29,225),(24,24,430,134),border_radius=12)
            pygame.draw.rect(s,(242,184,66,255),(24,40,4,50),border_radius=2)
            text('COMPUTAÇÃO GRÁFICA  /  ETAPA 3',44,39,18,(136,178,185))
            text('OPERAÇÃO ROVER',44,62,46)
            text('Missão de desobstrução',46,111,24,(193,206,197))
            pygame.draw.rect(s,(8,22,29,225),(880,24,376,108),border_radius=12)
            text('MISSÃO  %02d   /   %s'%(mission.cycles+1,'PAUSADA' if mission.paused else 'EM OPERAÇÃO'),900,42,20,(242,190,76))
            text('%02d / 07   %s'%(mission.state.value+1,LABELS[mission.state.value].split(' • ')[0]),900,68,24)
            pygame.draw.rect(s,(45,65,70),(902,108,330,4),border_radius=2)
            pygame.draw.rect(s,(91,195,172),(902,108,int(330*mission.progress),4),border_radius=2)
            text('%s   /   SOMBRAS %s'%('MOUSE ATIVO' if mouse else 'CÂMERA LIVRE',
                                       'ON' if shadows else 'OFF'),905,143,18,(158,187,187))
            if show_stats:
                pygame.draw.rect(s,(8,22,29,228),(1006,172,250,124),border_radius=10)
                text('MONITOR DE DESEMPENHO',1023,184,18,(242,190,76))
                text(f'FPS  {int(fps):3d}',1023,207,24,(125,225,193))
                text(f'CPU  {cpu}',1023,232,20)
                text(f'{source}  {gpu}',1023,255,18)
                if source=='GPU motor*':
                    text('*motor mais ocupado',1023,275,18,(140,169,178))
            if help_visible:
                pygame.draw.rect(s,(8,22,29,231),(24,600,1232,96),border_radius=10)
                text('WASD mover   SETAS orientar   Q/E altura   SHIFT acelerar   MOUSE botão direito para olhar',44,608,24)
                text('ESPAÇO pausar   R reiniciar   C câmera   L sombras   F12 captura   H ajuda   ESC sair',44,636,20,(143,177,180))
                toggles='F1 Bloom %s   F2 Bump %s   F3 Pós %s   F4 Métricas'%tuple('ON' if e else 'OFF' for e in effects)
                text(toggles,44,662,20,(143,195,180))
            else:
                text('H ajuda',30,680,20)
            glActiveTexture(GL_TEXTURE0);glBindTexture(GL_TEXTURE_2D,self.tex)
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,1280,720,0,GL_RGBA,GL_UNSIGNED_BYTE,
                         pygame.image.tobytes(s,'RGBA',True))
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glUseProgram(self.program)
        glActiveTexture(GL_TEXTURE0);glBindTexture(GL_TEXTURE_2D,self.tex)
        glUniform1i(glGetUniformLocation(self.program,'hudTexture'),0)
        glUniform1f(glGetUniformLocation(self.program,'fade'),fade)
        glDisable(GL_DEPTH_TEST);glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glBindVertexArray(self.vao);glDrawArrays(GL_TRIANGLES,0,6)
        glBindVertexArray(0);glDisable(GL_BLEND);glEnable(GL_DEPTH_TEST)

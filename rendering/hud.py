"""Legenda 2D enviada como textura OpenGL; a cena é inteiramente 3D."""
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
        self.buffer=glGenBuffers(1); glBindBuffer(GL_ARRAY_BUFFER,self.buffer)
        vertices=np.array([[-1,-1,0,0],[1,-1,1,0],[1,1,1,1],[-1,-1,0,0],[1,1,1,1],[-1,1,0,1]],dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER,vertices.nbytes,vertices,GL_STATIC_DRAW)
        for loc,offset in ((0,0),(1,8)):
            glEnableVertexAttribArray(loc)
            glVertexAttribPointer(loc,2,GL_FLOAT,False,16,ctypes.c_void_p(offset))
        self.fonts={s:pygame.font.Font(None,s) for s in (18,20,24,32,46)}
        self.last=None

    def draw(self,mission,fps,shadows,mouse,help_visible,fade,width,height):
        state=(mission.state,mission.paused,int(mission.progress*80),int(fps),shadows,mouse,help_visible,mission.cycles)
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
            if help_visible:
                pygame.draw.rect(s,(8,22,29,225),(24,625,1232,71),border_radius=10)
                text('WASD mover   SETAS orientar   Q/E altura   SHIFT acelerar   MOUSE botão direito para olhar',44,638,24)
                text('ESPAÇO pausar   R reiniciar   C câmera inicial   L sombras   F12 captura   H ajuda   ESC sair',44,668,20,(143,177,180))
            else:
                text('H  ajuda',30,680,20)
            text('%s   /   %d FPS   /   SOMBRAS %s'%('MOUSE ATIVO' if mouse else 'CÂMERA LIVRE',int(fps),'ON' if shadows else 'OFF'),875,143,18,(158,187,187))
            glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_2D,self.tex)
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,1280,720,0,GL_RGBA,GL_UNSIGNED_BYTE,pygame.image.tobytes(s,'RGBA',True))
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glUseProgram(self.program)
        glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_2D,self.tex)
        glUniform1i(glGetUniformLocation(self.program,'hudTexture'),0)
        glUniform1f(glGetUniformLocation(self.program,'fade'),fade)
        glDisable(GL_DEPTH_TEST); glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glBindVertexArray(self.vao); glDrawArrays(GL_TRIANGLES,0,6)
        glBindVertexArray(0); glDisable(GL_BLEND); glEnable(GL_DEPTH_TEST)

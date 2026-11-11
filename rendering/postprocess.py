"""Pipeline OpenGL 3.3: cena HDR, extração de luz, blur e composição."""
import ctypes
from pathlib import Path
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

SHADERS=Path(__file__).resolve().parents[1]/'shaders'

def shader_pair(name):
    vertex=compileShader((SHADERS/'post.vert').read_text(encoding='utf-8'),GL_VERTEX_SHADER)
    fragment=compileShader((SHADERS/(name+'.frag')).read_text(encoding='utf-8'),GL_FRAGMENT_SHADER)
    out=compileProgram(vertex,fragment)
    return out

class PostProcess:
    def __init__(self):
        self.extract=shader_pair('extract')
        self.blur=shader_pair('blur')
        self.compose=shader_pair('compose')
        self.vao=glGenVertexArrays(1);glBindVertexArray(self.vao)
        self.vbo=glGenBuffers(1);glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        quad=np.array([-1,-1,0,0, 1,-1,1,0, 1,1,1,1,
                       -1,-1,0,0, 1,1,1,1, -1,1,0,1],dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER,quad.nbytes,quad,GL_STATIC_DRAW)
        for index,offset in ((0,0),(1,8)):
            glEnableVertexAttribArray(index)
            glVertexAttribPointer(index,2,GL_FLOAT,False,16,ctypes.c_void_p(offset))
        glBindVertexArray(0)
        self.fbo=glGenFramebuffers(1)
        self.scene_tex=self._texture()
        self.depth=glGenRenderbuffers(1)
        self.blur_fbo=[int(glGenFramebuffers(1)) for _ in range(2)]
        self.blur_tex=[self._texture() for _ in range(2)]
        self.size=None

    @staticmethod
    def _texture():
        tex=glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,tex)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE)
        return tex

    @staticmethod
    def _check(label):
        code=glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if code!=GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError('Framebuffer '+label+' incompleto: '+str(code))

    def resize(self,width,height):
        if self.size==(width,height):return
        self.size=width,height
        self.half=(max(1,width//2),max(1,height//2))
        glBindTexture(GL_TEXTURE_2D,self.scene_tex)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA16F,width,height,0,GL_RGBA,GL_FLOAT,None)
        glBindFramebuffer(GL_FRAMEBUFFER,self.fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,self.scene_tex,0)
        glBindRenderbuffer(GL_RENDERBUFFER,self.depth)
        glRenderbufferStorage(GL_RENDERBUFFER,GL_DEPTH_COMPONENT24,width,height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_RENDERBUFFER,self.depth)
        self._check('HDR')
        for i in range(2):
            glBindTexture(GL_TEXTURE_2D,self.blur_tex[i])
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA16F,*self.half,0,GL_RGBA,GL_FLOAT,None)
            glBindFramebuffer(GL_FRAMEBUFFER,self.blur_fbo[i])
            glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,self.blur_tex[i],0)
            self._check('blur '+str(i))
        glBindFramebuffer(GL_FRAMEBUFFER,0)

    def begin(self,width,height):
        self.resize(width,height)
        glBindFramebuffer(GL_FRAMEBUFFER,self.fbo)
        glViewport(0,0,width,height)
        glEnable(GL_DEPTH_TEST)

    def _fullscreen(self,program,texture):
        glUseProgram(program)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,texture)
        glUniform1i(glGetUniformLocation(program,'sourceTexture'),0)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES,0,6)

    def end(self,width,height,bloom=True,post=True):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
        bloom_tex=self.blur_tex[0]
        if bloom:
            glBindFramebuffer(GL_FRAMEBUFFER,self.blur_fbo[0])
            glViewport(0,0,*self.half)
            glClear(GL_COLOR_BUFFER_BIT)
            self._fullscreen(self.extract,self.scene_tex)
            source=self.blur_tex[0]
            # Três ciclos H/V, em meia resolução para preservar desempenho.
            for i in range(6):
                index=1 if i%2==0 else 0
                glBindFramebuffer(GL_FRAMEBUFFER,self.blur_fbo[index])
                glViewport(0,0,*self.half)
                glClear(GL_COLOR_BUFFER_BIT)
                glUseProgram(self.blur)
                glUniform1i(glGetUniformLocation(self.blur,'horizontal'),int(i%2==0))
                self._fullscreen(self.blur,source)
                source=self.blur_tex[index]
            bloom_tex=source
        glBindFramebuffer(GL_FRAMEBUFFER,0)
        glViewport(0,0,width,height)
        glUseProgram(self.compose)
        glActiveTexture(GL_TEXTURE1);glBindTexture(GL_TEXTURE_2D,bloom_tex)
        glUniform1i(glGetUniformLocation(self.compose,'bloomTexture'),1)
        glUniform1i(glGetUniformLocation(self.compose,'useBloom'),int(bloom))
        glUniform1i(glGetUniformLocation(self.compose,'usePost'),int(post))
        glUniform1f(glGetUniformLocation(self.compose,'exposure'),1.10)
        self._fullscreen(self.compose,self.scene_tex)
        glBindVertexArray(0)
        glActiveTexture(GL_TEXTURE0)
        glEnable(GL_DEPTH_TEST)

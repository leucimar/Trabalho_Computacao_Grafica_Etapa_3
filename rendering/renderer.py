"""Renderer de duas passagens para Mesh/Attribute do framework da disciplina."""
from pathlib import Path
import numpy as np
import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from core.mesh import Mesh
from core.uniform import Uniform
from scene.camera_controls import look_at
from rendering.postprocess import PostProcess

ROOT=Path(__file__).resolve().parents[1]


def program(name):
    # Explicit locations bind the same framework VAO in both passes.
    vertex=compileShader((ROOT/'shaders'/f'{name}.vert').read_text(encoding='utf-8'),GL_VERTEX_SHADER)
    fragment=compileShader((ROOT/'shaders'/f'{name}.frag').read_text(encoding='utf-8'),GL_FRAGMENT_SHADER)
    ref=glCreateProgram(); glAttachShader(ref,vertex); glAttachShader(ref,fragment)
    if name!='hud':
        for loc,key in enumerate(('vertexPosition','vertexNormal','vertexUV')):
            glBindAttribLocation(ref,loc,key)
    glLinkProgram(ref)
    if not glGetProgramiv(ref,GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(ref).decode())
    glDeleteShader(vertex); glDeleteShader(fragment)
    return ref


class SceneMaterial:
    def __init__(self):
        self.programRef=program('scene')


class Renderer:
    def __init__(self,size=2048):
        self.depth_program=program('depth')
        self.material=SceneMaterial()
        self.shadow_size=size
        self.shadows=True
        self.bump=True
        self.bloom=True
        self.post=True
        self.postfx=PostProcess()
        self.locations={}
        self.matrix_uniforms={}
        self.direction=np.array([-.55,-1.,-.45],dtype=np.float32)
        self.direction/=np.linalg.norm(self.direction)
        # Orthographic light frustum covers the complete 23x15 diorama.
        ortho=np.array([[1/16,0,0,0],[0,1/16,0,0],[0,0,-2/59,-61/59],[0,0,0,1]],dtype=np.float32)
        self.light_space=ortho@look_at(-self.direction*26,[0,0,0])
        self.depth_texture=glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.depth_texture)
        glTexImage2D(GL_TEXTURE_2D,0,GL_DEPTH_COMPONENT24,size,size,0,GL_DEPTH_COMPONENT,GL_FLOAT,None)
        for prop in (GL_TEXTURE_MIN_FILTER,GL_TEXTURE_MAG_FILTER):
            glTexParameteri(GL_TEXTURE_2D,prop,GL_NEAREST)
        for prop in (GL_TEXTURE_WRAP_S,GL_TEXTURE_WRAP_T):
            glTexParameteri(GL_TEXTURE_2D,prop,GL_CLAMP_TO_BORDER)
        glTexParameterfv(GL_TEXTURE_2D,GL_TEXTURE_BORDER_COLOR,np.ones(4,dtype=np.float32))
        self.fbo=glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER,self.fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,self.depth_texture,0)
        glDrawBuffer(GL_NONE); glReadBuffer(GL_NONE)
        status=glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status!=GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(f'Shadow FBO incompleto: {status}')
        glBindFramebuffer(GL_FRAMEBUFFER,0)
        self.textures={}
        for path in sorted((ROOT/'assets'/'textures').glob('*.png')):
            surface=pygame.image.load(str(path))
            tex=glGenTextures(1); glBindTexture(GL_TEXTURE_2D,tex)
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,surface.get_width(),surface.get_height(),0,GL_RGBA,GL_UNSIGNED_BYTE,pygame.image.tobytes(surface,'RGBA',True))
            glGenerateMipmap(GL_TEXTURE_2D)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
            self.textures[path.stem]=tex
        glEnable(GL_DEPTH_TEST)
        # Course BoxGeometry has outward CCW winding; two-sided rendering also
        # supports thin panels and avoids relying on face culling for shadows.
        glDisable(GL_CULL_FACE)
        glClearColor(.075,.135,.175,1)

    def location(self,ref,name):
        key=(ref,name)
        if key not in self.locations:
            self.locations[key]=glGetUniformLocation(ref,name)
        return self.locations[key]

    def matrix(self,ref,name,value):
        key=(ref,name)
        if key not in self.matrix_uniforms:
            uniform=Uniform('mat4',value)
            uniform.locateVariable(ref,name)
            self.matrix_uniforms[key]=uniform
        uniform=self.matrix_uniforms[key]
        uniform.data=value
        uniform.uploadData()

    def draw(self,scene,camera,width,height):
        meshes=[node for node in scene.getDescendantList() if isinstance(node,Mesh) and node.visible]
        glEnable(GL_DEPTH_TEST); glDisable(GL_BLEND)
        # Pass 1: depth from the directional light, rerendered every frame.
        glBindFramebuffer(GL_FRAMEBUFFER,self.fbo)
        glViewport(0,0,self.shadow_size,self.shadow_size)
        glClear(GL_DEPTH_BUFFER_BIT); glUseProgram(self.depth_program)
        self.matrix(self.depth_program,'lightSpaceMatrix',self.light_space)
        for mesh in meshes:
            if mesh.cast_shadow:
                self.matrix(self.depth_program,'modelMatrix',mesh.getWorldMatrix())
                glBindVertexArray(mesh.vaoRef)
                glDrawArrays(GL_TRIANGLES,0,mesh.geometry.vertexCount)
        # Pass 2: camera, texture, local illumination and depth comparison.
        self.postfx.begin(width,height)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        ref=self.material.programRef; glUseProgram(ref)
        self.matrix(ref,'viewMatrix',camera.view)
        self.matrix(ref,'projectionMatrix',camera.projection(width/height))
        self.matrix(ref,'lightSpaceMatrix',self.light_space)
        glUniform3fv(self.location(ref,'lightDirection'),1,self.direction)
        glUniform3fv(self.location(ref,'cameraPosition'),1,camera.position.astype(np.float32))
        glUniform1i(self.location(ref,'shadowsEnabled'),int(self.shadows))
        glUniform1i(self.location(ref,'bumpEnabled'),int(self.bump))
        glUniform1i(self.location(ref,'colorTexture'),0)
        glUniform1i(self.location(ref,'shadowMap'),1)
        glActiveTexture(GL_TEXTURE1); glBindTexture(GL_TEXTURE_2D,self.depth_texture)
        glActiveTexture(GL_TEXTURE0)
        for mesh in meshes:
            self.matrix(ref,'modelMatrix',mesh.getWorldMatrix())
            glUniform3f(self.location(ref,'baseColor'),*mesh.color)
            glUniform2f(self.location(ref,'uvRepeat'),*mesh.uv_repeat)
            glUniform1f(self.location(ref,'emission'),mesh.emission)
            glUniform1f(self.location(ref,'bumpStrength'),getattr(mesh,'bump_strength',0.0))
            glBindTexture(GL_TEXTURE_2D,self.textures[mesh.texture_name])
            glBindVertexArray(mesh.vaoRef)
            glDrawArrays(GL_TRIANGLES,0,mesh.geometry.vertexCount)
        glBindVertexArray(0)
        self.postfx.end(width,height,self.bloom,self.post)

    def depth_pixels(self):
        glBindTexture(GL_TEXTURE_2D,self.depth_texture)
        return np.asarray(glGetTexImage(GL_TEXTURE_2D,0,GL_DEPTH_COMPONENT,GL_FLOAT),dtype=np.float32)

    def screenshot(self,path,width,height):
        path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
        glPixelStorei(GL_PACK_ALIGNMENT,1)
        pixels=glReadPixels(0,0,width,height,GL_RGB,GL_UNSIGNED_BYTE)
        surface=pygame.image.frombytes(pixels,(width,height),'RGB')
        pygame.image.save(pygame.transform.flip(surface,False,True),str(path))

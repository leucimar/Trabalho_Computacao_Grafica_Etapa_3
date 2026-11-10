#version 330 core
in vec3 vertexPosition;
uniform mat4 modelMatrix;
uniform mat4 lightSpaceMatrix;
void main() {
    gl_Position = lightSpaceMatrix * modelMatrix * vec4(vertexPosition,1.0);
}

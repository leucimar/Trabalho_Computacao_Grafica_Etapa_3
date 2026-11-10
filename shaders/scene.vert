#version 330 core
in vec3 vertexPosition;
in vec3 vertexNormal;
in vec2 vertexUV;
uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform mat4 lightSpaceMatrix;
uniform vec2 uvRepeat;
out vec3 worldPosition;
out vec3 worldNormal;
out vec2 uv;
out vec4 lightPosition;
void main() {
    vec4 world = modelMatrix * vec4(vertexPosition, 1.0);
    worldPosition = world.xyz;
    worldNormal = transpose(inverse(mat3(modelMatrix))) * vertexNormal;
    uv = vertexUV * uvRepeat;
    lightPosition = lightSpaceMatrix * world;
    gl_Position = projectionMatrix * viewMatrix * world;
}

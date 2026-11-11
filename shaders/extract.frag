#version 330 core
in vec2 uv;
out vec4 fragColor;
uniform sampler2D sourceTexture;
void main() {
    vec3 color=texture(sourceTexture,uv).rgb;
    // Usa o pico HDR para incluir o sinalizador vermelho em todo o pulso.
    float brightness=max(color.r,max(color.g,color.b));
    fragColor=vec4(brightness>1.12 ? color : vec3(0.0),1.0);
}

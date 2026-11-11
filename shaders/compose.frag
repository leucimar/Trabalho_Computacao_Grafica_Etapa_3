#version 330 core
in vec2 uv;
out vec4 fragColor;
uniform sampler2D sourceTexture;
uniform sampler2D bloomTexture;
uniform bool useBloom;
uniform bool usePost;
uniform float exposure;
void main() {
    vec3 scene=texture(sourceTexture,uv).rgb;
    if(useBloom) scene+=texture(bloomTexture,uv).rgb*.65;
    if(usePost) {
        scene=vec3(1.0)-exp(-scene*exposure);
        scene=pow(max(scene,vec3(0.0)),vec3(1.0/2.2));
    } else scene=clamp(scene,0.0,1.0);
    fragColor=vec4(scene,1.0);
}

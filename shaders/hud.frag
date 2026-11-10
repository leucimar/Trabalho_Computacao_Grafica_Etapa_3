#version 330 core
in vec2 uv;
uniform sampler2D hudTexture;
uniform float fade;
out vec4 fragColor;
void main(){
    vec4 overlay=texture(hudTexture,uv);
    // Alpha composition with an independent transition over the 3D scene.
    vec3 ink=vec3(0.04,0.08,0.10);
    float a=overlay.a+fade*(1.0-overlay.a);
    fragColor=vec4(a>0.0 ? (overlay.rgb*overlay.a+ink*fade*(1.0-overlay.a))/a : ink,a);
}

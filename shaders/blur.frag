#version 330 core
in vec2 uv;
out vec4 fragColor;
uniform sampler2D sourceTexture;
uniform bool horizontal;
void main() {
    vec2 texel=1.0/vec2(textureSize(sourceTexture,0));
    vec2 axis=horizontal ? vec2(texel.x,0.0) : vec2(0.0,texel.y);
    vec3 result=texture(sourceTexture,uv).rgb*.227027;
    const float weight[4]=float[4](.1945946,.1216216,.054054,.016216);
    for(int i=1;i<=4;i++) {
        result+=texture(sourceTexture,uv+axis*float(i)).rgb*weight[i-1];
        result+=texture(sourceTexture,uv-axis*float(i)).rgb*weight[i-1];
    }
    fragColor=vec4(result,1.0);
}

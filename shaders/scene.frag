#version 330 core
in vec3 worldPosition;
in vec3 worldNormal;
in vec2 uv;
in vec4 lightPosition;
uniform sampler2D colorTexture;
uniform sampler2D shadowMap;
uniform vec3 baseColor;
uniform vec3 lightDirection;
uniform vec3 cameraPosition;
uniform float emission;
uniform bool shadowsEnabled;
out vec4 fragColor;
float shadowVisibility(vec3 normal) {
    vec3 projected = lightPosition.xyz / lightPosition.w * 0.5 + 0.5;
    if (!shadowsEnabled || projected.z > 1.0 || projected.z < 0.0 ||
        projected.x < 0.0 || projected.x > 1.0 || projected.y < 0.0 || projected.y > 1.0)
        return 1.0;
    float bias = max(0.0012 * (1.0 - dot(normal, -lightDirection)), 0.00035);
    vec2 texel = 1.0 / vec2(textureSize(shadowMap, 0));
    float lit = 0.0;
    for (int x=-1; x<=1; ++x)
        for (int y=-1; y<=1; ++y) {
            float nearest = texture(shadowMap, projected.xy + vec2(x,y)*texel).r;
            lit += projected.z - bias <= nearest ? 1.0 : 0.0;
        }
    return lit / 9.0;
}
void main() {
    vec3 normal = normalize(worldNormal);
    vec3 light = normalize(-lightDirection);
    float diffuse = max(dot(normal, light), 0.0);
    vec3 halfway = normalize(light + normalize(cameraPosition-worldPosition));
    float specular = pow(max(dot(normal, halfway), 0.0), 36.0) * 0.12;
    float visibility = shadowVisibility(normal);
    vec3 albedo = texture(colorTexture, uv).rgb * baseColor;
    vec3 color = albedo * (0.36 + visibility * diffuse * 0.72 + emission)
               + vec3(1.0,0.96,0.84) * specular * visibility;
    // Gentle distance haze integrates geometry with the background.
    float haze = clamp((distance(cameraPosition,worldPosition)-20.0)/75.0,0.0,0.22);
    color = mix(color,vec3(0.12,0.20,0.25),haze);
    fragColor = vec4(color,1.0);
}

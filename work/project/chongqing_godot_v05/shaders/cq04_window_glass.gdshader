shader_type spatial;
render_mode blend_mix, depth_prepass_alpha, cull_disabled, diffuse_burley, specular_schlick_ggx;

// Thin ordinary architectural glass. The real window cavity remains visible.
// Continuous centimetre-scale residue varies the reflection lobe without
// painting a view onto the pane or using high-frequency sparkling speckle.
uniform vec4 glass_tint : source_color = vec4(0.18, 0.25, 0.27, 1.0);
uniform float base_opacity : hint_range(0.05, 0.8) = 0.22;
uniform float base_roughness : hint_range(0.05, 0.8) = 0.23;
uniform float grime_strength : hint_range(0.0, 0.4) = 0.12;
varying vec3 world_position;

float hash2(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float smooth_noise(vec2 p) {
    vec2 cell = floor(p);
    vec2 local = fract(p);
    vec2 curve = local * local * (3.0 - 2.0 * local);
    return mix(mix(hash2(cell), hash2(cell + vec2(1.0, 0.0)), curve.x),
               mix(hash2(cell + vec2(0.0, 1.0)), hash2(cell + vec2(1.0, 1.0)), curve.x), curve.y);
}

void vertex() { world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }

void fragment() {
    float facing = clamp(abs(dot(normalize(NORMAL), normalize(VIEW))), 0.0, 1.0);
    float fresnel = pow(1.0-facing,5.0);
    vec2 plane = vec2(world_position.x * 0.73 + world_position.z * 0.67, world_position.y);
    float residue = smoothstep(0.28, 0.80, smooth_noise(plane * vec2(3.1, 1.8)));
    float streak = smooth_noise(plane * vec2(14.0, 0.85) + vec2(3.4, 7.8));
    float grime = 0.72 * residue + 0.28 * streak;
    ALBEDO = glass_tint.rgb;
    METALLIC = 0.0;
    SPECULAR = 0.5;
    ROUGHNESS = clamp(base_roughness + grime_strength * grime, 0.08, 0.65);
    ALPHA = clamp(base_opacity + 0.54 * fresnel + 0.24 * grime_strength * grime, 0.0, 0.84);
}

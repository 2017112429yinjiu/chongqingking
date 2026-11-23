shader_type spatial;
render_mode diffuse_burley, specular_disabled, cull_back;

uniform sampler2D bark_albedo : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform vec4 bark_tint : source_color = vec4(1.0);
uniform bool use_secondary_uv = false;
uniform vec2 bark_uv_scale = vec2(1.0);
uniform vec2 bark_uv_offset = vec2(0.0);

void fragment() {
    vec2 authored_uv = use_secondary_uv ? UV2 : UV;
    vec3 scanned_bark = texture(bark_albedo, authored_uv * bark_uv_scale + bark_uv_offset).rgb;
    ALBEDO = clamp(scanned_bark * bark_tint.rgb, vec3(0.0), vec3(1.0));
    ROUGHNESS = 0.88;
    METALLIC = 0.0;
    SPECULAR = 0.0;
    AO = 1.0;
}

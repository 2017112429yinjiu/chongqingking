shader_type spatial;
render_mode cull_disabled, diffuse_burley;

uniform sampler2D fabric : source_color, filter_linear_mipmap_anisotropic;
uniform float gust_strength : hint_range(0., 1.) = 1.;

void vertex() {
	float panel = sin(PI * clamp((UV.y - .17) / .83, 0., 1.));
	float hem = 1. - smoothstep(.0, .17, UV.y);
	float shelter = sin(PI * clamp(UV.x, 0., 1.));
	float breeze = .62 * sin(TIME * 1.31 + UV.x * 9.4) + .38 * sin(TIME * 2.05 - UV.x * 15.);
	VERTEX += NORMAL * gust_strength * breeze * (.010 * panel + .028 * hem) * (.35 + .65 * shelter);
}

void fragment() {
	ALBEDO = texture(fabric, UV).rgb;
	ROUGHNESS = .91;
	SPECULAR = .21;
}

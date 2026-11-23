shader_type spatial;
render_mode diffuse_burley, specular_schlick_ggx;

uniform sampler2D rock : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D grain_normal : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D roughness_scan : repeat_enable, filter_linear_mipmap_anisotropic;
uniform bool coping = false;
varying vec3 world;
varying vec3 surface_normal;

void vertex() {
	world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	surface_normal = normalize(MODEL_NORMAL_MATRIX * NORMAL);
}

void fragment() {
	vec3 sample_color = texture(rock, UV).rgb;
	float stone = dot(sample_color, vec3(.27,.56,.17));
	float top = smoothstep(.35,.92,surface_normal.y);
	float damp = 1.0 - smoothstep(7.83, 8.12, world.y);
	float worn = 1.0 - smoothstep(.28, 1.23, abs(world.x + 21.38));
	vec3 color = (vec3(.016,.014,.011) + stone * vec3(.41,.40,.345)) * mix(.86,1.04,top);
	float rough = texture(roughness_scan, UV).r * .18 + .70;
	if (coping) {
		// One stone cover course crosses the slope. Wall masonry remains below it.
		float run = (world.x + .065 * world.z) / 1.17;
		float to_joint = abs(fract(run + .5) - .5) * 1.17;
		float half_pixel = max(fwidth(run) * .65, .0003);
		float joint = 1.0 - smoothstep(.003 - half_pixel, .006 + half_pixel, to_joint);
		color = mix(color * vec3(.70,.73,.70), vec3(.034,.032,.028), joint * .86);
	} else {
		color *= 1.0 + .06 * top * worn;
		rough -= .085 * top * worn;
	}
	ALBEDO = color * mix(vec3(1.0),vec3(.82,.84,.77),damp);
	NORMAL_MAP = texture(grain_normal, UV).rgb;
	NORMAL_MAP_DEPTH = mix(.25,.14,top*worn);
	ROUGHNESS = clamp(rough-.04*damp,.61,.98);
	SPECULAR = .23;
}

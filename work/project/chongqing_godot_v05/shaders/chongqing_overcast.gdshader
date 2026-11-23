// Original static overcast sky for the Chongqing district.
// The four-octave field is evaluated only while updating the radiance cubemap.
// Background frames sample that cached cubemap. No TIME, external textures,
// camera-position dependency, image postprocessing, or animation is used.
shader_type sky;

uniform vec4 zenith_color : source_color = vec4(0.56, 0.62, 0.65, 1.0);
uniform vec4 horizon_color : source_color = vec4(0.76, 0.79, 0.79, 1.0);
uniform vec4 cloud_light_color : source_color = vec4(0.81, 0.82, 0.80, 1.0);
uniform vec4 cloud_shadow_color : source_color = vec4(0.49, 0.54, 0.57, 1.0);
uniform vec4 lower_hemisphere_color : source_color = vec4(0.29, 0.31, 0.30, 1.0);
uniform float cloud_coverage : hint_range(0.0, 1.0) = 0.76;
uniform float cloud_strength : hint_range(0.0, 1.0) = 0.62;
uniform float cloud_scale : hint_range(0.2, 6.0) = 1.35;
uniform float cloud_seed : hint_range(0.0, 100.0) = 17.0;

float cell_hash(vec2 cell) {
	vec2 q = fract(cell * vec2(0.1173, 0.1317));
	q += dot(q.yx, q + vec2(19.7, 37.3));
	return fract(q.x * q.y * 73.17);
}

float soft_noise(vec2 point) {
	vec2 cell = floor(point);
	vec2 local = fract(point);
	vec2 blend = local * local * (3.0 - 2.0 * local);
	float a = cell_hash(cell);
	float b = cell_hash(cell + vec2(1.0, 0.0));
	float c = cell_hash(cell + vec2(0.0, 1.0));
	float d = cell_hash(cell + vec2(1.0, 1.0));
	return mix(mix(a, b, blend.x), mix(c, d, blend.x), blend.y);
}

float cloud_field(vec2 point) {
	float sum = 0.0;
	float amplitude = 0.5;
	mat2 turn_and_scale = mat2(vec2(1.6, 1.2), vec2(-1.2, 1.6));
	for (int octave = 0; octave < 4; octave++) {
		sum += soft_noise(point) * amplitude;
		point = turn_and_scale * point + vec2(3.7, 8.3);
		amplitude *= 0.5;
	}
	return sum / 0.9375;
}

vec3 overcast_color(vec3 direction) {
	float up = clamp(direction.y, 0.0, 1.0);
	float sky_height = smoothstep(0.0, 0.92, up);
	vec3 clear_tone = mix(horizon_color.rgb, zenith_color.rgb, sky_height);
	if (direction.y < 0.0) {
		float depth = smoothstep(0.0, 0.45, -direction.y);
		return mix(horizon_color.rgb, lower_hemisphere_color.rgb, depth);
	}
	// Broad cloud sheets, softened toward the hazy urban horizon.
	vec2 projection = direction.xz / (0.34 + up);
	vec2 seed_offset = vec2(cloud_seed * 0.371, cloud_seed * 0.163);
	float field = cloud_field(projection * cloud_scale + seed_offset);
	float coverage_edge = 1.0 - cloud_coverage;
	float mask = smoothstep(coverage_edge - 0.18, coverage_edge + 0.28, field);
	float lightness = smoothstep(0.20, 0.77, field);
	vec3 cloud_tone = mix(cloud_shadow_color.rgb, cloud_light_color.rgb, lightness);
	float horizon_fade = smoothstep(0.015, 0.25, up);
	return mix(clear_tone, cloud_tone, mask * cloud_strength * horizon_fade);
}

void sky() {
	if (AT_CUBEMAP_PASS) {
		COLOR = overcast_color(normalize(EYEDIR));
	} else {
		COLOR = textureLod(RADIANCE, EYEDIR, 0.0).rgb;
	}
}

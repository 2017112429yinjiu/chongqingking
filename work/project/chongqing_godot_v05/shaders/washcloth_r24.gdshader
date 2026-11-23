shader_type spatial;
render_mode cull_disabled, diffuse_burley;

uniform vec4 dye : source_color = vec4(.6, .58, .49, 1.);
uniform float phase = 0.;
uniform sampler2D loop_pile : repeat_enable, filter_linear_mipmap_anisotropic;
uniform vec2 cloth_size_m = vec2(.4, .6);
uniform float sample_time = -1.;

void vertex() {
	// glTF UV.y is 1 along the line and 0 at the towel's lower edge.
	float fall = 1. - UV.y;
	float loose = smoothstep(.065, 1., fall);
	float t = sample_time < 0. ? TIME : sample_time;
	float gust = sin(t * 1.27 + phase + fall * 1.9);
	float ripple = sin(t * 2.17 + phase * 1.6 + UV.x * 5.4 - fall * 3.);
	vec3 motion = vec3(.010 * gust, .003 * ripple, .025 * gust + .013 * ripple);
	VERTEX += (inverse(MODEL_MATRIX) * vec4(motion * loose * loose, 0.)).xyz;
}

float filtered_thread(float cycles) {
	float visible = 1. - smoothstep(.18, .55, fwidth(cycles));
	return cos(cycles * 6.283185) * visible;
}

float woven_band(float distance_from_hem, float middle, float width) {
	float aa = max(fwidth(distance_from_hem), .0005);
	return 1. - smoothstep(width - aa, width + aa, abs(distance_from_hem - middle));
}

void fragment() {
	vec2 uv = UV;
	float height = .104 + .027 * sin(phase * 3.);
	float band = woven_band(uv.y, height, .013 + .009 * cos(phase * 1.5));
	float accent = woven_band(uv.y, height - .035, .004) + woven_band(uv.y, height + .034, .003);
	float edge = min(min(uv.x, 1. - uv.x), min(uv.y, 1. - uv.y));
	float hem = 1. - smoothstep(.009, .017, edge);
	float weft = filtered_thread(uv.y * 186.);
	float warp = filtered_thread(uv.x * 134. + .17 * weft);
	float terry = filtered_thread(uv.x * 110. + uv.y * 92.) * filtered_thread(uv.y * 124. - uv.x * 29.);
	float jacquard = filtered_thread(uv.x * 32. + uv.y * 37.) * filtered_thread(uv.y * 44.);
	float wear = .5 + .5 * sin(uv.x * 9. + phase + uv.y * 3.) * sin(uv.y * 12. + sin(uv.x * 9.));
	float nap = (1. - max(band, hem)) * (.045 * weft + .045 * warp + .08 * terry);
	vec3 yarn = mix(dye.rgb, vec3(.34, .305, .25), .12 + .06 * wear);
	vec3 border = mix(yarn, vec3(.49, .413, .302), .32 + .10 * sin(phase));
	vec2 scan_uv = uv * cloth_size_m / vec2(.36705, .36320) + vec2(.31, .57) * phase;
	vec3 scan = texture(loop_pile, scan_uv).rgb;
	float raised = 1. - max(band, hem);
	vec3 cloth = mix(yarn, border * (.88 + .12 * jacquard), band);
	cloth *= 1. + raised * (scan.b - .5) * .66;
	NORMAL_MAP = vec3(scan.rg, 1.);
	NORMAL_MAP_DEPTH = mix(.16, .83, raised);
	ALBEDO = mix(cloth, border * .68, clamp(accent + .35 * hem, 0., 1.)) * (1. + nap);
	ROUGHNESS = .96 - .06 * band;
	SPECULAR = .13;
	BACKLIGHT = ALBEDO * .075;
}

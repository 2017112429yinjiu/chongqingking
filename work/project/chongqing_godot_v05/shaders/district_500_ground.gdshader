shader_type spatial;

uniform sampler2D street_mask : filter_linear_mipmap, repeat_disable;
uniform sampler2D asphalt : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D asphalt_normal : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D asphalt_rough : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D paving : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D soil : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D aggregate : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float river_level = -15.8;
varying vec3 world_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 east_north = vec2(world_position.x, -world_position.z);
	vec2 uv = vec2(east_north.x + 250.0, 250.0 - east_north.y) / 500.0;
	vec3 layout = texture(street_mask, uv).rgb;
	vec2 tile_uv = east_north / 2.4;
	vec3 earth = texture(soil, tile_uv).rgb;
	vec3 grit = texture(aggregate, tile_uv * 0.8).rgb;
	vec3 vegetation = earth * vec3(0.69, 0.94, 0.52);
	vec3 bank = mix(earth, vegetation, layout.b * 0.79);
	float damp = 1.0 - smoothstep(river_level + 0.6, river_level + 4.5, world_position.y);
	vec3 surface = mix(bank, grit * (0.63 + 0.22 * layout.b), damp);
	vec3 footway = texture(paving, tile_uv).rgb * 0.91;
	surface = mix(surface, footway, layout.g);
	// Match the registered old carriageways' world-space aggregate scale and direction.
	vec2 street_uv = world_position.xz * 0.42;
	float grain = dot(texture(asphalt, street_uv).rgb, vec3(0.25, 0.55, 0.20));
	float substrate = texture(asphalt, world_position.xz * 0.124 + vec2(0.23, 0.47)).g;
	vec3 binder = (vec3(0.023, 0.023, 0.022) + grain * vec3(0.52, 0.53, 0.51));
	binder *= mix(0.82, 1.09, smoothstep(0.07, 0.41, substrate));
	ALBEDO = mix(surface, binder, layout.r);
	NORMAL_MAP = mix(vec3(0.5, 0.5, 1.0), texture(asphalt_normal, street_uv).rgb, layout.r);
	NORMAL_MAP_DEPTH = 0.55;
	ROUGHNESS = mix(0.94, 0.70 + 0.21 * texture(asphalt_rough, street_uv).r, layout.r);
	SPECULAR = mix(0.22, 0.24, layout.r);
}

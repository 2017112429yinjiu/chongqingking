shader_type spatial;

uniform sampler2D street_mask : filter_linear_mipmap, repeat_disable;
uniform sampler2D asphalt : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
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
	vec3 road = texture(asphalt, tile_uv * 0.88).rgb;
	float wear = 0.90 + 0.08 * sin(east_north.x * 0.35 + east_north.y * 0.22);
	ALBEDO = mix(surface, road * wear, layout.r);
	ROUGHNESS = mix(0.94, 0.80, layout.r);
	SPECULAR = 0.22;
}

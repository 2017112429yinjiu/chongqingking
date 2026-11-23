shader_type spatial;
render_mode diffuse_burley,specular_schlick_ggx;
#include "res://shaders/street_use_r24.gdshaderinc"
uniform sampler2D stone_scan : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D irregular_normal : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D stone_rough : repeat_enable, filter_linear_mipmap_anisotropic;
varying vec3 world;
varying vec3 stone_normal;
void vertex(){
	world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
	stone_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment(){
	vec3 n=normalize(stone_normal);
	float top=smoothstep(.40,.83,n.y);
	
	vec2 uv=UV;
	vec3 sample_color=texture(stone_scan,uv).rgb;
	float grain=dot(sample_color,vec3(.27,.54,.19));
	float vein=.10+.32*COLOR.r;
	vec3 use_pattern=use_at(world.xz);
	float traffic=use_pattern.r*top;
	float patina=max(use_pattern.g,.32*(1.-top));
	float base=(.048+.36*grain+.082*vein)*mix(.61,.99,top);
	vec3 pigment=base*vec3(1.12,.952,.771)*mix(vec3(.46),vec3(1.20),COLOR.rgb);
	pigment*=mix(1.,1.13,traffic);
	pigment=mix(pigment,pigment*vec3(.50,.585,.47),patina*.76);
	ALBEDO=pigment;
	ROUGHNESS=clamp(.71+.19*texture(stone_rough,uv).r-.075*traffic-.11*use_pattern.b,.56,.96);
	SPECULAR=.26;
	NORMAL_MAP=texture(irregular_normal,uv).rgb;
	NORMAL_MAP_DEPTH=mix(.59,.39,traffic);
}

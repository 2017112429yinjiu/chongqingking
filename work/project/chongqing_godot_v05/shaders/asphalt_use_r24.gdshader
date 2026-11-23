shader_type spatial;
render_mode diffuse_burley,specular_schlick_ggx;
#include "res://shaders/street_use_r24.gdshaderinc"
#include "res://shaders/street_repairs_r24.gdshaderinc"
uniform sampler2D tar_scan : source_color,repeat_enable,filter_linear_mipmap_anisotropic;
uniform sampler2D tar_normal : hint_normal,repeat_enable,filter_linear_mipmap_anisotropic;
uniform sampler2D tar_rough : repeat_enable,filter_linear_mipmap_anisotropic;
varying vec3 asphalt_world;
void vertex(){asphalt_world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
void fragment(){
	vec2 ground=asphalt_world.xz;
	vec2 st=ground*.42;
	vec3 grit=texture(tar_scan,st).rgb;
	float body=dot(grit,vec3(.25,.55,.20));
	float substrate=texture(tar_scan,ground*.124+vec2(.23,.47)).g;
	vec3 trace=use_at(ground);
	float abraded=trace.r;
	float gutter=trace.g;
	vec3 binder=vec3(.023,.023,.022)+body*vec3(.52,.53,.51);
	binder*=mix(.82,1.09,smoothstep(.07,.41,substrate));
	binder*=mix(.91,1.09,abraded)*(1.-.09*gutter);
	// Saw-cut utility backfills. The finish is flush and follows the original sloping carriageway.
	vec2 yy=ground-vec2(-30.4,83.8);yy.y+=.112*yy.x;
	vec2 zz=ground-vec2(-13.2,85.4);zz.x-=.15*zz.y;
	float erosion=(substrate-.22)*.11+(body-.20)*.12;
	float repair=max(patch_box(yy,vec2(2.26,.47),erosion),patch_box(zz,vec2(.41,2.25),erosion));
	vec3 fresh=vec3(.018,.019,.020)+body*vec3(.39,.37,.35);
	ALBEDO=mix(binder,fresh,repair*.88);
	NORMAL_MAP=texture(tar_normal,st).rgb;NORMAL_MAP_DEPTH=mix(.55,.38,repair);
	ROUGHNESS=clamp(.70+.21*texture(tar_rough,st).r-.12*abraded-.035*repair,.58,.94);
	SPECULAR=.24;
}


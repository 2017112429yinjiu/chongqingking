shader_type spatial;
#include "res://shaders/terrace_paving_r24.gdshaderinc"
uniform sampler2D stone : source_color,repeat_enable,filter_linear_mipmap_anisotropic;

varying vec3 world;
varying vec3 wn;
void vertex(){world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;wn=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
	ALBEDO=vec3(.12);
	ROUGHNESS=.84;
	terrace_finish(world,stone,1.,ALBEDO,ROUGHNESS);
	NORMAL=terrace_light(world,normalize(wn),mat3(VIEW_MATRIX),NORMAL);
	SPECULAR=.21;
	NORMAL_MAP=vec3(.5,.5,1.);
	NORMAL_MAP_DEPTH=0.;
}

shader_type spatial;
render_mode cull_disabled;
uniform sampler2D aggregate : source_color,filter_linear_mipmap_anisotropic,repeat_enable,hint_default_white;
varying vec3 p;
varying vec3 n;
#include "res://shaders/street_use_r24.gdshaderinc"
#include "res://shaders/street_repairs_r24.gdshaderinc"
void vertex(){p=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;n=MODEL_NORMAL_MATRIX*NORMAL;}
void fragment(){
	float h=abs(n.x)>abs(n.z)?p.z:p.x;
	vec2 uv=abs(normalize(n).y)>.62?p.xz*.45:vec2(h,p.y)*.41;
	vec3 stone=texture(aggregate,uv).rgb;
	ALBEDO=(vec3(.032,.028,.024)+stone*vec3(.65,.62,.56))*(.94+.06*sin(h*.81+sin(p.y*2.5)));
	ROUGHNESS=.94;SPECULAR=.17;
 finish_paving(p,normalize(n),ALBEDO,ROUGHNESS);
 street_repair(p,normalize(n),ALBEDO,ROUGHNESS);
}

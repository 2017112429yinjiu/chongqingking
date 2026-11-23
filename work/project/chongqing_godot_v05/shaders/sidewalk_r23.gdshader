shader_type spatial;
render_mode diffuse_burley;
uniform sampler2D surface:source_color,filter_linear_mipmap_anisotropic,repeat_enable;
uniform sampler2D relief:hint_normal,filter_linear_mipmap_anisotropic,repeat_enable;
float h(vec2 p){return fract(sin(dot(p,vec2(31.51,77.93)))*4298.3);}
float noise2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+1.),f.x),f.y);}
#include "res://shaders/street_use_r24.gdshaderinc"
#include "res://shaders/street_repairs_r24.gdshaderinc"
varying vec3 use_world;
varying vec3 use_normal;
void vertex(){use_world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;use_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
	vec2 uv=UV;float course=floor(uv.y/1.10);float station=uv.x+course*.68;
	vec2 tile=vec2(station/1.37,uv.y/1.1);
	vec2 gap=(.5-abs(fract(tile)-.5))*vec2(1.37,1.1);
	float joint=1.-smoothstep(.006,.019,min(gap.x,gap.y));
	float seed=h(floor(tile));vec2 st=uv/3.4+seed*.72;
	vec3 stone=texture(surface,st).rgb;
	float patch=noise2(uv*vec2(.49,1.21));
	float gutter=(1.-smoothstep(.08,.46,uv.y+.11*(patch-.5)))*(.4+.6*patch);
	float moss=joint*(.4+.6*patch)*smoothstep(.48,.72,patch);
	ALBEDO=stone*mix(.62,.87,seed)*mix(.87,1.04,patch)*mix(vec3(1.),vec3(.60,.62,.53),gutter);
	ALBEDO*=mix(vec3(1.),vec3(.51,.50,.44),joint);
	ALBEDO=mix(ALBEDO,vec3(.075,.086,.052),moss*.33);
	NORMAL_MAP=texture(relief,st).rgb;NORMAL_MAP_DEPTH=.53;ROUGHNESS=.91-gutter*.20;SPECULAR=.19;
 finish_paving(use_world,use_normal,ALBEDO,ROUGHNESS);
 street_repair(use_world,use_normal,ALBEDO,ROUGHNESS);
}

shader_type spatial;
render_mode diffuse_burley,specular_schlick_ggx;
#include "res://shaders/sky_visibility_r20.gdshaderinc"
uniform sampler2D worn_floor : source_color, filter_linear_mipmap_anisotropic,repeat_enable;
uniform sampler2D floor_normal : hint_normal,filter_linear_mipmap_anisotropic,repeat_enable;
uniform bool stairs=false;
varying vec3 world;
varying vec3 wn;
float h(vec2 i){return fract(sin(dot(i,vec2(127.1,311.7)))*43758.5453);}
#include "res://shaders/street_use_r24.gdshaderinc"
#include "res://shaders/street_repairs_r24.gdshaderinc"
void vertex(){world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;wn=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
	vec3 n=normalize(wn);
	vec2 p=world.xz;
	float horizontal=smoothstep(.48,.78,abs(n.y));
	vec2 side=abs(n.x)>abs(n.z)?vec2(world.z,world.y):vec2(world.x,world.y);
	vec2 metre=mix(side,p,horizontal);
	vec2 uv=metre/2.8;
	float row=floor(metre.y/.61);
	vec2 dims=vec2(.95,.61);
	vec2 grid=metre/dims+vec2(.5*mod(row,2.),0.);
	vec2 cell=floor(grid);vec2 edge=min(fract(grid),1.-fract(grid))*dims;
	float footprint=max(.001,max(fwidth(metre.x),fwidth(metre.y)));
	float joint=stairs?0.:1.-smoothstep(.002-footprint*.4,.005+footprint*.4,min(edge.x,edge.y));
	joint*=1.-smoothstep(.024,.13,footprint);
	float variation=stairs?mix(.96,1.03,h(vec2(floor(world.y*5.6),0.))):mix(.945,1.047,h(cell));
	vec2 offset=stairs?vec2(0.):vec2(h(cell+31.),h(cell+56.))*.27;
	vec4 tex=textureGrad(worn_floor,uv+offset,dFdx(uv),dFdy(uv));
	float tone=dot(tex.rgb,vec3(.25,.55,.20));
	vec3 slab=mix(vec3(tone),tex.rgb,.44)*vec3(.91,.96,.98)*variation;
	ALBEDO=slab*mix(.67,1.,horizontal)*mix(1.,.38,joint);
	ROUGHNESS=mix(.77,.94,joint);
	SPECULAR=.26;
	finish_paving(world,n,ALBEDO,ROUGHNESS);
	NORMAL_MAP=textureGrad(floor_normal,uv+offset,dFdx(uv),dFdy(uv)).rgb;
	NORMAL_MAP_DEPTH=stairs?.52:.46;
	vec3 q=world+n*.18;vec3 point=vec3(q.x,-q.z,q.y);
	AO=sky_field(point,vec3(-35,-74,10),vec3(35,42,15),shop_sky)*sky_field(point,vec3(-42,37,24),vec3(35,50,16),alley_sky);
 street_repair(world,n,ALBEDO,ROUGHNESS);
}

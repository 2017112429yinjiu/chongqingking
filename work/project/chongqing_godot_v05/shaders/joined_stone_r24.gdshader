shader_type spatial;
render_mode cull_disabled,diffuse_burley,specular_schlick_ggx;
uniform sampler2D stone : source_color,repeat_enable,filter_linear_mipmap_anisotropic;
uniform sampler2D grain : hint_normal,repeat_enable,filter_linear_mipmap_anisotropic;
#include "res://shaders/district_courses_r24.gdshaderinc"
#include "res://shaders/terrace_paving_r24.gdshaderinc"
uniform bool east_shoulder=false;
uniform bool yard_paving=false;
uniform bool tread=false;
varying vec3 world;
varying vec3 surface_normal;
void vertex(){
	world=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
	surface_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment(){
	vec2 tex=UV*0.53;
	float scan=dot(texture(stone,tex).rgb,vec3(.27,.56,.17));
	vec2 metres=vec2(UV2.x,1.-UV2.y);
	float course=tread ? floor(world.y*5.93) : floor(metres.y/.69);
	vec2 brick=tread ? vec2(1.12,.88) : vec2(.87,.69);
	vec2 grid=metres/brick;
	grid.x+=.5*mod(course,2.);
	vec2 seam=abs(fract(grid+.5)-.5)*brick;
	float dist=min(seam.x,seam.y);
	float filter_size=max(.0005,min(.02,fwidth(dist)*.48));
	float joint=(1.-smoothstep(.003-filter_size,.008+filter_size,dist))*smoothstep(.65,.93,surface_normal.y);
	float variation=fract(sin(dot(floor(grid),vec2(39.7,13.1)))*1743.33);
	float wear=tread ? (1.-smoothstep(.012,.062,abs(metres.y)))*smoothstep(.65,.93,surface_normal.y) : 0.;
	vec3 shade=tread ? vec3(.56,.517,.442) : vec3(.61,.585,.52);
	vec3 face=(vec3(.024,.023,.021)+scan*shade)*(.92+.14*variation)*(1.+wear*.07);
	ALBEDO=mix(face,vec3(.044,.039,.032),joint*.78);
	ROUGHNESS=.87;
	if(yard_paving){yard_courses(world,normalize(surface_normal),stone,1.,ALBEDO,ROUGHNESS);}
	if(east_shoulder){NORMAL=shoulder_lighting(world,normalize(surface_normal),mat3(VIEW_MATRIX),NORMAL);yard_courses(world,normalize(surface_normal),stone,fork_course_weight(world.xz),ALBEDO,ROUGHNESS);}
	if(east_shoulder){NORMAL=terrace_light(world,normalize(surface_normal),mat3(VIEW_MATRIX),NORMAL);terrace_finish(world,stone,residential_terrace(world)*smoothstep(.72,.90,surface_normal.y),ALBEDO,ROUGHNESS);}
	SPECULAR=.21;
	NORMAL_MAP=texture(grain,tex).rgb;
	NORMAL_MAP_DEPTH=.19;
	if(east_shoulder){float weight=residential_terrace(world)*smoothstep(.72,.90,surface_normal.y);NORMAL_MAP=mix(NORMAL_MAP,vec3(.5,.5,1.),weight);NORMAL_MAP_DEPTH*=1.-weight;}
}

#include "res://shaders/district_courses_r24.gdshaderinc"
uniform sampler2D repair_aggregate : source_color,repeat_enable,filter_linear_mipmap_anisotropic;
uniform sampler2D support_heights : filter_linear, repeat_disable;
uniform sampler2D courtyard_wear : hint_default_black, repeat_disable, filter_linear_mipmap;
uniform sampler2D district_footpaths : hint_default_black, repeat_disable, filter_linear_mipmap;
uniform bool residential_age = false;
uniform int repair_site = 0;
uniform bool use_wall_toe = false;
float patch_box(vec2 point,vec2 half_extent,float erosion){
	vec2 q=abs(point)-half_extent;
	float d=length(max(q,0.))+min(max(q.x,q.y),0.)+erosion;
	return 1.-smoothstep(-.012,.012+fwidth(d)*.60,d);
}
void street_repair(vec3 loc,vec3 surface_normal,inout vec3 pigment,inout float gloss){
	if(repair_site==2 && surface_normal.y>.72){
		float passage = texture(district_footpaths,(loc.xz+100.)/200.).r;
		yard_courses(loc,surface_normal,repair_aggregate,max(passage,fork_course_weight(loc.xz)),pigment,gloss);
		pigment *= mix(vec3(1.),vec3(.95,.94,.92),passage);
		gloss = mix(gloss,.72,passage*.58);
	}
	if(repair_site==2 && surface_normal.y>.72 && loc.x>-78. && loc.x< -14. && loc.z>5. && loc.z<37.){
		float traffic=texture(courtyard_wear,(loc.xz-vec2(-78.,5.))/vec2(64.,32.)).r;
		// Use the same slab courses across the two legacy terrain material batches.
		vec2 fade=smoothstep(vec2(-51.,16.9),vec2(-49.,18.),loc.xz)*(1.-smoothstep(vec2(-22.,23.2),vec2(-20.,24.6),loc.xz));
		vec2 metre=loc.xz, size=vec2(1.04,.64);
		vec2 grid=metre/size+vec2(.5*mod(floor(metre.y/size.y),2.),0.);
		vec2 edge=min(fract(grid),1.-fract(grid))*size;
		vec2 pixel=max(fwidth(metre),vec2(.001));
		vec2 mortar=clamp((vec2(.0025)+pixel*.5-edge)/pixel,vec2(0.),vec2(1.))*min(vec2(1.),vec2(.005)/pixel);
		float joint=max(mortar.x,mortar.y);
		vec3 scan=texture(repair_aggregate,metre*.46).rgb;
		vec3 stone=mix(vec3(dot(scan,vec3(.28,.55,.17))),scan,.52)*vec3(.90,.89,.83);
		pigment=mix(pigment,stone*mix(1.,.67,joint),fade.x*fade.y);
		pigment*=mix(vec3(1.),vec3(.90,.89,.86),traffic*.64);
		gloss=mix(gloss,.81-.07*traffic,fade.x*fade.y);
	}
	if(repair_site != 0 && surface_normal.y>.68 && loc.x>-43. && loc.x< -10. && loc.z>71. && loc.z<82.){
		vec2 coord=loc.xz;
		vec3 stone=texture(repair_aggregate,coord*.65).rgb;
		float grain=dot(stone,vec3(.3,.52,.18));
		float offset=(stone.r-.22)*.12+.011*sin(coord.x*7.+coord.y*13.);
		// Narrow filled service trench and a hand-trowelled apron repair at the edge of the stand.
		vec2 trench=coord-vec2(-36.90,79.06);
		trench=vec2(trench.x+trench.y*.20,trench.y-trench.x*.20);
		float fill=repair_site==1 ? patch_box(trench,vec2(.32,1.26),offset) : 0.;
		vec2 apron=coord-vec2(-28.39,75.63);
		apron.y+=apron.x*.18;
		float mortar=repair_site==2 ? patch_box(apron,vec2(.76,.22),offset*2.6) : 0.;
		pigment=mix(pigment,vec3(.058,.057,.050)+grain*vec3(.48,.45,.36),fill*.95);
		pigment=mix(pigment,vec3(.051,.047,.039)+grain*vec3(.51,.47,.41),mortar*.63);
		gloss=mix(gloss,.87,max(fill,mortar)*.73);
	}
}
void stain_plaster(float height,float coarse,float fine_grain,inout vec3 pigment,inout float gloss){
	if(use_wall_toe && height>-.38 && height<1.56){
		float damp=(1.-smoothstep(.10,.64+coarse*.90,height))*smoothstep(-.38,.02,height);
		float effect=damp*(.32+.46*smoothstep(.22,.68,fine_grain));
		pigment=mix(pigment,pigment*vec3(.56,.60,.46),effect);
		gloss=mix(gloss,.73,effect);
	}
}

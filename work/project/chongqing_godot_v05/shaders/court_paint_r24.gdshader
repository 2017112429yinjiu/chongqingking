shader_type spatial;
render_mode diffuse_burley;
uniform sampler2D concrete : source_color,filter_linear_mipmap_anisotropic,repeat_enable;
varying vec3 world;
varying vec3 surface_normal;
void vertex(){
	world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
	surface_normal=MODEL_NORMAL_MATRIX*NORMAL;
}
float line_segment(vec2 p,vec2 a,vec2 b){
	vec2 edge=b-a;
	return length(p-a-edge*clamp(dot(p-a,edge)/dot(edge,edge),0.,1.));
}
void fragment(){
	vec2 p=abs(world.xz-vec2(-34.,0.));
	float scan=dot(texture(concrete,world.xz*.43).rgb,vec3(.28,.54,.18));
	vec3 pigment=vec3(.21,.205,.185);
	if(surface_normal.y>.8 && p.x<=10. && p.y<=14.){
		pigment=vec3(.137,.262,.234);
		if(p.x<2.45 && p.y>=7.3 && p.y<13.)pigment=vec3(.46,.227,.161);
		float d=min(line_segment(p,vec2(7.5,0.),vec2(7.5,13.)),line_segment(p,vec2(0.,13.),vec2(7.5,13.)));
		d=min(d,line_segment(p,vec2(0.,0.),vec2(7.5,0.)));
		d=min(d,abs(length(p)-1.8));
		d=min(d,abs(length(p-vec2(0.,7.3))-1.8));
		d=min(d,line_segment(p,vec2(0.,7.3),vec2(2.45,7.3)));
		d=min(d,line_segment(p,vec2(2.45,7.3),vec2(2.45,13.)));
		d=min(d,p.y<=10.9 ? abs(length(p-vec2(0.,10.9))-6.5) : line_segment(p,vec2(6.5,10.9),vec2(6.5,13.)));
		float aa=max(.001,fwidth(d)*.7);
		pigment=mix(pigment,vec3(.82,.82,.73),(1.-smoothstep(.025-aa,.025+aa,d))*.95);
	}
	ALBEDO=pigment*(.62+1.18*scan);
	ROUGHNESS=.91;
	SPECULAR=.16;
}

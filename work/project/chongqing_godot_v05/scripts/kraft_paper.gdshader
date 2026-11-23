shader_type spatial;
render_mode cull_disabled;
uniform vec4 kraft : source_color = vec4(0.60,0.455,0.30,1.0);
varying vec3 local_pos;

float hash21(vec2 p) {
	vec3 a=fract(vec3(p.xyx)*vec3(.1031,.1030,.0973));
	a+=dot(a,a.yzx+33.33);
	return fract((a.x+a.y)*a.z);
}
float paper_noise(vec2 p) {
	vec2 cell=floor(p);
	vec2 u=fract(p);
	u=u*u*(3.0-2.0*u);
	return mix(mix(hash21(cell),hash21(cell+vec2(1,0)),u.x),mix(hash21(cell+vec2(0,1)),hash21(cell+vec2(1,1)),u.x),u.y);
}
void vertex(){local_pos=VERTEX;}
void fragment(){
	vec2 p=vec2(local_pos.x+local_pos.z*.69,local_pos.y);
	float grain=(paper_noise(p*vec2(1150.,720.))-.5)*(1.-smoothstep(.0007,.0025,length(fwidth(p))));
	float pulp=paper_noise(p*vec2(87.,45.))-.5;
	float bottom_fold=1.-smoothstep(.0007,.0027,abs(local_pos.y-.034-.26*abs(local_pos.x)));
	float rim_fold=1.-smoothstep(.0006,.0021,abs(local_pos.y-.231));
	ALBEDO=kraft.rgb*(1.+.085*grain+.085*pulp-.095*bottom_fold-.075*rim_fold);
	ROUGHNESS=.91;
	SPECULAR=.22;
}
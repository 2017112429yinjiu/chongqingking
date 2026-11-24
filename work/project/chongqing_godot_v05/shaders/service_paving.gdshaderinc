// A shared stone finish on the graded hardscape around the community service station.
void service_finish(vec3 p,vec3 n,sampler2D photo,inout vec3 colour,inout float roughness){
	vec2 lo=smoothstep(vec2(-13.,-29.),vec2(-8.,-24.),p.xz);
	vec2 hi=1.-smoothstep(vec2(27.,-2.),vec2(32.,3.),p.xz);
	float w=lo.x*lo.y*hi.x*hi.y*smoothstep(.58,.85,n.y);
	if(w<.001)return;
	vec2 meter=p.xz;
	vec2 grid=meter/vec2(.91,.62);
	grid.x+=.5*mod(floor(grid.y),2.);
	vec2 joint=min(fract(grid),1.-fract(grid))*vec2(.91,.62);
	float edge=min(joint.x,joint.y);
	float aa=clamp(fwidth(edge)*.6,.001,.02);
	float mortar=1.-smoothstep(.004-aa,.004+aa,edge);
	vec3 mineral=texture(photo,meter*.41).rgb;
	float stone=dot(mineral,vec3(.26,.56,.18));
	vec3 skin=mix(vec3(.125,.121,.109)+stone*vec3(.42,.405,.368),vec3(.083,.081,.074),mortar*.65);
	colour=mix(colour,skin,w);
	roughness=mix(roughness,.90,w);
}

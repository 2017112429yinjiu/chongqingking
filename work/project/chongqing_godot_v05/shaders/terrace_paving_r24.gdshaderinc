// The two historic concrete batches and the replacement use the same metre grid.
// The mask ends beyond the resurfaced perimeter, leaving other street finishes intact.
float residential_terrace(vec3 p){
	vec2 lo=smoothstep(vec2(24.,39.),vec2(32.,45.),p.xz);
	vec2 hi=1.-smoothstep(vec2(77.,81.),vec2(89.,86.),p.xz);
	return lo.x*lo.y*hi.x*hi.y;
}
uniform sampler2D terrace_normals : filter_linear, repeat_disable;
uniform sampler2D terrace_grit : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
vec3 terrace_light(vec3 p,vec3 original,mat3 view_basis,vec3 current){
	float region=residential_terrace(p)*smoothstep(.68,.91,original.y);
	if(region<.001){return current;}
	vec2 pixel=((p.xz-vec2(24.,34.))*4.+.5)/vec2(273.,209.);
	vec4 sample_n=texture(terrace_normals,pixel);
	float w=sample_n.a*region;
	vec3 fitted=normalize(sample_n.rgb*2.-1.);
	vec2 terrace_pores=texture(terrace_grit,p.xz*.52).rg*2.-1.;
	vec3 along=normalize(vec3(1.,-fitted.x/max(fitted.y,.2),0.));
	vec3 across=normalize(cross(along,fitted));
	vec3 pore=normalize(fitted+.18*(terrace_pores.x*along+terrace_pores.y*across));
	return normalize(mix(current,view_basis*pore,w));
}
void terrace_finish(vec3 p,sampler2D terrace_photo,float weight,inout vec3 colour,inout float rough){
	if(weight<.001){return;}
	vec2 metre=p.xz;
	vec2 size=vec2(.91,.63);
	vec2 course=metre/size;
	course.x+=.5*mod(floor(course.y),2.);
	vec2 id=floor(course);
	float seed=fract(sin(dot(id,vec2(27.31,41.17)))*4836.77);
	vec2 uv=metre*.52;
	vec3 scan=texture(terrace_photo,uv+vec2(seed*.37,seed*.18)).rgb;
	float tone=dot(scan,vec3(.28,.55,.17));
	float patina=dot(texture(terrace_photo,metre*.103+vec2(.71,.28)).rgb,vec3(.28,.55,.17));
	vec3 old_slab=(vec3(.016,.016,.014)+mix(vec3(tone),scan,.36)*vec3(.65,.624,.577))*(.956+.074*seed);
	old_slab*=.93+.32*patina;
	vec2 edge=min(fract(course),1.-fract(course))*size;
	vec2 px=max(fwidth(metre),vec2(.001));
	vec2 seam=clamp((.0032+px*.45-edge)/px,vec2(0.),vec2(1.))*min(vec2(1.),vec2(.0064)/px);
	colour=mix(colour,mix(old_slab,vec3(.043,.04,.035),.7*max(seam.x,seam.y)),weight);
	rough=mix(rough,.84,weight);
}

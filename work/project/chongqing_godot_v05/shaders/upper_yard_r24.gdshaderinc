uniform sampler2D upper_yard_normals : repeat_disable, filter_linear;
float yard_extent(vec2 p,vec2 lo,vec2 hi){
	vec2 a=smoothstep(lo,lo+vec2(5.),p);
	vec2 b=1.-smoothstep(hi-vec2(5.),hi,p);
	return a.x*a.y*b.x*b.y;
}
float upper_yard(vec2 p){
	float school=yard_extent(p,vec2(-38.,-94.),vec2(57.,-46.));
	float east=yard_extent(p,vec2(22.,-43.),vec2(62.,20.));
	float central=yard_extent(p,vec2(-37.,-35.),vec2(-5.,1.));
	return max(school,max(east,central));
}
// Minor secondary paths retain their material map. Their surrounding concrete changes
// with foot traffic and runoff while staying continuous across the inherited triangle batches.
void upper_yard_finish(vec3 p,vec3 upper_surface_n,mat3 vr,float weight,sampler2D aggregate,sampler2D lane_mask,
	inout vec3 pigment,inout float rough,inout vec3 view_n){
	if(weight<.001){return;}
	vec4 normal_field=texture(upper_yard_normals,((p.xz-vec2(-43.,-96.))*2.+.5)/vec2(217.,249.));
	vec3 fitted=normalize(2.*normal_field.rgb-1.);
	view_n=normalize(mix(view_n,vr*fitted,weight*normal_field.a));
	float use=texture(lane_mask,(p.xz+100.)/200.).r;
	vec3 grains=texture(aggregate,p.xz*.49).rgb;
	float broad=dot(texture(aggregate,p.xz*.083+vec2(.11,.43)).rgb,vec3(.28,.55,.17));
	vec2 panel=fract(p.xz/vec2(2.7,2.35));
	vec2 dst=min(panel,1.-panel)*vec2(2.7,2.35);
	vec2 px=max(fwidth(p.xz),vec2(.001));
	vec2 edge=clamp((.003+px*.5-dst)/px,vec2(0.),vec2(1.))*min(vec2(1.),vec2(.006)/px);
	vec3 yard=(vec3(.016,.014,.012)+grains*vec3(.66,.63,.58))*(.92+.43*broad)*(1.-.26*max(edge.x,edge.y));
	float finish_r=.88;
	terrace_finish(p,aggregate,smoothstep(.06,.62,use),yard,finish_r);
	finish_paving(p,upper_surface_n,yard,finish_r);
	pigment=mix(pigment,yard,weight);
	rough=mix(rough,finish_r,weight);
}

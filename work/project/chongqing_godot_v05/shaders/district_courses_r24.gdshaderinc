uniform sampler2D shoulder_gradient : repeat_disable, filter_linear;
vec3 shoulder_lighting(vec3 pos,vec3 original,mat3 view_rotation,vec3 view_normal){
	vec2 uv=(pos.xz-vec2(30.,60.))/vec2(36.,24.);
	vec2 lo=smoothstep(vec2(.035,.04),vec2(.23,.20),uv);
	vec2 hi=1.-smoothstep(vec2(.76,.78),vec2(.975,.96),uv);
	float weight=lo.x*lo.y*hi.x*hi.y*smoothstep(.69,.86,original.y);
	if(weight<.001){return view_normal;}
	vec2 tc=(uv*vec2(192.,128.)+.5)/vec2(193.,129.);
	vec3 fitted=normalize(texture(shoulder_gradient,tc).rgb*2.-1.);
	return normalize(mix(view_normal,view_rotation*fitted,weight));
}
// Shared world-space stone courses where the footpath crosses an old material boundary.
void yard_courses(vec3 yc_loc,vec3 course_normal,sampler2D course_photo,float yc_amount,inout vec3 yc_colour,inout float yc_roughness){
	if(yc_amount<.004 || course_normal.y<.58){return;}
	vec2 yc_p=yc_loc.xz;
	vec2 yc_size=vec2(.91,.63);
	vec2 yc_course=yc_p/yc_size;
	yc_course.x+=.5*mod(floor(yc_course.y),2.);
	vec2 yc_cell=floor(yc_course);
	float yc_variation=fract(sin(dot(yc_cell,vec2(27.31,41.17)))*4836.77);
	vec2 yc_f=min(fract(yc_course),1.-fract(yc_course))*yc_size;
	vec2 yc_pixels=max(fwidth(yc_p),vec2(.001));
	vec2 yc_edge=clamp((.003+yc_pixels*.5-yc_f)/yc_pixels,vec2(0.),vec2(1.))*min(vec2(1.),vec2(.006)/yc_pixels);
	float yc_sc=dot(texture(course_photo,yc_p*.48+vec2(yc_variation*.21)).rgb,vec3(.28,.55,.17));
	vec3 yc_stone_color=(vec3(.022,.021,.019)+vec3(.64,.62,.575)*yc_sc)*(.94+.09*yc_variation);
	yc_colour=mix(yc_colour,mix(yc_stone_color,vec3(.047,.043,.036),max(yc_edge.x,yc_edge.y)*.68),yc_amount);
	yc_roughness=mix(yc_roughness,.84,yc_amount);
}
float fork_course_weight(vec2 yc_p){
	vec2 yc_a=smoothstep(vec2(36.,65.),vec2(41.,69.),yc_p);
	vec2 yc_b=1.-smoothstep(vec2(53.,77.3),vec2(60.,79.),yc_p);
	return yc_a.x*yc_a.y*yc_b.x*yc_b.y;
}

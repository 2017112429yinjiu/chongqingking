shader_type spatial;
render_mode diffuse_burley,specular_schlick_ggx;
uniform sampler2D cement:source_color,filter_linear_mipmap_anisotropic,repeat_enable;
uniform sampler2D grain:hint_normal,filter_linear_mipmap_anisotropic,repeat_enable;
uniform bool landing=false;
varying vec3 world;
void vertex(){world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
void fragment(){
	vec2 axis=normalize(vec2(.224,-.974));
	vec2 mat_uv=world.xz*vec2(.53,.51)+vec2(.75,.14);
	vec2 p=vec2(dot(world.xz,vec2(-axis.y,axis.x)),dot(world.xz,axis));
	vec2 slab=landing?vec2(1.03,.78):vec2(.80,.54);
	p/=slab;
	p.x+=mod(floor(p.y),2.)*.5;
	vec2 center=abs(fract(p+.5)-.5)*slab;
	float groove=min(center.x,center.y);
	float filter_width=max(.0008,max(fwidth(p.x)*slab.x,fwidth(p.y)*slab.y)*.56);
	float seam=1.-smoothstep(.002-filter_width,.0055+filter_width,groove);
	vec2 cell=floor(p);
	float variation=fract(sin(dot(cell,vec2(56.7,11.9)))*1534.61);
	float raw=dot(texture(cement,mat_uv).rgb,vec3(.29,.54,.17));
	vec3 color=(vec3(.041,.040,.036)+raw*vec3(.78,.75,.68))*(.95+.09*variation);
	ALBEDO=mix(color,vec3(.038,.035,.029),seam*.85);
	ROUGHNESS=.87+.035*variation;
	SPECULAR=.22;
	NORMAL_MAP=texture(grain,mat_uv).rgb;
	NORMAL_MAP_DEPTH=.24;
}

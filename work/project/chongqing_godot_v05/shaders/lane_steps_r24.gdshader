shader_type spatial;
render_mode diffuse_burley,specular_schlick_ggx;
uniform sampler2D stone:source_color,repeat_enable,filter_linear_mipmap_anisotropic;
uniform sampler2D rough:repeat_enable,filter_linear_mipmap_anisotropic;
uniform sampler2D grain:hint_normal,repeat_enable,filter_linear_mipmap_anisotropic;
varying vec3 world_normal;
varying vec3 world_pos;

void vertex(){
	world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
	world_pos=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
}
void fragment(){
	float top=smoothstep(.55,.9,world_normal.y);
	float course=floor((world_pos.y-23.5055+.007)/.169265);
	float along=UV2.x+mod(course,2.)*.27;
	float seam_dist=min(abs(along-.76),abs(along-1.68));
	float width=max(fwidth(along)*.60,.0008);
	float seam=1.-smoothstep(.002-width,.004+width,seam_dist);
	float aggregate=dot(texture(stone,UV).rgb,vec3(.28,.54,.18));
	vec3 tone=vec3(.019,.018,.016)+aggregate*vec3(.47,.45,.405);
	float edge=(1.-smoothstep(.008,.071,abs(UV2.y)))*top;
	ALBEDO=tone*mix(.87,1.,top)*(1.+.12*edge)*(1.-.30*seam);
	ROUGHNESS=clamp(.76+.14*texture(rough,UV).r-.1*edge,.57,.94);
	SPECULAR=.22;
	NORMAL_MAP=texture(grain,UV).rgb;
	NORMAL_MAP_DEPTH=.20;
}

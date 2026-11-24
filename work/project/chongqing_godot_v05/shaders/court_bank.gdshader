shader_type spatial;
render_mode diffuse_burley;
uniform sampler2D mineral : source_color,filter_linear_mipmap_anisotropic,repeat_enable;
varying vec3 world;
void vertex(){world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
void fragment(){
	bool across=world.z>14.86 && world.x>-45.98 && world.x<-22.06;
	float along=across?world.x:world.z;
	float crossway=across?world.z:world.x;
	vec2 uv=vec2(along,world.y*1.35+crossway*.06);
	vec3 grain=texture(mineral,uv*vec2(.41,.43)).rgb;
	ALBEDO=grain*vec3(.77,.73,.67);
	ROUGHNESS=.89;
}

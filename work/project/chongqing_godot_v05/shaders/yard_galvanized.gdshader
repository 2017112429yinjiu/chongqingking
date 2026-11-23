shader_type spatial;
render_mode diffuse_burley,specular_schlick_ggx;
uniform sampler2D paint_scan : source_color,repeat_enable,filter_linear_mipmap_anisotropic;
uniform vec4 coat : source_color;
varying vec3 world;
varying vec3 wn;
void vertex(){
	world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
	wn=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment(){
	vec3 n=abs(normalize(wn));
	vec2 m=n.y>.6?world.xz:(n.x>n.z?world.zy:world.xy);
	vec3 scan=texture(paint_scan,m*vec2(.56,.81)).rgb;
	float grain=dot(scan,vec3(.3,.51,.19));
	float rust=smoothstep(.048,.17,scan.r-scan.b)*smoothstep(.023,.16,scan.r);
	ALBEDO=mix(coat.rgb*(.76+grain*.70),vec3(.135,.069,.039),rust*.48);
	ROUGHNESS=mix(.64,.92,rust);
	METALLIC=mix(.62,.15,rust);
	SPECULAR=.37;
}

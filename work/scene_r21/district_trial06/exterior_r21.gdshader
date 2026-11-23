shader_type spatial;
render_mode diffuse_burley;
uniform sampler2D land : filter_linear_mipmap,repeat_disable;
uniform sampler2D earth : source_color,filter_linear_mipmap_anisotropic,repeat_enable;
uniform sampler2D paving : source_color,filter_linear_mipmap_anisotropic,repeat_enable;
varying vec2 xy;
void vertex(){vec3 p=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;xy=vec2(p.x,-p.z);}
void fragment(){
	vec3 m=texture(land,(xy+360.)/720.).rgb;
	vec3 dirt=texture(earth,xy/4.3).rgb;
	vec3 grit=texture(paving,xy/5.1).rgb;
	float broad=sin(xy.x*.065+sin(xy.y*.04)*2.5)*sin(xy.y*.036+xy.x*.017);
	vec3 slope=mix(vec3(.115,.109,.071),vec3(.119,.145,.086),.52+.39*broad);
	slope*=.70+dot(dirt,vec3(.30,.48,.22))*.76;
	vec3 court=mix(vec3(.14,.138,.119),grit,.27);
	ALBEDO=mix(mix(slope,court,m.r),vec3(.084,.087,.084),m.g);
	ALBEDO*=1.-m.b*.30;
	ROUGHNESS=.90;SPECULAR=.18;
}

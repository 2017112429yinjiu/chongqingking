shader_type spatial;
render_mode diffuse_burley;
uniform sampler2D surface:source_color,repeat_enable,filter_linear_mipmap_anisotropic;
uniform bool stone=false;
uniform bool viaduct=false;
varying vec3 p;
varying vec3 n;
void vertex(){p=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;n=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
	vec3 normal=abs(normalize(n));
	vec2 uv=normal.y>.59?p.xz:(normal.x>normal.z?p.zy:p.xy);
	vec3 tex=texture(surface,uv*(stone?vec2(.47,.47):vec2(.73,1.19))).rgb;
	ALBEDO=tex*(stone?vec3(.86,.84,.79):vec3(.80,.70,.53));
	if(viaduct){
		float s=p.x*.98-p.z*.16;
		float joint=smoothstep(.055,.105,abs(fract(s/9.2)*2.-1.));
		float drain=smoothstep(.81,.97,sin(s*2.17+.49*sin(s*.81)))*smoothstep(.55,1.,sin(s*.47))*(1.-normal.y);
		ALBEDO=mix(tex*.76,vec3(.24,.225,.20),.37)*(.88+.12*joint)*(1.-.21*drain);
	}
	ROUGHNESS=stone?.9:.79;SPECULAR=.22;
}

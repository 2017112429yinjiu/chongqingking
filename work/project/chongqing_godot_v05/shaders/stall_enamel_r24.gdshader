shader_type spatial;
uniform vec4 tint:source_color=vec4(.31,.39,.34,1.);
varying vec3 p;varying vec3 n;
void vertex(){p=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;n=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
float hash(vec2 x){return fract(sin(dot(x,vec2(53.71,29.97)))*29431.6);}
float grain(vec2 x){vec2 i=floor(x),f=fract(x);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
void fragment(){
	vec2 uv=abs(n.y)>.7?p.xz:vec2(abs(n.z)>.6?p.x:p.z,p.y);
	float chalk=grain(uv*vec2(4.7,3.1)), streak=grain(uv*vec2(17.,.91));
	float chip=smoothstep(.75,.86,grain(uv*vec2(61.,42.)))*smoothstep(.57,.83,streak);
	vec3 paint=tint.rgb*(.80+.22*chalk+.05*streak);
	paint=mix(paint,vec3(.158,.092,.046),chip*.88);
	ALBEDO=paint;METALLIC=.23*(1.-chip);ROUGHNESS=.72+.19*chalk;SPECULAR=.29;
}

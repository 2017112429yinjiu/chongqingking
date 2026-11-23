shader_type spatial;
varying vec3 point;
varying vec3 n;
void vertex(){point=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;n=MODEL_NORMAL_MATRIX*NORMAL;}
float hash(vec2 p){return fract(sin(dot(p,vec2(16.19,85.21)))*4321.53);}
float fb(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
void fragment(){
	vec2 uv=abs(n.y)>.65?point.xz:vec2(point.y,point.x+point.z);
	float fibres=fb(uv*vec2(5.,208.)+vec2(0.,fb(uv*4.)*2.3));
	float wear=fb(uv*vec2(7.,12.));
	vec3 wood=mix(vec3(.126,.079,.040),vec3(.284,.203,.115),fibres);
	ALBEDO=mix(wood,vec3(.258,.228,.184),.27*smoothstep(.42,.74,wear));
	ROUGHNESS=.71+.16*wear;SPECULAR=.23;
}

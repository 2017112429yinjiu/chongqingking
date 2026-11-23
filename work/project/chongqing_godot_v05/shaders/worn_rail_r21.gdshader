shader_type spatial;
render_mode diffuse_burley,specular_schlick_ggx;
varying vec3 p;
varying vec3 n;
float rnd(vec3 a){return fract(sin(dot(a,vec3(17.23,37.71,81.51)))*24713.47);}
float noise3(vec3 a){
	vec3 f=fract(a);vec3 i=floor(a);f=f*f*(3.-2.*f);
	return mix(mix(mix(rnd(i),rnd(i+vec3(1,0,0)),f.x),mix(rnd(i+vec3(0,1,0)),rnd(i+vec3(1,1,0)),f.x),f.y),
	           mix(mix(rnd(i+vec3(0,0,1)),rnd(i+vec3(1,0,1)),f.x),mix(rnd(i+vec3(0,1,1)),rnd(i+vec3(1,1,1)),f.x),f.y),f.z);
}
void vertex(){p=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;n=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
	float coat=noise3(p*vec3(.72,3.,.72));
	float patch=noise3(p*14.3);
	float detail=noise3(p*82.1);
	float near_sample=1.-smoothstep(.004,.035,length(fwidth(p)));
	float nick=smoothstep(.65,.79,.64*patch+.36*detail)*near_sample;
	float polished=smoothstep(.36,.94,n.y)*smoothstep(.44,.68,coat+patch*.17);
	vec3 paint=mix(vec3(.103,.045,.029),vec3(.245,.090,.051),coat);
	ALBEDO=mix(mix(paint,vec3(.091,.057,.036),nick),vec3(.27,.24,.19),polished*.59);
	ROUGHNESS=mix(.75,.40,polished);METALLIC=.24+.29*polished;SPECULAR=.37;
}

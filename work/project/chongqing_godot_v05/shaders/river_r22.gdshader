shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_schlick_ggx;
varying vec2 water_position;
float hash2(vec2 i) { return fract(sin(dot(i,vec2(127.1,311.7)))*43758.5453); }
float noise2(vec2 p) {
	vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
	return mix(mix(hash2(i),hash2(i+vec2(1,0)),f.x),mix(hash2(i+vec2(0,1)),hash2(i+1.),f.x),f.y);
}
void vertex() {
	water_position=(MODEL_MATRIX*vec4(VERTEX,1.)).xz;
}
void fragment() {
	vec2 p=water_position;
	float silt=noise2(p*.012)+.38*noise2(p*.031+13.);
	float run=noise2(vec2(p.x*.12+p.y*.042,p.y*.25)+vec2(.16*TIME,0.));
	float gust=noise2(vec2(p.y*.31,p.x*.14)-vec2(.13*TIME,0.));
	float filter_fine=1.-smoothstep(.7,4.5,max(fwidth(p.x),fwidth(p.y)));
	vec3 ripple=vec3((run-.5)*.037,1.,(gust-.5)*.045)*vec3(filter_fine,1.,filter_fine);
	NORMAL=normalize((VIEW_MATRIX*vec4(normalize(ripple),0.)).xyz);
	ALBEDO=mix(vec3(.077,.108,.102),vec3(.132,.151,.126),clamp(silt*.75,0.,1.));
	ROUGHNESS=.45+.06*run;
	SPECULAR=.255;
}

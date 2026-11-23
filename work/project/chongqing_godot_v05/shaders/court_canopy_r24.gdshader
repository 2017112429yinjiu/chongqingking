shader_type spatial;
uniform vec4 zinc: source_color=vec4(.51,.55,.54,1.);
varying vec3 wp;
void vertex(){wp=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
float hash2(vec2 xy){return fract(sin(dot(xy,vec2(17.13,89.47)))*3579.81);}
float grain(vec2 xy){
	vec2 k=floor(xy),f=fract(xy);f=f*f*(3.-2.*f);
	return mix(mix(hash2(k),hash2(k+vec2(1,0)),f.x),mix(hash2(k+vec2(0,1)),hash2(k+1.),f.x),f.y);
}
void fragment(){
	float sheet=floor(wp.x/.76);
	float stain=grain(wp.xz*vec2(13.4,1.4))*.48+grain(wp.xz*2.6)*.52;
	float overlap=1.-smoothstep(.008,.018,abs(fract(wp.x/.76+.5)-.5));
	float oxide=smoothstep(.64,.92,stain)*(.32+.24*hash2(vec2(sheet,2.)));
	ALBEDO=mix(zinc.rgb*(.82+.17*grain(wp.xz*18.)+.12*hash2(vec2(sheet,3.))),vec3(.205,.145,.095),oxide)*(1.-.16*overlap);
	ROUGHNESS=mix(.69,.90,stain);
	METALLIC=.28*(1.-oxide);
}


shader_type spatial;
render_mode cull_back;
uniform vec4 plaster: source_color=vec4(.52,.55,.55,1.);
varying vec3 world_pos;
varying vec3 world_normal;
void vertex(){
	world_pos=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
	world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
float hash(float f){return fract(sin(f)*4375.13);}
float pane(float x,float half_width){
	float fw=clamp(fwidth(x),.006,1.);
	float d=abs(fract(x)-.5);
	return mix(1.-smoothstep(half_width-fw*.5,half_width+fw*.5,d),half_width*2.,smoothstep(.28,.94,fw));
}
void fragment(){
	vec3 color=plaster.rgb;
	if(abs(world_normal.y)<.35){
		vec2 n=normalize(world_normal.xz);
		float wall=floor(dot(world_pos.xz,n)*.25+.5);
		float kind=hash(wall+19.);
		float across=dot(world_pos.xz,vec2(-n.y,n.x));
		vec2 bay=vec2(across/(1.65+kind*1.8),world_pos.y/(3.05+.42*kind));
		float windows=pane(bay.x,.32+.08*kind)*pane(bay.y+.2,.30);
		float bays=pane(bay.x/(3.+floor(4.*kind)),.43);
		float joints=pane(bay.y+.55,.075);
		vec3 glass=mix(color*.47,color*vec3(.77,.87,.91),kind);
		color=mix(color,glass,windows*(.5+.5*bays))*mix(1.,.88,joints);
	}
	ALBEDO=color;
	ROUGHNESS=.94;
}


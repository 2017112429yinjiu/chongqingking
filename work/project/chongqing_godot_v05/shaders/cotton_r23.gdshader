shader_type spatial;
render_mode cull_disabled, diffuse_burley;
uniform vec4 dye : source_color = vec4(.6,.58,.49,1.);
uniform float phase=0.;
void vertex(){
	float free=UV.y*UV.y;
	VERTEX.z+=free*(.013*sin(TIME*1.34+phase+UV.y*3.)+.006*sin(TIME*.71+UV.x*4.));
}
void fragment(){
	vec2 f=UV*vec2(210.,280.);
	vec2 aa=clamp(1.-fwidth(f)*1.35,0.,1.);
	float yarn=dot(cos(f*6.2831)*aa,vec2(.024,.019));
	float stripe=1.-smoothstep(.004,.009,min(abs(UV.y-.895),abs(UV.y-.922)));
	float hem=1.-smoothstep(.012,.023,min(min(UV.x,1.-UV.x),min(UV.y,1.-UV.y)));
	ALBEDO=dye.rgb*(1.+yarn-.12*hem-.30*stripe+.035*sin(UV.x*11.+sin(UV.y*4.)+phase));
	ROUGHNESS=.96;SPECULAR=.17;BACKLIGHT=ALBEDO*.12;
}

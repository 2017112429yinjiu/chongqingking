shader_type spatial;
render_mode cull_disabled;
uniform sampler2D atlas : source_color,filter_linear_mipmap,repeat_disable;
void fragment(){
	vec4 s=texture(atlas,UV);
	float root=smoothstep(.035,.30,1.-fract(UV.y*2.));
	ALBEDO=s.rgb*mix(vec3(.39,.46,.43),vec3(.78,.83,.74),root);
	ALPHA=s.a; ALPHA_SCISSOR_THRESHOLD=.40;
	NORMAL=normalize((VIEW_MATRIX*vec4(0.,1.,0.,0.)).xyz);
	ROUGHNESS=.96; SPECULAR=.12;
}

shader_type spatial;
render_mode cull_disabled, diffuse_burley;
uniform sampler2D atlas : source_color, filter_linear_mipmap, repeat_disable;
varying vec2 tile;
varying float shade;
void vertex(){
	vec3 eye=normalize(vec3(CAMERA_POSITION_WORLD.x-MODEL_MATRIX[3].x,0.,CAMERA_POSITION_WORLD.z-MODEL_MATRIX[3].z));
	vec3 right=cross(vec3(0.,1.,0.),eye);
	float size=length(MODEL_MATRIX[1].xyz);
	MODELVIEW_MATRIX=VIEW_MATRIX*mat4(vec4(right*size,0.),vec4(0.,size,0.,0.),vec4(eye*size,0.),MODEL_MATRIX[3]);
	float angle=atan(eye.x,eye.z)/(2.*PI)-INSTANCE_CUSTOM.x;
	tile=vec2(mod(floor(angle*4.+.5),4.),INSTANCE_CUSTOM.y);
	shade=INSTANCE_CUSTOM.z;
}
void fragment(){
	vec4 sample_rgba=texture(atlas,(tile+UV)/vec2(4.,2.));
	float root=smoothstep(.017,.24,1.-UV.y);
	ALBEDO=sample_rgba.rgb*shade*mix(vec3(.42,.47,.49),vec3(1.),root);
	AO=mix(.53,1.,root);
	AO_LIGHT_AFFECT=.58;
	ALPHA=sample_rgba.a;
	ALPHA_SCISSOR_THRESHOLD=.34;
	NORMAL=normalize((VIEW_MATRIX*vec4(0.,1.,0.,0.)).xyz);
	ROUGHNESS=.92;
	SPECULAR=.11;
}

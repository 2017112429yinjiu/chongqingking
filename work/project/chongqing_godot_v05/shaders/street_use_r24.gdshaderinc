uniform bool use_street_history = false;
uniform sampler2D street_history : filter_linear_mipmap, repeat_disable;
vec3 use_at(vec2 ground){
	return texture(street_history,clamp((ground+100.)/200.,vec2(0.),vec2(1.))).rgb;
}
void finish_paving(vec3 pos,vec3 finish_normal,inout vec3 pigment,inout float rough){
	if(use_street_history){
		vec3 wear=use_at(pos.xz);
		float top=smoothstep(.52,.88,finish_normal.y);
		float moisture=clamp(wear.b+wear.g*.45,0.,1.)*top;
		float grey=dot(pigment,vec3(.27,.57,.16));
		vec3 mineral=mix(pigment,vec3(grey),.25)*vec3(1.13,1.006,.855);
		mineral*=mix(.93,1.10,wear.r*top);
		pigment=mix(mineral,mineral*vec3(.48,.54,.46),moisture);
		rough=clamp(rough-.19*moisture-.045*wear.r*top,.49,.98);
	}
}

shader_type spatial;
uniform sampler2D original : source_color,filter_linear_mipmap_anisotropic,repeat_enable;
uniform vec3 dyed_cloth=vec3(.65,.82,.89);
uniform bool red_jacket=false;
void fragment(){
	vec3 c=texture(original,UV).rgb;
	float jacket=0.;
	if(red_jacket){
		jacket=smoothstep(.34,.60,(c.r-c.g)/max(.008,c.r))*step(UV.y,.835);
	}else{
		float knit=max(step(.314,UV.x)*step(UV.x,.687),step(.295,UV.y)*step(UV.y,.496));
		jacket=knit*smoothstep(.07,.17,c.r)*smoothstep(.025,.09,(c.r-c.b)/max(.012,c.r));
	}
	float value=dot(c,vec3(.30,.53,.17))*(red_jacket?1.52:1.);
	ALBEDO=mix(c,value*dyed_cloth,clamp(jacket,0.,1.));
	ROUGHNESS=.78;SPECULAR=.25;
}


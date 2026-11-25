shader_type spatial;
uniform sampler2D shore : filter_linear_mipmap, repeat_disable;
uniform sampler2D gravel : source_color, filter_linear_mipmap_anisotropic,repeat_enable;
uniform sampler2D mud : source_color, filter_linear_mipmap_anisotropic,repeat_enable;
uniform bool outer_ground=false;
uniform bool outer_district_cut=false;
uniform bool shoal=false;
uniform sampler2D land : filter_linear_mipmap,repeat_disable;
uniform sampler2D tree_shade : filter_linear_mipmap,repeat_disable;
uniform sampler2D paving : source_color, filter_linear_mipmap_anisotropic,repeat_enable;
varying vec3 p;
void vertex(){p=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
void fragment(){
	vec2 xy=vec2(p.x,-p.z);
	float core_distance=max(abs(xy.x),abs(xy.y));
	if(outer_district_cut && core_distance>=100. && core_distance<250.){discard;}
	vec2 uv=(xy-vec2(-1650.,-1690.))/vec2(2910.,2166.);
	vec3 field=texture(shore,clamp(uv,vec2(0.),vec2(1.))).rgb;
	float local=smoothstep(345.,438.,length(xy))*(1.-smoothstep(0.,.015,length(uv-clamp(uv,vec2(0.),vec2(1.)))));
	vec3 gravel_sample=texture(gravel,xy/5.1).rgb;
	vec3 earth_sample=texture(mud,xy/8.4).rgb;
	float mineral=dot(gravel_sample,vec3(.28,.54,.18));
	float earth=dot(earth_sample,vec3(.28,.54,.18));
	float broad=.5+.5*sin(xy.x*.016+1.9*sin(xy.y*.018))*sin(xy.y*.011+.9*sin(xy.x*.025));
	vec3 hills=mix(vec3(.175,.215,.181),vec3(.207,.239,.207),broad)*(.86+.50*earth);
	vec3 sand=mix(vec3(.29,.244,.165),vec3(.38,.343,.247),broad)*(.67+.63*mineral);
	float wet=1.-smoothstep(-15.4,-11.8,p.y);
	sand=mix(sand,sand*vec3(.61,.66,.67),wet*.78);
	float beach=max(smoothstep(.10,.68,field.g),smoothstep(.20,.47,field.b)*(1.-smoothstep(-10.,3.,p.y)));
	ALBEDO=mix(vec3(.20,.25,.23),mix(hills,sand,beach),local);
	ROUGHNESS=mix(.96,.73,beach*wet); SPECULAR=.19;
	if(shoal){
		float deposit=texture(gravel,xy/48.).g;
		float run=.5+.5*sin(xy.y*.105+xy.x*.042+2.3*sin(xy.x*.021)+1.3*sin(xy.y*.026));
		float damp=1.-smoothstep(-15.85,-13.25,p.y+deposit*.65);
		vec3 dry=mix(vec3(.253,.218,.158),vec3(.353,.300,.208),clamp(.22+deposit*.64+run*.21,0.,1.));
		ALBEDO=mix(dry,vec3(.111,.117,.093),damp*.83)*(.84+.58*mineral);
		ROUGHNESS=.96-.24*damp;
	}
	if(outer_ground){
		// Match the R21 yards and their tree shadows inside the playable district.
		vec2 city_uv=(xy+360.)/720.;
		vec3 mask=texture(land,city_uv).rgb;
		float variation=sin(xy.x*.065+sin(xy.y*.04)*2.5)*sin(xy.y*.036+xy.x*.017);
		vec3 slope=mix(vec3(.115,.109,.071),vec3(.119,.145,.086),.52+.39*variation);
		slope*=.70+dot(texture(mud,xy/4.3).rgb,vec3(.30,.48,.22))*.76;
		vec3 court=mix(vec3(.14,.138,.119),texture(paving,xy/5.1).rgb,.27);
		vec3 original=mix(mix(slope,court,mask.r),vec3(.084,.087,.084),mask.g)*(1.-mask.b*.30);
		vec3 cover=texture(tree_shade,city_uv).rgb;
		original*=mix(vec3(1.),vec3(.53,.61,.70),cover.r);
		float edge=local*smoothstep(.012,.28,field.b);
		ALBEDO=mix(original,ALBEDO,edge);
		AO=1.-max(cover.g*.83,cover.b*.30)*(1.-edge);
		AO_LIGHT_AFFECT=.68;
		ROUGHNESS=mix(.90,ROUGHNESS,edge);
		SPECULAR=mix(.18,SPECULAR,edge);
	}
}

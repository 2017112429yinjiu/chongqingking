shader_type spatial;
render_mode cull_disabled,diffuse_burley;
uniform vec4 body : source_color=vec4(.51,.28,.21,1.);
uniform vec4 stripe : source_color=vec4(.72,.62,.46,1.);
uniform bool striped=true;
float h(vec2 p){return fract(sin(dot(p,vec2(39.13,61.77)))*2345.92);}
float noise2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+1.),f.x),f.y);}
void fragment(){
	float roll=fract(UV.x*13.0);
	float edging=smoothstep(.48,.49,roll)*(1.-smoothstep(.61,.62,roll));
	float line=smoothstep(.68,.69,roll)*(1.-smoothstep(.71,.72,roll));
	float band=striped ? max(edging,line):0.;
	vec3 dye=mix(body.rgb,stripe.rgb,band);
	float chalk=noise2(UV*vec2(5.3,3.1));
	float drips=noise2(UV*vec2(35.,1.8))*(1.-smoothstep(-.03,.48,UV.y));
	float weave=cos(UV.x*520.*6.283)*max(0.,1.-abs(dFdx(UV.x*520.))-abs(dFdy(UV.x*520.)));
	dye=mix(dye,vec3(.31,.27,.19),.16*chalk);
	ALBEDO=dye*(1.-.21*drips+.015*weave);ROUGHNESS=.91;SPECULAR=.20;BACKLIGHT=dye*.14;
}

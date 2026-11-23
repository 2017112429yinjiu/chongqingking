shader_type spatial;
render_mode diffuse_burley;
uniform sampler2D surface:source_color,repeat_enable,filter_linear_mipmap_anisotropic;
uniform bool stone=false;
uniform bool viaduct=false;
uniform bool retaining=false;
uniform sampler2D masonry_scan : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
varying vec3 p;
varying vec3 n;
#include "res://shaders/street_use_r24.gdshaderinc"
void vertex(){p=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;n=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
	vec3 normal=abs(normalize(n));
	vec2 uv=normal.y>.59?p.xz:(normal.x>normal.z?p.zy:p.xy);
	vec3 tex=texture(surface,uv*(stone?vec2(.47,.47):vec2(.73,1.19))).rgb;
	ALBEDO=tex*(stone?vec3(.86,.84,.79):vec3(.80,.70,.53));
	if(viaduct){
		float s=p.x*.98-p.z*.16;
		float joint=smoothstep(.055,.105,abs(fract(s/9.2)*2.-1.));
		float drain=smoothstep(.81,.97,sin(s*2.17+.49*sin(s*.81)))*smoothstep(.55,1.,sin(s*.47))*(1.-normal.y);
		ALBEDO=mix(tex*.76,vec3(.24,.225,.20),.37)*(.88+.12*joint)*(1.-.21*drain);
	}
	if (retaining) {
		// The two ends taper into a crossing. Keep one projection along the full slope.
		vec2 face_uv = vec2(p.x + .12 * p.z, p.y);
		vec3 cement = texture(surface, face_uv * vec2(.74, 1.12)).rgb;
		vec3 aggregate = texture(masonry_scan, face_uv * vec2(.62, .83)).rgb;
		float grain = sqrt(dot(cement, vec3(.2126, .7152, .0722)));
		float stone_value = sqrt(dot(aggregate, vec3(.2126, .7152, .0722)));
		float seam_dist = abs(fract((p.x + .34) / 2.45 + .5) - .5) * 2.45;
		float seam = 1. - smoothstep(.005, .018 + fwidth(p.x), seam_dist);
		vec3 runoff_scan = texture(surface, vec2(p.x * 1.4, p.y * .11)).rgb;
		float runoff = smoothstep(.08, .32, dot(runoff_scan, vec3(.2126, .7152, .0722)));
		float mortar = .035 + .23 * grain + .035 * stone_value;
		ALBEDO = vec3(1., .966, .912) * mortar * (1. - .28 * runoff) * (1. - .30 * seam);
	}
	ROUGHNESS=stone?.9:.79;SPECULAR=.22;
	finish_paving(p,normalize(n),ALBEDO,ROUGHNESS);
}

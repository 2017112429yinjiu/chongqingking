// Original material treatment. Keep the licensed source PBR and metre UVs.
// Broad mineral variation plus wetness beside authored drain/wall locations.
shader_type spatial;
render_mode diffuse_burley, specular_schlick_ggx;
#include "res://shaders/sky_visibility_r20.gdshaderinc"
#include "res://shaders/facade_runoff_r21.gdshaderinc"
uniform sampler2D albedo_map : source_color, filter_linear_mipmap_anisotropic, repeat_enable, hint_default_white;
uniform sampler2D normal_map : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D rough_map : filter_linear_mipmap_anisotropic, repeat_enable, hint_default_white;
uniform vec4 base_color : source_color = vec4(1.0);
uniform vec4 rough_channel = vec4(0.0,1.0,0.0,0.0);
uniform vec3 uv_scale = vec3(1.0);
uniform vec3 uv_offset = vec3(0.0);
uniform float roughness_factor = 1.0;
uniform float normal_strength = 1.0;
uniform bool vertex_tint = false;
uniform bool has_normal = true;
uniform float surface_kind = 0.0;
uniform bool west_kitchen_weather = false;
uniform sampler2D west_kitchen_field : filter_linear_mipmap, repeat_disable;
uniform bool street_brick = false;
uniform vec2 masonry_repeat_m = vec2(3.8,2.15);
varying vec3 world_position;
varying vec3 world_normal;
float hash21(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float noise2(vec2 p) {
 vec2 i=floor(p),f=fract(p); f=f*f*(3.0-2.0*f);
 return mix(mix(hash21(i),hash21(i+vec2(1,0)),f.x),mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),f.x),f.y);
}
#include "res://shaders/street_use_r24.gdshaderinc"
#include "res://shaders/street_repairs_r24.gdshaderinc"
varying float height_above_pavement;
void vertex() {
 world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
 world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
 height_above_pavement=4.;
 if(use_wall_toe){height_above_pavement=world_position.y+8.-textureLod(support_heights,(world_position.xz+100.)/200.,0.).r*56.;}
}
void fragment() {
 vec2 uv=UV*uv_scale.xy+uv_offset.xy;
 if(street_brick && abs(normalize(world_normal).y)<.42){
   vec2 tangent=normalize(vec2(-world_normal.z,world_normal.x));
   uv=vec2(dot(world_position.xz,tangent),-world_position.y)/masonry_repeat_m;
 }
 vec3 source=texture(albedo_map,uv).rgb*base_color.rgb;
 if(vertex_tint) source*=COLOR.rgb;
 vec2 p=world_position.xz;
 float broad=noise2(p*.28+17.0);
 float fine=noise2(p*2.3);
 float detail=noise2(p*8.1);
 float damp=0.0;
 if(surface_kind<.5) {
   // Only the eatery's low drainage edge receives a damp strip.
   float frontage=smoothstep(-33.5,-32.8,p.x)*(1.0-smoothstep(-20.6,-19.8,p.x));
   float drainage=1.0-smoothstep(.12,.58,abs(p.y-60.1)+.15*(fine-.5));
   damp=frontage*drainage*.72;
   source*=mix(.66,1.01,broad)*mix(.96,1.0,detail);
   source=mix(source,source*vec3(.91,.87,.76),smoothstep(.58,.8,broad)*.22);
 } else if(surface_kind<1.5) {
   float shop=step(-33.2,p.x)*step(p.x,-19.8)*step(61.7,p.y)*step(p.y,73.2);
   float foot=1.0-smoothstep(11.4,12.5,world_position.y+(fine-.5)*.22);
   damp=shop*foot*.75;
   source*=mix(.86,1.0,noise2(vec2(p.x+p.y,world_position.y)*.43));
 }
 if(use_sky_field) {
   vec2 tap=vec2(-31.453,-51.228);
   vec2 along=vec2(-.545,.839);
   vec2 inward=vec2(-.839,-.545);
   vec2 delta=p-tap;
   float crosswise=abs(dot(delta,along));
   float reach=dot(delta,inward);
   float splash=1.-smoothstep(.045,.31,crosswise+.07*(fine-.5));
   float spread=1.-smoothstep(.09,.42,abs(reach));
   float below=1.-smoothstep(26.75,27.51,world_position.y+fine*.11);
   damp=max(damp,splash*spread*below*.76);
 }
 if(use_facade_weather){
   vec3 deposits=facade_deposits(world_position,normalize(world_normal));
   float breakup=.56+.44*noise2(vec2(p.x+p.y,world_position.y)*5.7);
   source*=1.-deposits.r*breakup*.49;
   source=mix(source,source*vec3(1.13,1.12,1.08)+vec3(.021,.020,.014),deposits.g*breakup*.72);
   source=mix(source,source*vec3(.62,.72,.61),deposits.b*breakup);
   damp=max(damp,deposits.b*.43);
 }
 ALBEDO=mix(source,source*vec3(.48,.53,.48),damp);
 float r=dot(texture(rough_map,uv),rough_channel)*roughness_factor;
 ROUGHNESS=mix(clamp(r,.66,1.0),.51,damp);
 METALLIC=0.0;
 SPECULAR=.28;
 if(surface_kind<.5){ finish_paving(world_position,normalize(world_normal),ALBEDO,ROUGHNESS); }
 if(use_sky_field) {
   vec3 q=world_position+normalize(world_normal)*.18;
   vec3 point=vec3(q.x,-q.z,q.y);
   AO=sky_field(point,vec3(-35,-74,10),vec3(35,42,15),shop_sky)
     *sky_field(point,vec3(-42,37,24),vec3(35,50,16),alley_sky);
   AO_LIGHT_AFFECT=0.;
 }
 if(west_kitchen_weather && world_normal.x < -.8 && abs(world_position.x+66.) < .28) {
   vec2 here=vec2((world_position.z-9.)/21.,(26.-world_position.y)/11.);
   vec3 marks=texture(west_kitchen_field,clamp(here,vec2(0.),vec2(1.))).rgb;
   ALBEDO*=mix(vec3(1.),vec3(.64,.69,.60),marks.r);
   ALBEDO=mix(ALBEDO,ALBEDO*vec3(1.07,1.04,.98)+vec3(.033,.029,.019),marks.g*.73);
   ALBEDO=mix(ALBEDO,ALBEDO*vec3(1.14,1.08,.95)+vec3(.029,.023,.014),marks.b*.80);
   ROUGHNESS=mix(ROUGHNESS,.77,marks.r*.57);
 }
 if(residential_age && abs(world_normal.y)<.42){
   vec2 wall_uv=vec2(dot(world_position.xz,normalize(vec2(-world_normal.z,world_normal.x))), world_position.y);
   float height=height_above_pavement;
   float stripe=noise2(vec2(wall_uv.x*2.9,wall_uv.y*.38));
   float broad_wash=noise2(wall_uv*vec2(.51,.32)+vec2(13.,6.));
   float plaster_grain=texture(albedo_map,uv*1.43+vec2(.21,.63)).r;
   float tide=(1.-smoothstep(.25,1.85+broad_wash*.65,height))*(.24+.66*broad_wash);
   float traces=smoothstep(.59,.84,stripe)*smoothstep(.39,.65,broad_wash);
   ALBEDO*=1.-.24*tide-.19*traces;
   float lime=smoothstep(.52,.79,broad_wash*.65+plaster_grain*.35)*(.45+.55*stripe);
   ALBEDO=mix(ALBEDO,ALBEDO*vec3(1.03,1.01,.96)+vec3(.028,.026,.019),lime*.62);
   ROUGHNESS=mix(ROUGHNESS,.86,lime*.56);
 }
 if(has_normal) { NORMAL_MAP=texture(normal_map,uv).rgb; NORMAL_MAP_DEPTH=normal_strength; }
 if(repair_site==2){NORMAL=shoulder_lighting(world_position,normalize(world_normal),mat3(VIEW_MATRIX),NORMAL);}
 if(surface_kind<.5){street_repair(world_position,normalize(world_normal),ALBEDO,ROUGHNESS);}
 if(abs(world_normal.y)<.50){stain_plaster(height_above_pavement,broad,fine,ALBEDO,ROUGHNESS); }
}

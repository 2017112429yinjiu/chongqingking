shader_type spatial;
uniform int finish = 0;
uniform vec4 tint : source_color = vec4(0.66,0.65,0.60,1.0);
uniform sampler2D grain : repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D scratches : repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D brush : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D patina : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D floor_photo : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D floor_normal : hint_normal, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D floor_rough : repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D wood : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform sampler2D chilli : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
varying vec3 world;
void vertex(){world=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    float scan=texture(grain,UV*.48).r;
    float rough=texture(scratches,UV*vec2(.90,.51)).r;
    vec3 c=tint.rgb;
    ROUGHNESS=.62;SPECULAR=.36;
    if(finish==0){
        ALBEDO=c*(.59+.25*rough+.24*scan);
        METALLIC=.76;ROUGHNESS=clamp(.23+.45*rough,.28,.69);
        NORMAL_MAP=texture(brush,UV*vec2(.98,.48)).rgb;NORMAL_MAP_DEPTH=.43;
    } else if(finish==1 || finish==2 || finish==8){
        float metres=finish==8?2.0:(finish==1?1.37:2.85);
        vec2 coord=UV/metres;
        if(finish==1){coord=mat2(vec2(.70710678,.70710678),vec2(-.70710678,.70710678))*coord;}
        vec3 sample_color=texture(floor_photo,coord).rgb;
        ALBEDO=sample_color*(finish==2?vec3(.86,.95,.86):vec3(.84,.86,.82));
        ROUGHNESS=clamp(texture(floor_rough,coord).r*.84+.10,.34,.94);
        NORMAL_MAP=texture(floor_normal,coord).rgb;NORMAL_MAP_DEPTH=finish==8?.52:.24;
    } else if(finish==7){
        float stripe=smoothstep(.4,.5,fract(UV.x*15.0))*(1.-smoothstep(.53,.66,fract(UV.x*15.0)));
        ALBEDO=mix(vec3(.32,.30,.22),vec3(.085,.14,.12),stripe*.85)*(.67+.24*scan);
        ROUGHNESS=.94;
    } else if(finish==3){
        ALBEDO=mix(c,c*texture(wood,UV*vec2(1.6,2.)).rgb*1.92,.49);ROUGHNESS=.56+.18*rough;
    } else if(finish==4){
        ALBEDO=texture(chilli,UV*4.).rgb*vec3(.91,.68,.50);ROUGHNESS=.30;SPECULAR=.50;
    } else if(finish==6){
        vec3 patch=texture(patina,UV*.54).rgb;
        ALBEDO=c*(.20+patch*.96);ROUGHNESS=.86;
    } else{
        ALBEDO=c*(.76+.17*rough+.12*scan);ROUGHNESS=.35+.23*rough;
        NORMAL_MAP=texture(brush,UV*.53).rgb;NORMAL_MAP_DEPTH=.065;
    }
    float bounce=clamp(COLOR.r,.075,1.0);
    ALBEDO*=mix(bounce,bounce*bounce,.36);
    AO=bounce;AO_LIGHT_AFFECT=.57;
}

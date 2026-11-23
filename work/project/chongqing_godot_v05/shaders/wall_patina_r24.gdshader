shader_type spatial;
render_mode blend_mix, depth_draw_never, cull_disabled;
uniform sampler2D stain : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
varying vec3 place;
void vertex(){
    place=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
}
void fragment(){
    vec4 pigment=texture(stain,UV);
    vec2 border=min(UV2,1.-UV2);
    float distance_to_edge=min(border.x,border.y);
    float broken=texture(stain,vec2(place.x+place.z,place.y)*1.39+vec2(.37,.68)).a;
    float feather=smoothstep(.008,.155+.096*broken,distance_to_edge);
    float distance_fade=1.-smoothstep(25.,43.,distance(CAMERA_POSITION_WORLD,place));
    ALBEDO=pigment.rgb*vec3(.90,.86,.94);
    ROUGHNESS=.93;
    SPECULAR=.13;
    ALPHA=pigment.a*feather*(.62+.24*broken)*distance_fade;
}

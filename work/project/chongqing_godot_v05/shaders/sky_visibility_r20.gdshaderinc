// A linear data atlas stacks Blender XY slices in ascending elevation.
uniform bool use_sky_field = false;
uniform sampler2D shop_sky : filter_linear, repeat_disable, hint_default_white;
uniform sampler2D alley_sky : filter_linear, repeat_disable, hint_default_white;
float sky_field(vec3 p, vec3 origin, vec3 dims, sampler2D atlas) {
    vec3 cell = (p-origin)/vec3(.5,.5,.75);
    vec3 border = min(cell,dims-1.0-cell);
    float interior = min(border.x,min(border.y,border.z));
    if (interior <= 0.0) { return 1.0; }
    float slice = floor(cell.z);
    vec2 size = vec2(dims.x,dims.y*dims.z);
    vec2 uv = (cell.xy+vec2(.5,.5+slice*dims.y))/size;
    float value = mix(texture(atlas,uv).r,texture(atlas,uv+vec2(0.,1./dims.z)).r,fract(cell.z));
    // Reserve diffuse bounce in narrow passages. Blend to the surrounding city.
    return mix(1.,mix(.37,1.,value),smoothstep(0.,2.,interior));
}

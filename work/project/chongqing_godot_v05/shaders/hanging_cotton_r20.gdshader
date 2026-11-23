shader_type spatial;
render_mode cull_disabled, diffuse_burley;
uniform vec4 dye : source_color = vec4(1.);
uniform float phase = 0.;
uniform bool still_frame = false;
void vertex() {
    vec3 world = (MODEL_MATRIX * vec4(VERTEX,1.)).xyz;
    float hang = smoothstep(.16,.74,31.69-world.y);
    float t = still_frame ? 2. : TIME;
    float gust = .65*sin(t*1.58+phase+world.x*2.4) + .35*sin(t*.83+world.z*3.);
    vec3 delta = vec3(.87,.08,.49)*(.038*hang*gust);
    VERTEX += (inverse(MODEL_MATRIX)*vec4(delta,0.)).xyz;
}
void fragment() {
    ALBEDO=dye.rgb*COLOR.rgb;
    ROUGHNESS=.96;
    SPECULAR=.18;
}

shader_type spatial;
render_mode cull_disabled;
void vertex() {
    float fall=UV.y;
    float wave=sin(fall*49.-TIME*19.)+.5*sin(fall*81.-TIME*29.);
    VERTEX.xz*=1.+.12*wave*fall;
    VERTEX.x+=.0015*wave*fall;
}
void fragment() {
    float rim=pow(1.-abs(dot(normalize(NORMAL),normalize(VIEW))),1.6);
    float stripe=sin(UV.x*31.+UV.y*26.-TIME*19.);
    ALBEDO=mix(vec3(.19,.25,.235),vec3(.64,.70,.68),rim);
    ALPHA=.14+.48*rim+.06*stripe;
    ROUGHNESS=.11;
    SPECULAR=.85;
}

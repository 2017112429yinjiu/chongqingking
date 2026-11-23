shader_type spatial;
render_mode unshaded, cull_disabled, shadows_disabled, fog_disabled;
uniform float phase=0.0;
varying float range_fade;
void vertex(){
    vec3 centre=MODEL_MATRIX[3].xyz;
    vec3 side=normalize(vec3(INV_VIEW_MATRIX[0].x,0.0,INV_VIEW_MATRIX[0].z));
    vec3 at=centre+side*VERTEX.x+vec3(0.0,VERTEX.y,0.0);
    POSITION=PROJECTION_MATRIX*VIEW_MATRIX*vec4(at,1.0);
    range_fade=1.0-smoothstep(6.0,13.0,distance(centre,INV_VIEW_MATRIX[3].xyz));
}
void fragment(){
    float y=1.0-UV.y;
    float t=TIME*.57+phase;
    float curl=.05*sin(y*10.0-t*2.0)+y*.085*sin(y*6.9-t);
    float x=UV.x-.5-curl;
    float width=.061+y*.14;
    float stream=exp(-x*x/(width*width))*.71;
    float strand=x+.116-.035*sin(y*15.0-t*2.2);
    stream+=.42*exp(-strand*strand/(width*width*.33));
    float pulse=.52+.48*pow(.5+.5*sin(y*13.5-t*3.1+.63*sin(y*8.0-t)),2.0);
    float dissolve=smoothstep(.006,.10,y)*(1.0-smoothstep(.32,1.0,y));
    ALBEDO=vec3(.70,.72,.70);
    ALPHA=clamp(stream*pulse*dissolve*range_fade*.114,0.0,.13);
}

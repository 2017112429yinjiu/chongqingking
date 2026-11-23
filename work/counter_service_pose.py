"""Original two-handed noodle-counter performance, Blender metres and seconds."""
import math
from mathutils import Vector


def ease(start, end, t):
    u = max(0.0, min(1.0, (t-start)/(end-start)))
    return u*u*(3-2*u)


def service_pose(t):
    reach = ease(.18,1.02,t)
    carry = ease(1.16,2.35,t)
    lower = ease(2.50,3.19,t)
    arc = math.sin(math.pi*carry)
    rest_r = Vector((-.24,-.12,.875))
    grasp = Vector((-.167,-.315,1.11))
    place = Vector((-.006,-.477,1.11))
    right = rest_r.lerp(grasp,reach).lerp(place,carry)
    right.z += .101*arc + .028*math.sin(math.pi*reach)
    right = right.lerp(rest_r,lower)
    # The left wrist approaches the upper gusset after the lead hand has committed.
    # Its fingers remain outside the mouth of the paper bag during the carry.
    support = ease(.53,1.29,t)*(1-ease(2.30,3.05,t))
    # Elbow roll moves the index pad toward the folded side at both ends of
    # the stroke. Measured against the skinned fingertip, not the wrist joint.
    side_clearance = .035-.023*arc*arc
    pad_fit=.0021*(1-ease(2.17,2.31,t))
    pad_fit+=.0033*math.exp(-((t-1.50)/.14)**2)+.0023*math.exp(-((t-2.07)/.13)**2)
    side_clearance-=pad_fit
    left = Vector((.245,-.15,.875)).lerp(right+Vector((.158+side_clearance,.035,-.050)),support)
    left.z += .028*math.sin(math.pi*support)
    follow = ease(.36,1.31,t)*(1-ease(2.49,3.18,t))
    lean = ease(.16,1.0,t)*(1-ease(2.44,3.18,t))
    turn = ease(.2,.9,t)*(1-ease(1.32,2.22,t))
    gaze = ease(.03,.61,t)*(1-ease(1.96,2.73,t))
    lag = ease(.72,1.43,t)*(1-ease(2.48,3.17,t))
    return {
        'right':right, 'left':left,
        'left_axis':Vector((.008,-.035,-.06)).lerp(Vector((-.027,-.029,-.068)),support),
        'grip':ease(.91,1.12,t)*(1-ease(2.40,2.57,t)),
        'pelvis':Vector((-.017*turn+.014*carry*(1-lower),-.052*lean,-.010*lean)),
        'lean':.012+.122*lean+.045*carry*(1-lower),
        'twist':-.105*turn+.068*carry*(1-lower),
        'head_pitch':.04+.15*gaze-.035*arc,
        'head_yaw':-.09*turn,
        'hem':[-.070*lag-.032*arc,-.088*follow,-.047*lean+.021*arc],
        'follow':follow,'bib_l':.012*lag+.004*arc,'bib_r':.022*turn+.006*lag
    }

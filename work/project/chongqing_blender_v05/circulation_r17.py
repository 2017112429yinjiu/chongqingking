"""Authored route corrections, Blender XY metres; no surveyed geometry claim."""
CENTRAL=[(16.,-66.),(6.,-59.5),(-20.,-52.),(-20.,-30.),(-18.,-8.),(-18.,14.),(-40.,38.)]
NARROW=[(-40.,38.),(-37.4,43.),(-33.3,50.),(-28.7,57.),(-29.,60.)]
UPPER=[(-29.,60.),(-25.,64.),(-17.,77.),(-27.,90.)]
WEST=[(-93.,-45.),(-74.,-34.),(-73.,-8.),(-76.,17.),(-69.,23.5),(-68.7,28.9),(-69.,34.2),(-74.,40.),(-77.,61.),(-76.,77.5)]
EAST=[(52.,-61.7),(48.,-49.),(52.,-35.),(49.,-19.),(51.,-11.),(53.,-4.),(48.,3.5),(42.,4.8),(35.,5.),(28.,14.)]
ROUTES=[('Central_stair_lane',CENTRAL,3.8,True),('Narrow_upper_passage',NARROW,1.35,True),('Upper_terrace_connection',UPPER,2.5,True),('West_residential_link',WEST,2.7,True),('East_photo_alley',EAST,2.5,True)]

def domestic_entry(shell,deco,width):
    """Private entrance vestibule: a level floor terminates at a real closed door.
    Public approach stairs remain outside. This is not an upper-storey stairwell.
    Geometry is local X across doorway, +Y outward, Z from ground-floor datum.
    """
    door_width=min(1.15,width-.50)
    # Closed leaf and reveal sit before the genuine back wall, not across the
    # street opening. Keep the 2.4 m deep vestibule usable for deliveries.
    deco.box((0,-2.255,1.145),(door_width,.065,2.11),'timber')
    for x in [-door_width/2-.045,door_width/2+.045]:
        deco.box((x,-2.24,1.16),(.09,.13,2.18),'wood')
    deco.box((0,-2.24,2.245),(door_width+.18,.13,.09),'wood')
    for z in [.43,1.18,1.87]:
        deco.box((0,-2.214,z),(door_width-.15,.022,.42),'painted_metal')
        for x in [-door_width/2+.07,door_width/2-.07]:
            deco.box((x,-2.20,z),(.025,.026,.45),'wood')
    deco.box((0,-2.21,.13),(door_width-.04,.035,.08),'aluminium')
    latch=door_width*.33
    deco.box((latch,-2.202,1.12),(.06,.024,.18),'aluminium')
    deco.cylinder((latch,-2.18,1.14),(latch-.14,-2.16,1.14),.014,'aluminium',12)
    deco.cylinder((latch,-2.18,1.075),(latch,-2.17,1.075),.012,'dark',12)
    for z in [.45,1.20,1.99]:
        deco.cylinder((-door_width/2-.006,-2.19,z-.043),(-door_width/2-.006,-2.19,z+.043),.014,'aluminium',10)
    deco.cylinder((0,-2.212,1.74),(0,-2.20,1.74),.018,'aluminium',12)
    deco.cylinder((0,-2.195,1.74),(0,-2.19,1.74),.009,'glass',12)
    # Separate bell, letter slot, and restrained metal edge wear.
    bell_x=door_width/2+.19
    deco.box((bell_x,-2.24,1.25),(.10,.07,.19),'offwhite')
    deco.cylinder((bell_x,-2.198,1.24),(bell_x,-2.184,1.24),.020,'dark',12)
    deco.box((0,-2.197,.91),(.25,.020,.045),'aluminium')
    deco.box((0,-2.184,.905),(.21,.010,.012),'dark')
    for x in [-door_width/2+.04,door_width/2-.04]:
        deco.box((x,-2.215,.21),(.009,.007,.11),'rust')

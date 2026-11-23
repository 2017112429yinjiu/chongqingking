from pathlib import Path
import json
here=Path(__file__).resolve().parent
def read(n):return json.loads((here/n).read_text('utf8'))
d=read('survey_before.json')
targets=[]
def camera(name,p,q):targets.append([name,p,q])
for rec in read('placement.json'):
    if rec['id'] not in [809889622,809889624,'A03','A04',1413081560,1335306667]:continue
    name=str(rec['id']);ds={'809889622':.8,'809889624':7.9,'A04':8.35,'A03':8.6,'1413081560':4.9,'1335306667':8.3}[name]
    row=min(rec['spans'],key=lambda x:abs(x[0]-ds));x,y=[rec['a'][i]+ds*rec['t'][i] for i in range(2)];z=row[1];nx,ny=rec['n'];tx,ty=rec['t']
    camera('wall_'+name,[x+nx*3.15-tx*1.15,z+1.55,-y-ny*3.15+ty*1.15],[x,z+1.33,-y])
camera('shelter_from_lane',[-72.8,16.65,26.6],[-66.95,16.65,22.8])
camera('shelter_passing',[-70.6,17.45,19.2],[-66.95,16.48,23.05])
for name,idx,ordinal,forward in [('school',28,.55,1),('southeast',23,.64,-1),('nanqu',18,.72,-1),('court',26,.3,-1),('west_steps',25,.56,1),('east_lane',29,.87,-1),('upper',27,.62,-1),('main_road',0,.61,1),('north_branch',5,.70,-1),('hill_spine',24,.55,-1)]:
    rows=[r for r in d['samples'] if r[0]==idx and r[1]==1 and r[4]];i=int(len(rows)*ordinal);a=rows[i];other=rows[i+11*forward];camera(name,[a[2],a[4][0][0]+1.57,-a[3]],[other[2],other[4][0][0]+.45,-other[3]])
camera('fork_shoulder',[43.05,10.87,75.4],[46.1,9.68,72.8])
camera('blue_bend_entry',[78.42,27.46,-22.62],[86.5,25.65,-17.63])
camera('blue_bend_reverse',[94.15,24.68,-5.05],[89.42,24.69,-13.82])
camera('east_courtyard_passage',[49.13,20.60,17.65],[50.2,20.,11.85])
camera('west_turn',[-75.12,23.28,-22.3],[-73.04,23.05,-26.0])
camera('west_entry_from_north',[-72.1,25.05,-35.46],[-70.52,23.17,-29.85])
camera('repair_corner',[-63.64,13.24,57.56],[-62.55,12.91,54.02])
camera('shed_from_door',[-71.6,17.15,23.55],[-66.08,16.88,22.65])
camera('school_to_court',[34.,31.37,-57.1],[42.,30.42,-55.8])
camera('upper_lane_crossing',[17.1,23.33,-8.25],[16.,22.,-3.5])
camera('repair_tools',[-64.06,13.00,56.61],[-62.67,12.53,54.15])
camera('north_junction_up',[66.85,34.19,-68.10],[66.74,33.75,-76.8])
camera('south_junction_up',[-43.7,7.13,97.15],[-50.45,6.46,92.2])
camera('north_flight_exit',[-17.07,32.68,-76.8],[-21.49,32.57,-82.9])
camera('school_side_entry',[-19.54,30.24,-61.70],[-24.96,29.24,-64.0])
(here/'views.json').write_text(json.dumps(targets),'utf8')
queries=[]
for i,l,x,y,hits in d['samples']:
    if not hits:
        z=next((a[4][0][0] for a in d['samples'] if a[0]==i and a[4] and (a[2]-x)**2+(a[3]-y)**2<2),14.)
    else:z=hits[0][0]
    queries.append([i,l,x,z,-y])
(here/'queries.json').write_text(json.dumps(queries,separators=(',',':')),'utf8')

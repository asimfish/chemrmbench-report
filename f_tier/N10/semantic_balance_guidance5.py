"""Guidance #5: closed-state semantic pan inventory, no physics or force correction.

The original 160 mm physical pan defines the region before terminal points are
classified. Cup-external particles on this pan remain part of the reading.
"""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util,json,sys
import numpy as np
from pxr import Usd,UsdGeom,UsdPhysics,Gf

HERE=Path(__file__).resolve().parent
R=HERE.parents[1]
STUDY=HERE/'mortar_quantity_pair'
OUTPUT=HERE/'semantic_balance_guidance5.json'
PAN_CENTER_XY=np.array([.62,-.14])
PAN_SIZE=np.array([.16,.16,.01])
PARTICLE_MASS_KG=1e-6
REST_RADIUS_M=.0007128

def load_json(path):return json.loads(path.read_text())

def rotation(q):
    x,y,z,w=q
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
      [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
      [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])

def world_points(points,pose):return np.asarray(points)@rotation(pose[3:]).T+pose[:3]

def pan_mask(points,top_z):
    local_xy=np.asarray(points)[:,:2]-PAN_CENTER_XY
    return np.all(np.abs(local_xy)<=PAN_SIZE[:2]/2,axis=1)&(np.asarray(points)[:,2]>=top_z)

def cavity_mask(points,pose,cavity,margin):
    local=(points-pose[:3])@rotation(pose[3:])
    profile=np.asarray(cavity['radius_profile_z_r_m'])
    radial=np.linalg.norm(local[:,:2]-cavity['center_xy_m'],axis=1)
    radius=np.interp(local[:,2]-margin,profile[:,0],profile[:,1])-margin
    return (radial<=radius)&(local[:,2]>=cavity['bottom_z_m']+margin)&(local[:,2]<=cavity['top_z_m']-margin)

def boxes_corners(boxes):
    signs=np.array([[i,j,k]for i in [-1,1]for j in [-1,1]for k in [-1,1]])
    return np.vstack([np.asarray(b['center_m'])+signs*np.asarray(b['size_m'])/2 for b in boxes])

def object_membership(vertices,top_z,mass):
    lo=np.min(vertices,axis=0);hi=np.max(vertices,axis=0)
    # Whole discrete objects, never a fractional object mass. The actual two
    # candidate objects are either wholly in the pan footprint or disjoint.
    xy_intersection=bool(np.all(hi[:2]>=PAN_CENTER_XY-PAN_SIZE[:2]/2)&np.all(lo[:2]<=PAN_CENTER_XY+PAN_SIZE[:2]/2))
    contained_xy=bool(np.all(lo[:2]>=PAN_CENTER_XY-PAN_SIZE[:2]/2)&np.all(hi[:2]<=PAN_CENTER_XY+PAN_SIZE[:2]/2))
    included=xy_intersection and bool(hi[2]>=top_z)
    assert not included or contained_xy,'Partially overlapping object requires explicit resolution, not result-selected fractional mass'
    return {'geometry_world_aabb_m':[lo.tolist(),hi.tolist()],'intersects_pan_column':included,
       'footprint_fully_contained':contained_xy,'native_body_mass_kg':mass,
       'included_mass_kg':mass if included else 0.}

def main():
    assert not OUTPUT.exists(),'Preserve the first guidance5 closed-state calculation'
    geometry_spec=importlib.util.spec_from_file_location('g5_fixed_tool_geometry',STUDY/'source_snapshot/geometry.py')
    geometry=importlib.util.module_from_spec(geometry_spec);geometry_spec.loader.exec_module(geometry)
    sys.path.insert(0,str(R))
    from pour_measurement_r2 import fit_cavity
    cup_mesh=np.load(R/'evidence/beaker_mesh_root_points_r1.npy')
    cavity=fit_cavity(cup_mesh,scale=1.)
    tool_vertices=boxes_corners(geometry.tool_boxes())
    protocol={
      'definition_set_before_classifying_terminal_points':True,
      'physical_pan_prim':'/World/Scale/Platform','physical_pan_local_size_m':PAN_SIZE.tolist(),
      'world_xy_m':[(PAN_CENTER_XY-PAN_SIZE[:2]/2).tolist(),(PAN_CENTER_XY+PAN_SIZE[:2]/2).tolist()],
      'vertical_region':'z >= terminal platform_z + physical half-thickness .005 m, with no upper height cutoff',
      'particle_rule':'Particle centers in exact original physical pan footprint and upper column; no radius/XY dilation, no removal of cup-external pan particles.',
      'object_rule':'Whole independent rigid objects with physical geometry intersecting the pan column; require the complete XY footprint contained, otherwise fail unresolved. Enumerate original cup and ready-mounted tool explicitly; the scale platform mass is included in gross and tare.',
      'external_entities':'Panda is an externally fixed-base actuator, not an independent scale load object; fixed source bowl/ground are outside the physical pan; display-only support/housing have no rigid mass or collision APIs. No robot-link mass is inferred from a visual intersection.',
      'tare':'Same native empty platform plus same native empty receiver body masses; initial particle stock must independently be outside the physical pan region. No loaded/tuned tare, no force-readout correction.',
      'comparison':'Semantic net inventory is compared separately with original five-ring mesh-frustum cup center/strict count and unchanged legacy cylinder-plus1mm count; cup-external pan mass is not hidden.',
      'platform_pose_limit':'Only terminal platform Z was logged. XY and orientation use the original Z-only prismatic joint constraints and native initial geometry; this is a semantic inventory, not measured force/support ownership.',
      'thresholds':{'cup_true_cavity_kg_min':.0007,'relative_semantic_vs_cup_ledger_max':.01},
      'no_native_steps':True,'no_F_audit':True,'particle_mass_kg':PARTICLE_MASS_KG}
    cases={}
    for label,folder in [('positive','native_positive'),('negative','native_negative')]:
      output=STUDY/folder;row=load_json(output/'terminal_control_observation.json');raw=load_json(output/'result.json')
      with np.load(output/'terminal_control_particles.npz',allow_pickle=False)as a:
        points=a['points'].copy();cup_pose=a['receiver_pose_xyzw'].copy();tool_pose=a['spoon_pose_xyzw'].copy();step=int(a['step'])
      assert len(points)==11200 and np.isfinite(points).all() and step==row['native_step']
      stage=Usd.Stage.Open(str(output/'scene_initial.usda'));assert stage
      platform=stage.GetPrimAtPath('/World/Scale/Platform');cube=UsdGeom.Cube(platform)
      size=float(cube.GetSizeAttr().Get());local_scale=np.array(UsdGeom.Xformable(platform).GetOrderedXformOps()[1].Get(),float)
      assert np.allclose(size*local_scale,PAN_SIZE,rtol=0,atol=1e-8)
      joint=UsdPhysics.PrismaticJoint(stage.GetPrimAtPath('/World/Spring'));assert joint.GetAxisAttr().Get()=='Z'
      assert str(joint.GetBody1Rel().GetTargets()[0])=='/World/Scale'
      instancer=UsdGeom.PointInstancer(stage.GetPrimAtPath('/World/Powder/particles'))
      initial_local=np.array(instancer.GetPositionsAttr().Get(),float)
      xf=UsdGeom.XformCache().GetLocalToWorldTransform(instancer.GetPrim())
      initial_world=np.array([list(xf.Transform(Gf.Vec3d(*p)))for p in initial_local])
      masses={k:float(np.asarray(v).reshape(-1)[0])for k,v in raw['native_masses_kg'].items()}
      usd_mass_sources={}
      for key,path in [('scale_platform','/World/Scale'),('receiver','/World/Receiver'),('spoon','/World/Spoon')]:
        attributes=[{'path':str(p.GetPath()),'mass_kg':float(UsdPhysics.MassAPI(p).GetMassAttr().Get())}
          for p in Usd.PrimRange(stage.GetPrimAtPath(path)) if p.HasAPI(UsdPhysics.MassAPI) and UsdPhysics.MassAPI(p).GetMassAttr().Get()]
        assert len(attributes)==1 and abs(attributes[0]['mass_kg']-masses[key])<1e-7
        usd_mass_sources[key]=attributes[0]
      top=float(row['platform_z_m'])+PAN_SIZE[2]/2
      mask=pan_mask(points,top);cup=cavity_mask(points,cup_pose,cavity,0.);strict=cavity_mask(points,cup_pose,cavity,REST_RADIUS_M)
      assert np.all(~cup|mask),'Cup contents outside pan column must not be silently reconciled'
      objects={'receiver':object_membership(world_points(cup_mesh,cup_pose),top,masses['receiver']),
               'tool':object_membership(world_points(tool_vertices,tool_pose),top,masses['spoon'])}
      initial_tare_pan_count=int(pan_mask(initial_world,top).sum());assert initial_tare_pan_count==0
      particle_mass=int(mask.sum())*PARTICLE_MASS_KG
      gross=masses['scale_platform']+sum(o['included_mass_kg']for o in objects.values())+particle_mass
      tare=masses['scale_platform']+masses['receiver'];net=gross-tare
      proxy=int(row['receiver_particles']);center=int(cup.sum());strict_n=int(strict.sum())
      comparisons={}
      for name,count in [('true_mesh_frustum_center',center),('true_mesh_frustum_strict_rest_envelope',strict_n),('legacy_cylinder_plus1mm',proxy)]:
        reference=count*PARTICLE_MASS_KG;error=abs(net-reference)
        comparisons[name]={'grains':count,'mass_kg':reference,'semantic_minus_reference_kg':net-reference,
          'absolute_error_kg':error,'relative_error':error/reference if reference else None,
          'within_1percent':error/reference<=.01 if reference else None,
          'zero_reference_scope':'For zero payload report absolute error; percentage is undefined.'if not reference else None}
      cases[label]={'native_step':step,'native_s':float(row['native_s']),'terminal_input':str(output.relative_to(R)/'terminal_control_particles.npz'),
        'original_scene':str(output.relative_to(R)/'scene_initial.usda'),'physical_platform_top_z_m':top,
        'native_masses_kg':masses,'matching_USD_mass_attributes':usd_mass_sources,'objects':objects,'initial_tare_pan_particle_count':initial_tare_pan_count,
        'pan_particle_count':int(mask.sum()),'cup_mesh_frustum_count':center,'cup_strict_count':strict_n,'original_proxy_count':proxy,
        'cup_external_pan_particle_count':int((mask&~cup).sum()),'outside_pan_particle_count':int((~mask).sum()),
        'pan_particle_mass_kg':particle_mass,'semantic_gross_kg':gross,'empty_pan_plus_empty_cup_tare_kg':tare,
        'semantic_net_kg':net,'comparison':comparisons,'raw_physical_spring_increment_kg':row['independent_scale_increment_kg'],
        'minimum_particle_distance_to_xy_pan_boundary_m':float(np.min(np.abs(np.abs(points[:,:2]-PAN_CENTER_XY)-PAN_SIZE[:2]/2))),
        'minimum_particle_distance_to_pan_top_m':float(np.min(np.abs(points[:,2]-top)))}
    positive=cases['positive'];negative=cases['negative']
    candidate=(positive['comparison']['true_mesh_frustum_center']['mass_kg']>=.0007 and positive['comparison']['true_mesh_frustum_center']['within_1percent'] and
       abs(negative['semantic_net_kg'])<=1e-12 and negative['cup_mesh_frustum_count']==0)
    result={'status':'GUIDANCE5_SEMANTIC_GATE_'+('CANDIDATE_PASS'if candidate else'NOT_MET'),
      'computed_utc':datetime.now(timezone.utc).isoformat(),'F_PASS':False,'eligible_for_root_F_candidate':bool(candidate),
      'protocol':protocol,'cases':cases,'cup_geometry':cavity,
      'preserved_physical_metrology':'Original physical spring is diagnostic under guidance5; rigid error about2.5%, PBD under-read42–82% in controlled light_balance evidence. Original .7g/10% physical-scale failures and all raw readings remain unchanged.',
      'physical_metrology_evidence':['f_tier/N10/light_balance_candidate/result.json','f_tier/N10/mortar_quantity_pair/result.json'],
      'prior_gate_failures':['f_tier/N10/entry_repair/collision_repair/native_positive/result.json','f_tier/N10/framework_dispatch_fix/native_positive/result.json','f_tier/N10/initialization_contract_fix/native_positive/result.json','f_tier/N10/mortar_native_candidate/native_positive/result.json','f_tier/N10/mortar_quantity_pair/result.json'],
      'scope':'Independent closed-state semantic inventory recomputation, no new native/parameter adjustment/F audit. Region fixed from original physical pan geometry; no outcome-selected cup-only region.'}
    OUTPUT.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'output':str(OUTPUT),'eligible_for_root_F_candidate':bool(candidate),
      'positive_pan_grains':positive['pan_particle_count'],'positive_cup_grains':positive['cup_mesh_frustum_count'],
      'positive_error':positive['comparison']['true_mesh_frustum_center']['relative_error'],
      'negative_absolute_error_kg':abs(negative['semantic_net_kg'])}))

if __name__=='__main__':main()

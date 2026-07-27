/*
 HDA-1 P2 — assembly wrapper around the reviewed P1 pressure-boundary envelope.
 P2 replaces only the unproven P1 mixer with the P2-B test candidate.
 Units: millimetres.  Not production CAD or a pressure-equipment calculation.
 PART = assembly|chamber|drain_cap|pan|lid|gasket|lock_ring|seal|splash|spindle|mixer|ports|motor
*/

use <main_node_p1.scad>;
use <p2_mixer_variants.scad>;

PART = "assembly";
CUTAWAY = true;

// P2 form: constant Ø150 mm inner bore; 1.68 L nominal geometric volume.
// Its 2.5 mm bottom top is z=15.5 mm. The tool itself begins 8 mm above it.
p2_pan_inner_d = 150;
p2_pan_inner_h = 95;
p2_pan_t = 2.5;
p2_pan_outer_d = 155;
p2_pan_rim_d = 170;
p2_pan_z = 13;
p2_tool_origin_z = p2_pan_z + p2_pan_t;

module pan_p2() {
  color([0.14,0.72,0.70]) union() {
    difference() {
      cylinder(d=p2_pan_outer_d,h=p2_pan_inner_h+p2_pan_t);
      translate([0,0,p2_pan_t]) cylinder(d=p2_pan_inner_d,h=p2_pan_inner_h+.2);
    }
    translate([0,0,p2_pan_inner_h+p2_pan_t-3]) annulus(p2_pan_rim_d,p2_pan_outer_d-4,5);
    // Three external keys prevent the removable form from rotating, outside the food volume.
    for(a=[30,150,270]) rotate([0,0,a]) translate([78,0,42]) cube([12,7,52],center=true);
  }
}

module p2_mixer() {
  // P2-A is the baseline: two connected open helical ribbons.
  // P2-B with the slotted ring remains a separate experimental alternative.
  // It has no lower support. Its lowest steel point remains z=23.2 mm.
  translate([0,0,p2_tool_origin_z]) tool_A();
}

module main_assembly_p2() {
  sectioned() chamber();
  sectioned() drain_cap();
  sectioned() translate([0,0,p2_pan_z]) pan_p2();
  sectioned() translate([0,0,142]) lid();
  sectioned() translate([0,0,142]) gasket();
  sectioned() translate([0,0,128]) lock_ring();
  sectioned() spindle();
  sectioned() seal();
  sectioned() splash();
  sectioned() ports();
  sectioned() motor();
  sectioned() p2_mixer();
}

if(PART=="assembly") main_assembly_p2();
else if(PART=="chamber") chamber();
else if(PART=="drain_cap") drain_cap();
else if(PART=="pan") translate([0,0,p2_pan_z]) pan_p2();
else if(PART=="lid") translate([0,0,142]) lid();
else if(PART=="gasket") translate([0,0,142]) gasket();
else if(PART=="lock_ring") translate([0,0,128]) lock_ring();
else if(PART=="seal") seal();
else if(PART=="splash") splash();
else if(PART=="spindle") spindle();
else if(PART=="mixer") p2_mixer();
else if(PART=="ports") ports();
else if(PART=="motor") motor();
else assert(false,str("Unknown PART: ",PART));

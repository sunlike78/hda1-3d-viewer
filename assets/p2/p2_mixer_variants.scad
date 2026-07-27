/*
 HDA-1 P2 — two testable, top-driven mixer candidates.
 Units: millimetres.  These are prototype tools, not serial production parts.
 Both are completely above the pan floor: there is no lower bearing/support.
 PART = "A" | "B" | "compare"
*/

PART = "compare";
$fn = 96;

// P2 insert: ID 150 mm, 95 mm working height. Tool geometry.
shaft_d = 20;
hub_d = 34;
tool_od = 134;                 // 8 mm radial clearance to nominal 150 mm form
tool_radius = 62;
floor_clear = 8;
ribbon_h = 76;
ribbon_radial_w = 10;
ribbon_t = 2.5;

assert(tool_od <= 150 - 2*floor_clear, "tool must retain radial food clearance");
assert(floor_clear >= 7, "no lower support: floor clearance must be >= 7 mm");

module ribbon(phase=0) {
  // A solid rectangular helical band: open, washable, no tube or wire loop.
  rotate([0,0,phase])
    linear_extrude(height=ribbon_h, twist=300, slices=48)
      translate([tool_radius-ribbon_radial_w/2, -ribbon_t/2])
        square([ribbon_radial_w,ribbon_t], center=false);
}

module quick_coupling() {
  // Four torque dogs; their strength is calculated separately from the visual model.
  cylinder(d=hub_d,h=18);
  for(a=[0:90:270]) rotate([0,0,a]) translate([15,0,9]) cube([10,7,7],center=true);
}

module tool_A() {
  color([0.72,0.76,0.78]) union() {
    // The central shaft begins 8 mm above the form floor: it is not a lower support.
    translate([0,0,floor_clear]) cylinder(d=20,h=ribbon_h+26);
    translate([0,0,floor_clear+ribbon_h+8]) quick_coupling();
    translate([0,0,floor_clear]) ribbon(0);
    translate([0,0,floor_clear]) ribbon(180);
    // Two lower and two upper radial ties make the helices one load path to the hub.
    for(a=[0,180]) rotate([0,0,a]) {
      translate([36,0,floor_clear+2.5]) cube([56,7,5],center=true);
      translate([36,0,floor_clear+ribbon_h-2.5]) cube([56,7,5],center=true);
    }
  }
}

module disperser_ring() {
  // A shallow, balanced annular disc with large open slots — not a random fan.
  difference() {
    cylinder(d=112,h=4);
    translate([0,0,-.1]) cylinder(d=42,h=4.2);
    // Slots stop short of both inner and outer rings; the disc remains one part.
    for(a=[0:45:315]) rotate([0,0,a]) translate([40,0,2]) cube([26,13,4.2],center=true);
  }
}

module tool_B() {
  color([0.72,0.76,0.78]) union() {
    translate([0,0,floor_clear]) cylinder(d=20,h=ribbon_h+26);
    translate([0,0,floor_clear+ribbon_h+8]) quick_coupling();
    translate([0,0,floor_clear]) ribbon(0);
    translate([0,0,floor_clear]) ribbon(180);
    for(a=[0,180]) rotate([0,0,a]) {
      translate([36,0,floor_clear+2.5]) cube([56,7,5],center=true);
      translate([36,0,floor_clear+ribbon_h-2.5]) cube([56,7,5],center=true);
    }
    // Four short bridges tie the upper disperser annulus to the central shaft.
    for(a=[0:90:270]) rotate([0,0,a]) translate([16,0,68]) cube([22,6,4],center=true);
    translate([0,0,66]) disperser_ring();
  }
}

module pan_reference() {
  color([0.15,0.65,0.70,0.18]) difference() {
    cylinder(d=150,h=95);
    translate([0,0,2]) cylinder(d=146,h=94);
  }
}

if(PART == "A") tool_A();
else if(PART == "B") tool_B();
else if(PART == "compare") {
  translate([-92,0,0]) { pan_reference(); tool_A(); }
  translate([92,0,0]) { pan_reference(); tool_B(); }
}
else assert(false, str("Unknown PART: ", PART));

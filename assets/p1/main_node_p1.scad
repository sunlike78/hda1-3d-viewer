/*
 HDA-1 P1 — pre-design main-node geometry (millimetres).
 P1 has a 2.5 mm nominal shell, 3 mm lower closure, 10 mm lid plate and
 8-lug ring selected by preliminary screening. It is NOT production CAD,
 not an EN 13445 calculation and not pressure-equipment approval.
 PART = assembly|chamber|drain_cap|pan|lid|gasket|lock_ring|seal|splash|spindle|mixer|ports|motor
*/

PART = "assembly";
CUTAWAY = true;
$fn = 72;

// ---- P1 design envelope and preliminary pressure boundary ----
pressure_working_mpa = 0.15;
pressure_design_mpa = 0.25;
pressure_hydrotest_mpa = 0.325;
design_temp_c = 60;
chamber_id = 210;
shell_t = 2.5;                 // P1 nominal, requires final code calculation
bottom_t = 3.0;                // P1 nominal closure, requires final code calculation
chamber_od = chamber_id + 2*shell_t;
chamber_h = 142;
top_flange_od = 238;
top_flange_h = 10;
lid_od = 236;
lid_h = 18;
lid_plate_t = 10;
ring_od = 260;
ring_id = 240;
ring_h = 14;
lug_count = 8;
lug_t = 7;
lug_engagement = 18;
pan_top_od = 160;
pan_bottom_od = 146;
pan_inner_h = 92;
pan_rim_od = 170;
pan_t = 2.2;
shaft_d = 22;
splash_od = 154;
mixer_span = 130;
mixer_floor_clear = 7;
motor_offset = 95;
gasket_major_d = 220;
gasket_minor_d = 5;
drain_offset = -90;
pan_z = 13;
mixer_z = pan_z + pan_t + mixer_floor_clear;

gap_pan_chamber = (chamber_id-pan_top_od)/2;
gap_mixer_pan = (pan_top_od-mixer_span)/2;
assert(shell_t >= 2.5, "P1 shell nominal must not be reduced without recalculation");
assert(bottom_t >= 3, "P1 bottom nominal must not be reduced without recalculation");
assert(lid_plate_t >= 10, "P1 lid plate must not be reduced without recalculation");
assert(lug_count == 8 && lug_t >= 7 && lug_engagement >= 18,
       "P1 lock screen assumes 8 lugs, 7 mm thickness and 18 mm engagement");
assert(gap_pan_chamber > 10, "pan-to-chamber radial clearance");
assert(gap_mixer_pan >= 12, "mixer-to-pan radial clearance");
assert(mixer_floor_clear >= 7, "mixer floor clearance");
assert(abs(drain_offset)-13 > pan_bottom_od/2, "drain must remain outside pan footprint");
assert(abs(drain_offset)+13 < chamber_id/2, "drain must remain inside chamber footprint");

// ---- helpers ----
module annulus(od,id,h) { difference(){ cylinder(d=od,h=h); translate([0,0,-.1]) cylinder(d=id,h=h+.2); } }
module x_cyl(d,l) { rotate([0,90,0]) cylinder(d=d,h=l,center=true); }
module y_cyl(d,l) { rotate([90,0,0]) cylinder(d=d,h=l,center=true); }
module torus_like(major_d,minor_d) { rotate_extrude() translate([major_d/2,0,0]) circle(d=minor_d); }
function polar_xyz(r,a,z) = [r*cos(a),r*sin(a),z];
module rod_path(points,d=3) {
  for(i=[0:len(points)-2]) hull() { translate(points[i]) sphere(d=d,$fn=24); translate(points[i+1]) sphere(d=d,$fn=24); }
}
module sectioned() { if(CUTAWAY) difference(){ children(); translate([0,0,-40]) cube([340,340,410]); } else children(); }

// ---- stationary pressure boundary ----
module chamber() {
  color([0.30,0.34,0.38])
  difference() {
    union() {
      cylinder(d=chamber_od,h=chamber_h);
      // P1 lower external foot ring: not a thick pressure bottom.
      translate([0,0,-4]) annulus(222,190,5);
      // Separate forged/welded upper flange envelope.
      translate([0,0,chamber_h-top_flange_h]) cylinder(d=top_flange_od,h=top_flange_h);
      // Offset drain boss in the annular space; never below the mixer axis.
      translate([drain_offset,0,-12]) cylinder(d=26,h=15);
    }
    translate([0,0,bottom_t]) cylinder(d=chamber_id,h=chamber_h+.2);
    translate([drain_offset,0,-13]) cylinder(d=14,h=27);
  }
}

module drain_cap() {
  color([0.72,0.48,0.10]) {
    translate([drain_offset,0,-17]) cylinder(d=19,h=4.5);
    translate([drain_offset,0,-12.7]) cylinder(d=13.6,h=7.5);
  }
}

// ---- product pan: removable and not a pressure boundary ----
module pan() {
  color([0.14,0.72,0.70]) union() {
    difference() {
      cylinder(d1=pan_bottom_od,d2=pan_top_od,h=pan_inner_h+pan_t);
      translate([0,0,pan_t]) cylinder(d1=pan_bottom_od-2*pan_t,d2=pan_top_od-2*pan_t,h=pan_inner_h+.2);
    }
    translate([0,0,pan_inner_h+pan_t-3]) annulus(pan_rim_od,pan_top_od-5,5);
    for(a=[30,150,270]) rotate([0,0,a]) translate([79,0,42]) cube([15,8,52],center=true);
  }
}

// ---- lid and 8-lug self-locking ring ----
module lid() {
  color([0.50,0.54,0.58]) union() {
    difference() {
      cylinder(d=lid_od,h=lid_h);
      // Underside pocket leaves a 10 mm central P1 plate; final FEA required.
      translate([0,0,-.1]) cylinder(d=180,h=lid_h-lid_plate_t+.1);
      // Static-gasket service groove, separated from the pressure opening.
      translate([0,0,-.1]) annulus(228,212,4.7);
    }
    translate([0,0,lid_h-3]) cylinder(d=108,h=3);
  }
}

module gasket() {
  color([0.92,0.33,0.08]) translate([0,0,2]) torus_like(gasket_major_d,gasket_minor_d);
}

module lock_ring() {
  color([0.94,0.55,0.12]) union() {
    annulus(ring_od,ring_id,ring_h);
    // Eight inward lugs: nominal 7 mm thick, 18 mm radial engagement.
    for(a=[0:360/lug_count:359]) rotate([0,0,a]) translate([114,0,4]) cube([lug_engagement,18,lug_t],center=true);
    // Outer grip ribs; they are not pressure load paths.
    for(a=[15:30:345]) rotate([0,0,a]) translate([ring_od/2-4,0,ring_h/2]) cube([6,10,ring_h-3],center=true);
  }
}

// ---- upper-supported spindle; no bottom support in the bowl ----
module spindle() {
  color([0.55,0.58,0.60]) translate([0,0,106]) cylinder(d=shaft_d,h=142);
  color([0.12,0.12,0.13]) translate([0,0,183]) annulus(42,shaft_d+1,12);
  color([0.12,0.12,0.13]) translate([0,0,225]) annulus(42,shaft_d+1,12);
  color([0.14,0.18,0.22]) translate([0,0,203]) annulus(70,shaft_d+1,10);
  color([0.86,0.68,0.15]) translate([0,0,166]) annulus(30,shaft_d+1,7);
  color([0.24,0.30,0.34]) translate([0,0,103]) cylinder(d=32,h=12);
  color([0.90,0.62,0.10]) translate([0,0,101]) cylinder(d=38,h=4);
}

module seal() {
  color([0.14,0.15,0.16]) translate([0,0,145]) annulus(56,shaft_d+2,16);
  color([0.82,0.30,0.08]) translate([0,0,150]) annulus(70,56,7);
  color([0.05,0.10,0.14]) difference() { translate([0,0,161]) annulus(78,60,14); translate([28,-12,160]) cube([30,24,17]); }
  color([0.25,0.75,0.85]) translate([36,0,162]) rotate([0,90,0]) cylinder(d=12,h=20);
}

module splash() {
  color([0.18,0.55,0.72]) difference() {
    translate([0,0,112]) annulus(splash_od,38,4);
    for(a=[0:90:270]) rotate([0,0,a]) translate([54,0,111]) cube([24,16,7],center=true);
  }
  color([0.18,0.55,0.72]) translate([0,0,116]) annulus(48,30,10);
}

// ---- P0 calculated hybrid mixer retained for P1 prototype comparison ----
module lower_swept_paddle(a=0) {
  rotate([0,0,a]) union() {
    hull() { translate([13,0,1]) cylinder(d=3,h=28,$fn=24); translate([38,6,3]) cylinder(d=3,h=28,$fn=24); }
    hull() { translate([38,6,3]) cylinder(d=3,h=28,$fn=24); translate([64,14,6]) cylinder(d=3,h=25,$fn=24); }
    hull() { translate([11,-4,2]) cylinder(d=6,h=26,$fn=24); translate([22,1,2]) cylinder(d=6,h=27,$fn=24); }
  }
}
module aerator_wire(a=0) {
  rotate([0,0,a]) rod_path([
    polar_xyz(13,0,39), polar_xyz(28,4,45), polar_xyz(40,8,51), polar_xyz(47,11,58),
    polar_xyz(49,12,64), polar_xyz(47,11,70), polar_xyz(40,8,78), polar_xyz(28,4,84), polar_xyz(13,0,88)
  ],3);
}
module mixer() {
  color([0.10,0.84,0.78]) union() {
    cylinder(d=shaft_d,h=96);
    cylinder(d=30,h=32);
    lower_swept_paddle(0); lower_swept_paddle(180);
    translate([0,0,34]) cylinder(d=30,h=8);
    for(a=[0:45:315]) aerator_wire(a);
    translate([0,0,84]) cylinder(d=30,h=8);
    translate([0,0,92]) cylinder(d1=30,d2=32,h=12);
  }
}

// ---- separate pressure ports and a recognisable safety valve envelope ----
module port_body(x,y,z,col=[0.8,0.2,0.1]) {
  color(col) translate([x,y,z]) x_cyl(17,30);
  color([0.18,0.18,0.18]) translate([x+18,y,z]) x_cyl(23,9);
}
module relief_valve_p1() {
  // Envelope of a purchased, independently certified spring safety valve.
  color([0.88,0.16,0.10]) translate([116,38,112]) x_cyl(18,30);
  color([0.18,0.18,0.18]) translate([134,38,112]) x_cyl(25,8);
  color([0.88,0.16,0.10]) translate([140,38,126]) cylinder(d=15,h=27);
  color([0.20,0.20,0.21]) translate([140,38,153]) cylinder(d=23,h=6);
  color([0.88,0.16,0.10]) translate([140,50,130]) y_cyl(12,24);
}
module ports() {
  port_body(-114,-45,112,[0.18,0.65,0.90]); // P1
  port_body(-114,0,112,[0.55,0.24,0.82]);   // P2
  port_body(-114,45,112,[0.20,0.72,0.42]);  // inlet
  port_body(114,-38,112,[0.95,0.58,0.10]);  // controlled exhaust
  relief_valve_p1();                         // independent mechanical relief
}

module motor() {
  color([0.12,0.18,0.25]) translate([0,-motor_offset,184]) cylinder(d=58,h=85);
  color([0.28,0.32,0.36]) translate([0,-motor_offset,174]) cylinder(d=72,h=18);
  color([0.12,0.12,0.13]) translate([0,-motor_offset,203]) annulus(48,10,10);
  color([0.06,0.07,0.08]) translate([0,0,203]) difference() {
    hull(){ translate([0,-motor_offset,0]) cylinder(d=58,h=10); cylinder(d=80,h=10); }
    translate([0,0,-.1]) hull(){ translate([0,-motor_offset,0]) cylinder(d=42,h=10.2); cylinder(d=64,h=10.2); }
  }
  color([0.24,0.27,0.30]) translate([0,-motor_offset,269]) cylinder(d=30,h=20);
  color([0.32,0.36,0.40]) translate([-54,-motor_offset,178]) cube([108,20,12],center=true);
}

module main_assembly() {
  color([0.30,0.34,0.38]) sectioned() chamber();
  color([0.72,0.48,0.10]) sectioned() drain_cap();
  color([0.14,0.72,0.70]) sectioned() translate([0,0,pan_z]) pan();
  color([0.50,0.54,0.58]) sectioned() translate([0,0,chamber_h]) lid();
  color([0.92,0.33,0.08]) sectioned() translate([0,0,chamber_h]) gasket();
  color([0.94,0.55,0.12]) sectioned() translate([0,0,chamber_h-ring_h]) lock_ring();
  color([0.55,0.58,0.60]) sectioned() spindle();
  color([0.82,0.30,0.08]) sectioned() seal();
  color([0.18,0.55,0.72]) sectioned() splash();
  color([0.78,0.24,0.18]) sectioned() ports();
  color([0.12,0.18,0.25]) sectioned() motor();
  color([0.10,0.84,0.78]) translate([0,0,mixer_z]) mixer();
}

if(PART=="assembly") main_assembly();
else if(PART=="chamber") chamber();
else if(PART=="drain_cap") drain_cap();
else if(PART=="pan") translate([0,0,pan_z]) pan();
else if(PART=="lid") translate([0,0,chamber_h]) lid();
else if(PART=="gasket") translate([0,0,chamber_h]) gasket();
else if(PART=="lock_ring") translate([0,0,chamber_h-ring_h]) lock_ring();
else if(PART=="seal") seal();
else if(PART=="splash") splash();
else if(PART=="spindle") spindle();
else if(PART=="mixer") translate([0,0,mixer_z]) mixer();
else if(PART=="ports") ports();
else if(PART=="motor") motor();
else assert(false,str("Unknown PART: ",PART));

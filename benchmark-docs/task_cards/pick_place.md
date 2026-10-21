# T1 — Pick and place

Setting: SafeLab100ml glass beaker in the reconstructed station-A scene; FR3
starts from the fixed home pose. Source xy varies±3cm, yaw±30degrees. Target
and instruction are public; no hidden memory or timing parameter (M0/T0).

Success: lift>=3cm, place the beaker centre<=2cm from target, tilt<10degrees,
release the fingers, final linear speed<0.01m/s. Stages are approach, grasp,
lift, transport, place_release, retreat. Safety thresholds are25N raw peak,
0.25rad deviation and20mm unintended displacement, with recorded coverage.

The beaker uses opaque frosted-blue material, opacity1.0, rather than clear
glass. Geometry/mass are preserved. Legacy sampled minimum clearance7.60mm
is recorded, not a continuous10mm certificate. Main19/20 includes one IK
error. The public action track records policy_start/end without requiring
teacher phase labels. See [protocol](../evaluation_protocol.md).

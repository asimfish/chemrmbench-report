# T7 — Stop at a visible endpoint

Engineering task, chemistry_calibrated=false. From the declared nominal
prepress-ready posture, the left key adds a simulated reagent increment and
the right key finishes. Public rule: stop when the receiver changes colour.
Hidden N* is uniform over3–7; it is never a policy field (M0/T-event).

At addition N*, the real rendered receiver material changes blue to red.
Success: zero additions after colour change, no early finish, physical finish
within5s. Every episode must show mean receiver RGB contrast>=30/255.
Press threshold4N, raw safety peak<=25N; intended local-panel contact follows
the same3cm fingerpad-only,<=1mm penetration rule as T4, excluding other controls.
Other safety thresholds remain0.25rad/20mm.

Main20/20, minimum RGB contrast0.319. Fixed-five-additions lower bound3/10,
analytical optimum1/5. Colour is an engineered event, not a chemical endpoint
model; there is no liquid. Expert truth access is marked privileged. The public
heuristic must inspect pixels after each increment, not query N*.

# T4-v2 — React to a cue from a ready pose

Fixed stirring-plate left control key; initial_posture=prepress_ready_3mm.
Reaching/alignment are outside this task. Public response window3s; hidden
cue onset t_c~U[2,17]s, visible as a green lamp (M0/T-dl).

Success requires physical button force crossing4N within[t_c,t_c+3s], with
no early press and no safety violation. Raw peak threshold stays25N; no
temporal smoothing changes it. Response latency uses measured contact.
The3cm intentional panel region permits fingerpads only, penetration<=1mm,
excluding other keys/knobs. Other safety limits0.25rad/20mm remain unchanged.

Main19/20 includes the original seed19 renderer timeout. Fixed initiation
4s/9.5s, five seeds each, gives4/10. Any fixed physical contact time has
upper bound3/15=0.2. T4-v1's narrower cue distribution and8/10 lower result
are retained as superseded, not pooled into v2. See
[version history](../version_history.md).

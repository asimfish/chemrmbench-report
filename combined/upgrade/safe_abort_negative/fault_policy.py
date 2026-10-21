"""Pure read-only calculations and command fence for one branch negative.

No simulator import, world step, pose/velocity setter, parameter search or retry.
Runtime inertia is the native COM tensor expressed in the body-prim frame.
"""
import math
import numpy as np

DT = 1 / 300
PULSE_STEPS = 5
PULSE_S = DT * PULSE_STEPS


def plan_pulse(inertia_column_major, omega_body_rad_s, *, mass_kg, clearance_m,
               vertical_velocity_m_s, both_contacts_lost, support_absent):
    inertia = np.asarray(inertia_column_major, dtype=float).reshape(3, 3, order='F')
    omega = np.asarray(omega_body_rad_s, dtype=float)
    if not np.isfinite(np.r_[inertia.ravel(), omega, mass_kg, clearance_m, vertical_velocity_m_s]).all():
        raise ValueError('NONFINITE_IMPULSE_INPUT')
    if not (both_contacts_lost and support_absent and .05 <= clearance_m <= .5):
        raise ValueError('PULSE_REQUIRES_RELEASED_AIRBORNE_BOTTOM_GE50MM')
    if not (.299 <= mass_kg <= .301) or not np.allclose(inertia,inertia.T,atol=1e-9,rtol=0):
        raise ValueError('UNEXPECTED_NATIVE_CUP_MASS_OR_INERTIA')
    eigenvalues = np.linalg.eigvalsh(inertia)
    if not (eigenvalues.min() > 1e-7 and eigenvalues.max() < .005 and eigenvalues.max()/eigenvalues.min() < 100):
        raise ValueError('INERTIA_NOT_FINITE_SPD_WITHIN_DECLARED_BOUNDS')
    # Positive z points upward. This is a free-COM-translation proxy; changing
    # cup footprint during rotation/contact is not represented by this estimate.
    vz, g = float(vertical_velocity_m_s), 9.81
    fall_s = (vz + math.sqrt(vz*vz+2*g*clearance_m))/g
    if fall_s < .05:
        raise ValueError('INSUFFICIENT_REMAINING_FALL_TIME_NO_PULSE')
    speed = min(30., (math.pi/2)/(fall_s-PULSE_S/2))
    target = np.array([-speed, 0., 0.])
    impulse = inertia @ (target-omega)
    torque = impulse / PULSE_S
    target_energy = float(.5*target @ inertia @ target)
    current_energy = float(.5*omega @ inertia @ omega)
    if np.linalg.norm(torque) > .5 or max(target_energy,current_energy) > .15:
        raise ValueError('TORQUE_OR_ROTATIONAL_ENERGY_BOUND_EXCEEDED_NO_PULSE')
    return dict(inertia_body_COM_kg_m2=inertia.tolist(), inertia_eigenvalues_kg_m2=eigenvalues.tolist(),
                original_omega_body_rad_s=omega.tolist(), target_omega_body_rad_s=target.tolist(),
                target_angle_freeflight_proxy_rad=float(speed*(fall_s-PULSE_S/2)),
                torque_body_Nm=torque.tolist(), angular_impulse_body_Nms=impulse.tolist(),
                force_body_N=[0.,0.,0.], pulse_native_steps=PULSE_STEPS,
                pulse_duration_s=PULSE_S, actual_clearance_m=float(clearance_m),
                actual_vertical_velocity_m_s=vz, remaining_fall_time_proxy_s=fall_s,
                target_rotational_energy_J=target_energy, initial_rotational_energy_J=current_energy,
                API_coordinates='pure torque about COM, body-prim/local axes; inertia9 column-major, no additional principal-axis quaternion rotation',
                model_limits='Ballistic rigid-body estimate, not a guaranteed final attitude or calibrated PBD two-way impulse model.')


def drop_verdict(*, elapsed_since_loss_s, stable_s, table_support_present,
                 speed_m_s, angular_speed_rad_s, tilt_deg, spill_particles):
    """Exact original C01b stable-fall decision thresholds, extracted for checks."""
    if not np.isfinite([elapsed_since_loss_s,stable_s,speed_m_s,angular_speed_rad_s,tilt_deg,spill_particles]).all() or spill_particles < 0:
        raise ValueError('INVALID_DROP_DIAGNOSIS_OBSERVATION')
    if not (elapsed_since_loss_s >= .5 and stable_s >= .25 and table_support_present
            and speed_m_s < .01 and angular_speed_rad_s < .1):
        return None
    return 'REPLAN_FROM_OBSERVED_POSE' if tilt_deg <= 10. and spill_particles == 0 else 'SAFE_ABORT_TIPPED_OR_SPILLED'


def assert_blocked_command(raw, held_open, *, heater_on=False, commanded_stage=None):
    """After monitor latches, only the exact sameEE/open command is permitted."""
    if heater_on or commanded_stage != 'safe_abort_observe':
        raise RuntimeError('UNSAFE_POST_BLOCK_PROGRESS_OR_HEATER_COMMAND')
    a, b = np.asarray(raw), np.asarray(held_open)
    if a.shape != (1,8) or not np.array_equal(a,b) or a[0,7] != 1.:
        raise RuntimeError('POST_BLOCK_COMMAND_IS_NOT_EXACT_HELD_EE_OPEN')


def angular_response(before_body_rad_s, after_world_rad_s, after_body_to_world):
    """Sanity response only; no match to predicted omega/causal attribution."""
    before = np.asarray(before_body_rad_s,dtype=float)
    after_world = np.asarray(after_world_rad_s,dtype=float)
    rotation = np.asarray(after_body_to_world,dtype=float)
    finite = bool(np.isfinite(np.r_[before.ravel(),after_world.ravel(),rotation.ravel()]).all())
    if not finite or before.shape != (3,) or after_world.shape != (3,) or rotation.shape != (3,3):
        return dict(finite_native_response=False,passed=False,
                    invalid_measurement_repr=repr((before,after_world,rotation)),
                    projected_negative_local_X_increase_rad_s=None)
    after_body = rotation.T @ after_world
    increase = float(before[0]-after_body[0])
    return dict(finite_native_response=True,before_omega_body_rad_s=before.tolist(),
                after_omega_world_rad_s=after_world.tolist(),after_omega_body_rad_s=after_body.tolist(),
                after_body_to_world_rotation=rotation.tolist(),
                projected_negative_local_X_increase_rad_s=increase,
                minimum_increase_rad_s=1.,passed=bool(increase>=1.),
                scope='Observed native response sanity; not exact predicted-omega agreement or attribution of later tip/spill to this torque alone.')

"""Four-state, once-only saved-state rate diagnosis; never a controller or rollout."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROBES = HERE.parent / 'actuator_velocity_ff_candidate/full_task_probes'
LIMITS = {
    'ur5e': {'vmax_rad_s': [3.141592653589793] * 6,
             'joint_names': ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint', 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint'],
             'source': 'https://raw.githubusercontent.com/UniversalRobots/Universal_Robots_ROS2_Description/f90e50e27036f285c9fb0ab2efbb5e10e69438ad/config/ur5e/joint_limits.yaml',
             'source_units': '!degrees 180.0 for all six; converted to pi rad/s'},
    'flexiv': {'vmax_rad_s': [2.0944, 2.0944, 2.4435, 2.4435, 4.8869, 4.8869, 4.8869],
              'joint_names': ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6', 'joint7'],
              'source': 'https://raw.githubusercontent.com/flexivrobotics/flexiv_description/920f4effba3f04acde78e6e79293a60093e60416/config/Rizon4/joint_limits.yaml',
              'source_units': 'rad/s; fixed decimal public values'},
}


def utc():
    return datetime.now(timezone.utc).isoformat()


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def relative(path):
    return str(path.relative_to(ROOT))


def prepare():
    """Read archived arrays/journals only; no MuJoCo or scientific solver import."""
    import numpy as np
    if (HERE / 'protocol.json').exists():
        raise RuntimeError('Protocol already prepared; do not replace selected inputs')
    cases = json.loads((PROBES / 'casebank.json').read_text())['cases']
    packets = []
    for case in cases:
        run = PROBES / 'runs' / case['robot'] / case['label']
        data = np.load(run / 'learning_data.npz')
        rates = data['desired_joint_velocities']
        peak_i, peak_j = np.unravel_index(np.abs(rates).argmax(), rates.shape)
        indices = [0, int(peak_i)]
        times = [float(data['times'][i]) for i in indices]
        ik_path = PROBES / 'attempt_details' / case['case_id'] / 'ik_diagnostics.jsonl'
        ff_path = run / 'velocity_ff_apply_readback.jsonl'
        matches = {'ik': {}, 'ff': {}}
        repeated_counts = {str(t): 0 for t in times}
        for kind, path in [('ik', ik_path), ('ff', ff_path)]:
            for line in path.open():
                row = json.loads(line)
                t = row['native_s'] if kind == 'ik' else row['control_time']
                for wanted in times:
                    if abs(t - wanted) < 1e-10:
                        if kind == 'ff':
                            repeated_counts[str(wanted)] += 1
                            if wanted in matches[kind]:
                                for key in ['qIK', 'actual_q_at_control', 'desired_joint_velocity', 'held_control_dt']:
                                    assert row[key] == matches[kind][wanted][key], 'Held-command records disagree'
                        elif wanted in matches[kind]:
                            raise RuntimeError('Multiple IK events for selected control time')
                        matches[kind].setdefault(wanted, row)
        for role, i, t in zip(['first_feedback', 'largest_abs_desired_joint_velocity'], indices, times):
            assert t >= 8.5 and t < 15 and t in matches['ik'] and t in matches['ff']
            packets.append({
                'robot': case['robot'], 'case_id': case['case_id'], 'role': role,
                'sample_index': i, 'native_s': t, 'peak_joint_zero_based': int(peak_j) if i == peak_i else None,
                'archive': relative(run / 'learning_data.npz'), 'scene': relative(run / 'scene.xml'),
                'ik_journal': relative(ik_path), 'ff_journal': relative(ff_path),
                'repeated_apply_rows_for_control': repeated_counts[str(t)],
                'arrays': {key: data[key][i].tolist() for key in [
                    'native_qpos', 'native_qvel', 'executed_actions', 'delayed_action_bases',
                    'actual_anchor_positions', 'actual_anchor_quaternions_xyzw', 'actual_control_dts',
                    'desired_joint_velocities', 'command_positions', 'command_quaternions_xyzw',
                    'goal_positions', 'goal_quaternions_xyzw']},
                'ik_record': matches['ik'][t], 'first_held_apply_record': matches['ff'][t],
            })
    assert len(packets) == 4
    protocol = {
        'registered_utc': utc(), 'scope': 'Four fixed archived control states; offline instantaneous kinematics only',
        'selection': 'Per robot index 0 and earliest row of global abs(desired_joint_velocities) argmax; no outcome filtering',
        'inputs': 'selected_inputs.json', 'source': 'analyze.py', 'site': 'rq_pinch',
        'maximum_explicit_mj_forward_calls': 4, 'maximum_mj_jacSite_calls': 4,
        'maximum_bounded_linear_solves': 4, 'maximum_per_state_each': 1,
        'native_steps': 0, 'controller_or_global_IK_calls': 0, 'GPU_contexts': 0,
        'rate_objective': 'min || [20 Jp; Jw; 0.001 I] qdot - [20 v_world; w_world; 0] ||_2',
        'world_twist': 'v_world=delayed_action_basis @ executed_action[3:]; w_world=delayed_action_basis @ executed_action[:3]',
        'bounds': 'max(-vmax,(original_model_joint_min+0.03-actual_q)/actual_dt) <= qdot <= min(vmax,(original_model_joint_max-0.03-actual_q)/actual_dt)',
        'position_constraint': 'One local Euler step of the recorded control dt; no nonlinear pose/path feasibility claim',
        'solver': {'function': 'scipy.optimize.lsq_linear', 'method': 'trf', 'lsq_solver': 'exact', 'tol': 1e-10, 'max_iter': 100},
        'singular_values': 'Raw 6xN geometric J and [20Jp;Jw]; raw mixes translation and rotation units; machine-precision rank criterion',
        'verified_velocity_sources': LIMITS,
        'velocity_source_verification': 'Both fixed-commit official YAMLs independently opened before protocol registration; joint order checked against saved MJCF at execution',
        'no_acceleration_constraint': 'No verified acceleration limits supplied; none guessed',
        'position_source_boundary': 'Keep original local MJCF ranges and 0.03 rad IK buffer; do not substitute official soft or planning positions (including UR elbow planning range)',
        'all_active_rate_summary': 'All 650 archived pre-control actual native_qvel samples per robot versus same vmax; desired rates separately reported; sampled counts, no duration inference',
        'limitations': ['No native dynamics, contact or new control/teacher execution',
                        'Linear optimizer termination does not establish exact twist feasibility or functional task success',
                        'Instantaneous Jacobian map is local; finite IK displacement and actual tracking dynamics differ',
                        'Cache decomposition alone cannot establish a global IK branch switch or unique cause',
                        'Velocity limits are external diagnostic references; original five physics gates and all F statuses unchanged',
                        'No parameter/seed/pose/regularization scans; no new controller; all 20-pilot switches remain disabled'],
    }
    write(HERE / 'selected_inputs.json', packets)
    write(HERE / 'protocol.json', protocol)
    print(json.dumps({'prepared': True, 'selected': [{k: p[k] for k in ['robot', 'role', 'sample_index', 'native_s', 'peak_joint_zero_based']} for p in packets]}))


def diagnose():
    import numpy as np
    import mujoco
    from scipy.optimize import lsq_linear
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '', 'CPU-only diagnostic requires empty CUDA mask'
    protocol = json.loads((HERE / 'protocol.json').read_text())
    packets = json.loads((HERE / 'selected_inputs.json').read_text())
    with (HERE / 'execution_once.json').open('x') as f:
        json.dump({'started_utc': utc(), 'protocol': 'protocol.json', 'pid': os.getpid(), 'one_run_only': True}, f)
    counts = {'explicit_mj_forward': 0, 'mj_jacSite': 0, 'bounded_linear_solves': 0, 'native_steps': 0}
    def forbidden(*args, **kwargs):
        raise RuntimeError('Native integration is forbidden in this offline diagnosis')
    mujoco.mj_step = mujoco.mj_step1 = mujoco.mj_step2 = forbidden
    results, summaries = [], {}
    for robot in ['ur5e', 'flexiv']:
        selected = [p for p in packets if p['robot'] == robot]
        assert len(selected) == 2
        model = mujoco.MjModel.from_xml_path(str(ROOT / selected[0]['scene']))
        n = len(LIMITS[robot]['vmax_rad_s'])
        joint_ids = model.actuator_trnid[:n, 0]
        qa, va = model.jnt_qposadr[joint_ids], model.jnt_dofadr[joint_ids]
        joint_names = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, int(j)) for j in joint_ids]
        assert joint_names == LIMITS[robot]['joint_names'], (robot, joint_names)
        site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, protocol['site'])
        assert site >= 0
        vmax = np.asarray(LIMITS[robot]['vmax_rad_s'])
        lo, hi = model.jnt_range[joint_ids, 0] + .03, model.jnt_range[joint_ids, 1] - .03
        archive = np.load(ROOT / selected[0]['archive'])
        actual_all = archive['native_qvel'][:, va]
        desired_all = archive['desired_joint_velocities']
        assert len(actual_all) == len(desired_all) == 650
        def velocity_summary(values):
            mask = np.abs(values) > vmax
            peak_i, peak_j = np.unravel_index(np.abs(values).argmax(), values.shape)
            return {'sample_count': len(values), 'joint_scalar_count': int(values.size),
                    'exceeding_joint_scalar_count': int(mask.sum()), 'samples_with_any_exceedance': int(mask.any(axis=1).sum()),
                    'exceeding_samples_per_joint': mask.sum(axis=0).tolist(),
                    'max_abs_per_joint_rad_s': np.abs(values).max(axis=0).tolist(),
                    'max_ratio_to_limit_per_joint': (np.abs(values) / vmax).max(axis=0).tolist(),
                    'global_peak': {'sample_index': int(peak_i), 'native_s': float(archive['times'][peak_i]),
                                    'joint': joint_names[peak_j], 'signed_rate_rad_s': float(values[peak_i, peak_j])}}
        summaries[robot] = {'joint_names': joint_names, 'qpos_indices': qa.tolist(), 'qvel_indices': va.tolist(),
                            'vmax_rad_s': vmax.tolist(), 'original_buffered_position_range_rad': np.c_[lo, hi].tolist(),
                            'actual_joint_rates': velocity_summary(actual_all), 'desired_FF_joint_rates': velocity_summary(desired_all)}
        for p in selected:
            a, ik, ff = p['arrays'], p['ik_record'], p['first_held_apply_record']
            q, qvel = np.asarray(a['native_qpos']), np.asarray(a['native_qvel'])
            actual = q[qa]; dt = float(a['actual_control_dts']); old_rate = np.asarray(a['desired_joint_velocities'])
            qik, prior = np.asarray(ik['nominal_q_after']), np.asarray(ik['prior_nominal_q'])
            assert np.array_equal(actual, np.asarray(ik['actual_arm_q_before']))
            assert np.array_equal(qik, np.asarray(ff['qIK']))
            assert np.array_equal(old_rate, np.asarray(ff['desired_joint_velocity']))
            assert dt == ff['held_control_dt'] and dt > 0
            data = mujoco.MjData(model)
            data.qpos[:] = q; data.qvel[:] = qvel; data.time = p['native_s']
            q_before, v_before = data.qpos.copy(), data.qvel.copy()
            mujoco.mj_forward(model, data); counts['explicit_mj_forward'] += 1
            jp_all, jw_all = np.zeros((3, model.nv)), np.zeros((3, model.nv))
            mujoco.mj_jacSite(model, data, jp_all, jw_all, site); counts['mj_jacSite'] += 1
            assert np.array_equal(data.qpos, q_before) and np.array_equal(data.qvel, v_before)
            jp, jw = jp_all[:, va], jw_all[:, va]
            basis, action = np.asarray(a['delayed_action_bases']), np.asarray(a['executed_actions'])
            v, w = basis @ action[3:], basis @ action[:3]
            j = np.vstack([jp, jw]); j_weighted = np.vstack([20 * jp, jw])
            singular = np.linalg.svd(j, compute_uv=False); singular_weighted = np.linalg.svd(j_weighted, compute_uv=False)
            def sv_summary(matrix, values):
                tol = values[0] * max(matrix.shape) * np.finfo(float).eps
                return {'singular_values': values.tolist(), 'rank_tolerance': float(tol), 'rank': int((values > tol).sum()),
                        'condition_number': float(values[0] / values[-1]) if values[-1] > 0 else None}
            def mapping(rate):
                vp, wp = jp @ rate, jw @ rate
                return {'linear_world_m_s': vp.tolist(), 'angular_world_rad_s': wp.tolist(),
                        'linear_error_world_m_s': (vp - v).tolist(), 'angular_error_world_rad_s': (wp - w).tolist(),
                        'linear_error_norm_m_s': float(np.linalg.norm(vp - v)), 'angular_error_norm_rad_s': float(np.linalg.norm(wp - w)),
                        'weighted_twist_error_norm': float(np.linalg.norm(np.r_[20 * (vp - v), wp - w]))}
            lower, upper = np.maximum(-vmax, (lo - actual) / dt), np.minimum(vmax, (hi - actual) / dt)
            if np.any(lower >= upper):
                projected = {'status': 'NOT_SOLVED_EMPTY_OR_ZERO_WIDTH_LOCAL_BOUNDS', 'lower': lower.tolist(), 'upper': upper.tolist()}
            else:
                design = np.vstack([20 * jp, jw, .001 * np.eye(n)])
                target = np.r_[20 * v, w, np.zeros(n)]
                fit = lsq_linear(design, target, bounds=(lower, upper), method='trf', lsq_solver='exact', tol=1e-10, max_iter=100)
                counts['bounded_linear_solves'] += 1
                projected = {'status': 'SOLVED_ONCE', 'solver_success': bool(fit.success), 'solver_status': int(fit.status),
                             'solver_message': str(fit.message), 'iterations': int(fit.nit), 'optimality': float(fit.optimality),
                             'cost': float(fit.cost), 'qdot_rad_s': fit.x.tolist(), 'lower_rad_s': lower.tolist(), 'upper_rad_s': upper.tolist(),
                             'active_mask': fit.active_mask.tolist(), 'predicted_one_step_joint_positions_rad': (actual + dt * fit.x).tolist(),
                             'maximum_abs_rate_ratio': float(np.max(np.abs(fit.x) / vmax)), 'mapping': mapping(fit.x),
                             'interpretation': 'Regularized local bounded least-squares fit; not an exact-feasibility certificate or controller result'}
            branch_delta, tracking_delta = qik - prior, prior - actual
            record = {'robot': robot, 'role': p['role'], 'sample_index': p['sample_index'], 'native_s': p['native_s'], 'actual_control_dt_s': dt,
                      'joint_names': joint_names, 'actual_q_rad': actual.tolist(), 'actual_qvel_rad_s': qvel[va].tolist(),
                      'requested_twist': {'linear_world_m_s': v.tolist(), 'angular_world_rad_s': w.tolist(), 'executed_action_angular_then_linear': action.tolist(), 'historical_basis': basis.tolist()},
                      'jacobian_world_linear': jp.tolist(), 'jacobian_world_angular': jw.tolist(),
                      'jacobian_spectrum': sv_summary(j, singular), 'weighted_jacobian_spectrum': sv_summary(j_weighted, singular_weighted),
                      'FK_actual_anchor_position_error_m': float(np.linalg.norm(data.site_xpos[site] - np.asarray(a['actual_anchor_positions']))),
                      'FK_archived_ee_position_error_m': float(np.linalg.norm(data.site_xpos[site] - np.asarray(ik['actual_ee_position_before_m']))),
                      'original_accepted_ik_diagnostic': ik['diagnostic'],
                      'decomposition': {'identity': 'qIK-actual = (qIK-prior_cache) + (prior_cache-actual)',
                                        'qIK_rad': qik.tolist(), 'prior_nominal_q_rad': prior.tolist(),
                                        'qIK_minus_actual_rad': (qik - actual).tolist(), 'qIK_minus_prior_cache_rad': branch_delta.tolist(),
                                        'prior_cache_minus_actual_rad': tracking_delta.tolist(),
                                        'IK_increment_over_dt_rad_s': (branch_delta / dt).tolist(), 'cache_tracking_gap_over_dt_rad_s': (tracking_delta / dt).tolist(),
                                        'max_abs_IK_increment_rad': float(np.abs(branch_delta).max()), 'max_abs_cache_tracking_gap_rad': float(np.abs(tracking_delta).max()),
                                        'old_rate_formula_error_rad_s': float(np.max(np.abs(old_rate - (qik - actual) / dt))),
                                        'additive_rate_identity_error_rad_s': float(np.max(np.abs(old_rate - branch_delta / dt - tracking_delta / dt)))},
                      'old_FF_qdot_rad_s': old_rate.tolist(), 'old_FF_mapping': mapping(old_rate),
                      'actual_joint_qvel_mapping': mapping(qvel[va]), 'projected_local_rate': projected,
                      'first_apply_ctrl_clipping_flags': ff['control_limit_saturated'],
                      'first_apply_held_nominal_outside_physical_joint_range': ff['held_nominal_outside_physical_joint_range'],
                      'state_and_velocity_unchanged_by_offline_FK': True}
            results.append(record)
            write(HERE / 'result.json', {'status': 'OFFLINE_DIAGNOSIS_IN_PROGRESS', 'protocol': 'protocol.json', 'counts': counts, 'selected_states': results, 'active_rate_summaries': summaries})
    assert counts == {'explicit_mj_forward': 4, 'mj_jacSite': 4, 'bounded_linear_solves': 4, 'native_steps': 0}
    write(HERE / 'result.json', {'status': 'OFFLINE_DIAGNOSIS_COMPLETE', 'closed_utc': utc(), 'protocol': 'protocol.json',
                                'inputs': 'selected_inputs.json', 'counts': counts, 'selected_states': results,
                                'active_rate_summaries': summaries, 'velocity_limit_sources': LIMITS,
                                'limitations': protocol['limitations'], 'functional_success_claimed': False,
                                'new_controller_implemented': False, 'native_or_training_authorized': False,
                                'original_F_statuses_and_success_gates_unchanged': True})
    print(json.dumps({'status': 'COMPLETE', 'counts': counts, 'result': str(HERE / 'result.json')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--execute-offline-once', action='store_true')
    args = parser.parse_args()
    if args.prepare == args.execute_offline_once:
        parser.error('Choose exactly one phase')
    prepare() if args.prepare else diagnose()

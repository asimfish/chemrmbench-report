"""Plot closed native traces only; no simulator, dynamics or IK calls."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

B = Path(__file__).resolve().parent


def main():
    result = json.loads((B / 'result.json').read_text())
    assert (result['started'], result['closed'], result['successes']) == (2, 2, 0)
    with (B / 'runs/ur5e/velocity_ff_script_expert_56002/trace.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    t = np.asarray([float(row['time_s']) for row in rows])
    counts = {key: np.asarray([int(row[key]) for row in rows])
              for key in ['source_count', 'receiver_count', 'spill_count']}
    assert np.all(sum(counts.values()) == 240)
    release = result['failure_analysis']['ur5e']['first_postfeedback_outside_increase']['native_s']
    path = B / 'attempt_details/flexiv_velocity_ff_script_expert_56002/ik_diagnostics.jsonl'
    ik = [json.loads(line) for line in path.read_text().splitlines()]
    ik = [row for row in ik if not row['initial'] and row['native_s'] >= 8.5]
    ti = np.asarray([row['native_s'] for row in ik])
    actual_q4 = np.asarray([row['actual_arm_q_before'][3] for row in ik])
    nominal_q4 = np.asarray([row['diagnostic']['q'][3] for row in ik])
    residual = np.asarray([row['diagnostic']['orientation_error_rad'] for row in ik])
    rejected = np.asarray([not row['accepted'] for row in ik])
    assert rejected.sum() == 1 and rejected[-1]
    apply_path = B / 'runs/flexiv/velocity_ff_script_expert_56002/velocity_ff_apply_readback.jsonl'
    with apply_path.open() as stream:
        q4_min = json.loads(next(stream))['IK_buffered_joint_range'][3][0]
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False, 'pdf.fonttype': 42})
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
    fig.subplots_adjust(left=.05, right=.985, bottom=.23, top=.78, wspace=.34)
    ax = axes[0]
    for key, label, color in [('source_count', 'In source', '#6d7885'),
                              ('receiver_count', 'In receiver', '#167d9a'),
                              ('spill_count', 'Outside / flight', '#c47722')]:
        ax.step(t, counts[key], where='post', label=label, color=color, lw=1.8)
    ax.axvspan(8.5, 15, color='#dbe9f0', alpha=.45, zorder=-1)
    ax.axvline(release, color='#a04642', ls=':', lw=1.5)
    ax.annotate('64 retained at feedback end', xy=(15.002, 64), xytext=(11.4, 118),
                fontsize=8.5, arrowprops={'arrowstyle': '->', 'color': '#555'})
    ax.text(19.6, 105, '62 of these become\noutside after release', fontsize=8.5)
    ax.set(xlim=(8, 23.2), ylim=(-5, 280), xlabel='Native time (s)', ylabel='Particles',
           title='A  UR5e: residual payload is released later')
    ax.legend(loc='upper right', fontsize=8, frameon=False)
    ax = axes[1]
    ax.plot(ti, actual_q4, color='#167d9a', label='Actual q4', lw=1.5)
    ax.plot(ti, nominal_q4, color='#b36d2a', label='IK q4', lw=1.3, alpha=.8)
    ax.axhline(q4_min, color='#a04642', ls=':', label='Original buffered lower limit')
    ax.axvline(ti[-1], color='#a04642', ls=':', lw=1)
    ax.set(xlim=(8.4, 16.2), xlabel='Native time (s)', ylabel='Joint angle (rad)',
           title='B  Flexiv: return reaches a joint bound')
    ax.legend(loc='upper right', fontsize=8, frameon=False)
    ax = axes[2]
    ax.plot(ti, residual, color='#167d9a', lw=1.5, label='Optimized IK residual')
    ax.axhline(.02, color='#555', ls='--', lw=1, label='Original 0.02 rad gate')
    ax.scatter(ti[rejected], residual[rejected], color='#a04642', zorder=4, s=36)
    ax.annotate('Rejected at 16.040 s', xy=(ti[-1], residual[-1]), xytext=(15.03, .0138),
                fontsize=8.5, arrowprops={'arrowstyle': '->', 'color': '#555'})
    ax.set(xlim=(14.95, 16.13), ylim=(-.0005, .023), xlabel='Native time (s)',
           ylabel='Orientation residual (rad)', title='C  Original local-IK acceptance fails')
    ax.legend(loc='upper left', fontsize=8, frameon=False)
    for ax in axes:
        ax.grid(alpha=.18)
    fig.suptitle('Two known full-task probes: 0 / 2 pass the original full-episode gates',
                 y=.97, fontsize=15)
    fig.text(.5, .87, 'Same CPU world, seed 56002; actual anchor + held velocity feedforward',
             ha='center', fontsize=11)
    fig.text(.5, .11, 'UR5e: 175 / 240 received, 63 outside.  Flexiv: 232 / 240 received; return stops at 16.040 s.',
             ha='center', fontsize=10)
    fig.text(.5, .055, 'Sampled native traces and recorded IK only; no new physics. Chronology does not prove a unique cause or global unreachability.',
             ha='center', fontsize=9)
    for suffix in ['png', 'pdf']:
        fig.savefig(B / ('failure_timeline.' + suffix), dpi=180)
    plt.close(fig)
    print(json.dumps({'figure': str(B / 'failure_timeline.png'),
                      'native_steps': 0, 'UR_trace_rows': len(rows),
                      'Flex_recorded_IK_rows': len(ik)}))


if __name__ == '__main__':
    main()

"""Three local resolutions plus a source-pinned, pixel-digitized VOF reference.

No fitted time shift, solver tuning, original F acceptance change, or claim that
a shrinking pairwise difference proves asymptotic convergence.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def main():
    destination = HERE/'convergence.json'
    assert not destination.exists(), 'Preserve the completed supplement'
    grid = np.linspace(0, 3, 301)
    curves, rows = [], []
    for label, dx in [('dam_break_native_trace', .01), ('dam_break_intermediate_convergence', .0075), ('dam_break_refinement', .005)]:
        folder = HERE/'runs'/label
        d = read(folder/('result.json' if (folder/'result.json').exists() else 'metrics.json'))
        sample = read(folder/'samples.json')
        T = np.r_[0, [r['t'] for r in sample]]*np.sqrt(2*9.81/.06)
        Z = np.r_[1, [r['front_x_m']/.06 for r in sample]]
        curves.append(np.interp(grid, T, Z))
        rows.append(dict(label=label, particles=d['metrics']['particles'], spacing_m=dx,
                         raw_experiment_max_relative_error=d['dam_break_comparison']['max_relative_error'],
                         meets_original_local_10pct_gate=d['dam_break_comparison']['max_relative_error'] <= .1,
                         source=f'f_tier/A01/runs/{label}/samples.json'))
    differences = []
    for index in range(2):
        delta = curves[index+1]-curves[index]
        differences.append(dict(pair=[rows[index]['particles'], rows[index+1]['particles']],
                                RMS_delta_Z=float(np.sqrt(np.mean(delta**2))), max_absolute_delta_Z=float(np.max(np.abs(delta)))))
    # This source image's axes are exact known plotted ranges: T0..3.5, Z1..4.
    # Black curve/markers; red experimental points and legend are not the curve.
    image = np.asarray(Image.open(HERE/'lethe_reference_front.png').convert('RGB'))
    assert image.shape[:2] == (480, 640)
    pixels = []
    for x in range(100, 531):
        ys = np.flatnonzero(np.all(image[64:424, x, :] < 80, axis=1))+64
        # Exclude the source legend's rectangle. Where red experiment markers
        # occlude the numerical curve, no dark curve pixels can be extracted;
        # those columns remain gaps rather than becoming black legend text.
        if x <= 407:
            ys = ys[ys > 114]
        if len(ys):
            bottom = ys.max()
            # The numerical curve is the lowest dark connected segment in each
            # column. The detached legend is above it wherever they overlap X.
            ys = ys[ys >= bottom-8]
            pixels.append([x, float(np.median(ys))])
    pixels = np.asarray(pixels)
    corrected_T = (pixels[:, 0]-80)/(576-80)*3.5
    digitized_Z = 1+(427-pixels[:, 1])/(427-58)*3
    raw_T = corrected_T-.175  # Undo, rather than fit, the publisher's correction.
    usable = (raw_T >= .25) & (raw_T <= 3)
    raw_T, digitized_Z = raw_T[usable], digitized_Z[usable]
    assert len(raw_T) > 200 and np.min(digitized_Z) >= 1
    reference_grid = np.linspace(max(.25, raw_T.min()), min(3., raw_T.max()), 251)
    reference_Z = np.interp(reference_grid, raw_T, digitized_Z)
    for row, curve in zip(rows, curves):
        native = np.interp(reference_grid, grid, curve)
        delta = native-reference_Z
        row['digitized_VOF_comparison'] = dict(RMSE_Z=float(np.sqrt(np.mean(delta**2))),
            mean_relative_error=float(np.mean(np.abs(delta/reference_Z))),
            max_relative_error=float(np.max(np.abs(delta/reference_Z))))
    np.savetxt(HERE/'reference_lethe/digitized_front.csv', np.c_[raw_T, digitized_Z], delimiter=',',
               header='raw_dimensionless_T,digitized_front_Z', comments='')
    result = dict(status='THREE_RESOLUTION_AND_PUBLIC_NUMERICAL_COMPARISON_COMPLETE',
        completed_utc=datetime.now(timezone.utc).isoformat(), new_native_runs=1,
        local_resolutions=rows, pairwise_differences=differences,
        adjacent_RMS_difference_ratio=differences[1]['RMS_delta_Z']/differences[0]['RMS_delta_Z'],
        interpretation='Adjacent differences shrink modestly, while agreement with the1952experiment worsens under refinement. Neither the coarse pass nor this three-level trend establishes asymptotic convergence or physical validity.',
        dissipation_hypothesis='Reduced numerical dissipation under refinement and unmodeled release/bottom effects can explain a faster front. These data do not isolate that cause from boundary/finite-width/solver-discretization errors; no viscosity/clock correction was fitted.',
        count_correction='240/1920/15360 are the separate robot-pour resolutions. The existing dam-break column is432/3456; a1024-particle intermediate preserves its0.06x0.06x0.12m geometry instead of changing the shape to force requested counts.',
        numerical_reference=dict(method='Lethe2023 two-phase VOF Q1-Q1/BDF1, slip walls, adaptive refinement3..5 (finest nominaldx=1/32, columnwidth/dx112).',
            commit='34d345af9ca9c05214cc7ebced1e65e94643bb27',
            source='https://github.com/chaos-polymtl/lethe/tree/34d345af9ca9c05214cc7ebced1e65e94643bb27/doc/source/examples/multiphysics/dam-break',
            figure='f_tier/A01/lethe_reference_front.png', digitized_data='f_tier/A01/reference_lethe/digitized_front.csv',
            raw_numerical_data_available=False, pixel_uncertainty=dict(assumed_pixels=5, T=.0353, Z=.0407),
            time_shift_fitted=False, undo_publisher_dimensionless_time_shift=.175,
            comparability='Same height/width2, nondimensional variables. Independent two-dimensional two-phase slip-wall reference versus finite-width3D single-phase localDFSPH; gravity/viscosity scales imply unequal Reynolds numbers. Pixel data supports a descriptive comparison only, not a high-precision validation gate.'),
        acceptance_changed=False)
    destination.write_text(json.dumps(result, indent=2)+'\n')
    canonical = read(HERE/'result.json')
    canonical['dam_break_convergence_supplement'] = result
    note = 'Three dam-break resolutions432/1024/3456 have raw experiment errors8.04/11.15/14.52%; pairwise trend does not establish convergence. A source-pinned2023 LetheVOF figure is digitized with pixel uncertainty and its published+.175time shift undone, not fitted.'
    if note not in canonical['differences']: canonical['differences'].append(note)
    (HERE/'result.json').write_text(json.dumps(canonical, indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), layout='constrained')
    for row, curve, color in zip(rows, curves, ['#35788f', '#d99938', '#9e4b61']):
        axes[0].plot(grid, curve, color=color, label=f"{row['particles']}particles")
    experiment = read(HERE/'runs/dam_break_native_trace/result.json')['dam_break_comparison']
    axes[0].scatter(experiment['T_ref'], experiment['Z_ref'], marker='x', color='black', s=20, label='Martin & Moyce1952')
    axes[0].plot(raw_T, digitized_Z, color='#333', ls='--', label='Lethe2023VOF, digitized/raw time')
    axes[0].set(xlabel='T = t sqrt(2g/a)', ylabel='Front Z = x/a', xlim=(0, 3), title='Unshifted front position')
    axes[0].legend(frameon=False, fontsize=7)
    axes[1].plot(grid, curves[1]-curves[0], label='1024−432')
    axes[1].plot(grid, curves[2]-curves[1], label='3456−1024')
    axes[1].set(xlabel='T = t sqrt(2g/a)', ylabel='Adjacent resolution difference in Z', title='Modest shrinking differences; no proven order')
    axes[1].legend(frameon=False, fontsize=8)
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(alpha=.15)
    fig.supxlabel('One run per local resolution. Source figure digitization: ±5pixels; different3D/2D and Reynolds numbers.', fontsize=8)
    fig.savefig(HERE/'convergence.pdf')
    fig.savefig(HERE/'convergence.png', dpi=170)
    plt.close(fig)
    print(json.dumps(dict(rows=rows, pairwise=differences, ratio=result['adjacent_RMS_difference_ratio'])))


if __name__ == '__main__':
    main()

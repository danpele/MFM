"""Public Quantlet presentation only: retain all fitted models and statistics."""
CASE_NOTE = """The Hill intervals condition on the chosen tail threshold k; the block-bootstrap interval accounts for dependence through the resampled blocks, but not uncertainty from choosing k; persistence intervals and the IGARCH boundary test appear in the GARCH summary. A profile interval touching one permits an unbounded half-life: a finite point estimate does not resolve that uncertainty. Losses, VaR and ES use percentage-return units. The MCS and comparative ES zones rank forecasts relative to competitors; inclusion does not establish absolute calibration. Kupiec and DQ can still reject a relatively well-ranked model."""
NSE_NOTE = """The annual measures |VR−1| and AR(1) R² measure departures from the corresponding no-predictability benchmark. A negative change means less measured predictability under that proxy, not proof of market efficiency in every sense. The IQR is dispersion across 27 specifications on the same data, not a sampling confidence interval. Compare it with the median within-specification SE, while retaining the different targets of the three change measures. Relative differences can become very large when the preceding annual measure is near zero; a large percentage is not automatically evidence of an economically large change. The Anderson–Darling statistics rank distributional differences descriptively: the groups share data and specifications, so the independent-sample critical value is not a calibrated significance test here. For differences, the displayed SE uses sd/√n and ignores serial dependence; for the trend, the scaling mean is treated as fixed."""
CASE_PRINT = """# Summaries of results already computed above.
import json
print('Tail behaviour and sample facts')
print(json.dumps(RES['facts'], indent=1, default=float))
print('GARCH parameters and profile-likelihood inference')
_garch_summary = {k: v for k, v in RES['garch'].items() if k != 'profile'}
_garch_summary['profile'] = {k: v for k, v in RES['garch']['profile'].items() if k not in ('grid', 'lr')}
print(json.dumps(_garch_summary, indent=1, default=float))
print('Expected shortfall summaries and the 2020 VaR episode')
print(json.dumps({k: RES[k] for k in ('es', 'var_2020')}, indent=1, default=float))
"""
NSE_PRINT = """# Summaries of the same 27 paths shown below.
import json
print('Across-specification dispersion and within-specification standard errors')
print(json.dumps({label: {k: v for k, v in NSE[label].items() if k != 'table'}
                  for label in NSE_INDICES.values()}, indent=1, default=float))
print('Anderson–Darling statistics are descriptive here; groups are dependent.')
"""
def apply(nb, name):
    if name not in ('MFM_ch19_case_study', 'MFM_ch19_nonstandard_errors'):
        return nb
    note = CASE_NOTE if name.endswith('case_study') else NSE_NOTE
    for cell in nb['cells']:
        src = ''.join(cell['source'])
        if cell['cell_type'] == 'code':
            src = src.replace("CHART_DIR = '.'", "CHART_DIR = OUT_DIR if globals().get('SAVE_TO_DRIVE') else '.'")
            # Only the saving helpers have this close/print sequence.
            src = src.replace('    plt.close()\n    print(f"   saved {name}")', '    plt.show()\n    plt.close()\n    print(f"   saved {name}")') if '    plt.show()\n    plt.close()\n    print(f"   saved {name}")' not in src else src
            if name.endswith('case_study') and src.startswith('part_facts()') and CASE_PRINT not in src:
                src = src.replace("pd.DataFrame(RES['backtest']).T.round(4)", CASE_PRINT + "pd.DataFrame(RES['backtest']).T.round(4)")
            if name.endswith('nonstandard_errors') and src.startswith('part_nse()') and NSE_PRINT not in src:
                src = src.replace('pd.concat(', NSE_PRINT + 'pd.concat(', 1)
        else:
            if src == '## Analysis':
                src += '\n\n' + note
            if src.startswith('![ch19_'):
                # Repository figures are reference snapshots, not fresh cell outputs.
                label = src.split(']')[0][2:]
                assert src == f'![{label}](./{label}.png)\n\nOutput: `{label}.pdf`', 'Unexpected caption: preserve it explicitly'
                src = f'Figure file: [{label}](./{label}.png). The analysis displays its freshly generated figure inline and saves PDF and PNG files in CHART_DIR.'
        cell['source'] = src
    code = '\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type'] == 'code')
    markdown = [''.join(c['source']) for c in nb['cells'] if c['cell_type'] == 'markdown']
    expected_print = CASE_PRINT if name.endswith('case_study') else NSE_PRINT
    assert code.count(expected_print) == 1, 'Expected one analysis summary insertion'
    assert code.count("CHART_DIR = OUT_DIR if globals().get('SAVE_TO_DRIVE') else '.'") == 1
    assert code.count('    plt.show()\n    plt.close()\n    print(f"   saved {name}")') == 1
    assert sum(note in text for text in markdown) == 1, 'Expected one interpretation note'
    return nb

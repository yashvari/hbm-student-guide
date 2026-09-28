# Head-drop results: a beginner's guide

VIVA+ 50F head lateral drop at 3.5 m/s, adapted for OpenRadioss.
Analysis of `head_drop_final_history.csv`, from the completed 11 ms run with animation output every 0.1 ms.

## The short answer

The simulation completed and all 1,100 rows × 647 numeric columns are finite. However, the support-force curve does **not** reproduce the published experimental response closely. Our filtered peak is about 15% lower and arrives later. Successful calculation and scientific validation are two different things. The solver finishing is the beginning of the checking—not a graduation certificate for the model!

## What to show, in this order

1. **Animation:** what moves, deforms and rebounds. Describe it as a head-component drop test, not a whole-body sled test.
2. **01_force_comparison.png:** the most important scientific comparison. Grey shows the published experimental corridor; black is the experimental average; dashed curves are published LS-DYNA results; teal is this adapted OpenRadioss run.
3. **02_energy_checks.png:** energy changes and added mass. Energy of motion decreases as the head/pad system deforms. These checks help detect numerical problems, but do not prove experimental accuracy.
4. **03_head_motion.png:** downward displacement, slowing down and rebound. The velocity starts at −3.5 m/s; positive Z velocity later means rebound. Acceleration now shows CFC1000 filtering with a faint raw trace.
5. **04_acceleration_filtered.png:** a larger raw-versus-filtered acceleration plot. Use this when explaining signal processing. Neither acceleration peak is an injury prediction.

PNG files are for sharing; PDF files retain vector lines for reports. The numerical tables and Python script support reproducibility.

## Main numbers

| Curve | Peak force (kN) | Time of peak on comparison axis (ms) |
|---|---:|---:|
| Experimental average | 4.601 | 3.325 |
| Published LS-DYNA, cortical MAT124 | 4.785 | 3.110 |
| Published LS-DYNA, cortical MAT81 | 4.825 | 3.260 |
| Our OpenRadioss, CFC1000 | 3.913 | 4.960 |

The OpenRadioss filtered peak is 14.95% below the experimental average and 1.635 ms later using the stated time convention. Its curve is broader and contains a later secondary rise; looking only at the peak would hide these differences. These are descriptive comparisons, not an acceptance score or proof of a solver defect.

The final saved time is 10.99029 ms (the requested run end was 11 ms). Total system mass stays at 21.08616 kg: this includes the test setup, **not just the head**. Initial kinetic energy is 21.52119 J; final internal energy is 18.86751 J and final kinetic energy is 2.916282 J. Peak absolute hourglass energy is approximately 0.149% of initial kinetic energy. Added mass is approximately zero; the exported tiny negative value is consistent with numerical round-off. No universal pass/fail threshold is implied by these figures.

## How we made a fairer comparison

### Same type of force

We used the X/Y/Z support reactions at primary node 9041005 of rigid part 100003. The Starter listing connects that node to the constrained bottom support. We did **not** compare the head-pad contact-force resultant with the load-cell reference: these are different measurements and can have different peaks.

### Filtering

The reference processing definition `_env/04_yoganandan_load_cell_force.def` filters each reaction-force component with CFC1000, then takes the vector magnitude. We follow this order. Think of filtering as reducing very fast fluctuations, not as making the curve agree with experiments.

For reproducibility, the **force analysis** uses the CFC implementation from **Dynasaur 1.3.18**, unmodified, with `mirroring=False`, time expressed in milliseconds and the appropriate conversion to seconds. The original version used to generate the published CSVs is not established, so exact historical filter equivalence is not claimed. The upstream implementation and its end treatment are retained without correction. The original package, including its licence, is in `vendor/`.

Our exported time intervals vary from 0.009719 to 0.010090 ms. Before filtering we linearly interpolate each force component onto 1,100 equally spaced points over the original time range (0.010000263876 ms interval). The published LS-DYNA CSVs are already processed and are **not filtered again**. The raw OpenRadioss force is also shown faintly; its peak is 3.918 kN, so filtering does not explain the disagreement.

### Head acceleration: CFC1000 update

NHTSA's THOR-50M head-impact procedure (August 2016, section 4.6 and Table 4-2, printed page 32) specifies CFC1000 for each head CG acceleration component and then calculates the resultant. We use this established head-impact convention for our educational nodal plot; we are not claiming the HBM is a THOR dummy or that this is the exact processing prescribed by the Yoganandan experiment.

The acceleration routine uses the coefficient equations in SAE J211-1 (1995), Appendix C, with CFC = 1000. A second-order Butterworth section is applied forward and backward using SciPy `filtfilt`, producing the usual four-pole phaseless response. CFC1000 is a filter class, not a sharp cutoff at 1000 Hz. We do not apply a moving average or select a stronger filter merely for appearance.

Processing order: linearly resample AX/AY/AZ onto the same uniform time grid (~100 kHz), filter each component, calculate sqrt(AX² + AY² + AZ²), then convert to g. Endpoint handling uses odd reflection about each endpoint value for 1,000 samples (slightly over 10 ms) at each end, with steady-state filter initialization. This acceleration implementation retains exact sample alignment and uses its own documented endpoint handling; it does not call the legacy Dynasaur force routine. No gravity removal or measurement-offset correction is applied to these simulated kinematic accelerations. This is not a reconstruction of a physical accelerometer's complete measurement chain.

The filtered curve is shown prominently and raw data faintly. Displacement and velocity are not filtered. Endpoint behaviour can depend on the padding assumption, and offline filtering can spread a sharp event into neighbouring samples. Filtering cannot fix aliased output, a material-model error or a model-validation discrepancy. Full SAE channel compliance is not established by choosing a digital filter alone.

`processed_head_acceleration.csv` contains time, filtered components and filtered resultant; `numerical_checks.json` includes raw and filtered peaks. Source: [NHTSA head qualification procedure](https://www.nhtsa.gov/sites/nhtsa.gov/files/thor-50m_qualification_august2016.pdf), and [public SAE J211-1 (1995) text, Appendix C](https://law.resource.org/pub/us/cfr/ibr/005/sae.j211-1.1995.html).

### Time alignment

The published validation notebook subtracts **1 ms** from both 3.5 m/s LS-DYNA histories. We apply the same plotting convention to OpenRadioss and keep experiment times unchanged. We do not shift peaks to make them match. Equivalent physical contact onset has not been independently established. The energy and motion plots use original simulation time, without this shift.

### Units

- Simulation: mm, ms, kg; force is kN and energy is J.
- 1 mm/ms = 1 m/s.
- Experiment CSVs: seconds and newtons, converted to milliseconds and kilonewtons.
- Acceleration plot: magnitude of global AX/AY/AZ at node 1090010 after component-wise CFC1000 filtering, divided by 0.00980665 mm/ms² per g. The raw resultant is retained as a comparison. Gravity is retained; this is not HIC or another injury metric.

## Limitations to keep visible

- This is an adapted educational model, not an independently validated replacement for the published LS-DYNA model.
- The published notebook identifies VIVA+ 2.0.0 beta 1 and LS-DYNA mpp d R12.1. Do not label our head submodel VIVA+ 2.0.2 merely because that version was downloaded for a separate full-body attempt.
- The experimental corridor is reproduced as supplied; it should not be described as a statistical confidence interval without checking its construction.
- Curves 10, 112 and 150 in the setup were reordered by abscissa for import. This changed the input representation; its physical implications and any load/unload interpretation still require review. The successful Starter check alone does not validate this modification.
- Input-path and unit declarations were adapted; solver mappings, contact settings, material behaviour, mesh dependence and time-step sensitivity remain to be assessed.
- Energy plots show exported channels separately. They are not a reconstructed complete solver energy balance; do not sum every channel because some contributions may overlap.
- All values being finite is necessary, not sufficient. The force discrepancy remains material.
- Published reference curves were extracted from the user's validation archive. They were not generated by us and should be credited accordingly.

## Sensible next scientific step

Before changing parameters to improve a plot, check the head/pad material mapping and the reordered curve definitions against the original setup. Confirm model/version and contact-onset equivalence. Then run controlled sensitivity checks, changing one justified setting at a time. Do not tune directly to the experimental peak and call that validation.

For a first student release, show the working workflow and the discrepancy openly. Students learn more from a clearly explained limitation than from a suspiciously perfect overlay.

## Reproduce the figures

From the repository root, install the versions in `analysis/requirements.txt`, then run:

```bash
python analysis/analyze.py
```

The script reads `analysis/data/` and the bundled upstream filter module in `analysis/vendor/`. Figures are written to `figures/`; derived tables and checks are written under `analysis/`. It regenerates the plots, `force_metrics.csv`, `numerical_checks.json`, `processed_support_force.csv` and `input_sha256.json`. No solver rerun is needed. It overwrites only these analysis outputs. Duplicate part titles in the history header are not merged; selected node/global columns are located explicitly.

The reference data files retain their upstream ownership and terms. This package is an analysis working copy; review the original archive's licences and attribution requirements before redistributing it publicly. The bundled Dynasaur wheel includes its GPL licence. Do not remove it or claim ownership of upstream code or data.

## Sources and credits

- [VIVA+ validation case and reference notebook](https://vivaplus-validation.readthedocs.io/en/latest/Yoganandan-2004-Head-lateral-drop/Yoganandan-2004.html)
- [VIVA+ model documentation](https://vivaplus.readthedocs.io/)
- [Dynasaur source project](https://gitlab.com/VSI-TUGraz/Dynasaur)
- [Dynasaur 1.3.18 package](https://pypi.org/project/dynasaur/1.3.18/)
- [OpenRadioss](https://www.openradioss.org/)

Reference archive paths are under `catalog/Yoganandan-2004-Head-lateral-drop/`:

- `data/experiment/3.5avg.csv` and `3.5corr.csv`
- `data/processed/dyna/50F/drop_test/drop_3.5/Dynasaur_output.csv` (MAT124)
- `data/processed/dyna/50F/drop_test_mat81/drop_3.5/Dynasaur_output.csv` (MAT81)
- `Yoganandan-2004.ipynb` and `_env/04_yoganandan_load_cell_force.def`

Credit VIVA+ and the original test/model/setup contributors. Yash Kumar Vari's contribution is the educational OpenRadioss adaptation, execution, troubleshooting and documented workflow—not the original HBM or published reference simulations. This independent educational project does not imply Audi endorsement.

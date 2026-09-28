# Input adaptation record

The upstream case is `catalog/Yoganandan-2004-Head-lateral-drop/dyna/50F/drop_test/drop_3.5/main.key` in the VIVA+ validation archive. The local working copy changed:

1. Inserted `*CONTROL_UNITS` / `mm        ms        kg` after `*KEYWORD`.
2. Changed its `*INCLUDE_PATH_RELATIVE` for the head from `../../../../../submodels/` to `../../../../../../submodels/Head/` to resolve includes in this archive arrangement.
3. Replaced only the setup include filename with `yoganandan_2005_setup-openradioss.key`.
4. Sorted point pairs by abscissa in curves **10, 112 and 150** in a *copy* of `setup/yoganandan_2005_setup.key`. Original numerical pairs are retained, but changing their order can change interpolation and physical meaning; it has not been established whether these three curves affect the head-drop response. Active pad material 10 references curve 11, which was not reordered.
5. For smoother animation only, shortened output interval to 0.1 ms; history exports used about 0.01 ms sampling. The exact final HPC job deck and version metadata should be archived before anyone claims a byte-for-byte rerun.

`original_automation_record.py` records the initial curve reordering procedure and expected inversion counts. It was written for the local working directory and is **not** a one-command reproducible installer. Compare every generated deck and archive its hash. The result files here enable the figures to be reproduced without rerunning the solver.

Important: the published reference notebook identifies VIVA+ **2.0.0 beta 1** with LS-DYNA R12.1. Whether the exact archived input revision generated the published curves has not been established. The separate later VIVA+ 2.0.2 download is unrelated to this run.

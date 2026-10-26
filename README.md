# Geospatial Eye-Tracking Dataset: Technical Validation Code

Python notebooks and a script for technical validation and visualization of an eye-tracking dataset collected during geospatial tasks. The analyses cover STAT, TMA, SLSO, and STT; STAT-A and STAT-B are combined as STAT where applicable.

## Contents

The original analysis folder names and relative input paths are retained.

| Folder under `code/` | Entry point | Purpose |
| --- | --- | --- |
| `AOI fixation count proportions by response accuracy/` | `AOI.ipynb` | Compare key-AOI and correct-answer-AOI fixation count proportions between correct and incorrect responses. |
| `comparisons between geography and non-geography participants/` | `group_comparisons.ipynb` | Compare participant-level eye-movement measures between academic-background groups. |
| `example pupil diameter traces from four recording segments/` | `pupil.py` | Plot left-eye, right-eye, and filtered pupil-diameter traces and summarize valid-sample proportions by item. |
| `illustrative gaze patterns for four geospatial task items/` | `saccade_directions.ipynb` | Plot saccade-direction distributions for four selected task items. |
| `response time distributions/` | `response_time_distributions.ipynb` | Summarize and plot response-time distributions for the four task datasets. |

The pupil script generates one plot per available eligible item, rather than automatically selecting four recording segments. The saccade-direction notebook generates directional rose plots; it does not generate fixation maps or scan-path overlays.

## Installation

Use Python 3.10 or later in a virtual environment. From the repository root:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

`requirements.txt` specifies dependency ranges, rather than a frozen record of the original analysis environment. Calibri and Arial are requested by the plotting code. If unavailable, Matplotlib may substitute fonts, changing the appearance of figures.

## Input data

The input data are not included in this repository; please download the dataset separately and place the required files in the corresponding data/ folders before running the code.

## Running the analyses

Each module is independent. **Run with the module folder as the working directory**.

For example, from the repository root:

```bash
cd "code/AOI fixation count proportions by response accuracy"
jupyter lab
```

Open `AOI.ipynb`, select the installed Python environment, and run all cells from top to bottom. Follow the same procedure for each of the other notebooks, changing to its corresponding folder first.

For the pupil script, start from the repository root and run:

```bash
cd "code/example pupil diameter traces from four recording segments"
python pupil.py
```

Outputs are written into the current module folder. Re-running an analysis overwrites outputs with the same names. 

## Analysis details

### AOI proportions and response accuracy

`fix_ratio_kz` and `fix_ratio_ra` are fixation count proportions for the key AOI and correct-answer AOI, respectively. The notebook first averages trials within each participant, dataset, and accuracy condition. Paired tests retain participants with observations in both accuracy conditions for the relevant dataset and metric.

Paired-samples t tests compare correct and incorrect responses, with Holm correction across the eight comparisons (four datasets × two AOI metrics). The notebook also calculates Wilcoxon signed-rank tests, descriptive statistics, 95% confidence intervals for mean differences, and Cohen's dz. Figure significance markers use the adjusted t-test p-values.

### Academic-background comparisons

The notebook averages trials within participant and dataset, then averages across each participant's available datasets. These participant-level means are joined to the participant table. Geography and non-geography are defined by the supplied `subject` coding; this notebook does not derive groups from text labels of majors.

Welch's independent-samples t tests are performed with Holm correction within each metric family: AOI allocation, fixation timing, saccade behavior, and behavioral performance. Selected measures are tested after a natural-log transformation, excluding nonpositive values for those tests. Descriptive means and standard deviations remain on the original scale; Hedges' g uses the test scale. Mann–Whitney U tests use the original scale and their p-values are not adjusted by this code.

The figure displays three prespecified measures: correct-answer AOI fixation proportion, average saccade amplitude, and response time. This selection is fixed in the notebook and does not automatically change when another input produces different significance results.

### Pupil-diameter traces

The script retains `Eye Tracker` rows and matches numeric item identifiers extracted from `Presented Media name` against a fixed allowed-item list. A sample is counted as valid when both eyes are marked `Valid` and all three pupil-diameter fields are nonmissing. This rule is used to rank item-level valid-sample proportions and set plotting limits; the plotted lines use all retained rows for each item, including rows not passing that validity rule.

Pupil diameter is displayed in millimeters. The supplied export's recording timestamps are treated as milliseconds and divided by 1,000 for display in seconds. The horizontal axis retains recording time rather than resetting to zero at each item. The script groups by item number, so a replacement export containing multiple participants or recordings must be separated before use if distinct traces are required.

### Saccade directions

The selected items are `ET_Item_008`, `ET_Item_026`, `ET_Item_061`, and `ET_Item_113`. Only events marked `Saccade` and `Whole` are retained. Directions are normalized to [0°, 360°) and grouped into 24 bins centered every 15°. Directional proportions are calculated within participant and item, then averaged across participants. Error bars show approximate 95% intervals calculated as mean ± 1.96 × SEM. 
### Response times

The notebook retains positive, finite response times in the four task datasets, combines STAT-A and STAT-B, and converts `Duration_of_interval` from milliseconds to seconds. It reports trial-level descriptive statistics and draws histograms with kernel density curves scaled to the frequency axis.

## Outputs

| Module | Saved output |
| --- | --- |
| AOI accuracy | `correct_incorrect_AOI_comparison.png` |
| Academic background | `eye_tracking_group_comparisons.xlsx`; `major_group_eye_movement_comparison.png` |
| Pupil traces | `pupil_data_validity_proportion_ranking.csv`; `pupil_plots_all/pupil_question_<item>.png` |
| Saccade directions | `selected_TOI_saccade_direction.png` |
| Response times | `response_time_frequency_4_datasets.png` |

# Supplementary Appendix and Input Datasets

Supporting materials for **Optimization-Based Explicit Reliability Assessment for Joint Planning of Switches and Grid-Forming Resources in Distribution Networks**.

## Files

| File | Contents |
| --- | --- |
| `IEEE_PESGM_2027_Appendix_Complete.docx` | Complete model, derivations, mixed-integer reformulations, experimental settings, and numerical configuration tables. Equations are editable in Word. |
| `omra_case_10node_data.xlsx` | Base network data and reference device configurations for the 10-bus test system. |
| `omra_case_54node_data.xlsx` | Base network data and reference device configurations for the 54-bus test system. |

## How to use the materials

The Excel workbooks provide base network data and reference device configurations. **The experiment-specific settings and overrides in Section H of the Supplementary Appendix take precedence over workbook defaults when interpreting the reported experiments.** These include inverter ratings and types, device availability, planning candidates, and the normal topology used in the study. The workbooks alone do not uniquely specify every experiment.

The appendix is organized as follows:

- **A:** Sets, variables, and assumptions.
- **B:** Protection, restoration, radiality, and reference eligibility.
- **C:** Electrical operating snapshots and disturbance definitions.
- **D:** Analytical frequency response and topology-dependent aggregation.
- **E:** Reliability indices and investment optimization.
- **F:** Exact mixed-integer reformulations and approximation bounds.
- **G:** Local two-step switch-defined pickup experiment.
- **H:** Network data, frequency settings, candidate ratings, and experimental configurations.
- **I:** Computation, verification, and reproduction settings.

## Experimental distinctions

The 10-bus two-step experiment concerns only the isolated buses 4 and 5 following fault 3–4. Its reported EENS is the annual contribution of those buses under that fault. The separate whole-network switch–GFM interaction comparisons aggregate all eight modeled branch faults and use one restoration state per fault. The parameter overrides for these experiments differ; see Sections G and H2.

For the 54-bus planning study, the actual normal topology is derived from endpoint-device states: **branch 27–28 is normally closed and included in the fault set, while branch 35–36 is normally open and excluded.** These states resolve legacy inconsistencies in the workbook's branch flags. See Sections H3–H4 for the actual topology, planning candidates, costs, budgets, and full asset configurations.

This repository contains the supplementary document and input datasets. It does not contain the optimization source code or an executable reproduction package. Solver settings and verification descriptions are documented in the appendix; they should be interpreted together with the stated modeling assumptions and experiment-specific overrides.

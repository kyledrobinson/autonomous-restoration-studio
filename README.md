# Autonomous Restoration Studio

Autonomous Restoration Studio is an experimental research project exploring whether AI agents can perform high-fidelity digital restoration of historical artwork **without human aesthetic judgement in the loop**.

The system is designed as a multi-agent pipeline that ingests scanned historical images, performs restoration using AI models, critiques its own outputs using independent AI critics, and iterates until a quality threshold is reached.

This project focuses on conservation-minded restoration: preserving structure, style, and historical plausibility rather than creating “enhanced” or modernized reinterpretations.

---

## What This Project Does

- Ingests high-resolution scans of historical artwork (e.g. botanical plates, engravings, illustrations)
- Detects and maps common degradation:
  - stains
  - fading
  - paper yellowing
  - tears
  - noise
- Performs automated restoration:
  - background cleanup
  - color stabilization
  - detail recovery
  - denoising
- Generates multiple restoration candidates
- Evaluates results using autonomous critic agents
- Iterates until predefined quality metrics are met
- Produces a final restored image and a restoration report

This is not an image “stylizer.” It is a restoration pipeline.

---

## What “Autonomous” Means

In this project, **autonomous** means:

- No human aesthetic judgement is used to select the final restoration.
- AI agents generate, critique, score, and select outputs.
- Human involvement is limited to:
  - providing input scans
  - reviewing results after completion
  - improving system design and metrics

The goal is to test whether AI systems can self-regulate quality in restoration tasks without human taste influencing the final result.

---

## Inputs

The system accepts:

- High-resolution scanned images of historical works
- Public domain or properly licensed materials only
- Examples include:
  - botanical illustrations
  - engravings
  - plates from historical archives
  - scanned prints and manuscripts

Each input must be accompanied by source metadata and archive references to ensure traceability.

---

## Outputs

For each restoration job, the system produces:

- A final restored image (e.g. `winner.png`)
- Intermediate restoration candidates (for audit/debugging)
- A structured restoration report containing:
  - scoring metrics
  - model parameters
  - restoration steps taken
  - source references
  - reproducibility information (seeds/configs)

The intent is to make each restoration **auditable, reproducible, and explainable**.

---

## Non-Goals

This project is not intended to:

- Create modern reinterpretations of historical art  
- Add new artistic elements  
- “Improve” artwork beyond plausible restoration  
- Replace professional conservators  
- Make aesthetic or curatorial decisions  

The goal is technical exploration of autonomous restoration pipelines, not cultural authority.

---

## Ethics & Provenance

All inputs must be:
- Public domain or explicitly licensed  
- Properly attributed to their source archives  
- Logged in `SOURCES.md`  

Restoration outputs must reference original sources and may not be presented as originals.

---

## Project Status

Early research and prototyping phase.  
Expect breaking changes, evolving architecture, and experimental results.

---

## License

TBD

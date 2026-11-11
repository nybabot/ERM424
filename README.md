# ERM 424: Statistics and Data Analytics for Risk Management

Course files for ERM 424, Northwestern University School of Professional Studies, Winter 2027. Instructor: Bany Ismail. The course runs in Python on Google Colab; the notebooks here read their data from this repository, so you never download a file by hand.

## How to open a notebook

1. Open the notebook's link from the Canvas assignment page (it opens in Google Colab), or use the links at the end of this readme.
2. In Colab, choose File, then Save a copy in Drive. Work in your copy.
3. Run the first cell before anything else. It checks versions and sets up the data loader.

## What is here

| Folder | Contents |
|---|---|
| `notebooks/student/` | The assignment notebooks: Toolkit Check (Module 1), First Contact (Module 2), Clean It Twice (Module 3), Stage 1: Framing and Quantifying (Module 5) |
| `notebooks/companion/` | The van Buuren Python companion (Module 3, ungraded) |
| `data/claims/` | The Corvane Mutual claims data for Modules 1 to 3, with the data dictionaries (`m2_claims_DICTIONARY.md`, `m3_DICTIONARY.md`) |
| `generators/claims_world.py` | The generator that First Contact Stage 3 uses to build a 2,000,000-row frame inside your session |
| `data/lakefill/` | The Lakefill National Bank operational loss data for Modules 5 to 10: the 2021 to 2025 loss event history (`lakefill_losses_raw.csv`), the monthly exposure table (`lakefill_exposure_monthly.csv`) and the data dictionary (`lakefill_DICTIONARY.md`). Later files are added in the weeks the course names. |
| `generators/lakefill_world.py` | The Lakefill schema, loaders and panel builder that the Module 5 to 10 notebooks use |
| `docs/ai_protocol/` | The AI Protocol page, the Module 3 and Module 5 role prompts, and the Part B disclosure form (AI means artificial intelligence) |
| `docs/module_05/` | The Lakefill engagement documents for Module 5: the Chief Risk Officer's sponsor letter, the engagement charter template and a worked example for a different sponsor, the Analyst Note template with the week 5 topics, the coverage memo template, and the Basel event-type reference sheet |
| `docs/media/` | The risk analytics workflow one-pager |
| `docs/sync/` | The week 2 live-session notebook, added after that session |

Modules 4 to 10 are added as the course progresses.

## About the data

Corvane Mutual Insurance Company (Modules 1 to 4) and Lakefill National Bank (Modules 5 to 10) are fictional. Every data file is synthetic and generated for this course; no real claims, policyholders, losses or people appear in it. Read each module's data dictionary before working with its file.

## Questions

Use the Q&A discussion in Canvas or office hours. Please do not open issues or pull requests on this repository.

## Notebooks

| Module | What you'll be doing | Notebook |
|---|---|---|
| Module 1: The Risk Analytics Workflow and Your Toolkit | Confirm your Colab environment works, then make two small code changes and rerun them. Graded for completion only. | [Toolkit Check](https://colab.research.google.com/github/nybabot/ERM424/blob/main/notebooks/student/ERM424_M1_Toolkit_Check.ipynb) |
| Module 2: Getting Honest with Data: Variable Types, Summaries, and Profiling | Classify and summarize every column of the claims data by hand, check a profiling tool against your findings, see what happens at 1,000 times the size, and write a data-quality note. | [First Contact](https://colab.research.google.com/github/nybabot/ERM424/blob/main/notebooks/student/ERM424_M2_First_Contact.ipynb) |
| Module 3: Cleaning and Preparing Risk Data | Join the claims and policyholder tables, investigate missingness, and clean the data with a logged decision for each change (Part A). Then run and audit an AI-proposed cleaning script (Part B). | [Clean It Twice](https://colab.research.google.com/github/nybabot/ERM424/blob/main/notebooks/student/ERM424_M3_Clean_It_Twice.ipynb) |
| Module 3: Cleaning and Preparing Risk Data | Run the van Buuren Chapter 1 demonstrations in Python alongside the reading. Ungraded. | [van Buuren Companion](https://colab.research.google.com/github/nybabot/ERM424/blob/main/notebooks/companion/ERM424_M3_vanBuuren_Companion.ipynb) |
| Module 5: Framing Risk Questions and Quantifying Exposure | Open the Lakefill engagement: check the raw loss register for your business line, prepare it lightly with a logged decision for each treatment, judge its fitness against BCBS 239 (the Basel Committee on Banking Supervision's risk data standard), and fit candidate frequency and severity models (Part A). Then audit an AI's draft charter and model proposals (Part B). | [Stage 1: Framing and Quantifying](https://colab.research.google.com/github/nybabot/ERM424/blob/main/notebooks/student/ERM424_M5_Stage1_Framing_and_Quantifying.ipynb) |

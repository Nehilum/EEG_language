# EEG_language
Project Overview
This project focuses on the preparation, optimization, and sequencing of auditory stimuli (syllables) for EEG/ERP experiments. The pipeline ensures that all stimuli meet high experimental standards, including uniform duration, loudness normalization, clarity enhancement, consistent sampling rates, and systematic organization for reproducibility.

Directory Structure
bash
Copy
Edit
EEG_LANGUAGE/
├── experiment/               # Experiment-related outputs and data
│   ├── ADR/                  # ADR-specific experimental data
│   ├── HDR/                  # HDR-specific experimental data
│   ├── order_lists/          # Final experimental orders for presentation
│   └── notify.wav            # Notification sound for task triggers
│
├── pipeline/                 # Main pipeline scripts for processing and sequencing
│   ├── scr01_generate_sequence_list.py
│   ├── scr02_generate_sequence.py
│   ├── scr03_create_order_list.py
│   ├── scr04_convert_all_csv_to_order.py
│   └── README.md             # Documentation for pipeline scripts
│
├── stimuli/                  # Stimuli processing and storage
│   ├── raw/                  # Raw input syllables
│   ├── processed/            # Processed stimuli through the pipeline
│   ├── sequences/            # Final concatenated sequences for experiments
│   │   ├── combined_wav/     # Concatenated .wav sequences
│   │   └── sequences_csv/    # Corresponding sequence configuration files
│   └── func_audio_processing.py  # Core audio processing functions
│
├── tests/                    # Scripts for testing and validation
│   └── cutter.ipynb          # Notebook for validating segmentation and trimming
│
└── README.md                 # Main project documentation
Processing Workflow
The pipeline is structured into sequential processing steps to prepare high-quality auditory stimuli for EEG experiments. Each step is implemented as an independent Python script and produces intermediate outputs stored in dedicated folders.

1. Duration Standardization
Objective: Ensure all syllables have a uniform length of 0.4 seconds for ERP time-locking.
Method: Acoustic onset alignment followed by trimming and padding.
Script: scr01_process_audio_folder.py
2. Loudness Normalization
Objective: Normalize syllable intensity to -23 LUFS to eliminate volume-based biases.
Method: LUFS normalization using the pyloudnorm library.
Script: scr03_normalize_LUFS.py
3. Noise Reduction
Objective: Remove background noise while preserving natural phonetic features.
Method: Spectral subtraction using the noisereduce library.
Script: scr04_denoise_nr.py
4. Sampling Rate Adjustment
Objective: Resample all audio files to a consistent sampling rate of 48,000 Hz for compatibility with EEG equipment.
Method: Resampling using the librosa library.
Script: scr05_resample_audio.py
5. Spectral Smoothing
Objective: Reduce high-frequency artifacts to ensure smooth and natural auditory perception.
Method: Low-pass filtering using a 10th-order Butterworth filter.
Script: scr06_smooth_spectrum.py
6. Renaming for Standardization
Objective: Rename syllable files to a systematic format for better organization and reference.
Method: Phonetic-based renaming (e.g., be.wav → A1_e_b.wav).
Script: scr07_rename_syllables.py
Key Features
Modular and Transparent Workflow

Each step of the pipeline is independent and produces intermediate outputs stored in dedicated folders.
High-Quality Stimuli

Processed syllables are acoustically optimized for experimental needs, including duration, loudness, and clarity.
Reproducibility

Scripts are reusable and parameterized, ensuring that experiments can be replicated or adapted easily.
Systematic File Organization

Outputs are organized into distinct folders (raw, processed, sequences), enabling efficient data management.
How to Use
Setup
Clone the Repository:
bash
Copy
Edit
git clone https://github.com/your-repo/EEG_Language.git
cd EEG_Language
Install Dependencies:
Required Python libraries:
bash
Copy
Edit
pip install numpy librosa pydub pyloudnorm noisereduce scipy
Run the Pipeline
Step 1: Process Audio Files

Standardize duration:
bash
Copy
Edit
python stimuli/scr01_process_audio_folder.py
Step 2: Normalize Loudness

bash
Copy
Edit
python stimuli/scr03_normalize_LUFS.py
Step 3: Reduce Noise

bash
Copy
Edit
python stimuli/scr04_denoise_nr.py
Step 4: Adjust Sampling Rate

bash
Copy
Edit
python stimuli/scr05_resample_audio.py
Step 5: Smooth Spectra

bash
Copy
Edit
python stimuli/scr06_smooth_spectrum.py
Step 6: Rename Files

bash
Copy
Edit
python stimuli/scr07_rename_syllables.py
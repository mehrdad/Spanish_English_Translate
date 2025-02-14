# Spanish_English_Translate
Batch Audio Translation Tool
This tool processes multiple MP3 audio files in Spanish and provides English translations. It supports parallel processing for efficient batch operations and includes progress tracking and detailed logging.
Features

Batch processing of MP3 files
Parallel processing support
Spanish to English translation
Progress tracking with status bar
Detailed logging system
Automatic temporary file cleanup
Individual output files for each translation

Prerequisites
System Requirements

Python 3.7 or higher
FFmpeg installation

Installing FFmpeg

Windows:

Download FFmpeg from https://ffmpeg.org/download.html
Extract the downloaded file
Add the FFmpeg bin folder to your system's PATH environment variable


Linux:
bashCopysudo apt-get update
sudo apt-get install ffmpeg

macOS:
bashCopybrew install ffmpeg


Python Dependencies
Create a virtual environment (recommended):
bashCopypython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install required Python packages:
bashCopypip install -r requirements.txt
Project Structure
Copyaudio-translation/
├── requirements.txt
├── translation_script.py
├── temp_files/          # Created automatically
├── output/             # Created automatically
└── translation_batch.log
Usage

Prepare your MP3 files in a directory
Update the input and output directory paths in the script:
pythonCopyinput_dir = "path/to/your/mp3/files"
output_dir = "path/to/output/directory"

Run the script:
bashCopypython translation_script.py


The script will:

Process all MP3 files in the input directory
Show a progress bar
Create translation files in the output directory
Generate a log file with detailed information
Show a summary of successful and failed translations

Output Format
For each MP3 file, the script creates a text file with:
CopyOriginal Text (Spanish):
=====================
[Spanish transcription]

English Translation:
===================
[English translation]
Configuration Options
You can modify these parameters in the script:

Number of parallel processes:
pythonCopyprocess_batch(input_dir, output_dir, max_workers=4)

Chunk duration (in milliseconds):
pythonCopychunk_duration = 30000  # 30 seconds


Logging
The script creates a translation_batch.log file containing:

Processing status for each file
Error messages
Warning messages
Success confirmations

Troubleshooting

File Access Errors:

Ensure no other programs are using the MP3 files
Check file permissions


Audio Processing Errors:

Verify FFmpeg is properly installed
Ensure MP3 files are not corrupted


Translation Errors:

Check internet connection
Verify audio quality is sufficient for transcription



Dependencies List
CopySpeechRecognition>=3.8.1
pydub>=0.25.1
googletrans==3.1.0a0
tqdm>=4.65.0
Notes

Audio files are processed in 30-second chunks
Temporary files are automatically cleaned up
Internet connection is required for both transcription and translation
The script uses Google's speech recognition and translation services

Limitations

Maximum file size depends on available system memory
Quality of translation depends on audio quality
Internet connection required
Google API usage limits may apply

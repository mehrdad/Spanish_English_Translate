import os
import speech_recognition as sr
from pydub import AudioSegment
from googletrans import Translator
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import logging
import uuid
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='translation_batch.log'
)

def get_temp_directory():
    """Create and return a temporary directory for process-specific files"""
    temp_dir = os.path.join(os.getcwd(), 'temp_files')
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def clean_temp_files(temp_dir, process_id):
    """Clean up temporary files for a specific process"""
    try:
        pattern = f"*{process_id}*"
        for file in os.listdir(temp_dir):
            if process_id in file:
                try:
                    file_path = os.path.join(temp_dir, file)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logging.error(f"Error removing temporary file {file}: {e}")
    except Exception as e:
        logging.error(f"Error in cleanup: {e}")

def mp3_to_text_translation(mp3_file, output_dir, src_lang='es', dest_lang='en'):
    # Generate unique process ID
    process_id = str(uuid.uuid4())
    temp_dir = get_temp_directory()
    
    try:
        # Create output filename based on input filename
        base_name = os.path.splitext(os.path.basename(mp3_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"{base_name}_translation_{timestamp}.txt")
        
        # Create process-specific temporary WAV file
        wav_file = os.path.join(temp_dir, f"temp_audio_{process_id}.wav")
        
        # Initialize recognizer and translator
        recognizer = sr.Recognizer()
        translator = Translator()
        
        # Lists to store all transcribed and translated segments
        all_transcribed = []
        all_translated = []

        # Load and convert MP3 to WAV with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                audio = AudioSegment.from_mp3(mp3_file)
                audio.export(wav_file, format="wav")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)  # Wait before retrying
        
        # Process audio in chunks of 30 seconds
        chunk_duration = 30000  # 30 seconds in milliseconds
        for i in range(0, len(audio), chunk_duration):
            chunk = audio[i:i + chunk_duration]
            chunk_wav = os.path.join(temp_dir, f"chunk_{process_id}_{i}.wav")
            
            try:
                chunk.export(chunk_wav, format="wav")
                
                with sr.AudioFile(chunk_wav) as source:
                    logging.info(f"Processing {base_name} - chunk {i//chunk_duration + 1}")
                    audio_data = recognizer.record(source)
                    try:
                        transcribed_chunk = recognizer.recognize_google(audio_data, language=src_lang)
                        translated_chunk = translator.translate(transcribed_chunk, src=src_lang, dest=dest_lang).text
                        
                        all_transcribed.append(transcribed_chunk)
                        all_translated.append(translated_chunk)
                        
                    except sr.UnknownValueError:
                        logging.warning(f"Could not understand audio in {base_name} - chunk {i//chunk_duration + 1}")
                    except sr.RequestError as e:
                        logging.error(f"Error with {base_name} - chunk {i//chunk_duration + 1}: {e}")
            finally:
                # Clean up chunk file immediately after processing
                if os.path.exists(chunk_wav):
                    try:
                        os.remove(chunk_wav)
                    except Exception as e:
                        logging.error(f"Error removing chunk file {chunk_wav}: {e}")

        # Combine all chunks and write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Original Text (Spanish):\n")
            f.write("=====================\n")
            f.write("\n".join(all_transcribed))
            f.write("\n\nEnglish Translation:\n")
            f.write("===================\n")
            f.write("\n".join(all_translated))

        logging.info(f"Successfully processed: {mp3_file}")
        return (mp3_file, output_file, True)

    except Exception as e:
        logging.error(f"Error processing {mp3_file}: {e}")
        return (mp3_file, None, False)
    finally:
        # Clean up all temporary files for this process
        clean_temp_files(temp_dir, process_id)

def process_batch(input_dir, output_dir, max_workers=4):
    """
    Process all MP3 files in the input directory using parallel processing
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of all MP3 files
    mp3_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) 
                 if f.lower().endswith('.mp3')]
    
    if not mp3_files:
        logging.warning(f"No MP3 files found in {input_dir}")
        return
    
    # Process files in parallel
    successful = 0
    failed = 0
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(mp3_to_text_translation, mp3_file, output_dir): mp3_file 
            for mp3_file in mp3_files
        }
        
        # Process results with progress bar
        with tqdm(total=len(mp3_files), desc="Processing files") as pbar:
            for future in as_completed(future_to_file):
                original_file, output_file, success = future.result()
                if success:
                    successful += 1
                else:
                    failed += 1
                pbar.update(1)
    
    # Print summary
    print("\nBatch Processing Summary:")
    print(f"Total files processed: {len(mp3_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Check translation_batch.log for detailed processing information")

    # Final cleanup of temp directory
    temp_dir = get_temp_directory()
    try:
        for file in os.listdir(temp_dir):
            try:
                os.remove(os.path.join(temp_dir, file))
            except Exception as e:
                logging.error(f"Error cleaning up temporary file {file}: {e}")
    except Exception as e:
        logging.error(f"Error in final cleanup: {e}")

def main():
    # Example usage
    input_dir = "C:/speechAnalytics/mp3"  # Replace with your input directory
    output_dir = "C:/speechAnalytics/output"  # Replace with your output directory
    
    print("Starting batch translation process...")
    process_batch(input_dir, output_dir)

if __name__ == "__main__":
    main()
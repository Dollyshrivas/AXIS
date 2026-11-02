
import soundfile as sf
import numpy as np
from pathlib import Path

files = [
    "indic_parler_hindi_test.wav",
    "tts_offline/output/axis_speech.wav",
]

for file in files:
    path = Path(file)

    if not path.exists():
        print(f"\nMissing: {file}")
        continue

    audio, sample_rate = sf.read(path, dtype="float32")

    print(f"\nFile: {file}")
    print("Sample rate:", sample_rate)
    print("Duration:", round(len(audio) / sample_rate, 3), "seconds")
    print("Peak:", round(float(np.max(np.abs(audio))), 4))
    print("RMS:", round(float(np.sqrt(np.mean(audio ** 2))), 4))
    print("Clipped samples:", int(np.sum(np.abs(audio) >= 0.999)))
    print("Non-finite samples:", int(np.sum(~np.isfinite(audio))))

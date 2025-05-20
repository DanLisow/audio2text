import warnings
from audio_queue.consumer import Queue

warnings.filterwarnings("ignore", message="Module 'speechbrain.pretrained' was deprecated")
warnings.filterwarnings("ignore", message="std\\(\\): degrees of freedom")

if __name__ == "__main__":
    Queue.start_worker()
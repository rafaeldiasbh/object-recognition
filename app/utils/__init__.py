import os
import glob
from decouple import config

LOG_PATH = config('LOG_PATH')

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

def __clean_logs(directory):

    log_files = glob.glob(os.path.join(directory, 'log_*.log'))

    if len(log_files) > 30:

        log_files.sort(key=lambda x: os.path.getctime(x))

        num_files_to_remove = len(log_files) - 30

        for i in range(num_files_to_remove):
            len(log_files[i])
            os.remove(log_files[i])
            print(f'Removed log: {log_files[i]}')

__clean_logs(LOG_PATH)
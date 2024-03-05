import os
import json
from pathlib import Path

# Main project directory
main_dr = Path(__file__).parent.parent.absolute()

# Load some values from global config json
with open(os.path.join(main_dr, 'config.json')) as f:
    config = json.load(f)

# Get directory where main raw data was downloaded
raw_data_dr = config['raw_data_dr']

# Get directory where data should be saved
data_dr = os.path.join(main_dr, 'data')
import pandas as pd
import numpy as np
import json
with open('course.json', encoding='utf-8') as f:
    data = json.load(f)

data = pd.DataFrame(data)


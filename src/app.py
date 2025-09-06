# src/app.py

import streamlit as st
import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from PIL import Image
import plotly.express as px

# -------------------------
# Setup FastF1 Cache
# -------------------------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cache_folder = os.path.join(project_root, "cache")
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)
ff1.Cache.enable_cache(cache_folder)
plotting.setup_mpl()

st.set_page_config(page_title="F1 Telemetry Dashboard", layout="wide")
st.title("🏎️ F1 Telemetry Dashbo

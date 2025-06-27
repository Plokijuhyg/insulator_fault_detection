# Insulator Fault Detection AI Project

This project uses AI and drone-based inspection to detect faults on power line insulators, generate detailed reports, and locate nearby suppliers using Google APIs.

## Features

- Detect insulator faults from uploaded images or drone live stream (future).
- Generate an AI-powered fault report using a local LLM (distilGPT2).
- Search and display nearby insulator supplier companies with Google Places API.
- Visualize fault location on an interactive map.
- Save detailed fault reports as downloadable Word (.docx) documents.
- Simple web interface built with Streamlit.

## Project Structure

Insulator-Fault-Detection-AI/
│
├── model/ # YOLOv8 model files
├── distilgpt2/ # Local LLM model files
├── images/ # Uploaded or drone images
├── reports/ # Generated fault reports (.docx)
├── maps/ # Generated fault location maps (.html)
├── utils/ # Helper modules (detection, report, map, Google API)
├── app.py # Streamlit web app main script
├── requirements.txt # Python dependencies
└── README.md # This file
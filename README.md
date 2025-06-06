# Alltius Project

This project consists of a FastAPI backend and a Vite-based frontend application.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn package manager

## Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your environment variables:
```
OPENAI_API_KEY=your_api_key_here
```

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Backend

1. Make sure your virtual environment is activated
2. Start the FastAPI server:
```bash
uvicorn main:app --reload
```
The backend will be available at `http://localhost:8000`

### Frontend

1. In a new terminal, navigate to the frontend directory:
```bash
cd frontend
```

2. Start the development server:
```bash
npm run dev
```
The frontend will be available at `http://localhost:5173`

3. Visit `http://localhost:5173` in your browser to start testing the application!



## Project Structure

- `/frontend` - Vite-based React frontend application
- `/rag` - RAG (Retrieval-Augmented Generation) related code
- `/data` - Data storage directory
- `/data_processing` - Data processing scripts
- `main.py` - FastAPI backend entry point

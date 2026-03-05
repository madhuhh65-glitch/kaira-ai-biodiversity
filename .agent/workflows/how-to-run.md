---
description: how to run the application
---

To run the Kaira AI Species Identification System, follow these steps:

### 1. Prerequisites
Ensure you have **MongoDB** installed and running on your system (defaulting to `mongodb://localhost:27017`).

### 2. Install Dependencies
Open your terminal in the `biodiversity_ai` directory and run:

```powershell
pip install -r requirements.txt
```

### 3. Launch the Backend
Navigate to the `kaira ai` directory and start the FastAPI server:

```powershell
cd 'kaira ai'
python main.py
```

### 4. Access the Application
Once the server is running, open your browser and go to:
[http://localhost:8001/app/home.html](http://localhost:8001/app/home.html)

---
> [!NOTE]
> The server runs on port **8001** by default.

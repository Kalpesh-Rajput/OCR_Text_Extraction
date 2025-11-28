import os


folders = {
    "src": ["preprocessing.py", "ocr_engine.py", "text_extraction.py", "utils.py"],
    "notebooks": [],
    "tests": [],
    "results": []
}

def create_structure():
    base_path = os.getcwd()  # Current working directory

    # Create folders and files
    for folder, files in folders.items():
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)

        # Create empty files inside each folder
        for filename in files:
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "w") as f:
                pass

    # Create root-level files
    root_files = ["app.py", "requirements.txt"]
    for filename in root_files:
        with open(os.path.join(base_path, filename), "w") as f:
            pass

    print("Project structure created successfully!")

if __name__ == "__main__":
    create_structure()

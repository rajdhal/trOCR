# University of Windsor 4990/4690 Sign-In Sheet Text Recognizer (UW-TROCR)

Welcome to the University of Windsor Text Recognition project! This open-source repository is dedicated to helping the University of Windsor community streamline the process of recognizing text from forms using a customized version of Microsoft's trOCR technology. With Gradio, a user-friendly web interface, this project enables easy interaction with the underlying machine learning model for text recognition.

## Features

- Seamlessly integrated with our custom trOCR technology.
- Leveraging YOLO object detection for precise image analysis and text localization.
- User-friendly interface powered by Gradio.
- Quickly recognize text from forms and documents.
- Customizable for your specific use case.

## Table of Contents

- [Getting Started](#getting-started)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

Before you get started, ensure you have the following prerequisites in place:

- Python 3.7+
- Pip package manager

## Installation

1. Clone this repository to your local machine:

```bash
git clone https://github.com/rajdhal/uw-trOCR.git
```

2. Navigate to the project directory:

```bash
cd uw-trOCR
```

3. Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the Gradio web application:

```bash
python main.py
```

2. Open your web browser and navigate to `http://localhost:7860` (by default).

3. Upload an image of the form you want to recognize text from.

4. Click the "Submit" button, and the annotated image alongside a downloadable CSV file will be available in the output.

5. Customize the application to suit your specific needs by modifying the Gradio interface and machine learning model as necessary.

## Contributing

We welcome contributions from the University of Windsor community and the open-source community at large. If you'd like to contribute to this project, please follow these steps:

1. Fork this repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your changes to your fork.
5. Create a pull request back to this repository.

---

We hope that the University of Windsor Text Recognition (UW-TR) project simplifies text recognition tasks for the university community. If you have any questions, feedback, or suggestions, please don't hesitate to reach out. We look forward to collaborating with you to improve and expand this application.

# VoiceSynth Build Your Own Text-to-Speech App

A serverless web application that converts text( can either be a blog post, for example, you can use the application to read you a book while driving or riding a bike) into natural-sounding speech using Amazon Polly. This project demonstrates the integration of a modern frontend with cloud-based AI services through a serverless API backend.

## Have a prototype 

[Insert your live application URL here after deployment]
*(example  https://your-website.bucket.s3-website-us-east-1.amazonaws.com)* **Should be a URL of the app hosted on S3**

## Project Overview

This project is meant to explore the capabilities of cloud-based AI and serverless architectures. The application allows users to input text, select from a variety of voices, and instantly play the generated speech directly in their browser.

### Architecture Diagram

```
 User's Browser
       |
       | (HTTP POST/GET)
       v
 AWS API Gateway (REST API)
       |
       | (Invocation)
       v
    AWS Lambda (Python/Node.js)
       |
       | (SDK Call)
       v
  Amazon Polly (TTS Service)
```

### Features

-   **Real-time Synthesis:** Convert text to speech in real-time.
-   **Multiple Voices:** Choose from a wide selection of neural and standard voices across different languages.
-   **Audio Playback:** Stream and play generated audio directly in the browser with a built-in player.
-   **Serverless Backend:** Entirely built on scalable AWS serverless technologies (Lambda, API Gateway).
-   **Clean UI:** A simple and intuitive user interface.

## Technology Stack

Component          | Technology Used                         
------------------ | ----------------------------------------
**Frontend**       | HTML5, CSS3, JavaScript          
**Backend (API)**  | AWS Lambda (Python 3.x / Node.js)       
**API Gateway**    | AWS API Gateway (REST API)              
**Text-to-Speech** | Amazon Polly                            
**Security**       | AWS IAM (Roles & Policies)              
**Storage (Optional)** | AWS S3 (for file downloads)          
**Hosting**        | AWS S3 Static Website Hosting         

## Project Structure

```
text-to-speech-app/
├── frontend/                 # All frontend source files
│   ├── index.html            # Main application page
│   ├── style.css             # Stylesheets
│   ├── script.js             # Main application logic
│   └── voices.json           # Optional: Static list of voices
├── backend/                  # Backend Lambda function code
│   └── lambda_function.py    # or app.js for Node.js
├── docs/                     # Additional documentation
│   └── ARCHITECTURE.md       # Detailed architecture explanation
├── README.md                 # This file
└── .gitignore                # Git ignore file
```

## ⚙️ Setup & Installation

### Prerequisites

-   An AWS Account (with appropriate permissions to create Lambda, API Gateway, and Polly).
-   Git is installed on your local machine.
-   A code editor, VS Code.


## Learning Objectives

This project was designed to help you learn:
-   The practical use of cloud AI/ML services (Amazon Polly).
-   Serverless backend development with AWS Lambda and API Gateway.
-   Asynchronous programming in JavaScript to handle API requests.
-   Security best practices using IAM roles and policies.
-   Full-stack application design and deployment.

**Biggest Challenges Overcome:**
*   Configuring the IAM roles correctly to allow Lambda to invoke Polly.
*   Handling the binary audio response from the API in the frontend.
*   Debugging CORS issues between API Gateway and the frontend.

## License

This project is licensed for educational purposes. See the [MIT LICENSE](LICENSE) file for details.

## Support

If you get stuck, here are some resources:
-   [Amazon Polly Documentation](https://docs.aws.amazon.com/polly/)
-   [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
-   [MDN Web Docs: Using the Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)

**Built as part of the Cloud Intensive Course.** *Happy Coding* ☕

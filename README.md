# Smart Flashcards

A Django-based web application that automates the generation of flashcards from scanned academic documents using OCR and large language models.

This end-to-end system supports document upload (PDF/image), text extraction with Tesseract, semantic analysis and question generation via OpenAI, and flashcard management with spaced repetition.

## 🚀 Features

- 📄 **Document Upload** – users can upload scanned PDFs or images for processing
- 🧠 **OCR + NLP Pipeline**
  - Text extracted using Tesseract OCR
  - Passed to OpenAI API to generate:
    - Concise summaries
    - Key-concept flashcards
    - Comprehension questions
- 🗂 **Flashcard System**
  - Editable flashcards with tags and categories
  - Spaced repetition and adaptive review
- 🔐 **Authentication** – Django’s built-in auth system
- ⚙️ **Admin Panel** – full admin CRUD for managing content

## 🧱 Architecture Overview


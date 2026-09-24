# AXIS — AI Device Assistant 🤖

> An AI-powered device assistant designed to help users interact with their devices, automate everyday tasks, and create a smarter cross-device experience with gesture screenshots and file sharing, voice and system access.

---

## 🚀 Overview

**AXIS** is an AI-powered device assistant project that aims to make everyday device interactions smarter, faster, and more natural.

Instead of manually performing repetitive tasks, users can communicate with AXIS using natural language and let the AI understand the request and assist with the required action.

AXIS is designed as a foundation for building a future-ready personal AI assistant that can work across devices such as laptops and smartphones.

Axis is designed for gesture screenshots, file sharing, and full system access.

---

## ✨ Key Features

- 🤖 **AI-Powered Assistant**
  - Understands natural-language user requests.
  - Provides intelligent responses and assistance.

- 💻 **Device Assistance**
  - Designed to interact with device-level tasks.
  - Helps users perform everyday operations more efficiently.
  - Accesses the full device and completes everyday tasks.

- 🔄 **Cross-Device Concept**
  - Designed with laptop and mobile device integration in mind.
  - Can be extended toward seamless device-to-device interaction.

- 🧠 **AI Task Automation**
  - Designed to automate repetitive workflows.
  - Future versions can learn user preferences and patterns.

- ⚡ **FastAPI Backend**
  - Lightweight Python backend.
  - REST API architecture for communication between the frontend and AI system.

- 🔌 **Tool-Based Architecture**
  - AXIS can be extended with additional tools and functions.
  - New capabilities can be added without rebuilding the entire system.

---

## 🏗️ Project Architecture

```text
                    ┌─────────────────────┐
                    │       User          │
                    │  Natural Language   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │        AXIS         │
                    │   AI Assistant      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    │      Python         │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
             ┌──────────────┐      ┌──────────────┐
             │   Gemini AI  │      │    Tools     │
             │    Model     │      │  & Actions   │
             └──────────────┘      └──────────────┘

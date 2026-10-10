# taskpilot-ai
AI Powered Personal Task Tracker and Remainder

Problem Statement: Many professionals and students struggle to manage tasks efficiently due to scattered notes, emails, messages, and manual to-do lists. Traditional task management tools require users to manually enter task details, set priorities, categorize tasks, and configure reminders. As the number of tasks increases, users often miss deadlines, forget important activities, and spend excessive time organizing work instead of completing it.

Solution being Developed: Currently developing TaskPilot AI, an AI-powered task management application that enables users to create and manage tasks using natural language. The application aims to leverage Generative AI to automatically extract task details, categorize tasks, assign priorities, identify deadlines, and generate actionable summaries. The system will provide intelligent reminders and centralized task tracking to help users stay organized and improve productivity.


### Technology Stack

#### Implemented

* Python

* FastAPI – REST API development
* SQLAlchemy – ORM and database operations


* Uvicorn – ASGI server
####  Planned

* Google gemini AI - natural language task processing
* APIScheduler - scheduled remainder
* dateparser and python-dateutil - natural language date and time handling
* React and typescript - frontend development
* Tailwind CSS - UI styling
* Axios - frontend API communication

### Implemented features



* Task CRUD APIs: Create, retrieve, update, and delete tasks.
* Task Retrieval: Retrieve all tasks or retrieve a task by its ID.

* Task Filtering: Filter tasks by category, priority, severity, and status.
* Deadline Management: Store optional task due dates and times.
* Request Validation: Validate task data using Pydantic models

* Database Persistence: Store task records in SQLite using SQLAlchemy.

* REST API Documentation: Explore and test endpoints through FastAPI's Swagger UI.

### Planned Features

* AI-Powered Task Creation: Convert natural-language prompts into structured tasks using Google Gemini
* Task Summarization: Generate concise, actionable task titles and summaries.
* Intelligent Classification: Suggest task categories, priorities, and severity levels.
* Natural-Language Deadline Extraction: Interpret expressions such as "by this weekend" and convert them into deadlines.
* Date-Based Filtering: Retrieve tasks due today, upcoming tasks, and overdue tasks.
* Automated Reminders: Schedule explicit and priority-based reminders using APScheduler.
* Frontend Dashboard: Build a user interface for task creation, filtering, status updates, and deadline tracking.
# 🎯 ETC Outreach Optimisation

Welcome to the ETC Outreach Optimisation project! This project aims to streamline and optimise the engagement tracking and compliance process through a robust web application. 

## 🌟 Features

- 📁 **Upload and Preview Data**: Easily upload and preview engagement data from Excel files.
- 📝 **Process Engagement Data**: Filter and process engagement data with custom criteria.
- 📊 **Dynamic Reports**: Generate detailed reports and export them in various formats.
- 💾 **Database Integration**: Seamlessly integrate with a PostgreSQL database for data storage.
- 🔔 **Real-time Notifications**: Get real-time notifications for data processing status.
- 🔍 **Search and Filter**: Advanced search and filter options for better data management.
- 🛠️ **User Management**: Add multiple delegates for engagements with ease.

## 🚀 Getting Started

Follow these instructions to set up the project locally.

### Prerequisites

- Python 3.8+
- PostgreSQL
- Virtual Environment (optional but recommended)

### Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/outreachOptimisation.git
    cd outreachOptimisation
    ```

2. **Set up a virtual environment** (optional but recommended):
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up PostgreSQL Database**:
    - Ensure PostgreSQL is running.
    - Create a database named `etc_compliance_db`.
    - Update the `.env` file with your database credentials.

### Configuration

Create a `.env` file in the root directory of the project with the following content:

```env
DB_NAME=etc_compliance_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your_secret_key
```

### Running the Application

1. **Run the Flask app**:
    ```sh
    flask run
    ```

2. **Open your browser and navigate to**:
    ```
    http://127.0.0.1:5000
    ```

## 📂 Project Structure

```
├── app.py                  # Main application file
├── database_utils.py       # Database utility functions
├── dataLoadFunction.py     # Data processing functions
├── forms.py                # Flask-WTF forms
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── .env                    # Environment variables
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
└── tests/                  # Unit tests
```

## 🛠️ Usage

### Upload Data

- Navigate to the **Upload** page to upload your Excel file.
- Preview the uploaded data and set custom filters.

### Process Data

- On the **Process Data** page, apply your filters and process the data.
- View a summary of the processed data and download the full dataset.

### Manage Delegates

- Add multiple delegates to engagements with their details.
- Ensure you have the necessary permissions to manage the delegates.

## 🤝 Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

If you have any questions, feel free to open an issue or contact us at [your-email@example.com](mailto:your-email@example.com).

---

Made with ❤️ by [Nick aka Solstice](https://github.com/solstice035)

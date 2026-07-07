# Advanced QR Code Generator & Management System 📱

A full-featured QR Code Generator developed using Python, Flask, and SQLite. It creates permanent QR codes with no expiry, supporting multiple types, customization, and management features.

## 🚀 Features
- **Unlimited QR Generation**: No limits or expiry.
- **Multiple QR Types**:
  - Website URLs
  - Plain Text
  - Email (with subject/body)
  - Phone Numbers & SMS
  - Wi-Fi Credentials
  - Contact (vCard)
  - Google Maps Location
  - WhatsApp Links
- **Customization**:
  - Custom QR colors & background colors.
  - Logo embedding (planned/extensible).
  - Adjustable size.
- **Management**:
  - Responsive Dashboard.
  - QR History & Search.
  - Download tracking.
  - Bulk QR generation from CSV.
- **UI/UX**:
  - Dark Mode support.
  - Responsive design using Bootstrap 5.
  - Input validation & Error handling.

## 🛠️ Tech Stack
- **Backend**: Python, Flask
- **Database**: SQLite (SQLAlchemy)
- **QR Engine**: `qrcode`, `Pillow`
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5

## 📦 Installation & Setup

1. **Extract the project**:
   ```bash
   cd qr_management_system
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5000`.

4. **Register/Login**:
   Create an account to start generating and managing your QR codes.

## 📊 Database Modules
- **Users**: Authentication and profile management.
- **QR Codes**: Metadata, file paths, and customization settings.
- **Activity Logs**: Tracks generation and download history.

## 📄 License
Ahtisham-Irfan. Free to use for personal and commercial projects.

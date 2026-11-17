# Hospital Management System (Django)

A hospital management system built with Django, MySQL, Bootstrap 5, Bootstrap Icons and Django REST Framework.

## Modules (14 models in 12 apps)

| App | Models | Responsibility |
|---|---|---|
| accounts | User | Login, roles, account status, hashed passwords |
| patients | Patient | Patient registration |
| doctors | Doctor | Doctors, specialization, availability, consultation fee |
| departments | Department | Departments and their heads |
| appointments | Appointment | Booking, with doctor double-booking prevention |
| consultations | Consultation | Symptoms, diagnosis, treatment |
| admissions | Admission, Ward | Admissions and discharge; ward free beds update automatically |
| laboratory | LabTest | Lab requests and results |
| pharmacy | Medicine, Prescription | Stock, expiry and low-stock alerts; dispensing reduces stock |
| billing | Bill | Charges; can calculate them from the patient's records; total and status computed automatically |
| payments | Payment | Payments with auto-generated transaction references; overpayment is blocked |
| staff | Staff | Employees, positions, salaries |

## Role-based access

| Role | Can edit | Can view |
|---|---|---|
| Administrator | Everything | Everything |
| Receptionist | Patients, appointments | Doctors, departments, wards, admissions, bills, payments |
| Doctor | Appointments, consultations, admissions, lab tests, prescriptions | Patients, medicines, wards |
| Nurse | Admissions | Patients, appointments, consultations, lab tests, prescriptions, medicines, wards |
| Lab technician | Lab tests | Patients |
| Pharmacist | Medicines, dispensing | Patients, prescriptions |
| Accountant | Bills, payments | Patients, admissions, lab tests, prescriptions, staff |

The same rules apply to the REST API.

## Setup

```bash
pip install -r requirements.txt
```

### 1. Create the MySQL database

Open MySQL Workbench and run `mysql_setup.sql`. It creates `hospital_db` and an optional `hms_user`.

### 2. Set the connection details (PowerShell)

```powershell
$env:DB_NAME="hospital_db"; $env:DB_USER="root"; $env:DB_PASSWORD="your-password"
# optional: $env:DB_HOST="127.0.0.1"; $env:DB_PORT="3306"
```

To try the system without MySQL, set `$env:DB_ENGINE="sqlite"` instead.

### 3. Create the tables and run the server

```bash
python manage.py migrate
python manage.py seed_demo          # optional sample data
python manage.py createsuperuser    # or use the demo 'admin' account
python manage.py runserver
```

Open http://127.0.0.1:8000/

**Included sample database:** the repository ships with `db.sqlite3`, already filled with demo data. Run with `$env:DB_ENGINE="sqlite"; python manage.py runserver` and log in as `admin` (or any demo account below) with the password `hospital123`.

**Demo accounts** (after `seed_demo`): `admin`, `doctor`, `nurse`, `receptionist`, `lab_technician`, `pharmacist`, `accountant`. The password for all of them is `Hospital@123`.

## URLs

- `/`: dashboard with stats, today's appointments, ward occupancy, stock alerts, and revenue for accountants
- `/patients/`, `/doctors/`, `/appointments/`, ...: the modules, each with search, filters, pagination, detail, print, add, edit and delete
- `/api/`: browsable REST API, for example `/api/patients/?search=john`
- `/admin/`: Django admin

## Typical workflow

1. The receptionist registers a patient and books an appointment.
2. The doctor opens the appointment and clicks **Start consultation**. From the consultation they can **Prescribe medicine**, **Request lab test** or **Admit patient**.
3. The lab technician records results. The pharmacist clicks **Dispense**, which reduces stock.
4. The nurse discharges the patient, which frees the bed.
5. The accountant creates a bill and clicks **Calculate charges from records**, then **Record payment**. The bill status becomes Partially paid or Paid automatically.

## Tests

```bash
$env:DB_ENGINE="sqlite"; python manage.py test core
```

## Project structure

```
hms/          settings, root urls, REST API (api.py)
core/         shared CRUD framework (crud.py), role permissions, dashboard, seed command, tests
<app>/        models.py, urls.py (module config: fields, columns, roles), admin.py, migrations
templates/    base layout, generic list/detail/form templates, dashboard, login
static/css/   styles
```

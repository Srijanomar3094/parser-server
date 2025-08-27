# Contract Intelligence Parser - Backend

A Django-based REST API for automatically processing contracts and extracting critical financial and operational data.

## Features

- **Contract Upload**: Accept PDF contracts with background processing
- **Data Extraction**: Extract parties, financial details, payment terms, SLAs, and more
- **Scoring System**: Weighted scoring algorithm (0-100 points) with gap analysis
- **Status Tracking**: Real-time processing status and progress monitoring
- **RESTful API**: Complete CRUD operations for contracts
- **MongoDB Integration**: Scalable document-based storage

## API Endpoints

### 1. Contract Upload
- **POST** `/contracts/upload`
- Upload PDF contract files
- Returns `contract_id` immediately
- Initiates background processing

### 2. Processing Status
- **GET** `/contracts/{contract_id}/status`
- Check parsing progress
- Returns: `pending`, `processing`, `completed`, `failed`
- Includes progress percentage and error details

### 3. Contract Data
- **GET** `/contracts/{contract_id}`
- Returns parsed contract data in JSON
- Available only when processing is complete
- Includes extracted fields and confidence scores

### 4. Contract List
- **GET** `/contracts`
- Paginated list of all contracts
- Filtering by status, date, score
- Sorting and search capabilities

### 5. Contract Download
- **GET** `/contracts/{contract_id}/download`
- Download original contract file
- Maintains file integrity

## Data Extraction Fields

### Party Identification
- Contract parties (customer, vendor, third parties)
- Legal entity names and registration details
- Authorized signatories and roles

### Account Information
- Customer billing details
- Account numbers and references
- Contact information for billing/technical support

### Financial Details
- Line items with descriptions, quantities, and unit prices
- Total contract value and currency
- Tax information and additional fees

### Payment Structure
- Payment terms (Net 30, Net 60, etc.)
- Payment schedules and due dates
- Payment methods and banking details

### Revenue Classification
- Recurring vs. one-time payments
- Subscription models and billing cycles
- Renewal terms and auto-renewal clauses

### Service Level Agreements
- Performance metrics and benchmarks
- Penalty clauses and remedies
- Support and maintenance terms

## Scoring Algorithm

**Weighted Scoring System (0-100 points)**
- Financial completeness: **30 points**
- Party identification: **25 points**
- Payment terms clarity: **20 points**
- SLA definition: **15 points**
- Contact information: **10 points**

## Setup Instructions

### Prerequisites
- Python 3.12+
- Docker and Docker Compose
- MongoDB (or use Docker)

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd parser
   ```

2. **Start the services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Django API: http://localhost:8000
   - Admin interface: http://localhost:8000/admin
   - MongoDB: localhost:27017

### Option 2: Local Development

1. **Create virtual environment**
   ```bash
   python -m venv penv
   source penv/bin/activate  # On Windows: penv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MongoDB**
   - Install MongoDB locally or use Docker
   - Create database named "parser"

4. **Set environment variables**
   ```bash
   export DEBUG=True
   export SECRET_KEY=your-secret-key
   export MONGODB_HOST=localhost
   export MONGODB_PORT=27017
   export MONGODB_NAME=parser
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the server**
   ```bash
   python manage.py runserver
   ```

## Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_NAME=parser
```

## Testing

Run the test suite:
```bash
python manage.py test
```

## API Usage Examples

### Upload a Contract
```bash
curl -X POST http://localhost:8000/contracts/upload \
  -F "file=@contract.pdf"
```

### Check Status
```bash
curl http://localhost:8000/contracts/1/status
```

### Get Contract Data
```bash
curl http://localhost:8000/contracts/1
```

### List Contracts
```bash
curl "http://localhost:8000/contracts?status=completed&page=1"
```

## Project Structure

```
parser/
├── contracts/           # Main app
│   ├── models.py       # Contract model
│   ├── views.py        # API views
│   ├── urls.py         # URL routing
│   └── admin.py        # Admin interface
├── parser/             # Project settings
│   ├── settings.py     # Django settings
│   ├── urls.py         # Main URL config
│   └── wsgi.py         # WSGI application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker services
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.


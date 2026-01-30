# Scissor URL Backend API

A high-performance URL shortening service built with FastAPI, featuring advanced rate limiting, QR code generation, and secure URL management capabilities.

## Overview

Scissor URL Backend is a robust REST API that enables users to create, manage, and track shortened URLs. The service provides administrative controls for customizing shortened URL addresses, monitoring click analytics, and generating QR codes for seamless sharing.

## Technology Stack

-   **Framework**: FastAPI 0.115.4
-   **Language**: Python 3.x
-   **Database**: Supabase (PostgreSQL-based backend-as-a-service)
-   **Server**: Uvicorn (ASGI server)
-   **Additional Libraries**:
    -   `pydantic` - Data validation and settings management
    -   `segno` - QR code generation
    -   `cachetools` - In-memory caching with TTL support
    -   `python-dotenv` - Environment variable management
    -   `email-validator` - URL and email validation
    -   `CORS middleware` - Cross-origin request handling

## Project Structure

```
scissorapp/
├── __init__.py
├── database.py              # Supabase client initialization
├── dependencies.py          # Utility functions and business logic
├── models.py               # Data models (Pydantic)
├── schemas.py              # API request/response schemas
├── rate_limiter.py         # Custom rate limiting implementation
├── instance/
│   ├── __init__.py
│   └── config.py           # Configuration and environment settings
└── routers/
    ├── __init__.py
    └── link_shortener.py   # URL shortening endpoints
main.py                      # Application entry point
requirements.txt            # Project dependencies
```

## Core Features

### 1. URL Shortening

-   **Endpoint**: `POST /shorten-url`
-   **Description**: Generates a shortened URL from a long URL
-   **Validation**: Validates input URLs before processing
-   **Response**: Returns shortened URL and administrative details

### 2. Custom Short URLs

-   **Endpoint**: `PUT /{url_key}`
-   **Description**: Customize the shortened URL address
-   **Use Case**: Create memorable, branded short links
-   **Error Handling**: Prevents duplicate custom addresses

### 3. QR Code Generation

-   **Endpoint**: `GET /{url_key}/qrcode`
-   **Description**: Generates a QR code for the shortened URL
-   **Rate Limiting**: Limited to 10 requests per 60 seconds
-   **Caching**: Implements TTL-based caching for performance optimization
-   **Response Format**: Returns image stream (PNG format)

### 4. URL Tracking

-   **Click Analytics**: Tracks the number of clicks for each shortened URL
-   **Active Status**: Supports activating/deactivating URLs
-   **Admin Access**: Secure access using secret keys

### 5. Rate Limiting

-   **Custom Implementation**: IP-based rate limiting
-   **Configurable**: Easily adjustable limits per endpoint
-   **Protection**: Prevents API abuse and ensures fair usage

## API Endpoints

### POST /shorten-url

Shortens a long URL.

**Request Body:**

```json
{
    "target_url": "https://example.com/very/long/url"
}
```

**Response:**

```json
{
    "target_url": "https://example.com/very/long/url",
    "shortened_url": "https://yourapi.com/abc123",
    "admin_url": "https://yourapi.com/admin/abc123_secretkey123",
    "is_active": true,
    "clicks": 0
}
```

### PUT /{url_key}

Customizes the shortened URL address.

**Query Parameters:**

-   `url` (string): The key of the shortened URL or full address
-   `new_address` (string): The new custom address

**Response:**
Returns updated URL information with new address

### GET /{url_key}

Redirects to the target URL (with click tracking).

### GET /{url_key}/qrcode

Generates and returns a QR code image.

**Rate Limit**: 10 requests per 60 seconds

### GET /

Health check endpoint.

**Response:**

```json
{
    "msg": "Welcome to Scissor URL :)"
}
```

## Setup and Installation

### Prerequisites

-   Python 3.x
-   Supabase account and credentials
-   pip package manager

### Installation Steps

1. **Clone the repository**

    ```bash
    git clone <repository-url>
    cd scissor_url
    ```

2. **Create a virtual environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:

    ```env
    ENV_NAME=Production
    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_key
    BASE_URL=https://yourdomain.com
    ```

5. **Run the application**

    ```bash
    uvicorn main:app --reload
    ```

    The API will be available at `http://localhost:8000`

## Database Schema

The application uses a Supabase PostgreSQL table named `urls` with the following structure:

| Column     | Type             | Description                  |
| ---------- | ---------------- | ---------------------------- |
| id         | UUID             | Primary key                  |
| target_url | VARCHAR          | Original long URL            |
| key        | VARCHAR (UNIQUE) | Short URL identifier         |
| secret_key | VARCHAR (UNIQUE) | Secret key for admin access  |
| is_active  | BOOLEAN          | URL status (active/inactive) |
| clicks     | INTEGER          | Click count tracker          |
| created_at | TIMESTAMP        | Creation timestamp           |

## Configuration

### Environment Variables

-   `ENV_NAME`: Environment identifier (e.g., "Local Environment", "Production")
-   `SUPABASE_URL`: Supabase project URL
-   `SUPABASE_KEY`: Supabase API key
-   `BASE_URL`: Base URL for shortened links (default: `http://localhost:8000`)

### CORS Configuration

The application is configured to accept requests from:

-   `http://127.0.0.1:5500` (local development)
-   `https://v-scissor.netlify.app` (frontend deployment)

Modify `main.py` to adjust CORS settings as needed.

## Key Components

### Rate Limiter (`rate_limiter.py`)

Custom rate limiting implementation with:

-   IP-based request tracking
-   Configurable time intervals
-   HTTPException responses with remaining time details
-   Default: 10 requests per 60 seconds

### Dependencies (`dependencies.py`)

Utility functions handling:

-   Database operations (CRUD)
-   URL validation
-   Key generation (random and unique)
-   QR code generation
-   Error handling and HTTP exceptions

### Models (`models.py`)

Core data model:

-   `URL`: Represents a shortened URL with all associated metadata

### Schemas (`schemas.py`)

API schemas for validation:

-   `User_URL`: Input schema for URL shortening
-   `URL`: Extended schema with metadata
-   `URL_Info`: Response schema with admin information

## Testing

Run the test suite:

```bash
pytest test_main.py -v
```

## API Documentation

Interactive API documentation is available at:

-   **Swagger UI**: `/docs`
-   **ReDoc**: `/redoc`

The Swagger UI provides a comprehensive interface to test all endpoints with real-time responses.

## Performance Optimizations

1. **TTL Caching**: QR codes are cached for 5 minutes to reduce generation overhead
2. **Efficient Key Generation**: Unique keys are generated using cryptographic randomness
3. **Database Indexing**: The `key` and `secret_key` fields should be indexed for fast lookups
4. **Connection Pooling**: Supabase handles connection management automatically

## Error Handling

The API implements comprehensive error handling:

| Status Code | Scenario                   |
| ----------- | -------------------------- |
| 200         | Successful request         |
| 400         | Invalid URL or bad request |
| 404         | URL not found              |
| 429         | Rate limit exceeded        |
| 500         | Server error               |

All errors include descriptive messages to aid debugging.

## Security Considerations

1. **Secret Keys**: Each shortened URL has a unique secret key for administrative access
2. **URL Validation**: Input URLs are validated before processing
3. **Rate Limiting**: Protects against abuse and DDoS attacks
4. **Environment Variables**: Sensitive credentials are stored in `.env`
5. **CORS**: Restricted to specific domains in production
6. **Active Status Flag**: Allows disabling shortened URLs without deletion

## Deployment

The backend is deployed on Render:

-   **Production URL**: https://scissor-url.onrender.com
-   **Docs**: https://scissor-url.onrender.com/docs

### Deployment Steps

1. Push code to connected GitHub repository
2. Render automatically builds and deploys on push
3. Ensure environment variables are configured in Render dashboard

## Contributing

To contribute to the backend:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request with detailed description

## Future Enhancements

-   User authentication and authorization
-   URL expiration dates
-   Custom domain support
-   Advanced analytics dashboard
-   Batch URL shortening
-   API key management for programmatic access

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue in the repository or contact the development team.

---

**Last Updated**: January 2026
**Version**: 1.0.0

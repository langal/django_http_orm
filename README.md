# Django HTTP ORM

**A RESTful HTTP interface for Django ORM operations**

This library provides a simple, powerful HTTP API that exposes Django model operations through REST endpoints. It enables direct database operations via HTTP requests, making it useful for microservices, mobile apps, or any client that needs to interact with your Django models.

## 🚀 Features

- **Model Discovery**: List all models in a Django app
- **Schema Introspection**: Get detailed field information for any model
- **Full CRUD Operations**: Create, Read, Update, Delete via HTTP methods
- **Flexible Authentication**: Configurable auth and permission classes
- **Django Integration**: Uses Django's built-in ORM and serialization

## 📋 API Endpoints

### 1. Model Discovery
```
GET /orm/schema/module/{APP_NAME}
```
Returns a list of all Django models in the specified app.

**Example:**
```bash
curl https://your.server.com/orm/schema/module/myapp
```

**Response:**
```json
[
  {"name": "myapp.models.User"},
  {"name": "myapp.models.Product"}
]
```

### 2. Schema Introspection
```
GET /orm/schema/{FULL_MODEL_NAME}
```
Returns detailed field information for the specified model.

**Example:**
```bash
curl https://your.server.com/orm/schema/myapp.User
```

**Response:**
```json
[
  {
    "name": "id",
    "type": "AutoField",
    "nullable": "false",
    "auto_created": "true",
    "has_default": "false"
  },
  {
    "name": "email",
    "type": "EmailField", 
    "nullable": "false",
    "auto_created": "false",
    "has_default": "false"
  }
]
```

### 3. Query & Filter (GET)
```
GET /orm/query/{FULL_MODEL_NAME}?{field1}={value1}&{field2}={value2}
```
Searches and filters model instances using query parameters.

**Example:**
```bash
curl https://your.server.com/orm/query/myapp.User?email=john@example.com&is_active=true
```

### 4. Create (POST)
```
POST /orm/query/{FULL_MODEL_NAME}
Content-Type: application/json

{"field1": "value1", "field2": "value2"}
```
Creates a new model instance with the provided data.

**Example:**
```bash
curl -X POST https://your.server.com/orm/query/myapp.User \
     -H "Content-Type: application/json" \
     -d '{"email": "john@example.com", "first_name": "John"}'
```

### 5. Update (PUT)
```
PUT /orm/query/{FULL_MODEL_NAME}/{ID}
Content-Type: application/json

{"field1": "new_value"}
```
Updates an existing model instance by ID.

**Example:**
```bash
curl -X PUT https://your.server.com/orm/query/myapp.User/123 \
     -H "Content-Type: application/json" \
     -d '{"first_name": "Jane"}'
```

### 6. Delete (DELETE)
```
DELETE /orm/query/{FULL_MODEL_NAME}/{ID}
```
Deletes a model instance by ID.

**Example:**
```bash
curl -X DELETE https://your.server.com/orm/query/myapp.User/123
```

## 🏗️ Architecture

```
┌─────────────────┐    HTTP     ┌──────────────────┐    ORM    ┌──────────┐
│   HTTP Client   │ ──────────► │ Django HTTP ORM  │ ────────► │ Database │
│                 │             │                  │           │          │
│ • Browser       │             │ • ModuleSchema   │           │ • Models │
│ • Mobile App    │ ◄────────── │ • Schema         │ ◄──────── │ • Tables │
│ • API Client    │   JSON      │ • Query (CRUD)   │  Results  │ • Records│
└─────────────────┘             └──────────────────┘           └──────────┘
```

## 📦 Installation

1. **Install the package** in your Django project:
   ```python
   # Add to INSTALLED_APPS in settings.py
   INSTALLED_APPS = [
       # ... your other apps
       'django_http_orm',
   ]
   ```

2. **Include the URLs** in your main `urls.py`:
   ```python
   from django.urls import path, include
   
   urlpatterns = [
       # ... your other URLs
       path('', include('django_http_orm.urls')),
   ]
   ```

3. **Configure Authentication** (optional):
   ```python
   # settings.py
   DHOM_AUTH_CLASSES = [
       'rest_framework.authentication.TokenAuthentication',
       'rest_framework.authentication.SessionAuthentication',
   ]
   
   DHOM_PERM_CLASSES = [
       'rest_framework.permissions.IsAuthenticated',
   ]
   ```

## 🔐 Security Configuration

This library provides **direct database access** via HTTP, so proper security is crucial:

### Authentication Classes
Configure authentication by setting `DHOM_AUTH_CLASSES` in your Django settings:

```python
DHOM_AUTH_CLASSES = [
    'rest_framework.authentication.TokenAuthentication',
    'rest_framework.authentication.BasicAuthentication',
]
```

### Permission Classes  
Configure permissions by setting `DHOM_PERM_CLASSES` in your Django settings:

```python
DHOM_PERM_CLASSES = [
    'rest_framework.permissions.IsAuthenticated',
    'rest_framework.permissions.DjangoModelPermissions',
]
```

## 💡 Use Cases

- **Rapid Prototyping**: Quickly expose database operations for testing
- **Mobile App Backend**: Simple REST API for mobile applications
- **Microservices**: Database operations without complex API development
- **Admin Tools**: Custom admin interfaces with direct model access
- **Data Migration**: Bulk data operations via HTTP

## ⚠️ Important Considerations

- **Security**: Always configure proper authentication and permissions
- **Performance**: Consider caching and query optimization for production use
- **Validation**: Django model validation is applied automatically
- **Relationships**: Foreign key relationships are handled automatically
- **Transactions**: Each request is wrapped in a database transaction

## 🔧 Advanced Configuration

### Custom Model Access
The URL pattern accepts any Django model using the format `{app_name}.{ModelName}`:
- `myapp.User`
- `inventory.Product` 
- `auth.User` (built-in Django models)

### Field Types Support
Supports all Django field types including:
- Basic fields (CharField, IntegerField, etc.)
- Choice fields with enum support
- Foreign keys and relationships
- Auto-generated fields (timestamps, IDs)

## 🤝 Contributing

This is a simple but powerful tool for Django developers. Contributions are welcome for:
- Enhanced security features
- Performance optimizations
- Additional field type support
- Documentation improvements


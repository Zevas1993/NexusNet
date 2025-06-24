# NexusNet API Documentation

## Overview

The NexusNet API provides a comprehensive REST interface for interacting with the NexusNet neural network framework. This documentation covers all available endpoints, request/response formats, authentication methods, and usage examples.

**Base URL**: `http://localhost:8000` (default)  
**API Version**: v1  
**Content-Type**: `application/json`

## Authentication

### API Key Authentication

Include your API key in the request headers:

```http
Authorization: Bearer your-api-key-here
```

### JWT Authentication

For session-based authentication, first obtain a JWT token:

```http
POST /auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

Use the token in subsequent requests:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Core Endpoints

### Health Check

Check the health and status of the NexusNet service.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600.5,
  "system_info": {
    "cpu_count": 8,
    "memory_total": 32768,
    "gpu_available": true,
    "gpu_count": 1
  }
}
```

**Status Codes**:
- `200`: Service is healthy
- `503`: Service is unhealthy

### Process Input

Process input data through NexusNet's neural network.

**Endpoint**: `POST /process`

**Request Body**:
```json
{
  "input_data": "Your input text or data here",
  "input_type": "text",
  "options": {
    "max_length": 512,
    "temperature": 0.7,
    "top_p": 0.9,
    "enable_dreaming": true
  }
}
```

**Parameters**:
- `input_data` (required): The input data to process
- `input_type` (optional): Type of input - "text", "image", "audio", "video", "multimodal"
- `options` (optional): Processing options and parameters

**Response**:
```json
{
  "output": "Processed output text or data",
  "processing_time": 0.245,
  "metadata": {
    "model_version": "1.0.0",
    "tokens_processed": 128,
    "confidence_score": 0.95,
    "attention_weights": [...],
    "memory_usage": 1024
  }
}
```

**Status Codes**:
- `200`: Processing successful
- `400`: Invalid request format
- `422`: Invalid input data
- `500`: Processing error

**Example**:
```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "input_data": "What is the capital of France?",
    "input_type": "text",
    "options": {
      "max_length": 100,
      "temperature": 0.5
    }
  }'
```

### Batch Processing

Process multiple inputs in a single request.

**Endpoint**: `POST /process/batch`

**Request Body**:
```json
{
  "inputs": [
    {
      "input_data": "First input",
      "input_type": "text",
      "options": {"temperature": 0.7}
    },
    {
      "input_data": "Second input",
      "input_type": "text",
      "options": {"temperature": 0.5}
    }
  ],
  "batch_options": {
    "parallel": true,
    "max_batch_size": 32
  }
}
```

**Response**:
```json
{
  "results": [
    {
      "output": "First output",
      "processing_time": 0.123,
      "metadata": {...}
    },
    {
      "output": "Second output",
      "processing_time": 0.156,
      "metadata": {...}
    }
  ],
  "total_processing_time": 0.279,
  "batch_metadata": {
    "batch_size": 2,
    "parallel_processing": true
  }
}
```

## Training Endpoints

### Start Training

Initiate a training process with custom data.

**Endpoint**: `POST /train`

**Request Body**:
```json
{
  "data": [
    {
      "input": "Training input 1",
      "output": "Expected output 1",
      "metadata": {"category": "example"}
    },
    {
      "input": "Training input 2",
      "output": "Expected output 2",
      "metadata": {"category": "example"}
    }
  ],
  "training_config": {
    "epochs": 10,
    "learning_rate": 0.001,
    "batch_size": 32,
    "validation_split": 0.2,
    "early_stopping": true,
    "save_checkpoints": true
  }
}
```

**Response**:
```json
{
  "training_id": "train_123456789",
  "status": "started",
  "message": "Training started in background",
  "estimated_duration": 3600
}
```

### Training Status

Check the status of a training process.

**Endpoint**: `GET /train/{training_id}/status`

**Response**:
```json
{
  "training_id": "train_123456789",
  "status": "running",
  "progress": 45.5,
  "current_epoch": 5,
  "total_epochs": 10,
  "metrics": {
    "loss": 0.234,
    "accuracy": 0.892,
    "validation_loss": 0.267,
    "validation_accuracy": 0.876
  },
  "estimated_time_remaining": 1980
}
```

**Status Values**:
- `queued`: Training is queued
- `starting`: Training is initializing
- `running`: Training is in progress
- `completed`: Training completed successfully
- `failed`: Training failed
- `cancelled`: Training was cancelled

### Cancel Training

Cancel a running training process.

**Endpoint**: `DELETE /train/{training_id}`

**Response**:
```json
{
  "training_id": "train_123456789",
  "status": "cancelled",
  "message": "Training cancelled successfully"
}
```

## Model Management

### Model Information

Get information about the current model.

**Endpoint**: `GET /model/info`

**Response**:
```json
{
  "model_name": "NexusNet",
  "version": "1.0.0",
  "parameters": 175000000,
  "memory_usage": 2048.5,
  "capabilities": [
    "text_processing",
    "multimodal_understanding",
    "code_generation",
    "reasoning",
    "creative_writing"
  ],
  "supported_languages": ["en", "es", "fr", "de", "zh", "ja"],
  "max_context_length": 8192,
  "training_data_cutoff": "2024-01-01"
}
```

### Load Model

Load a specific model version or configuration.

**Endpoint**: `POST /model/load`

**Request Body**:
```json
{
  "model_name": "nexusnet-large",
  "version": "1.1.0",
  "config": {
    "precision": "fp16",
    "device": "cuda",
    "max_memory": 8192
  }
}
```

**Response**:
```json
{
  "status": "success",
  "model_name": "nexusnet-large",
  "version": "1.1.0",
  "load_time": 45.2,
  "memory_usage": 4096.0
}
```

### Save Model

Save the current model state.

**Endpoint**: `POST /model/save`

**Request Body**:
```json
{
  "save_path": "/models/custom_model",
  "include_optimizer": true,
  "compress": true,
  "metadata": {
    "description": "Custom trained model",
    "tags": ["production", "v1.0"]
  }
}
```

**Response**:
```json
{
  "status": "success",
  "save_path": "/models/custom_model",
  "file_size": 1024.5,
  "checksum": "sha256:abc123..."
}
```

## Memory Management

### Memory Usage

Get current memory usage statistics.

**Endpoint**: `GET /memory/usage`

**Response**:
```json
{
  "memory_usage": {
    "total_memory": 10000,
    "used_memory": 7500,
    "available_memory": 2500,
    "memory_efficiency": 0.75,
    "fragmentation": 0.05
  },
  "memory_pools": {
    "short_term": {
      "size": 3000,
      "utilization": 0.80
    },
    "long_term": {
      "size": 4000,
      "utilization": 0.70
    },
    "episodic": {
      "size": 500,
      "utilization": 0.60
    }
  }
}
```

### Memory Consolidation

Trigger memory consolidation process.

**Endpoint**: `POST /memory/consolidate`

**Request Body** (optional):
```json
{
  "force": false,
  "target_efficiency": 0.85,
  "preserve_recent": true
}
```

**Response**:
```json
{
  "status": "success",
  "result": {
    "memories_consolidated": 1250,
    "memory_freed": 512.5,
    "consolidation_time": 2.3,
    "efficiency_improvement": 0.12
  }
}
```

### Memory Search

Search through stored memories.

**Endpoint**: `POST /memory/search`

**Request Body**:
```json
{
  "query": "machine learning concepts",
  "limit": 10,
  "similarity_threshold": 0.7,
  "memory_types": ["episodic", "semantic"],
  "time_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  }
}
```

**Response**:
```json
{
  "results": [
    {
      "memory_id": "mem_123",
      "content": "Machine learning is a subset of AI...",
      "similarity_score": 0.95,
      "timestamp": "2024-06-15T10:30:00Z",
      "memory_type": "semantic",
      "metadata": {...}
    }
  ],
  "total_results": 25,
  "search_time": 0.045
}
```

## Evolution System

### Evolution Status

Get the current status of the evolution system.

**Endpoint**: `GET /evolution/status`

**Response**:
```json
{
  "evolution_status": {
    "active": true,
    "current_generation": 15,
    "population_size": 10,
    "best_fitness": 0.94,
    "average_fitness": 0.87,
    "evolution_progress": 0.75,
    "mutations_this_generation": 23,
    "crossovers_this_generation": 12
  },
  "current_population": [
    {
      "individual_id": "ind_001",
      "fitness": 0.94,
      "architecture": {...},
      "hyperparameters": {...}
    }
  ]
}
```

### Trigger Evolution

Manually trigger an evolution cycle.

**Endpoint**: `POST /evolution/trigger`

**Request Body** (optional):
```json
{
  "force_evolution": true,
  "target_fitness": 0.95,
  "max_generations": 5,
  "mutation_rate": 0.02
}
```

**Response**:
```json
{
  "status": "success",
  "result": {
    "evolution_triggered": true,
    "generation_started": 16,
    "estimated_duration": 1800,
    "evolution_id": "evo_789"
  }
}
```

### Evolution History

Get evolution history and statistics.

**Endpoint**: `GET /evolution/history`

**Query Parameters**:
- `limit`: Number of generations to return (default: 10)
- `include_details`: Include detailed population data (default: false)

**Response**:
```json
{
  "evolution_history": [
    {
      "generation": 15,
      "timestamp": "2024-06-24T12:00:00Z",
      "best_fitness": 0.94,
      "average_fitness": 0.87,
      "diversity_score": 0.65,
      "improvements": ["attention_heads", "layer_depth"]
    }
  ],
  "statistics": {
    "total_generations": 15,
    "fitness_improvement": 0.23,
    "convergence_rate": 0.05,
    "diversity_trend": "stable"
  }
}
```

## Immune System

### Immune Status

Get the current status of the neural immune system.

**Endpoint**: `GET /immune/status`

**Response**:
```json
{
  "immune_status": {
    "active": true,
    "health_score": 0.92,
    "threats_detected": 3,
    "threats_resolved": 2,
    "last_scan": "2024-06-24T11:45:00Z",
    "scan_frequency": 300,
    "auto_healing": true
  },
  "threat_categories": {
    "bias_detection": {
      "active": true,
      "threats_found": 1,
      "severity": "low"
    },
    "error_detection": {
      "active": true,
      "threats_found": 1,
      "severity": "medium"
    },
    "vulnerability_scan": {
      "active": true,
      "threats_found": 1,
      "severity": "low"
    }
  }
}
```

### Scan for Threats

Manually trigger a threat scan.

**Endpoint**: `POST /immune/scan`

**Request Body** (optional):
```json
{
  "scan_types": ["bias", "errors", "vulnerabilities"],
  "deep_scan": true,
  "auto_heal": true
}
```

**Response**:
```json
{
  "scan_id": "scan_456",
  "status": "completed",
  "threats_found": 2,
  "threats_healed": 1,
  "scan_duration": 15.7,
  "results": [
    {
      "threat_id": "threat_001",
      "type": "bias",
      "severity": "medium",
      "description": "Gender bias detected in text generation",
      "location": "attention_layer_3",
      "healed": true,
      "healing_method": "weight_adjustment"
    }
  ]
}
```

### Threat History

Get history of detected and resolved threats.

**Endpoint**: `GET /immune/threats`

**Query Parameters**:
- `limit`: Number of threats to return (default: 50)
- `severity`: Filter by severity level
- `status`: Filter by status (detected, resolved, ignored)
- `type`: Filter by threat type

**Response**:
```json
{
  "threats": [
    {
      "threat_id": "threat_001",
      "timestamp": "2024-06-24T10:30:00Z",
      "type": "bias",
      "severity": "medium",
      "status": "resolved",
      "description": "Gender bias in text generation",
      "resolution": "Automatic weight adjustment applied",
      "resolution_time": 2.3
    }
  ],
  "summary": {
    "total_threats": 127,
    "resolved_threats": 124,
    "pending_threats": 3,
    "average_resolution_time": 1.8
  }
}
```

## Plugin System

### List Plugins

Get a list of all available plugins.

**Endpoint**: `GET /plugins`

**Response**:
```json
{
  "plugins": [
    {
      "name": "TextEncoderPlugin",
      "version": "1.0.0",
      "status": "active",
      "capabilities": ["text_encoding", "tokenization"],
      "description": "Advanced text encoding plugin",
      "author": "NexusNet Team"
    },
    {
      "name": "ImageProcessorPlugin",
      "version": "1.2.0",
      "status": "inactive",
      "capabilities": ["image_processing", "feature_extraction"],
      "description": "Image processing and analysis plugin",
      "author": "Community"
    }
  ],
  "total_plugins": 15,
  "active_plugins": 12
}
```

### Plugin Status

Get detailed status of a specific plugin.

**Endpoint**: `GET /plugins/{plugin_name}/status`

**Response**:
```json
{
  "name": "TextEncoderPlugin",
  "status": "active",
  "initialized": true,
  "version": "1.0.0",
  "capabilities": ["text_encoding", "tokenization"],
  "configuration": {
    "max_length": 512,
    "vocab_size": 50000
  },
  "performance_metrics": {
    "requests_processed": 1250,
    "average_response_time": 0.023,
    "error_rate": 0.001
  },
  "last_used": "2024-06-24T11:30:00Z"
}
```

### Activate Plugin

Activate a specific plugin.

**Endpoint**: `POST /plugins/{plugin_name}/activate`

**Response**:
```json
{
  "status": "success",
  "plugin_name": "ImageProcessorPlugin",
  "message": "Plugin activated successfully",
  "activation_time": 1.2
}
```

### Deactivate Plugin

Deactivate a specific plugin.

**Endpoint**: `POST /plugins/{plugin_name}/deactivate`

**Response**:
```json
{
  "status": "success",
  "plugin_name": "ImageProcessorPlugin",
  "message": "Plugin deactivated successfully"
}
```

### Plugin Configuration

Update plugin configuration.

**Endpoint**: `PUT /plugins/{plugin_name}/config`

**Request Body**:
```json
{
  "config": {
    "max_length": 1024,
    "temperature": 0.7,
    "custom_parameter": "value"
  }
}
```

**Response**:
```json
{
  "status": "success",
  "plugin_name": "TextEncoderPlugin",
  "message": "Configuration updated successfully",
  "updated_config": {
    "max_length": 1024,
    "temperature": 0.7,
    "custom_parameter": "value"
  }
}
```

## System Statistics

### System Stats

Get comprehensive system statistics.

**Endpoint**: `GET /stats`

**Response**:
```json
{
  "cpu_usage": 45.2,
  "memory_usage": 67.8,
  "gpu_usage": 82.1,
  "active_connections": 15,
  "requests_processed": 12847,
  "uptime": 86400,
  "system_load": {
    "1min": 1.2,
    "5min": 1.1,
    "15min": 0.9
  },
  "disk_usage": {
    "total": 1000000,
    "used": 450000,
    "available": 550000
  },
  "network": {
    "bytes_sent": 1048576000,
    "bytes_received": 2097152000,
    "packets_sent": 1000000,
    "packets_received": 1500000
  }
}
```

### Performance Metrics

Get detailed performance metrics.

**Endpoint**: `GET /stats/performance`

**Query Parameters**:
- `timeframe`: Time range for metrics (1h, 24h, 7d, 30d)
- `granularity`: Data granularity (1m, 5m, 1h, 1d)

**Response**:
```json
{
  "timeframe": "24h",
  "granularity": "1h",
  "metrics": {
    "request_rate": [
      {"timestamp": "2024-06-24T00:00:00Z", "value": 120.5},
      {"timestamp": "2024-06-24T01:00:00Z", "value": 98.2}
    ],
    "response_time": [
      {"timestamp": "2024-06-24T00:00:00Z", "value": 0.245},
      {"timestamp": "2024-06-24T01:00:00Z", "value": 0.198}
    ],
    "error_rate": [
      {"timestamp": "2024-06-24T00:00:00Z", "value": 0.002},
      {"timestamp": "2024-06-24T01:00:00Z", "value": 0.001}
    ]
  },
  "summary": {
    "avg_request_rate": 109.3,
    "avg_response_time": 0.221,
    "avg_error_rate": 0.0015,
    "peak_request_rate": 245.7,
    "peak_response_time": 1.234
  }
}
```

## Configuration

### Get Configuration

Get current system configuration.

**Endpoint**: `GET /config`

**Response**:
```json
{
  "config": {
    "core": {
      "hidden_dim": 768,
      "device": "cuda",
      "precision": "fp16",
      "max_memory_size": 10000
    },
    "features": {
      "enable_dreaming": true,
      "enable_evolution": true,
      "enable_immune_system": true,
      "enable_compression": true
    },
    "api": {
      "host": "0.0.0.0",
      "port": 8000,
      "workers": 4,
      "timeout": 300
    },
    "security": {
      "enable_auth": true,
      "rate_limiting": true,
      "max_requests_per_minute": 100
    }
  }
}
```

### Update Configuration

Update system configuration.

**Endpoint**: `POST /config`

**Request Body**:
```json
{
  "config_updates": {
    "core.hidden_dim": 1024,
    "features.enable_dreaming": false,
    "api.timeout": 600
  }
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Configuration updated successfully",
  "updated_fields": [
    "core.hidden_dim",
    "features.enable_dreaming",
    "api.timeout"
  ],
  "restart_required": false
}
```

## WebSocket API

### Real-time Processing

Connect to the WebSocket endpoint for real-time processing.

**Endpoint**: `ws://localhost:8000/ws`

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
    console.log('Connected to NexusNet WebSocket');
};

ws.onmessage = function(event) {
    const response = JSON.parse(event.data);
    console.log('Received:', response);
};

// Send data for processing
ws.send(JSON.stringify({
    "input_data": "Process this in real-time",
    "input_type": "text",
    "options": {"stream": true}
}));
```

**Message Format**:
```json
{
  "type": "process",
  "data": {
    "input_data": "Your input here",
    "input_type": "text",
    "options": {}
  }
}
```

**Response Format**:
```json
{
  "type": "result",
  "data": {
    "output": "Processed output",
    "processing_time": 0.123,
    "metadata": {}
  }
}
```

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "The provided input data is invalid",
    "details": {
      "field": "input_data",
      "reason": "Input data cannot be empty"
    },
    "timestamp": "2024-06-24T12:00:00Z",
    "request_id": "req_123456"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT` | 400 | Invalid input data or parameters |
| `UNAUTHORIZED` | 401 | Authentication required or invalid |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `PROCESSING_ERROR` | 500 | Internal processing error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Rate Limiting

API requests are subject to rate limiting:

**Headers**:
- `X-RateLimit-Limit`: Maximum requests per time window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

**Rate Limit Response**:
```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 100,
      "window": "1 minute",
      "retry_after": 45
    }
  }
}
```

## SDK and Client Libraries

### Python SDK

```python
from nexusnet_client import NexusNetClient

client = NexusNetClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Process input
result = client.process("Hello, world!", input_type="text")
print(result.output)

# Batch processing
results = client.process_batch([
    {"input_data": "First input", "input_type": "text"},
    {"input_data": "Second input", "input_type": "text"}
])

# Training
training_id = client.start_training(
    data=training_data,
    config={"epochs": 10, "learning_rate": 0.001}
)

# Monitor training
status = client.get_training_status(training_id)
```

### JavaScript SDK

```javascript
import { NexusNetClient } from 'nexusnet-js';

const client = new NexusNetClient({
    baseUrl: 'http://localhost:8000',
    apiKey: 'your-api-key'
});

// Process input
const result = await client.process({
    inputData: 'Hello, world!',
    inputType: 'text'
});

console.log(result.output);

// WebSocket connection
const ws = client.createWebSocket();
ws.onMessage((data) => {
    console.log('Received:', data);
});

ws.send({
    inputData: 'Real-time processing',
    inputType: 'text'
});
```

### cURL Examples

#### Basic Processing
```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "input_data": "What is machine learning?",
    "input_type": "text",
    "options": {
      "max_length": 200,
      "temperature": 0.7
    }
  }'
```

#### Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

#### Get System Stats
```bash
curl -X GET "http://localhost:8000/stats" \
  -H "Authorization: Bearer your-api-key"
```

## Versioning

The NexusNet API uses semantic versioning. The current version is included in all responses:

```json
{
  "api_version": "1.0.0",
  "data": {...}
}
```

### Version Compatibility

- **Major version changes** (e.g., 1.x.x to 2.x.x): Breaking changes
- **Minor version changes** (e.g., 1.0.x to 1.1.x): New features, backward compatible
- **Patch version changes** (e.g., 1.0.0 to 1.0.1): Bug fixes, backward compatible

### API Deprecation

Deprecated endpoints will include a deprecation warning:

```http
Warning: 299 - "This endpoint is deprecated and will be removed in v2.0.0. Use /v2/process instead."
```

## Support

For API support and questions:

- **Documentation**: [https://nexusnet.readthedocs.io/api](https://nexusnet.readthedocs.io/api)
- **Issues**: [GitHub Issues](https://github.com/nexusnet/nexusnet/issues)
- **Email**: api-support@nexusnet.ai
- **Discord**: [NexusNet API Channel](https://discord.gg/nexusnet-api)

---

*This documentation is automatically generated from the NexusNet API specification. Last updated: 2024-06-24*


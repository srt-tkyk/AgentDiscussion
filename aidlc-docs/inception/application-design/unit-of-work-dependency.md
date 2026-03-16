# Unit of Work Dependencies

## Dependency Management Approach
**Strategy**: Shared dependency management across all units
**Architecture**: Centralized dependency injection with global configuration access

---

## Unit Dependency Matrix

### Inter-Unit Dependencies

| Unit | Depends On | Dependency Type | Communication Method |
|------|------------|-----------------|---------------------|
| Core Application (Unit 1) | AI Integration Service (Unit 2) | Service Dependency | API calls, streaming responses |
| Core Application (Unit 1) | Export Service (Unit 3) | Service Dependency | Export requests, file generation |
| AI Integration Service (Unit 2) | Core Application (Unit 1) | Callback Dependency | Streaming updates, status notifications |
| Export Service (Unit 3) | Core Application (Unit 1) | Data Dependency | Discussion data access |

### External Dependencies

| Unit | External Dependency | Purpose | Management Strategy |
|------|-------------------|---------|-------------------|
| Core Application | Streamlit Framework | Web UI framework | Shared dependency management |
| Core Application | Local File System | Data persistence | Centralized through FileManager |
| Core Application | YAML Configuration | Application settings | Global configuration access |
| AI Integration Service | Claude API (Anthropic) | AI agent responses | Secure API key management |
| AI Integration Service | HTTP Client Libraries | API communication | Shared dependency management |
| Export Service | File System | Export file generation | Centralized file operations |

---

## Dependency Architecture

### Shared Dependencies (All Units)
```python
# Core shared dependencies
dependencies = {
    "configuration": ConfigurationManager(),  # Global configuration access
    "file_manager": FileManager(),           # Centralized file operations
    "logging": LoggingManager(),             # Shared logging infrastructure
    "error_handling": ErrorHandler(),        # Consistent error handling
}
```

### Unit-Specific Dependencies

#### Core Application (Unit 1)
```python
core_dependencies = {
    # UI Framework
    "streamlit": "streamlit>=1.28.0",
    
    # Service Dependencies
    "ai_service": AIIntegrationService(),
    "export_service": ExportService(),
    
    # Internal Components
    "persona_service": PersonaService(),
    "discussion_service": DiscussionService(),
    
    # Shared Infrastructure
    "config": shared_dependencies["configuration"],
    "files": shared_dependencies["file_manager"],
}
```

#### AI Integration Service (Unit 2)
```python
ai_dependencies = {
    # External API
    "anthropic": "anthropic>=0.7.0",
    "httpx": "httpx>=0.24.0",
    
    # Configuration Access
    "config": shared_dependencies["configuration"],
    
    # Error Handling
    "error_handler": shared_dependencies["error_handling"],
    
    # Streaming Support
    "streaming_utils": StreamingUtilities(),
}
```

#### Export Service (Unit 3)
```python
export_dependencies = {
    # Export Libraries
    "markdown": "markdown>=3.4.0",
    "jinja2": "jinja2>=3.1.0",  # Template engine
    
    # File Operations
    "files": shared_dependencies["file_manager"],
    
    # Configuration
    "config": shared_dependencies["configuration"],
    
    # Data Access
    "discussion_data": DiscussionDataAccess(),
}
```

---

## Dependency Injection Strategy

### Centralized Container
```python
class DependencyContainer:
    """Centralized dependency injection container"""
    
    def __init__(self):
        # Initialize shared dependencies first
        self.config = ConfigurationManager()
        self.file_manager = FileManager(self.config)
        self.error_handler = ErrorHandler(self.config)
        
        # Initialize unit-specific dependencies
        self._initialize_core_dependencies()
        self._initialize_ai_dependencies()
        self._initialize_export_dependencies()
    
    def _initialize_core_dependencies(self):
        """Initialize Core Application dependencies"""
        self.persona_service = PersonaService(
            persona_manager=PersonaManager(self.file_manager, self.config),
            config=self.config
        )
        
        self.discussion_service = DiscussionService(
            discussion_engine=self.get_ai_service(),
            persona_service=self.persona_service,
            file_manager=self.file_manager,
            config=self.config
        )
        
        self.streamlit_ui = StreamlitUI(
            persona_service=self.persona_service,
            discussion_service=self.discussion_service,
            export_service=self.get_export_service(),
            config=self.config
        )
    
    def _initialize_ai_dependencies(self):
        """Initialize AI Integration Service dependencies"""
        self.ai_client = ClaudeAPIClient(self.config)
        self.discussion_engine = DiscussionEngine(
            api_client=self.ai_client,
            config=self.config,
            file_manager=self.file_manager
        )
    
    def _initialize_export_dependencies(self):
        """Initialize Export Service dependencies"""
        self.export_service = ExportService(
            file_manager=self.file_manager,
            config=self.config,
            template_engine=TemplateEngine()
        )
    
    def get_core_application(self):
        """Get Core Application with all dependencies"""
        return self.streamlit_ui
    
    def get_ai_service(self):
        """Get AI Integration Service"""
        return self.discussion_engine
    
    def get_export_service(self):
        """Get Export Service"""
        return self.export_service
```

### Application Initialization
```python
def initialize_application():
    """Initialize application with proper dependency injection"""
    
    # Create dependency container
    container = DependencyContainer()
    
    # Get main application with all dependencies injected
    app = container.get_core_application()
    
    return app, container
```

---

## Communication Patterns

### Core Application ↔ AI Integration Service
```python
# Core Application calls AI Service
class DiscussionService:
    def execute_discussion(self, session):
        # Request AI response
        response_stream = self.ai_service.stream_response(agent, context)
        
        # Handle streaming updates
        for chunk in response_stream:
            self.ui.stream_message_update(agent.name, chunk)

# AI Service streams back to Core Application
class DiscussionEngine:
    def stream_response(self, agent, context):
        # Generate streaming response
        for chunk in self.generate_ai_response(agent, context):
            yield chunk  # Stream back to Core Application
```

### Core Application ↔ Export Service
```python
# Core Application requests export
class DiscussionService:
    def export_discussion(self, discussion, format):
        # Request export from Export Service
        export_result = self.export_service.export_discussion(
            discussion, format, self.get_export_options()
        )
        return export_result

# Export Service accesses discussion data
class ExportService:
    def export_discussion(self, discussion, format, options):
        # Access discussion data through Core Application
        formatted_content = self.format_discussion(discussion, format)
        file_path = self.file_manager.save_export(formatted_content, format)
        return ExportResult(file_path, format)
```

---

## Dependency Lifecycle Management

### Singleton Dependencies
```python
# Global singletons
ConfigurationManager  # Single instance across all units
FileManager          # Centralized file operations
ErrorHandler         # Consistent error handling
```

### Unit-Scoped Dependencies
```python
# Per-unit instances
PersonaService       # Core Application scope
DiscussionService    # Core Application scope
ExportService        # Export Service scope
DiscussionEngine     # AI Integration Service scope
```

### Request-Scoped Dependencies
```python
# Per-request instances
DiscussionSession    # Created per discussion
ExportRequest        # Created per export operation
APIRequest           # Created per AI API call
```

---

## Configuration Management

### Shared Configuration Access
```python
# All units access configuration through global manager
class ConfigurationManager:
    def get_api_key(self) -> str:
        """Secure API key access for AI Integration Service"""
        
    def get_storage_path(self) -> str:
        """File storage path for Core Application"""
        
    def get_export_settings(self) -> dict:
        """Export configuration for Export Service"""
        
    def get_ui_settings(self) -> dict:
        """UI configuration for Core Application"""
```

### Unit-Specific Configuration Sections
```yaml
# config.yaml
core_application:
  ui_theme: "light"
  default_agents: 4
  max_turns: 20

ai_integration:
  api_key: "${CLAUDE_API_KEY}"
  timeout: 30
  retry_attempts: 3
  rate_limit: 100

export_service:
  default_format: "markdown"
  template_path: "./templates"
  output_path: "./exports"
```

---

## Error Handling and Resilience

### Cross-Unit Error Propagation
```python
# Errors flow through dependency chain
AI Integration Service Error → Discussion Service → UI Error Display
Export Service Error → Discussion Service → UI Error Display
```

### Unit-Specific Error Handling
```python
# Each unit handles its domain-specific errors
class AIIntegrationService:
    def handle_api_error(self, error):
        # Handle API-specific errors (rate limits, network issues)
        
class ExportService:
    def handle_export_error(self, error):
        # Handle export-specific errors (file permissions, template issues)
        
class CoreApplication:
    def handle_ui_error(self, error):
        # Handle UI-specific errors (user input, display issues)
```

---

## Dependency Summary

### Dependency Metrics
- **Inter-Unit Dependencies**: 4 relationships
- **External Dependencies**: 6 external systems/libraries
- **Shared Dependencies**: 4 global singletons
- **Unit-Specific Dependencies**: 8 specialized components

### Dependency Principles
- **Centralized Management**: Single dependency container manages all dependencies
- **Shared Infrastructure**: Common services (config, files, errors) shared across units
- **Clear Boundaries**: Each unit has well-defined dependency interfaces
- **Loose Coupling**: Units communicate through well-defined service interfaces
- **Dependency Injection**: All dependencies injected at initialization time

This dependency architecture ensures proper separation of concerns while enabling effective communication and shared resource management across all units.

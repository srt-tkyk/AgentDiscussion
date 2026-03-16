# Component Dependencies

## Dependency Management Approach
**Configuration**: Global configuration object accessible by all components
**File Persistence**: Centralized file manager component handling all persistence

---

## Dependency Matrix

### Component Dependencies
```
StreamlitUI
├── PersonaService (service)
├── DiscussionService (service)
├── ExportService (service)
└── ConfigurationManager (component)

PersonaUI
├── PersonaService (service)
└── ConfigurationManager (component)

DiscussionEngine
├── ConfigurationManager (component)
└── FileManager (component - for materials loading)

PersonaManager
├── FileManager (component)
└── ConfigurationManager (component)

FileManager
└── ConfigurationManager (component)

ConfigurationManager
└── (no dependencies - base component)
```

### Service Dependencies
```
PersonaService
├── PersonaManager (component)
├── PersonaUI (component)
└── ConfigurationManager (component)

DiscussionService
├── DiscussionEngine (component)
├── PersonaService (service)
├── FileManager (component)
├── StreamlitUI (component)
└── ConfigurationManager (component)

ExportService
├── FileManager (component)
├── DiscussionService (service)
└── ConfigurationManager (component)
```

---

## Communication Patterns

### UI Layer Communication
**Pattern**: UI components communicate through services, not directly with other components

```python
# StreamlitUI → Services → Components
class StreamlitUI:
    def __init__(self, persona_service: PersonaService, discussion_service: DiscussionService, 
                 export_service: ExportService, config: ConfigurationManager):
        self.persona_service = persona_service
        self.discussion_service = discussion_service
        self.export_service = export_service
        self.config = config
    
    def render_persona_selection(self):
        # UI calls service, service orchestrates components
        personas = self.persona_service.get_available_personas()
        return self.display_persona_options(personas)

# PersonaUI → PersonaService → PersonaManager
class PersonaUI:
    def __init__(self, persona_service: PersonaService, config: ConfigurationManager):
        self.persona_service = persona_service
        self.config = config
    
    def create_custom_persona(self, persona_data):
        # UI validates input, service handles business logic
        result = self.persona_service.create_persona(persona_data)
        return self.display_result(result)
```

### Service Layer Communication
**Pattern**: Services orchestrate components and communicate with other services through defined interfaces

```python
# DiscussionService orchestrates multiple components
class DiscussionService:
    def __init__(self, discussion_engine: DiscussionEngine, persona_service: PersonaService,
                 file_manager: FileManager, config: ConfigurationManager):
        self.discussion_engine = discussion_engine
        self.persona_service = persona_service
        self.file_manager = file_manager
        self.config = config
    
    def setup_discussion(self, topic, persona_ids, config):
        # Service coordinates multiple components
        personas = self.persona_service.manage_persona_selection(persona_ids)
        materials = self.file_manager.load_materials(config.materials_path)
        session = self.discussion_engine.start_discussion(topic, personas.data, config)
        return session
```

### Component Layer Communication
**Pattern**: Components access shared resources through global configuration and centralized file manager

```python
# All components access global configuration
class DiscussionEngine:
    def __init__(self, config: ConfigurationManager, file_manager: FileManager):
        self.config = config
        self.file_manager = file_manager
    
    def call_claude_api(self, prompt):
        # Component accesses global configuration
        api_key = self.config.get_api_key()
        # Direct API integration as designed
        return self.make_api_call(prompt, api_key)
    
    def load_discussion_materials(self, materials_path):
        # Component uses centralized file manager
        return self.file_manager.load_materials(materials_path)

# PersonaManager uses centralized file operations
class PersonaManager:
    def __init__(self, file_manager: FileManager, config: ConfigurationManager):
        self.file_manager = file_manager
        self.config = config
    
    def create_custom_persona(self, persona_data):
        # Component uses centralized file manager for persistence
        persona = self.create_persona_object(persona_data)
        self.file_manager.save_custom_persona(persona)
        return persona
```

---

## Data Flow Diagrams

### Discussion Workflow Data Flow
```
User Input (Topic, Personas, Config)
    ↓
StreamlitUI.render_discussion_setup()
    ↓
DiscussionService.setup_discussion()
    ├── PersonaService.manage_persona_selection()
    │   └── PersonaManager.get_personas()
    │       └── FileManager.load_custom_personas()
    │           └── ConfigurationManager.get_persona_storage_path()
    ├── FileManager.load_materials()
    │   └── ConfigurationManager.get_materials_path()
    └── DiscussionEngine.start_discussion()
        └── ConfigurationManager.get_api_key()
    ↓
DiscussionService.execute_discussion()
    ├── DiscussionEngine.get_next_response()
    │   └── Claude API (direct integration)
    └── StreamlitUI.stream_message_update()
    ↓
DiscussionService.save_discussion_results()
    └── FileManager.save_discussion()
        └── ConfigurationManager.get_discussion_storage_path()
    ↓
ExportService.export_discussion()
    └── FileManager.export_discussion()
        └── ConfigurationManager.get_export_path()
```

### Configuration Access Pattern
```
ConfigurationManager (Global Access Point)
    ├── API Key → DiscussionEngine
    ├── Storage Paths → FileManager
    ├── UI Settings → StreamlitUI, PersonaUI
    ├── Discussion Defaults → DiscussionService
    └── Export Settings → ExportService
```

### File Operations Pattern
```
FileManager (Centralized File Operations)
    ├── Discussion Persistence ← DiscussionService
    ├── Custom Persona Storage ← PersonaManager
    ├── Configuration Files ← ConfigurationManager
    ├── Export Generation ← ExportService
    └── Materials Loading ← DiscussionEngine
```

---

## Dependency Injection and Initialization

### Application Initialization Pattern
```python
def initialize_application():
    """Initialize application with proper dependency injection"""
    
    # Base layer - no dependencies
    config = ConfigurationManager()
    config.load_config()
    
    # Data layer - depends on config
    file_manager = FileManager(config)
    
    # Component layer - depends on config and file_manager
    persona_manager = PersonaManager(file_manager, config)
    discussion_engine = DiscussionEngine(config, file_manager)
    
    # Service layer - depends on components
    persona_service = PersonaService(persona_manager, config)
    discussion_service = DiscussionService(discussion_engine, persona_service, file_manager, config)
    export_service = ExportService(file_manager, discussion_service, config)
    
    # UI layer - depends on services
    persona_ui = PersonaUI(persona_service, config)
    streamlit_ui = StreamlitUI(persona_service, discussion_service, export_service, config)
    
    return streamlit_ui, persona_ui
```

### Dependency Lifecycle Management
```python
# Singleton pattern for global configuration
class ConfigurationManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Service instances created once and reused
class ApplicationContainer:
    def __init__(self):
        self.config = ConfigurationManager()
        self.file_manager = FileManager(self.config)
        # ... other component initialization
    
    def get_streamlit_ui(self):
        return self.streamlit_ui
```

---

## Error Handling and Communication

### Error Propagation Pattern
```python
# Errors flow up through service layer
Component Error → Service Error → UI Error Display

# Example error flow
PersonaManager.create_custom_persona() → ValidationError
    ↓
PersonaService.create_persona() → ServiceResult[Error]
    ↓
PersonaUI.create_custom_persona() → Display Error Message
```

### Cross-Component Communication Rules
1. **UI → Service → Component**: UI never directly calls components
2. **Service → Service**: Services can call other services through defined interfaces
3. **Component → Component**: Components only communicate through services or shared resources
4. **Global Access**: Configuration and FileManager provide global access points
5. **Event Flow**: Real-time updates flow from components through services to UI

---

## Dependency Summary

### Dependency Layers (Bottom-up)
1. **Base Layer**: ConfigurationManager (no dependencies)
2. **Data Layer**: FileManager (depends on ConfigurationManager)
3. **Component Layer**: PersonaManager, DiscussionEngine (depend on data layer)
4. **Service Layer**: PersonaService, DiscussionService, ExportService (depend on component layer)
5. **UI Layer**: StreamlitUI, PersonaUI (depend on service layer)

### Key Dependency Principles
- **Global Configuration**: Single configuration access point for all components
- **Centralized File Operations**: Single file manager handles all persistence
- **Service Orchestration**: Services coordinate component interactions
- **Dependency Injection**: Dependencies injected at initialization
- **Layered Architecture**: Clear dependency hierarchy prevents circular dependencies

**Total Dependencies**: 15 component dependencies + 8 service dependencies = 23 total dependency relationships

# Service Layer Design

## Service Architecture Approach
**Orchestration Level**: Domain services with separate services for personas, discussions, and exports
**API Integration**: Direct integration within discussion component (no separate API service layer)

---

## Domain Services

### PersonaService
**Purpose**: Domain service for persona management operations and business logic
**Responsibilities**:
- Orchestrate persona-related operations across components
- Implement persona business rules and validation
- Coordinate between PersonaManager and PersonaUI
- Handle persona lifecycle management
- Provide persona data to other services

**Service Methods**:
```python
def get_available_personas() -> List[Persona]
    """Get all available personas (pre-defined + custom)"""
    # Orchestrates: PersonaManager.get_predefined_personas() + custom personas
    # Business Logic: Combines and validates persona availability
    # Returns: Complete list of selectable personas

def create_persona(persona_data: PersonaData) -> ServiceResult[Persona]
    """Create new custom persona with validation"""
    # Orchestrates: PersonaUI.validate_persona_input() + PersonaManager.create_custom_persona()
    # Business Logic: Validates persona uniqueness, constraints, and business rules
    # Returns: Created persona or validation errors

def manage_persona_selection(selected_personas: List[str]) -> ServiceResult[List[Persona]]
    """Validate and process persona selection for discussion"""
    # Orchestrates: PersonaManager persona retrieval + selection validation
    # Business Logic: Ensures 2-6 persona limit, no duplicates, persona availability
    # Returns: Validated persona list or selection errors

def update_custom_persona(persona_id: str, updates: PersonaData) -> ServiceResult[Persona]
    """Update existing custom persona with validation"""
    # Orchestrates: PersonaManager.update_persona() + validation
    # Business Logic: Validates updates don't conflict with existing personas
    # Returns: Updated persona or validation errors

def delete_custom_persona(persona_id: str) -> ServiceResult[bool]
    """Delete custom persona with dependency checking"""
    # Orchestrates: PersonaManager.delete_persona() + dependency validation
    # Business Logic: Ensures persona not in use, handles cleanup
    # Returns: Success status or dependency errors
```

### DiscussionService
**Purpose**: Domain service for discussion orchestration and workflow management
**Responsibilities**:
- Orchestrate complete discussion workflows
- Coordinate between DiscussionEngine, FileManager, and UI components
- Implement discussion business rules and state management
- Handle discussion lifecycle from setup to completion
- Manage discussion persistence and retrieval

**Service Methods**:
```python
def setup_discussion(topic: str, persona_ids: List[str], config: DiscussionConfig) -> ServiceResult[DiscussionSession]
    """Set up new discussion with validation and initialization"""
    # Orchestrates: PersonaService.manage_persona_selection() + DiscussionEngine.start_discussion()
    # Business Logic: Validates topic, personas, configuration; initializes discussion state
    # Returns: Discussion session ready for execution or setup errors

def execute_discussion(session: DiscussionSession) -> ServiceResult[Discussion]
    """Execute complete discussion workflow with streaming"""
    # Orchestrates: DiscussionEngine sequential methods + StreamlitUI streaming updates
    # Business Logic: Manages turn sequence, handles streaming, monitors progress
    # Returns: Completed discussion or execution errors

def save_discussion_results(discussion: Discussion) -> ServiceResult[str]
    """Save completed discussion with metadata"""
    # Orchestrates: FileManager.save_discussion() + metadata generation
    # Business Logic: Generates discussion metadata, handles file naming, validates save
    # Returns: Save location or persistence errors

def load_discussion_history() -> ServiceResult[List[DiscussionSummary]]
    """Load and format discussion history for display"""
    # Orchestrates: FileManager.get_discussion_list() + summary formatting
    # Business Logic: Formats discussion metadata, sorts by date, handles pagination
    # Returns: Formatted discussion list or retrieval errors

def retrieve_discussion(discussion_id: str) -> ServiceResult[Discussion]
    """Retrieve specific discussion for viewing"""
    # Orchestrates: FileManager.load_discussion() + validation
    # Business Logic: Validates discussion exists, handles file corruption, formats for display
    # Returns: Complete discussion or retrieval errors

def load_discussion_materials(materials_path: str) -> ServiceResult[List[MaterialFile]]
    """Load and validate discussion materials"""
    # Orchestrates: FileManager.load_materials() + content validation
    # Business Logic: Validates file formats, handles missing directory, processes content
    # Returns: Processed materials or loading errors
```

### ExportService
**Purpose**: Domain service for discussion export and formatting operations
**Responsibilities**:
- Handle discussion export workflows
- Implement export formatting and business rules
- Coordinate between discussion data and file generation
- Manage export format options and validation
- Handle export file lifecycle

**Service Methods**:
```python
def export_discussion(discussion: Discussion, format: ExportFormat, options: ExportOptions) -> ServiceResult[ExportResult]
    """Export discussion in specified format with options"""
    # Orchestrates: Discussion formatting + FileManager.export_discussion()
    # Business Logic: Formats discussion content, applies export options, generates metadata
    # Returns: Export file path and metadata or export errors

def generate_meeting_minutes(discussion: Discussion) -> ServiceResult[MeetingMinutes]
    """Generate structured meeting minutes from discussion"""
    # Orchestrates: Discussion analysis + content structuring
    # Business Logic: Extracts key points, summarizes perspectives, formats sections
    # Returns: Structured meeting minutes or generation errors

def validate_export_options(format: ExportFormat, options: ExportOptions) -> ServiceResult[bool]
    """Validate export format and options compatibility"""
    # Orchestrates: Format validation + option compatibility checking
    # Business Logic: Ensures format supports options, validates file paths, checks permissions
    # Returns: Validation success or compatibility errors

def get_export_formats() -> List[ExportFormat]
    """Get available export formats and their capabilities"""
    # Orchestrates: Format enumeration + capability mapping
    # Business Logic: Lists supported formats, describes capabilities, provides format metadata
    # Returns: Available export formats with metadata
```

---

## Service Interactions and Orchestration

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

### Cross-Service Communication
```python
# PersonaService → DiscussionService
personas = PersonaService.get_available_personas()
selected = PersonaService.manage_persona_selection(user_selection)

# DiscussionService → PersonaService
discussion_setup = DiscussionService.setup_discussion(topic, persona_ids, config)

# DiscussionService → ExportService
export_result = ExportService.export_discussion(completed_discussion, format, options)

# ExportService → DiscussionService
discussion = DiscussionService.retrieve_discussion(discussion_id)
```

### Service Orchestration Patterns

#### Complete Discussion Workflow
```python
def complete_discussion_workflow(topic: str, persona_selection: List[str], config: DiscussionConfig) -> ServiceResult[ExportResult]:
    """Orchestrate complete discussion workflow from setup to export"""
    
    # 1. Setup Phase
    session = DiscussionService.setup_discussion(topic, persona_selection, config)
    if not session.success:
        return session.error
    
    # 2. Execution Phase
    discussion = DiscussionService.execute_discussion(session.data)
    if not discussion.success:
        return discussion.error
    
    # 3. Persistence Phase
    save_result = DiscussionService.save_discussion_results(discussion.data)
    if not save_result.success:
        return save_result.error
    
    # 4. Export Phase (optional)
    export_result = ExportService.export_discussion(discussion.data, ExportFormat.MARKDOWN, default_options)
    
    return export_result
```

---

## Service Layer Summary

### Domain Services (3 services)
- **PersonaService**: Persona management and validation
- **DiscussionService**: Discussion workflow orchestration
- **ExportService**: Export and formatting operations

### Service Characteristics
- **Stateless**: Services don't maintain state between calls
- **Orchestration**: Services coordinate component interactions
- **Business Logic**: Services implement domain-specific business rules
- **Error Handling**: Services provide consistent error handling and validation
- **Separation of Concerns**: Each service focuses on specific domain area

### Integration Points
- Services interact through well-defined interfaces
- Components are accessed through services (not directly by UI)
- Cross-service communication follows dependency hierarchy
- Configuration is accessed through ConfigurationManager by all services

**Total Service Methods**: 15 methods across 3 domain services

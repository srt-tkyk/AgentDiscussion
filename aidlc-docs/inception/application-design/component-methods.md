# Component Methods

## Method Design Approach
**Discussion Flow**: Single discussion manager with sequential methods
**Streaming**: Built into each component that generates streaming content

---

## UI Components Methods

### StreamlitUI Methods

#### Interface Rendering Methods
```python
def render_topic_input() -> str
    """Render topic input interface and return entered topic"""
    # Input: None
    # Output: Topic string
    # Purpose: Display topic entry form and capture user input

def render_persona_selection(available_personas: List[Persona]) -> List[Persona]
    """Render persona selection interface and return selected personas"""
    # Input: List of available personas
    # Output: List of selected personas (2-6 agents)
    # Purpose: Display persona options and capture user selections

def render_discussion_config() -> DiscussionConfig
    """Render discussion configuration interface and return settings"""
    # Input: None
    # Output: DiscussionConfig object with turn count and materials path
    # Purpose: Capture discussion parameters from user

def render_discussion_display(discussion_state: DiscussionState) -> None
    """Render real-time discussion display with streaming updates"""
    # Input: Current discussion state
    # Output: None (UI display)
    # Purpose: Show discussion progress with real-time streaming

def render_export_options(discussion: Discussion) -> ExportFormat
    """Render export options and return selected format"""
    # Input: Completed discussion object
    # Output: Export format selection
    # Purpose: Capture export preferences from user

def render_history_view(discussions: List[DiscussionSummary]) -> Optional[Discussion]
    """Render discussion history and return selected discussion"""
    # Input: List of discussion summaries
    # Output: Selected discussion for viewing (optional)
    # Purpose: Display past discussions and handle selection
```

#### Streaming Methods
```python
def stream_message_update(agent_name: str, message_chunk: str) -> None
    """Stream individual message chunks to UI in real-time"""
    # Input: Agent name and message chunk
    # Output: None (UI update)
    # Purpose: Display streaming message content as it arrives

def update_discussion_progress(current_turn: int, total_turns: int) -> None
    """Update discussion progress indicators"""
    # Input: Current turn number and total turns
    # Output: None (UI update)
    # Purpose: Show discussion progress to user
```

### PersonaUI Methods

```python
def display_predefined_personas(personas: List[Persona]) -> None
    """Display available pre-defined personas"""
    # Input: List of pre-defined personas
    # Output: None (UI display)
    # Purpose: Show persona options with descriptions

def render_custom_persona_form() -> PersonaData
    """Render custom persona creation form and return data"""
    # Input: None
    # Output: PersonaData with name and description
    # Purpose: Capture custom persona details from user

def handle_persona_selection(personas: List[Persona]) -> List[Persona]
    """Handle persona selection logic and return choices"""
    # Input: Available personas
    # Output: Selected personas (validated 2-6 selection)
    # Purpose: Process persona selection with validation

def validate_persona_input(persona_data: PersonaData) -> ValidationResult
    """Validate persona input data"""
    # Input: Persona data from form
    # Output: Validation result with errors if any
    # Purpose: Ensure persona data meets requirements
```

---

## API Components Methods

### DiscussionEngine Methods

#### Core Discussion Flow (Sequential Methods)
```python
def start_discussion(topic: str, personas: List[Persona], config: DiscussionConfig) -> DiscussionState
    """Initialize discussion with topic, agents, and configuration"""
    # Input: Topic string, selected personas, discussion configuration
    # Output: Initial discussion state
    # Purpose: Set up discussion context and prepare for agent responses

def get_next_response(discussion_state: DiscussionState) -> AgentResponse
    """Generate next agent response in sequence"""
    # Input: Current discussion state
    # Output: Agent response with content and metadata
    # Purpose: Generate next agent's contribution to discussion

def complete_discussion(discussion_state: DiscussionState) -> Discussion
    """Finalize discussion and return complete discussion object"""
    # Input: Final discussion state
    # Output: Complete discussion with all responses and metadata
    # Purpose: Wrap up discussion and prepare for export/storage

def get_discussion_state() -> DiscussionState
    """Get current discussion state and progress"""
    # Input: None
    # Output: Current discussion state
    # Purpose: Provide discussion status for UI updates
```

#### Streaming Methods (Built-in)
```python
def stream_response(agent: Persona, context: DiscussionContext) -> Iterator[str]
    """Stream agent response in real-time chunks"""
    # Input: Agent persona and discussion context
    # Output: Iterator yielding message chunks
    # Purpose: Generate streaming response content for real-time display

def generate_agent_response(agent: Persona, context: DiscussionContext) -> str
    """Generate complete agent response (internal method)"""
    # Input: Agent persona and discussion context
    # Output: Complete agent response
    # Purpose: Internal method for generating agent contributions
```

#### API Integration Methods (Direct Integration)
```python
def call_claude_api(prompt: str, persona: Persona) -> str
    """Direct Claude API integration for agent responses"""
    # Input: Formatted prompt and persona context
    # Output: API response content
    # Purpose: Handle direct API communication with Claude

def format_api_prompt(topic: str, persona: Persona, context: List[str]) -> str
    """Format prompt for Claude API based on discussion context"""
    # Input: Topic, persona, and previous discussion context
    # Output: Formatted API prompt
    # Purpose: Prepare context-aware prompts for API calls
```

### PersonaManager Methods

```python
def get_predefined_personas() -> List[Persona]
    """Retrieve all pre-defined personas"""
    # Input: None
    # Output: List of built-in personas (optimist, critic, engineer, philosopher)
    # Purpose: Provide default persona options

def create_custom_persona(name: str, description: str) -> Persona
    """Create new custom persona"""
    # Input: Persona name and personality description
    # Output: Created persona object
    # Purpose: Add user-defined persona to available options

def update_persona(persona_id: str, updates: PersonaData) -> Persona
    """Update existing custom persona"""
    # Input: Persona ID and update data
    # Output: Updated persona object
    # Purpose: Modify custom persona details

def delete_persona(persona_id: str) -> bool
    """Delete custom persona"""
    # Input: Persona ID to delete
    # Output: Success status
    # Purpose: Remove custom persona from available options

def validate_persona(persona_data: PersonaData) -> ValidationResult
    """Validate persona data constraints"""
    # Input: Persona data to validate
    # Output: Validation result with any errors
    # Purpose: Ensure persona meets system requirements
```

---

## Data Components Methods

### FileManager Methods (Centralized File Operations)

#### Discussion Persistence
```python
def save_discussion(discussion: Discussion) -> str
    """Save completed discussion to local storage"""
    # Input: Complete discussion object
    # Output: File path where discussion was saved
    # Purpose: Persist discussion for future access

def load_discussion(discussion_id: str) -> Discussion
    """Load specific discussion from storage"""
    # Input: Discussion identifier
    # Output: Complete discussion object
    # Purpose: Retrieve past discussion for viewing

def get_discussion_list() -> List[DiscussionSummary]
    """Get list of all saved discussions"""
    # Input: None
    # Output: List of discussion summaries with metadata
    # Purpose: Provide discussion history for user selection
```

#### Configuration Operations
```python
def save_configuration(config: AppConfig) -> bool
    """Save application configuration to file"""
    # Input: Configuration object
    # Output: Success status
    # Purpose: Persist configuration changes

def load_configuration() -> AppConfig
    """Load application configuration from file"""
    # Input: None
    # Output: Configuration object with all settings
    # Purpose: Initialize application with saved settings
```

#### Export and Materials
```python
def export_discussion(discussion: Discussion, format: ExportFormat) -> str
    """Generate export file for discussion"""
    # Input: Discussion object and export format
    # Output: Path to generated export file
    # Purpose: Create shareable discussion summary

def load_materials(materials_path: str) -> List[MaterialFile]
    """Load discussion materials from specified directory"""
    # Input: Path to materials directory
    # Output: List of material files with content
    # Purpose: Provide context materials to discussion engine
```

### ConfigurationManager Methods (Global Configuration)

```python
def load_config() -> AppConfig
    """Load and validate complete application configuration"""
    # Input: None
    # Output: Validated configuration object
    # Purpose: Initialize application configuration

def get_setting(key: str) -> Any
    """Retrieve specific configuration value"""
    # Input: Configuration key
    # Output: Configuration value
    # Purpose: Provide configuration access to components

def update_setting(key: str, value: Any) -> bool
    """Update specific configuration value"""
    # Input: Configuration key and new value
    # Output: Success status
    # Purpose: Modify configuration settings

def validate_config(config: AppConfig) -> ValidationResult
    """Validate configuration completeness and correctness"""
    # Input: Configuration object
    # Output: Validation result with any errors
    # Purpose: Ensure configuration is valid for application operation

def get_api_key() -> str
    """Secure access to Claude API key"""
    # Input: None
    # Output: API key string
    # Purpose: Provide secure API key access to discussion engine
```

---

## Method Summary

### Total Methods by Component
- **StreamlitUI**: 8 methods (6 rendering + 2 streaming)
- **PersonaUI**: 4 methods (display and validation)
- **DiscussionEngine**: 8 methods (4 core flow + 2 streaming + 2 API)
- **PersonaManager**: 5 methods (CRUD operations + validation)
- **FileManager**: 7 methods (persistence + export + materials)
- **ConfigurationManager**: 5 methods (configuration management)

**Total Methods**: 37 methods across 6 components

**Note**: Detailed business rules and implementation logic will be defined later in Functional Design (CONSTRUCTION phase).

# Application Components

## Component Organization
**Approach**: UI-focused organization with clear separation between UI components, API components, and data components.

---

## UI Components

### StreamlitUI
**Purpose**: Main user interface component handling all Streamlit-based interactions
**Responsibilities**:
- Render topic input interface
- Display persona selection and custom persona creation forms
- Show discussion configuration options (turn count, materials directory)
- Present real-time discussion streaming display
- Provide export and history management interfaces
- Handle user interactions and form submissions
- Coordinate with other components for data display

**Key Interfaces**:
- `render_topic_input()` - Topic entry interface
- `render_persona_selection()` - Persona management interface
- `render_discussion_config()` - Discussion parameter setup
- `render_discussion_display()` - Real-time discussion view
- `render_export_options()` - Export functionality interface
- `render_history_view()` - Past discussions interface

### PersonaUI
**Purpose**: Specialized UI component for persona management
**Responsibilities**:
- Display pre-defined persona selection interface
- Handle custom persona creation forms
- Manage persona editing and deletion
- Validate persona input data
- Coordinate with PersonaManager for persona operations

**Key Interfaces**:
- `display_predefined_personas()` - Show available personas
- `render_custom_persona_form()` - Custom persona creation
- `handle_persona_selection()` - Process persona choices
- `validate_persona_input()` - Input validation

---

## API Components

### DiscussionEngine
**Purpose**: Core discussion management component with direct Claude API integration
**Responsibilities**:
- Manage discussion flow and agent turn sequencing
- Integrate directly with Claude API for agent responses
- Handle discussion state and progression
- Generate agent responses based on topic, personas, and context
- Stream responses in real-time
- Coordinate discussion completion

**Key Interfaces**:
- `start_discussion()` - Initialize discussion with topic and agents
- `get_next_response()` - Generate next agent response
- `stream_response()` - Handle real-time response streaming
- `complete_discussion()` - Finalize discussion
- `get_discussion_state()` - Current discussion status

### PersonaManager
**Purpose**: Separate component for persona management operations
**Responsibilities**:
- Manage pre-defined persona definitions
- Handle custom persona creation, editing, and deletion
- Validate persona data and constraints
- Provide persona data to discussion engine
- Persist custom personas

**Key Interfaces**:
- `get_predefined_personas()` - Retrieve built-in personas
- `create_custom_persona()` - Add new custom persona
- `update_persona()` - Modify existing persona
- `delete_persona()` - Remove custom persona
- `validate_persona()` - Validate persona data

---

## Data Components

### FileManager
**Purpose**: Centralized file management component handling all persistence operations
**Responsibilities**:
- Handle all file I/O operations for the application
- Manage discussion history persistence
- Handle configuration file operations
- Manage custom persona storage
- Handle export file generation
- Manage discussion materials directory access

**Key Interfaces**:
- `save_discussion()` - Persist completed discussion
- `load_discussion()` - Retrieve past discussion
- `get_discussion_list()` - List all saved discussions
- `save_configuration()` - Persist app configuration
- `load_configuration()` - Load app settings
- `export_discussion()` - Generate export files
- `load_materials()` - Access discussion materials

### ConfigurationManager
**Purpose**: Global configuration management component
**Responsibilities**:
- Load and validate application configuration
- Provide configuration access to all components
- Handle configuration updates and persistence
- Validate API keys and settings
- Manage default settings and user preferences

**Key Interfaces**:
- `load_config()` - Load configuration from file
- `get_setting()` - Retrieve specific configuration value
- `update_setting()` - Modify configuration value
- `validate_config()` - Validate configuration completeness
- `get_api_key()` - Secure API key access

---

## Component Summary

### UI Layer (2 components)
- **StreamlitUI**: Main interface coordination
- **PersonaUI**: Specialized persona management interface

### API Layer (2 components)  
- **DiscussionEngine**: Core discussion logic with direct API integration
- **PersonaManager**: Persona management operations

### Data Layer (2 components)
- **FileManager**: Centralized file operations
- **ConfigurationManager**: Global configuration access

**Total Components**: 6 components with clear separation of concerns and focused responsibilities.

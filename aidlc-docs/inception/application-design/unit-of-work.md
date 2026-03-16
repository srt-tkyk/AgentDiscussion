# Unit of Work

## Unit Decomposition Approach
**Strategy**: Journey-based units with hybrid deployment architecture
**Deployment**: Containerized application with core monolith + separate services
**Streaming**: Consolidated streaming logic in core unit for consistency

---

## Unit Definitions

### Unit 1: Core Application (Monolith)
**Type**: Core Monolithic Service
**Deployment**: Primary container with Streamlit application

**Responsibilities**:
- Main Streamlit web interface
- User journey orchestration (setup → discussion → export → history)
- Real-time streaming coordination (consolidated streaming logic)
- Core business logic and workflow management
- Local file system operations
- Configuration management

**Components Included**:
- StreamlitUI (main interface)
- PersonaUI (persona management interface)
- DiscussionService (workflow orchestration)
- PersonaService (persona operations)
- FileManager (centralized file operations)
- ConfigurationManager (global configuration)

**User Stories Covered**:
- US-1.1: Basic Application Setup
- US-2.1: Topic Input
- US-2.2: Select Pre-defined Personas
- US-2.3: Create Custom Persona
- US-2.4: Configure Discussion Parameters
- US-2.5: Access Discussion Materials
- US-3.1: Start Discussion
- US-3.2: Stream Agent Messages (consolidated streaming)
- US-3.3: Display Discussion History
- US-4.1: Export Meeting Minutes
- US-4.2: Auto-save Discussion
- US-5.1: View Discussion List
- US-5.2: Load Previous Discussion

**Key Features**:
- Complete user interface and experience
- Discussion workflow management
- Real-time streaming (all streaming logic consolidated here)
- File persistence and configuration
- Export functionality
- History management

### Unit 2: AI Integration Service (Separate Service)
**Type**: External Service
**Deployment**: Separate service/module for AI API integration

**Responsibilities**:
- Claude API integration and communication
- AI prompt formatting and context management
- Response processing and error handling
- API rate limiting and retry logic
- Agent persona context management for API calls

**Components Included**:
- DiscussionEngine (AI integration portion)
- PersonaManager (persona context for AI)
- API client utilities and error handling

**User Stories Covered**:
- US-6.1: Handle API Errors (AI-specific error handling)
- Supporting functionality for discussion execution stories

**Key Features**:
- Secure API key management
- Robust error handling for external API
- Context-aware prompt generation
- Response streaming to core application

### Unit 3: Export Service (Separate Service)
**Type**: Specialized Service
**Deployment**: Separate service/module for export operations

**Responsibilities**:
- Meeting minutes generation and formatting
- Export file creation and management
- Multiple export format support
- Export template management
- Export validation and quality assurance

**Components Included**:
- ExportService (specialized export operations)
- Export formatting utilities
- Template management

**User Stories Covered**:
- US-4.1: Export Meeting Minutes (specialized formatting)
- Export-related portions of history stories

**Key Features**:
- Multiple export formats (Markdown, PDF, etc.)
- Structured meeting minutes generation
- Export template customization
- Export file management

---

## Unit Architecture

### Hybrid Deployment Model
```
┌─────────────────────────────────────────────────────────────┐
│                    Container Environment                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Core Application (Unit 1)              │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │    │
│  │  │ StreamlitUI │ │ Discussions │ │ File Manager│   │    │
│  │  │             │ │   Service   │ │             │   │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │    │
│  │  │ PersonaUI   │ │   Persona   │ │   Config    │   │    │
│  │  │             │ │   Service   │ │  Manager    │   │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          AI Integration Service (Unit 2)            │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │    │
│  │  │ Discussion  │ │   Persona   │ │ API Client  │   │    │
│  │  │   Engine    │ │   Manager   │ │ Utilities   │   │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Export Service (Unit 3)                  │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │    │
│  │  │   Export    │ │  Formatting │ │  Template   │   │    │
│  │  │   Service   │ │  Utilities  │ │  Manager    │   │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Unit Communication
- **Core Application** ↔ **AI Integration Service**: API calls for discussion execution
- **Core Application** ↔ **Export Service**: Export requests and file generation
- **AI Integration Service** → **Core Application**: Streaming responses and status updates
- **Export Service** → **Core Application**: Generated export files and status

---

## Code Organization Strategy

### Directory Structure (Feature-based)
```
agent_discussion/
├── personas/                    # Persona management features
│   ├── __init__.py
│   ├── ui.py                   # PersonaUI component
│   ├── service.py              # PersonaService
│   ├── manager.py              # PersonaManager component
│   └── models.py               # Persona data models
├── discussions/                 # Discussion features
│   ├── __init__.py
│   ├── service.py              # DiscussionService
│   ├── engine.py               # DiscussionEngine component
│   ├── streaming.py            # Consolidated streaming logic
│   └── models.py               # Discussion data models
├── exports/                     # Export features
│   ├── __init__.py
│   ├── service.py              # ExportService
│   ├── formatters.py           # Export formatting utilities
│   └── templates/              # Export templates
├── ui/                         # Main UI components
│   ├── __init__.py
│   ├── main.py                 # StreamlitUI main interface
│   ├── components.py           # Shared UI components
│   └── utils.py                # UI utilities
├── core/                       # Core infrastructure
│   ├── __init__.py
│   ├── config.py               # ConfigurationManager
│   ├── files.py                # FileManager
│   ├── dependencies.py         # Dependency injection
│   └── models.py               # Shared data models
├── ai/                         # AI integration (Unit 2)
│   ├── __init__.py
│   ├── client.py               # Claude API client
│   ├── prompts.py              # Prompt formatting
│   └── errors.py               # AI-specific error handling
├── main.py                     # Application entry point
├── requirements.txt            # Dependencies
├── config.yaml                 # Configuration file
└── README.md                   # Documentation
```

### Python Package Structure
**Single Package with Submodules**: `agent_discussion.ui`, `agent_discussion.services`, etc.

```python
# Package imports
from agent_discussion.ui.main import StreamlitUI
from agent_discussion.personas.service import PersonaService
from agent_discussion.discussions.service import DiscussionService
from agent_discussion.exports.service import ExportService
from agent_discussion.core.config import ConfigurationManager
from agent_discussion.core.files import FileManager
```

---

## Unit Characteristics

### Unit 1: Core Application
- **Size**: Large (primary application logic)
- **Complexity**: High (orchestrates all user workflows)
- **Dependencies**: AI Integration Service, Export Service
- **Deployment**: Primary container, always running
- **Scaling**: Single instance (personal tool)

### Unit 2: AI Integration Service
- **Size**: Medium (focused on API integration)
- **Complexity**: Medium (API handling and error management)
- **Dependencies**: External Claude API
- **Deployment**: Service module within container
- **Scaling**: Single instance with retry logic

### Unit 3: Export Service
- **Size**: Small (specialized functionality)
- **Complexity**: Low (formatting and file generation)
- **Dependencies**: Core Application for data
- **Deployment**: Service module within container
- **Scaling**: On-demand execution

---

## Development Workflow

### Unit Development Sequence
1. **Core Application (Unit 1)**: Develop main application structure and UI
2. **AI Integration Service (Unit 2)**: Implement API integration and streaming
3. **Export Service (Unit 3)**: Add export functionality and formatting

### Integration Points
- **Shared Models**: Common data structures across units
- **Dependency Injection**: Centralized dependency management
- **Configuration**: Global configuration accessible to all units
- **Error Handling**: Consistent error handling patterns across units

### Testing Strategy
- **Unit 1**: UI testing, workflow testing, integration testing
- **Unit 2**: API integration testing, error handling testing, streaming testing
- **Unit 3**: Export format testing, template testing, file generation testing

This unit decomposition provides a balanced approach with a core monolithic application for user experience consistency, while separating concerns for AI integration and export functionality to enable focused development and maintenance.

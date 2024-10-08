# 🏗️ Fenec Models

The models in Fenec are the core structures used to represent and handle code blocks within a project. They play a crucial role in parsing projects, storing information in both vector and graph databases, and facilitating code analysis and interaction. Due to the recent decision to use ChromaDB as the primary database (a single source of truth), the current model structure is less than optimal and a temporary stop gap. We welcome any suggestions for improvement.

## 🌟 Features

-   📊 Hierarchical representation of code structures
-   🔗 Support for various code block types (modules, classes, functions, etc.)
-   🧠 Integration with and use by AI services for code summarization
-   🔄 Conversion methods for ChromaDB storage and retrieval

> **NOTE:** The models in Fenec are internal structures used for code analysis and are not intended for direct interaction by end-users. They are designed to be used by Fenec's code analysis pipeline to parse, store, and analyze code structures. The documentation is provided for reference and internal development purposes and should be used for diagnosing issues, extending Fenec's functionality, or gaining a better understanding of how Fenec works.

> **IMPORTANT:** Due to time constraints and the need to quickly adapt to using ChromaDB as a single source of truth, the current model structure may not be optimal. We welcome any suggestions for improvement. If you have ideas for better ways to structure these models or to work with ChromaDB's limitations, or if you think a different database should be added as a single source of truth, please open an issue or submit a pull request. Your contributions can help shape the future of Fenec!

## 🧩 Core Components

### Enums

-   `ImportModuleType`: Categorizes import types (e.g., STANDARD_LIBRARY, LOCAL, THIRD_PARTY).
-   `CommentType`: Identifies important comment types (e.g., TODO, FIXME, NOTE).
-   `BlockType`: Defines the types of code blocks (e.g., MODULE, CLASS, FUNCTION).

### Base Models

All the models in Fenec inherit from Pydantic's `BaseModel` for data validation and serialization.

#### BaseCodeBlockModel

The foundation for all code block models, containing common attributes such as:

-   `id`: Unique identifier
-   `file_path`: Path to the source file
-   `parent_id`: Identifier of the parent block
-   `block_type`: Type of the code block
-   `start_line_num` and `end_line_num`: Line numbers in the source file
-   `code_content`: Actual code content
-   `important_comments`: List of important comments
-   `dependencies`: List of imports and dependencies
-   `summary`: AI-generated summary of the code block
-   `children_ids`: List of child block identifiers

#### Specific Models

1. **ModuleModel**: Represents a Python module file.

    - Additional attributes: `docstring`, `header`, `footer`, `imports`

2. **ClassModel**: Represents a Python class.

    - Additional attributes: `class_name`, `decorators`, `bases`, `keywords`

3. **FunctionModel**: Represents a Python function or method.

    - Additional attributes: `function_name`, `parameters`, `returns`, `is_method`, `is_async`

4. **StandaloneCodeBlockModel**: Represents standalone code snippets.

    - Additional attributes: `variable_assignments`

5. **DirectoryModel**: Represents a directory in the project structure.
    - Attributes: `directory_name`, `sub_directories_ids`, `children_ids`

### Supporting Models

-   `ImportNameModel`: Represents the name of an import.
-   `ImportModel`: Represents an import statement.
-   `DependencyModel`: Represents a module dependency.
-   `CommentModel`: Represents an important comment.
-   `DecoratorModel`: Represents a decorator.
-   `ClassKeywordModel`: Represents a class keyword.
-   `ParameterModel` and `ParameterListModel`: Represent function parameters.

## 🚀 Usage

These models are used throughout Fenec for parsing, storing, and analyzing code. Here's a basic example of how they might be used:

```python
from fenec.models import (
    ModuleModel,
    FunctionModel,
    ImportModel,
    BlockType,
    ImportModuleType,
)

# Create a module model
module = ModuleModel(
    id="module_1",
    file_path="/path/to/module.py",
    block_type=BlockType.MODULE,
    start_line_num=1,
    end_line_num=100,
    code_content="...",
    imports=[
        ImportModel(
            import_names=[{"name": "os"}],
            import_module_type=ImportModuleType.STANDARD_LIBRARY
        )
    ]
)

# Create a function model
function = FunctionModel(
    id="function_1",
    file_path="/path/to/module.py",
    parent_id="module_1",
    block_type=BlockType.FUNCTION,
    start_line_num=10,
    end_line_num=20,
    code_content="def example_function():\n    pass",
    function_name="example_function"
)

# Add function to module's children
module.children_ids.append(function.id)
```

## 🔄 ChromaDB Integration

Each model includes methods for converting to and from metadata dictionaries, facilitating storage and retrieval from ChromaDB:

-   `convert_to_metadata()`: Converts and flattens the model to a metadata dictionary for ChromaDB storage.
-   `build_from_metadata()`: Creates a model instance from a metadata dictionary retrieved from ChromaDB.

These methods have been adapted to work with ChromaDB's flat structure, which presents some limitations compared to the original model design. The current implementation uses JSON serialization for complex nested structures to fit within ChromaDB's constraints.

## 🚧 Under Development

The model structure in Fenec is under active development. Current areas of focus include:

-   Optimizing model structures for more efficient parsing and storage in ChromaDB
-   Enhancing support for complex code relationships within ChromaDB's limitations
-   Improving integration with AI services for better code summarization
-   Exploring alternative strategies for storing hierarchical data in ChromaDB

## 🔮 Future Enhancements

1. **Directory Model Integration**: Enhancing the parsing and summarization logic to include use of the DirectoryModel to give the LLM a more comprehensive overview of the codebase.

2. **Project Model**: A new model is planned to represent an entire project, storing a comprehensive summary above the directory and module levels.

3. **Customizable CommentType Enum**: Allowing users to define their own important comment types for better code analysis of their projects.

4. **Partial Project Update**: The models may be extended or changed to better support updating parts of the project that have changed without needing to use git and remember to run Fenec on each commit.

5. **Alternative Data Storage**: Exploring options for storing hierarchical data more efficiently, possibly using a combination of ChromaDB and other storage solutions.

## 🤝 Contributing

We welcome contributions to improve and expand the model structures in Fenec! If you have ideas for better ways to represent code structures, enhance the existing models, or work around ChromaDB's limitations, please check our [Contributing Guidelines](../CONTRIBUTING.md) and consider opening an issue or submitting a pull request.

Some areas where contributions would be particularly valuable:

-   Tests, yes testing is lacking here too!
-   Optimizing model structures for performance and memory efficiency within ChromaDB constraints
-   Enhancing model conversion methods for ChromaDB compatibility
-   Implementing support for additional programming language constructs
-   Developing utilities for model analysis and visualization
-   Proposing alternative strategies for storing and retrieving hierarchical data in ChromaDB

## 🗺️ Roadmap

The future development of Fenec's models will focus on:

1. Tests, tests, and more tests!
2. Implementing the Project Model for comprehensive project representation
3. Reevaluating the model structure to better align with ChromaDB's capabilities and limitations
4. Exploring hybrid storage solutions to overcome ChromaDB's flat structure limitations

For a more comprehensive view of our plans, please refer to our [Roadmap](../ROADMAP.md).

We appreciate your interest in Fenec's model structures and look forward to your contributions in making them even more powerful and versatile!

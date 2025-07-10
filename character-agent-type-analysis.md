# Character and Agent Type Analysis Report

## Overview
This report compares the actual TypeScript definitions of `Character` and `Agent` types in the eliza codebase against what's documented in `core-concepts/agents.mdx`.

## Key Findings

### 1. Documentation is Significantly Incomplete

The current documentation in `agents.mdx` only covers a small subset of the available properties and uses incorrect property names in some cases.

#### Properties Missing from Documentation:
- `id` (optional UUID)
- `username` (optional string)
- `system` (optional system prompt)
- `templates` (prompt templates object)
- `bio` (required, but shown as `description` in docs)
- `postExamples` (array of example posts)
- `adjectives` (character traits)
- `settings` (configuration object)
- `secrets` (secure configuration)
- `style` (writing style guides with sub-properties: all, chat, post)

#### Properties with Incorrect Names in Documentation:
- Documentation shows `personality` but actual type uses `adjectives`
- Documentation shows `description` but actual type uses `bio`

### 2. Type Mismatches

#### `bio` Property:
- **Actual Type**: `string | string[]` (can be a single string or array of strings)
- **Documentation**: Not mentioned, shows `description` instead

#### `messageExamples` Property:
- **Actual Type**: `MessageExample[][]` (2D array - array of conversation arrays)
- **Documentation**: Shows flat array with incorrect structure

#### `knowledge` Property:
- **Actual Type**: `(string | { path: string; shared?: boolean } | DirectoryItem)[]`
- **Documentation**: Shows as simple string array

### 3. Missing Type Information

The documentation doesn't explain:
- The `Agent` type that extends `Character`
- The `TemplateType` for dynamic prompts
- The `MessageExample` interface structure
- The `DirectoryItem` interface for knowledge directories
- Optional vs required properties

### 4. Agent Type Extension

The `Agent` interface extends `Character` with:
```typescript
interface Agent extends Character {
  enabled?: boolean;
  status?: AgentStatus;
  createdAt: number;
  updatedAt: number;
}
```

This runtime representation is not mentioned in the documentation at all.

## Correct Character Structure

Based on the actual TypeScript definitions, here's the correct structure:

```typescript
interface Character {
  // Identification
  id?: UUID;                    // Optional unique identifier
  name: string;                 // Required display name
  username?: string;            // Optional username
  
  // Behavior Configuration
  system?: string;              // System prompt
  templates?: {                 // Prompt templates
    [key: string]: string | ((options: { state: State }) => string);
  };
  
  // Character Definition
  bio: string | string[];       // Biography (required)
  messageExamples?: MessageExample[][];  // 2D array of conversations
  postExamples?: string[];      // Example posts
  
  // Knowledge & Traits
  topics?: string[];            // Known topics
  adjectives?: string[];        // Character traits
  knowledge?: (string | { path: string; shared?: boolean } | DirectoryItem)[];
  
  // Extensions & Configuration
  plugins?: string[];           // Plugin names
  settings?: {                  // General settings
    [key: string]: string | boolean | number | Record<string, any>;
  };
  secrets?: {                   // Secure settings
    [key: string]: string | boolean | number;
  };
  
  // Style Guidelines
  style?: {
    all?: string[];           // General style rules
    chat?: string[];          // Chat-specific style
    post?: string[];          // Post-specific style
  };
}
```

## Recommendations

1. **Update Documentation Structure**: Completely rewrite the agents.mdx documentation to reflect the actual type structure.

2. **Add Type Reference**: Include TypeScript interface definitions in the documentation.

3. **Explain Complex Types**: Add sections explaining:
   - MessageExample structure and 2D array format
   - Knowledge item variations
   - Template types and dynamic prompts
   - Style guidelines usage

4. **Add Agent Type Documentation**: Explain how Agent extends Character for runtime use.

5. **Provide Complete Examples**: Show real character.json examples that demonstrate all available properties.

6. **Document Property Requirements**: Clearly indicate which properties are required vs optional.

7. **Version Compatibility**: Note that there are v1 and v2 specs, and document any differences.
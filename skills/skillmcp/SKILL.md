---
name: skillmcp
description: >-
  Connect to, query, and manage skills using the SkillMCP (Skill Management System) MCP server over Streamable HTTP (/mcp) or SSE (/sse).
  Use this skill whenever discovering, searching, inspecting, or fetching AI agent skills, reference documents, or examples from a SkillMCP server instance.
category: software
---

# SkillMCP MCP Server Integration

A guide and reference workflow for connecting to, discovering, searching, and consuming AI agent skills via the **SkillMCP (Skill Management System)** Model Context Protocol (MCP) server.

---

## 🚀 Quick Start

### 1. Connection Endpoints

SkillMCP supports both **Streamable HTTP Transport** (recommended) and **SSE Transport**:

| Transport Mode | Endpoint URL | HTTP Method | Header Requirements |
| :--- | :--- | :--- | :--- |
| **Streamable HTTP (Default)** | `http://<host>:8080/mcp` *(or `/sse`)* | `POST` | `Accept: application/json, text/event-stream` |
| **SSE Transport** | `http://<host>:8080/sse` | `GET` (stream) + `POST` (/messages) | Standard SSE headers |
| **Health Check** | `http://<host>:8080/healthz` | `GET` | None |

### 2. Antigravity MCP Configuration (`mcp_config.json`)

To register SkillMCP as a remote HTTP MCP server in Antigravity or standard MCP clients:

```json
{
  "mcpServers": {
    "skillmcp": {
      "type": "http",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

---

## 🛠️ Workflows

### Workflow 1: Connecting & Initializing the Server

1. **Verify Health**:
   Send a `GET` request to `http://<host>:8080/healthz`. Verify `status_code == 200` and response content `{"status": "healthy", ...}`.
2. **Perform MCP Handshake (Streamable HTTP)**:
   Send an `initialize` JSON-RPC request to `/mcp` with header `Accept: application/json, text/event-stream`:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "initialize",
     "params": {
       "protocolVersion": "2024-11-05",
       "capabilities": {},
       "clientInfo": { "name": "agent-client", "version": "1.0.0" }
     }
   }
   ```
3. **Confirm Capabilities**: Ensure server returns protocol version `2024-11-05` and declared capabilities for `tools`, `prompts`, and `resources`.

---

### Workflow 2: Discovering & Fetching Skills

1. **List All Available Skills**:
   Call the `list_skills` MCP tool to retrieve an array of available skills with names, descriptions, and metadata:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 2,
     "method": "tools/call",
     "params": {
       "name": "list_skills",
       "arguments": {}
     }
   }
   ```
2. **Search Skills by Keyword**:
   Call `search_skills` when looking for skills matching a specific workflow keyword or topic:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 3,
     "method": "tools/call",
     "params": {
       "name": "search_skills",
       "arguments": { "query": "python trem" }
     }
   }
   ```
3. **Fetch Full Skill Content**:
   Call `get_skill` to retrieve the complete `SKILL.md` instructions and frontmatter for a specific skill:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 4,
     "method": "tools/call",
     "params": {
       "name": "get_skill",
       "arguments": { "name": "trem-python" }
     }
   }
   ```

---

### Workflow 3: Inspecting References, Examples & Resources

1. **Read Bundled Skill Reference**:
   When a skill references additional documentation in `references/`, fetch it using `read_skill_reference`:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 5,
     "method": "tools/call",
     "params": {
       "name": "read_skill_reference",
       "arguments": {
         "name": "trem-python",
         "ref_path": "references/stack-patterns.md"
       }
     }
   }
   ```
2. **Read Bundled Skill Example**:
   When a skill references example walkthroughs in `examples/`, fetch it using `read_skill_example`:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 6,
     "method": "tools/call",
     "params": {
       "name": "read_skill_example",
       "arguments": {
         "name": "trem-python",
         "example_path": "examples/typer-fastmcp-example.md"
       }
     }
   }
   ```
3. **Read via MCP Resource URI**:
   SkillMCP exposes skills directly as MCP resources at `skill://{name}`:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 7,
     "method": "resources/read",
     "params": {
       "uri": "skill://trem-python"
     }
   }
   ```

---

## 📋 MCP Tools & Resources Reference Table

| Name | Type | Description | Key Arguments |
| :--- | :--- | :--- | :--- |
| `list_skills` | Tool | List all available skills with metadata, references, and examples. | None |
| `get_skill` | Tool | Get full instructions and markdown content for a skill. | `name` (str) |
| `search_skills` | Tool | Search available skills by keyword or topic query. | `query` (str) |
| `read_skill_reference` | Tool | Read a bundled reference document for a given skill. | `name` (str), `ref_path` (str) |
| `read_skill_example` | Tool | Read a bundled example document for a given skill. | `name` (str), `example_path` (str) |
| `skill://{name}` | Resource | MCP Resource URI returning full skill document markdown. | `name` (URI parameter) |

---

## 📚 Deep Dive References & Examples

- [SkillMCP API & JSON-RPC Specification](references/api-spec.md) — Complete JSON-RPC tool signatures and transport details.
- [MCP Client Implementation Examples](examples/mcp-client-usage.md) — Python, TypeScript, and cURL examples for interacting with SkillMCP.

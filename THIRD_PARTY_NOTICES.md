# Third-Party Notices & Skill Licenses

This document declares the skills bundled, distributed, and used within the **SkillMCP** project, along with their authors, provenance, and license terms.

---

## Summary of Packaged Server Skills (`skills/`)

These domain skills are served and distributed via the SkillMCP Model Context Protocol (MCP) server:

| Skill | Category | Primary Purpose | Origin / Attribution | License |
| :--- | :--- | :--- | :--- | :--- |
| **`skillmcp`** | `software` | MCP connection, discovery, and tool integration guide | SkillMCP Project (clivechung) | MIT |
| **`tdd`** | `software` | Test-Driven Development (red-green-refactor loop) | Agile / Kent Beck TDD methodology | MIT |
| **`trem`** | `software` | TREM code review & verification framework (T, R, E, M) | SkillMCP Quality Engineering | MIT |
| **`trem-python`** | `software` | Python engineering patterns (`uv`, `fastmcp`, `typer`) | SkillMCP Quality Engineering | MIT |

---

## Summary of Workspace Agent Skills (`.agents/skills/`)

These meta-skills assist autonomous coding agents during development within this repository:

| Skill | Primary Purpose | Origin / Attribution | License |
| :--- | :--- | :--- | :--- |
| **`write-a-skill`** | 4-phase interactive skill authoring workflow | Adapted from Matt Pocock's skill authoring methodology | MIT |
| **`to-spec`** | Synthesizes conversation context into structured specs | Adapted from Matt Pocock's agent workflows | MIT |
| **`handoff`** | Generates session handoff artifacts for agent continuity | Agent IDE Workflow Standards | MIT |
| **`tdd`** | Test-driven development red-green-refactor loop | Agile / Kent Beck TDD methodology | MIT |
| **`trem`** | TREM architectural review and quality audit | SkillMCP Quality Engineering | MIT |
| **`trem-python`** | Modern Python TREM development guide | SkillMCP Quality Engineering | MIT |

---

## Detailed Skill Declarations & Licenses

### 1. SkillMCP Server Integration (`skills/skillmcp`)
- **Path**: `skills/skillmcp/SKILL.md`
- **Author**: clivechung <https://github.com/clivechung/skillmcp>
- **License**: MIT
- **Copyright**: Copyright (c) 2026 clivechung
- **Description**: Operational workflow and JSON-RPC specifications for discovering, searching, inspecting, and retrieving skills from SkillMCP.

```text
MIT License

Copyright (c) 2026 clivechung

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

### 2. Test-Driven Development (`skills/tdd` & `.agents/skills/tdd`)
- **Paths**: `skills/tdd/SKILL.md`, `.agents/skills/tdd/SKILL.md`
- **Attribution**: Based on Agile / Extreme Programming TDD methodologies (Kent Beck)
- **License**: MIT
- **Description**: Red-green-refactor execution loop for building software with deterministic test seams.

```text
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

### 3. TREM Engineering Framework (`skills/trem` & `skills/trem-python`)
- **Paths**: `skills/trem/SKILL.md`, `skills/trem-python/SKILL.md`, `.agents/skills/trem/SKILL.md`, `.agents/skills/trem-python/SKILL.md`
- **Author**: SkillMCP Quality Engineering / clivechung
- **License**: MIT
- **Copyright**: Copyright (c) 2026 clivechung
- **Description**: Software quality assessment framework evaluating codebases against the 4 TREM pillars: Testable, Readable, Extensible, and Maintainable.

```text
MIT License

Copyright (c) 2026 clivechung

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

### 4. Skill Authoring & Spec Synthesis (`.agents/skills/write-a-skill` & `.agents/skills/to-spec`)
- **Paths**: `.agents/skills/write-a-skill/SKILL.md`, `.agents/skills/to-spec/SKILL.md`
- **Attribution**: Adapted from Matt Pocock's agent skill workflows and prompt design methodologies (<https://github.com/mattpocock>)
- **License**: MIT
- **Description**: Workflows for structured skill authoring, progressive disclosure decomposition, and conversation-to-spec synthesis.

```text
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

### 5. Agent Handoff (`.agents/skills/handoff`)
- **Path**: `.agents/skills/handoff/SKILL.md`
- **Attribution**: Agent IDE Multi-Session Continuity Guidelines
- **License**: MIT
- **Description**: Protocol for compacting conversation context and directing next-session agent skills.

```text
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## Main Project License

For the core SkillMCP server engine, CLI tools, Docker configurations, and tests, see [LICENSE](LICENSE).

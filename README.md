# Zhifeng Jin

**AI Agent · AIOps · MCP · RAG · DevOps**

I build enterprise systems that let AI agents operate infrastructure and knowledge under security, tenancy, and observability constraints — not chatbot demos.

[![GitHub](https://img.shields.io/badge/GitHub-zhifengjin050--arch-181717?logo=github)](https://github.com/zhifengjin050-arch)

---

## Focus

| Area | What I ship |
|------|----------------|
| **AI Agent** | Planner, tool calling, memory, traces |
| **AIOps** | Incident diagnosis, Kubernetes RCA, automation |
| **MCP** | Governed tools for Linux / Docker / K8s / SSH |
| **RAG** | Hybrid retrieval, knowledge graph, document pipelines |
| **DevOps** | Docker Compose, Kubernetes, Helm, CI |

---

## Core projects

### 1. [Enterprise AI DevOps Platform](https://github.com/zhifengjin050-arch/enterprise-ai-sre-platform)

LangGraph SRE Agent: MCP tool calling, RAG knowledge hub, memory, multi-tenant console, Docker.

`Python` `FastAPI` `LangGraph` `MCP` `RAG` `Kubernetes` `React`

### 2. [Enterprise DevOps MCP Server](https://github.com/zhifengjin050-arch/enterprise-devops-mcp-server)

MCP server with **17 tools** and a security layer (RBAC, execute gate, command filter, audit). Default **read-only**.

`Python` `MCP` `Docker` `Kubernetes` `SSH` `pytest`

### 3. [Enterprise AI Agent Platform](https://github.com/zhifengjin050-arch/enterprise-ai-agent-platform)

Enterprise knowledge-base Agent: connectors, hybrid RAG, knowledge graph, workflow engine, JWT/RBAC, Helm.

`Python` `FastAPI` `RAG` `Knowledge Graph` `Workflow` `Helm`

---

## Stack

```text
AI Agent Runtime    LangGraph / custom planner + tools + memory
Protocol            MCP (Model Context Protocol)
Retrieval           Hybrid RAG (vector + full-text + graph)
Backend             Python 3.11+ · FastAPI · SQLAlchemy
Frontend            React · TypeScript · Vite
Data                PostgreSQL · Redis · Chroma / pgvector
Ops                 Docker · Kubernetes · Helm · GitHub Actions
```

---

## How to evaluate in 5 minutes

1. Open the three repos above (README is bilingual).
2. Skim Architecture (Mermaid) + Screenshots.
3. Note security defaults: multi-tenant RBAC, MCP execute gate, Apache-2.0 / MIT licenses.

---

*Open-source packaging for hiring review — production-oriented Agent / AIOps work.*

import * as fs from "fs";
import * as path from "path";
import {
  ReposYaml,
  ServiceGraph,
  GraphNode,
  GraphEdge,
} from "../types/index.js";
import { loadRepos } from "../utils/loader.js";

const ROOT_DIR = path.resolve(__dirname, "../..");
const GENERATED_DIR = path.join(ROOT_DIR, "generated");

/**
 * Generate service dependency graph from repos.yml
 */
export function generateServiceGraph(
  reposData?: ReposYaml,
  filters?: {
    stage?: number;
    domain?: string;
    tier?: string;
  }
): ServiceGraph {
  const data = reposData || loadRepos();

  const graph: ServiceGraph = {
    nodes: [],
    edges: [],
  };

  // Filter repositories if needed
  let repos = data.repos;
  if (filters) {
    repos = repos.filter((repo) => {
      if (filters.stage !== undefined && repo.stage !== filters.stage)
        return false;
      if (filters.domain && repo.domain !== filters.domain) return false;
      if (filters.tier && repo.tier !== filters.tier) return false;
      return true;
    });
  }

  // Create nodes for each repository
  for (const repo of repos) {
    const node: GraphNode = {
      id: repo.id,
      name: repo.name,
      type: "service",
      metadata: {
        stage: repo.stage,
        domain: repo.domain,
        tier: repo.tier,
        status: repo.status,
        runtime: repo.runtime,
        tags: repo.tags,
      },
    };

    graph.nodes.push(node);
  }

  // Create edges for internal dependencies
  for (const repo of repos) {
    if (repo.dependencies?.internal) {
      for (const dep of repo.dependencies.internal) {
        // Check if dependency exists in filtered repos
        const depRepo = repos.find((r) => r.name === dep || r.id === dep);
        if (depRepo) {
          const edge: GraphEdge = {
            from: repo.id,
            to: depRepo.id,
            type: "internal",
            label: "depends on",
          };
          graph.edges.push(edge);
        }
      }
    }
  }

  return graph;
}

/**
 * Convert service graph to Mermaid diagram syntax
 */
export function graphToMermaid(graph: ServiceGraph): string {
  let mermaid = "graph TD\n";

  // Add nodes with labels
  for (const node of graph.nodes) {
    const label = `${node.name}`;
    const nodeStyle =
      node.metadata?.tier === "tier_0"
        ? ":::tier0"
        : node.metadata?.tier === "tier_1"
        ? ":::tier1"
        : ":::tier2";
    mermaid += `  ${node.id}["${label}"]${nodeStyle}\n`;
  }

  // Add edges
  for (const edge of graph.edges) {
    const label = edge.label ? `|"${edge.label}"|` : "";
    mermaid += `  ${edge.from} -->${label} ${edge.to}\n`;
  }

  // Add styling
  mermaid += "\n";
  mermaid +=
    "  classDef tier0 fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff\n";
  mermaid +=
    "  classDef tier1 fill:#4dabf7,stroke:#1971c2,stroke-width:2px,color:#fff\n";
  mermaid +=
    "  classDef tier2 fill:#69db7c,stroke:#2f9e44,stroke-width:2px,color:#fff\n";

  return mermaid;
}

/**
 * Convert service graph to DOT (Graphviz) format
 */
export function graphToDot(
  graph: ServiceGraph,
  graphName: string = "services"
): string {
  let dot = `digraph ${graphName} {\n`;
  dot += "  rankdir=LR;\n";
  dot += "  node [shape=box, style=rounded];\n\n";

  // Add nodes
  for (const node of graph.nodes) {
    const color =
      node.metadata?.tier === "tier_0"
        ? "red"
        : node.metadata?.tier === "tier_1"
        ? "blue"
        : "green";
    const label = `${node.name}\\n(${node.metadata?.stage || "N/A"})`;
    const attrs = `label="${label}", color="${color}", fillcolor="${color}20", style="filled,rounded"`;
    dot += `  "${node.id}" [${attrs}];\n`;
  }

  dot += "\n";

  // Add edges
  for (const edge of graph.edges) {
    const label = edge.label ? ` [label="${edge.label}"]` : "";
    dot += `  "${edge.from}" -> "${edge.to}"${label};\n`;
  }

  dot += "}\n";

  return dot;
}

/**
 * Write graph to file
 */
export function writeGraph(content: string, filename: string): string {
  if (!fs.existsSync(GENERATED_DIR)) {
    fs.mkdirSync(GENERATED_DIR, { recursive: true });
  }

  const outputPath = path.join(GENERATED_DIR, filename);
  fs.writeFileSync(outputPath, content, "utf8");

  return outputPath;
}

/**
 * Generate and write service graph in multiple formats
 */
export function generateAndWriteGraphs(filters?: {
  stage?: number;
  domain?: string;
  tier?: string;
}): {
  json: string;
  mermaid: string;
  dot: string;
} {
  const graph = generateServiceGraph(undefined, filters);

  const jsonPath = writeGraph(
    JSON.stringify(graph, null, 2),
    "service-graph.json"
  );
  const mermaidPath = writeGraph(graphToMermaid(graph), "service-graph.mmd");
  const dotPath = writeGraph(graphToDot(graph), "service-graph.dot");

  return {
    json: jsonPath,
    mermaid: mermaidPath,
    dot: dotPath,
  };
}

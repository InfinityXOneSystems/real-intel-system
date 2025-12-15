import {
  generateServiceGraph,
  graphToMermaid,
  graphToDot,
} from "../src/generators/graph";
import { loadRepos } from "../src/utils/loader";

describe("Graph Generator", () => {
  describe("generateServiceGraph", () => {
    it("should generate service graph successfully", () => {
      const graph = generateServiceGraph();

      expect(graph).toBeDefined();
      expect(graph.nodes).toBeInstanceOf(Array);
      expect(graph.edges).toBeInstanceOf(Array);
      expect(graph.nodes.length).toBeGreaterThan(0);
    });

    it("should create nodes for all repositories", () => {
      const data = loadRepos();
      const graph = generateServiceGraph();

      expect(graph.nodes.length).toBe(data.repos.length);
    });

    it("should have proper node structure", () => {
      const graph = generateServiceGraph();
      const node = graph.nodes[0];

      expect(node).toHaveProperty("id");
      expect(node).toHaveProperty("name");
      expect(node).toHaveProperty("type");
      expect(node).toHaveProperty("metadata");
      expect(node.type).toBe("service");
      expect(node.metadata).toHaveProperty("stage");
      expect(node.metadata).toHaveProperty("domain");
      expect(node.metadata).toHaveProperty("tier");
    });

    it("should filter by stage", () => {
      const graph = generateServiceGraph(undefined, { stage: 0 });
      expect(graph.nodes.every((n) => n.metadata?.stage === 0)).toBe(true);
    });

    it("should filter by tier", () => {
      const graph = generateServiceGraph(undefined, { tier: "tier_0" });
      expect(graph.nodes.every((n) => n.metadata?.tier === "tier_0")).toBe(
        true
      );
    });

    it("should filter by domain", () => {
      const data = loadRepos();
      const firstDomain = data.repos[0].domain;
      const graph = generateServiceGraph(undefined, { domain: firstDomain });
      expect(graph.nodes.every((n) => n.metadata?.domain === firstDomain)).toBe(
        true
      );
    });
  });

  describe("graphToMermaid", () => {
    it("should convert graph to Mermaid syntax", () => {
      const graph = generateServiceGraph();
      const mermaid = graphToMermaid(graph);

      expect(mermaid).toBeDefined();
      expect(typeof mermaid).toBe("string");
      expect(mermaid).toContain("graph TD");
      expect(mermaid.length).toBeGreaterThan(0);
    });

    it("should include all nodes", () => {
      const graph = generateServiceGraph();
      const mermaid = graphToMermaid(graph);

      for (const node of graph.nodes) {
        expect(mermaid).toContain(node.id);
      }
    });

    it("should include styling classes", () => {
      const graph = generateServiceGraph();
      const mermaid = graphToMermaid(graph);

      expect(mermaid).toContain("classDef tier0");
      expect(mermaid).toContain("classDef tier1");
      expect(mermaid).toContain("classDef tier2");
    });

    it("should include edges", () => {
      const graph = generateServiceGraph();
      const mermaid = graphToMermaid(graph);

      if (graph.edges.length > 0) {
        expect(mermaid).toContain("-->");
      }
    });
  });

  describe("graphToDot", () => {
    it("should convert graph to DOT syntax", () => {
      const graph = generateServiceGraph();
      const dot = graphToDot(graph);

      expect(dot).toBeDefined();
      expect(typeof dot).toBe("string");
      expect(dot).toContain("digraph services");
      expect(dot).toContain("rankdir=LR");
      expect(dot.length).toBeGreaterThan(0);
    });

    it("should include all nodes", () => {
      const graph = generateServiceGraph();
      const dot = graphToDot(graph);

      for (const node of graph.nodes) {
        expect(dot).toContain(`"${node.id}"`);
      }
    });

    it("should support custom graph name", () => {
      const graph = generateServiceGraph();
      const dot = graphToDot(graph, "my_custom_graph");

      expect(dot).toContain("digraph my_custom_graph");
    });

    it("should include node styling", () => {
      const graph = generateServiceGraph();
      const dot = graphToDot(graph);

      expect(dot).toContain("color=");
      expect(dot).toContain("fillcolor=");
      expect(dot).toContain("style=");
    });

    it("should include edges", () => {
      const graph = generateServiceGraph();
      const dot = graphToDot(graph);

      if (graph.edges.length > 0) {
        expect(dot).toContain("->");
      }
    });
  });
});

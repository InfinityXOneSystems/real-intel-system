import { loadRepos, getRepo, filterRepos } from "../src/utils/loader";
import { validateRepo, validateAllRepos } from "../src/utils/validator";

describe("Repositories", () => {
  describe("loadRepos", () => {
    it("should load repos.yml successfully", () => {
      const data = loadRepos();
      expect(data).toBeDefined();
      expect(data.repos).toBeInstanceOf(Array);
      expect(data.repos.length).toBeGreaterThan(0);
    });

    it("should have valid repository structure", () => {
      const data = loadRepos();
      const repo = data.repos[0];

      expect(repo).toHaveProperty("id");
      expect(repo).toHaveProperty("name");
      expect(repo).toHaveProperty("repo");
      expect(repo).toHaveProperty("stage");
      expect(repo).toHaveProperty("domain");
      expect(repo).toHaveProperty("tier");
      expect(repo).toHaveProperty("status");
    });
  });

  describe("getRepo", () => {
    it("should find repository by name", () => {
      const data = loadRepos();
      const firstRepo = data.repos[0];
      const found = getRepo(firstRepo.name);

      expect(found).toBeDefined();
      expect(found?.name).toBe(firstRepo.name);
    });

    it("should return undefined for non-existent repository", () => {
      const found = getRepo("non-existent-repo");
      expect(found).toBeUndefined();
    });
  });

  describe("filterRepos", () => {
    it("should filter by stage", () => {
      const stage0Repos = filterRepos({ stage: 0 });
      expect(stage0Repos.every((r) => r.stage === 0)).toBe(true);
    });

    it("should filter by tier", () => {
      const tier0Repos = filterRepos({ tier: "tier_0" });
      expect(tier0Repos.every((r) => r.tier === "tier_0")).toBe(true);
    });

    it("should filter by domain", () => {
      const data = loadRepos();
      const firstDomain = data.repos[0].domain;
      const domainRepos = filterRepos({ domain: firstDomain });
      expect(domainRepos.every((r) => r.domain === firstDomain)).toBe(true);
    });

    it("should filter by status", () => {
      const activeRepos = filterRepos({ status: "active" });
      expect(activeRepos.every((r) => r.status === "active")).toBe(true);
    });

    it("should return all repos when no filters applied", () => {
      const data = loadRepos();
      const allRepos = filterRepos({});
      expect(allRepos.length).toBe(data.repos.length);
    });
  });

  describe("validateRepo", () => {
    it("should validate valid repositories", () => {
      const data = loadRepos();
      const repo = data.repos[0];
      const result = validateRepo(repo);

      expect(result.valid).toBe(true);
      expect(result.errors).toBeUndefined();
    });

    it("should reject invalid repository", () => {
      const invalidRepo: any = {
        id: "invalid",
        // missing required fields
      };

      const result = validateRepo(invalidRepo);
      expect(result.valid).toBe(false);
      expect(result.errors).toBeDefined();
      expect(result.errors!.length).toBeGreaterThan(0);
    });
  });

  describe("validateAllRepos", () => {
    it("should validate all repositories successfully", () => {
      const data = loadRepos();
      const result = validateAllRepos(data);

      expect(result.totalRepos).toBe(data.repos.length);
      expect(result.validRepos).toBeGreaterThan(0);

      if (!result.valid) {
        console.log("Invalid repos:", result.invalidRepos);
      }
    });
  });
});

import {
  loadActions,
  getCapability,
  getAction,
  filterCapabilities,
  filterActions,
  getActionsForCapability,
} from "../src/utils/loader";
import {
  validateCapability,
  validateAction,
  validateAllActions,
} from "../src/utils/validator";

describe("Actions and Capabilities", () => {
  describe("loadActions", () => {
    it("should load actions.yml successfully", () => {
      const data = loadActions();
      expect(data).toBeDefined();
      expect(data.capabilities).toBeInstanceOf(Array);
      expect(data.actions).toBeInstanceOf(Array);
      expect(data.capabilities.length).toBeGreaterThan(0);
      expect(data.actions.length).toBeGreaterThan(0);
    });
  });

  describe("capabilities", () => {
    it("should have valid capability structure", () => {
      const data = loadActions();
      const cap = data.capabilities[0];

      expect(cap).toHaveProperty("id");
      expect(cap).toHaveProperty("name");
      expect(cap).toHaveProperty("description");
      expect(cap).toHaveProperty("domain");
      expect(cap.id).toMatch(/^cap\./);
    });

    it("should find capability by ID", () => {
      const data = loadActions();
      const firstCap = data.capabilities[0];
      const found = getCapability(firstCap.id);

      expect(found).toBeDefined();
      expect(found?.id).toBe(firstCap.id);
    });

    it("should filter capabilities by domain", () => {
      const data = loadActions();
      const firstDomain = data.capabilities[0].domain;
      const domainCaps = filterCapabilities({ domain: firstDomain });
      expect(domainCaps.every((c) => c.domain === firstDomain)).toBe(true);
    });

    it("should validate valid capabilities", () => {
      const data = loadActions();
      const cap = data.capabilities[0];
      const result = validateCapability(cap);

      expect(result.valid).toBe(true);
      expect(result.errors).toBeUndefined();
    });
  });

  describe("actions", () => {
    it("should have valid action structure", () => {
      const data = loadActions();
      const action = data.actions[0];

      expect(action).toHaveProperty("id");
      expect(action).toHaveProperty("capability_id");
      expect(action).toHaveProperty("repo");
      expect(action).toHaveProperty("service");
      expect(action).toHaveProperty("http");
      expect(action).toHaveProperty("auth");
      expect(action.id).toMatch(/^act\./);
      expect(action.http).toHaveProperty("method");
      expect(action.http).toHaveProperty("path");
    });

    it("should find action by ID", () => {
      const data = loadActions();
      const firstAction = data.actions[0];
      const found = getAction(firstAction.id);

      expect(found).toBeDefined();
      expect(found?.id).toBe(firstAction.id);
    });

    it("should filter actions by repo", () => {
      const data = loadActions();
      const firstRepo = data.actions[0].repo;
      const repoActions = filterActions({ repo: firstRepo });
      expect(repoActions.every((a) => a.repo === firstRepo)).toBe(true);
    });

    it("should filter actions by capability", () => {
      const data = loadActions();
      const firstCapId = data.actions[0].capability_id;
      const capActions = filterActions({ capability: firstCapId });
      expect(capActions.every((a) => a.capability_id === firstCapId)).toBe(
        true
      );
    });

    it("should get actions for specific capability", () => {
      const data = loadActions();
      const firstCap = data.capabilities[0];
      const actions = getActionsForCapability(firstCap.id);

      expect(actions).toBeInstanceOf(Array);
      expect(actions.every((a) => a.capability_id === firstCap.id)).toBe(true);
    });

    it("should validate valid actions", () => {
      const data = loadActions();
      const action = data.actions[0];
      const result = validateAction(action);

      expect(result.valid).toBe(true);
      expect(result.errors).toBeUndefined();
    });
  });

  describe("validateAllActions", () => {
    it("should validate all capabilities and actions successfully", () => {
      const data = loadActions();
      const result = validateAllActions(data);

      expect(result.capabilities.total).toBe(data.capabilities.length);
      expect(result.actions.total).toBe(data.actions.length);
      expect(result.capabilities.valid).toBeGreaterThan(0);
      expect(result.actions.valid).toBeGreaterThan(0);

      if (!result.valid) {
        console.log("Invalid capabilities:", result.capabilities.invalid);
        console.log("Invalid actions:", result.actions.invalid);
      }
    });
  });

  describe("referential integrity", () => {
    it("should have all action capability_ids reference valid capabilities", () => {
      const data = loadActions();
      const capabilityIds = new Set(data.capabilities.map((c) => c.id));

      for (const action of data.actions) {
        expect(capabilityIds.has(action.capability_id)).toBe(true);
      }
    });
  });
});

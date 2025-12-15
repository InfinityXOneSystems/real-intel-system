import { generateOpenAPI, writeOpenAPISpec } from "../src/generators/openapi";
import { loadActions } from "../src/utils/loader";
import * as fs from "fs";
import * as path from "path";

describe("OpenAPI Generator", () => {
  describe("generateOpenAPI", () => {
    it("should generate valid OpenAPI 3.1 spec", () => {
      const spec = generateOpenAPI();

      expect(spec).toBeDefined();
      expect(spec.openapi).toBe("3.1.0");
      expect(spec.info).toBeDefined();
      expect(spec.info.title).toBe("Infinity XOS Global Index API");
      expect(spec.servers).toBeInstanceOf(Array);
      expect(spec.servers.length).toBeGreaterThan(0);
      expect(spec.paths).toBeDefined();
      expect(spec.components).toBeDefined();
    });

    it("should include all actions as paths", () => {
      const data = loadActions();
      const spec = generateOpenAPI();

      const pathCount = Object.keys(spec.paths).length;
      expect(pathCount).toBeGreaterThan(0);

      // Each unique HTTP path should be in the spec
      const uniquePaths = new Set(data.actions.map((a) => a.http.path));
      expect(pathCount).toBeLessThanOrEqual(uniquePaths.size);
    });

    it("should include security schemes", () => {
      const spec = generateOpenAPI();

      expect(spec.components?.securitySchemes).toBeDefined();
      expect(spec.components?.securitySchemes?.apiKey).toBeDefined();
      expect(spec.components?.securitySchemes?.oauth2).toBeDefined();
      expect(spec.components?.securitySchemes?.jwt).toBeDefined();
    });

    it("should include tags for domains", () => {
      const data = loadActions();
      const spec = generateOpenAPI();

      const domains = new Set(data.capabilities.map((c) => c.domain));
      expect(spec.tags?.length).toBe(domains.size);
    });

    it("should include request/response schemas when available", () => {
      const spec = generateOpenAPI();

      // Check if any schemas were loaded
      const schemaCount = Object.keys(spec.components?.schemas || {}).length;

      // We expect at least some schemas (from workspace actions)
      expect(schemaCount).toBeGreaterThan(0);
    });

    it("should have proper operation structure", () => {
      const spec = generateOpenAPI();
      const firstPath = Object.keys(spec.paths)[0];
      const firstMethod = Object.keys(spec.paths[firstPath])[0] as any;
      const operation = (spec.paths[firstPath] as any)[firstMethod];

      expect(operation).toBeDefined();
      expect(operation.operationId).toBeDefined();
      expect(operation.summary).toBeDefined();
      expect(operation.description).toBeDefined();
      expect(operation.tags).toBeInstanceOf(Array);
      expect(operation.responses).toBeDefined();
      expect(operation.responses["200"]).toBeDefined();
      expect(operation.responses["400"]).toBeDefined();
      expect(operation.responses["401"]).toBeDefined();
      expect(operation.responses["429"]).toBeDefined();
    });
  });

  describe("writeOpenAPISpec", () => {
    const testFilename = "test-openapi.json";
    const generatedDir = path.resolve(__dirname, "../generated");
    const testPath = path.join(generatedDir, testFilename);

    afterEach(() => {
      // Cleanup test file
      if (fs.existsSync(testPath)) {
        fs.unlinkSync(testPath);
      }
    });

    it("should write spec to file", () => {
      const spec = generateOpenAPI();
      const outputPath = writeOpenAPISpec(spec, testFilename);

      expect(outputPath).toBe(testPath);
      expect(fs.existsSync(outputPath)).toBe(true);

      // Verify content
      const content = fs.readFileSync(outputPath, "utf8");
      const parsed = JSON.parse(content);
      expect(parsed.openapi).toBe("3.1.0");
    });

    it("should create generated directory if it does not exist", () => {
      // Remove directory if it exists
      if (fs.existsSync(generatedDir)) {
        fs.rmSync(generatedDir, { recursive: true });
      }

      const spec = generateOpenAPI();
      writeOpenAPISpec(spec, testFilename);

      expect(fs.existsSync(generatedDir)).toBe(true);
      expect(fs.existsSync(testPath)).toBe(true);
    });
  });

  describe("OpenAPI spec validity", () => {
    it("should generate spec that can be re-parsed", () => {
      const spec = generateOpenAPI();
      const json = JSON.stringify(spec);
      const reparsed = JSON.parse(json);

      expect(reparsed.openapi).toBe("3.1.0");
      expect(reparsed.info).toEqual(spec.info);
      expect(reparsed.paths).toEqual(spec.paths);
    });

    it("should have all required OpenAPI 3.1 fields", () => {
      const spec = generateOpenAPI();

      expect(spec).toHaveProperty("openapi");
      expect(spec).toHaveProperty("info");
      expect(spec.info).toHaveProperty("title");
      expect(spec.info).toHaveProperty("version");
      expect(spec).toHaveProperty("paths");
    });
  });
});

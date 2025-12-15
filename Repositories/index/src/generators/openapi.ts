import * as fs from "fs";
import * as path from "path";
import {
  ActionsYaml,
  OpenAPISpec,
  PathItem,
  Operation,
  Response,
} from "../types/index.js";
import { loadActions, loadSchema } from "../utils/loader.js";

const ROOT_DIR = path.resolve(__dirname, "../..");
const GENERATED_DIR = path.join(ROOT_DIR, "generated");

/**
 * Generate OpenAPI 3.1 specification from actions.yml
 */
export function generateOpenAPI(actionsData?: ActionsYaml): OpenAPISpec {
  const data = actionsData || loadActions();

  const spec: OpenAPISpec = {
    openapi: "3.1.0",
    info: {
      title: "Infinity XOS Global Index API",
      version: "1.0.0",
      description:
        "Tier-0 Global Index and Capabilities Registry for Infinity XOS / fullauto.systems. This API provides discovery and invocation of all platform capabilities, actions, and services.",
      contact: {
        name: "Infinity XOS Team",
        url: "https://github.com/InfinityXOneSystems",
      },
    },
    servers: [
      {
        url: "https://index.fullauto.systems",
        description: "Production Global Index",
      },
      {
        url: "https://index-staging.fullauto.systems",
        description: "Staging Global Index",
      },
      {
        url: "http://localhost:3000",
        description: "Local Development",
      },
    ],
    paths: {},
    components: {
      schemas: {},
      securitySchemes: {
        apiKey: {
          type: "apiKey",
          in: "header",
          name: "X-API-Key",
          description: "Internal API key for service-to-service authentication",
        },
        oauth2: {
          type: "oauth2",
          flows: {
            authorizationCode: {
              authorizationUrl: "https://auth.fullauto.systems/oauth/authorize",
              tokenUrl: "https://auth.fullauto.systems/oauth/token",
              scopes: {
                "workspace:read": "Read workspace data",
                "workspace:write": "Write workspace data",
                "social:read": "Read social data",
                "social:write": "Write social data",
                "agents:execute": "Execute agent actions",
                "ml:execute": "Execute ML actions",
              },
            },
          },
        },
        jwt: {
          type: "http",
          scheme: "bearer",
          bearerFormat: "JWT",
          description: "JWT token for authenticated requests",
        },
      },
    },
    tags: [],
  };

  // Group actions by domain for tags
  const domains = new Set<string>();
  data.capabilities.forEach((cap) => domains.add(cap.domain));

  spec.tags = Array.from(domains).map((domain) => ({
    name: domain,
    description: `${
      domain.charAt(0).toUpperCase() + domain.slice(1)
    } domain capabilities`,
  }));

  // Build paths from actions
  for (const action of data.actions) {
    const capability = data.capabilities.find(
      (c) => c.id === action.capability_id
    );

    if (!capability) {
      console.warn(
        `Capability ${action.capability_id} not found for action ${action.id}`
      );
      continue;
    }

    const pathKey = action.http.path;

    if (!spec.paths[pathKey]) {
      spec.paths[pathKey] = {};
    }

    const method = action.http.method.toLowerCase() as keyof PathItem;
    const operation: Operation = {
      operationId: action.id,
      summary: capability.name,
      description: action.description || capability.description,
      tags: [capability.domain],
      parameters: [],
      responses: {
        "200": {
          description: "Successful response",
          content: {},
        },
        "400": {
          description: "Bad request - invalid parameters",
        },
        "401": {
          description: "Unauthorized - missing or invalid authentication",
        },
        "403": {
          description: "Forbidden - insufficient permissions",
        },
        "429": {
          description: "Too many requests - rate limit exceeded",
        },
        "500": {
          description: "Internal server error",
        },
      },
    };

    // Add security based on auth type
    if (action.auth === "internal_api_key") {
      operation.security = [{ apiKey: [] }];
    } else if (action.auth === "oauth2") {
      operation.security = [{ oauth2: [`${capability.domain}:write`] }];
    } else if (action.auth === "jwt") {
      operation.security = [{ jwt: [] }];
    }

    // Add request body if input schema exists
    if (action.input_schema_ref) {
      operation.requestBody = {
        required: true,
        content: {
          "application/json": {
            schema: {
              $ref: `#/components/schemas/${action.id}_request`,
            },
          },
        },
      };

      // Load and add input schema to components
      try {
        const inputSchema = loadSchema(action.input_schema_ref);
        if (spec.components) {
          spec.components.schemas![`${action.id}_request`] = inputSchema;
        }
      } catch (error) {
        console.warn(`Failed to load input schema for ${action.id}: ${error}`);
      }
    }

    // Add response schema if output schema exists
    if (action.output_schema_ref) {
      (operation.responses["200"] as Response).content = {
        "application/json": {
          schema: {
            $ref: `#/components/schemas/${action.id}_response`,
          },
        },
      };

      // Load and add output schema to components
      try {
        const outputSchema = loadSchema(action.output_schema_ref);
        if (spec.components) {
          spec.components.schemas![`${action.id}_response`] = outputSchema;
        }
      } catch (error) {
        console.warn(`Failed to load output schema for ${action.id}: ${error}`);
      }
    }

    // Add rate limit info to description
    if (capability.rate_limit) {
      operation.description += `\n\n**Rate Limits:**\n`;
      if (capability.rate_limit.requests_per_minute) {
        operation.description += `- ${capability.rate_limit.requests_per_minute} requests per minute\n`;
      }
      if (capability.rate_limit.requests_per_hour) {
        operation.description += `- ${capability.rate_limit.requests_per_hour} requests per hour\n`;
      }
    }

    spec.paths[pathKey][method] = operation;
  }

  return spec;
}

/**
 * Write OpenAPI spec to file
 */
export function writeOpenAPISpec(
  spec: OpenAPISpec,
  filename: string = "openapi-actions.json"
): string {
  if (!fs.existsSync(GENERATED_DIR)) {
    fs.mkdirSync(GENERATED_DIR, { recursive: true });
  }

  const outputPath = path.join(GENERATED_DIR, filename);
  fs.writeFileSync(outputPath, JSON.stringify(spec, null, 2), "utf8");

  return outputPath;
}

/**
 * Generate and write OpenAPI spec in one step
 */
export function generateAndWriteOpenAPI(filename?: string): {
  spec: OpenAPISpec;
  path: string;
} {
  const spec = generateOpenAPI();
  const outputPath = writeOpenAPISpec(spec, filename);

  return { spec, path: outputPath };
}

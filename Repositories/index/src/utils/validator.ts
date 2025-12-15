import addFormats from "ajv-formats";
import draft2020 from "ajv/dist/2020.js";
import { loadSchema } from "./loader.js";
import {
  Repo,
  Capability,
  Action,
  ReposYaml,
  ActionsYaml,
} from "../types/index.js";

// Initialize AJV with JSON Schema Draft 2020-12
const ajv = new draft2020({
  strict: false,
  allErrors: true,
  verbose: true,
});

// Add format validation (email, uri, date-time, etc.)
addFormats(ajv);

// Cache compiled schemas
const schemaCache: Map<string, any> = new Map();

/**
 * Load and compile a JSON schema
 */
function getCompiledSchema(schemaPath: string) {
  if (schemaCache.has(schemaPath)) {
    return schemaCache.get(schemaPath);
  }

  const schema = loadSchema(schemaPath);
  // Remove $id to avoid duplicate registration errors
  const schemaCopy = { ...schema };
  delete schemaCopy.$id;
  const compiled = ajv.compile(schemaCopy);
  schemaCache.set(schemaPath, compiled);

  return compiled;
}

/**
 * Validate a repository against repo.schema.json
 */
export function validateRepo(repo: Repo): {
  valid: boolean;
  errors?: string[];
} {
  try {
    const validate = getCompiledSchema("repos/repo.schema.json");
    const valid = validate(repo);

    if (!valid && validate.errors) {
      return {
        valid: false,
        errors: validate.errors.map(
          (err: { instancePath: string; message?: string }) =>
            `${err.instancePath} ${err.message}`
        ),
      };
    }

    return { valid: true };
  } catch (error) {
    return {
      valid: false,
      errors: [error instanceof Error ? error.message : String(error)],
    };
  }
}

/**
 * Validate a capability against capability.schema.json
 */
export function validateCapability(capability: Capability): {
  valid: boolean;
  errors?: string[];
} {
  try {
    const validate = getCompiledSchema("capabilities/capability.schema.json");
    const valid = validate(capability);

    if (!valid && validate.errors) {
      return {
        valid: false,
        errors: validate.errors.map(
          (err: { instancePath: string; message?: string }) =>
            `${err.instancePath} ${err.message}`
        ),
      };
    }

    return { valid: true };
  } catch (error) {
    return {
      valid: false,
      errors: [error instanceof Error ? error.message : String(error)],
    };
  }
}

/**
 * Validate an action against action.schema.json
 */
export function validateAction(action: Action): {
  valid: boolean;
  errors?: string[];
} {
  try {
    const validate = getCompiledSchema("actions/action.schema.json");
    const valid = validate(action);

    if (!valid && validate.errors) {
      return {
        valid: false,
        errors: validate.errors.map(
          (err: { instancePath: string; message?: string }) =>
            `${err.instancePath} ${err.message}`
        ),
      };
    }

    return { valid: true };
  } catch (error) {
    return {
      valid: false,
      errors: [error instanceof Error ? error.message : String(error)],
    };
  }
}

/**
 * Validate all repositories in repos.yml
 */
export function validateAllRepos(reposData: ReposYaml): {
  valid: boolean;
  totalRepos: number;
  validRepos: number;
  invalidRepos: { name: string; errors: string[] }[];
} {
  const results = {
    valid: true,
    totalRepos: reposData.repos.length,
    validRepos: 0,
    invalidRepos: [] as { name: string; errors: string[] }[],
  };

  for (const repo of reposData.repos) {
    const validation = validateRepo(repo);

    if (validation.valid) {
      results.validRepos++;
    } else {
      results.valid = false;
      results.invalidRepos.push({
        name: repo.name,
        errors: validation.errors || ["Unknown error"],
      });
    }
  }

  return results;
}

/**
 * Validate all capabilities and actions in actions.yml
 */
export function validateAllActions(actionsData: ActionsYaml): {
  valid: boolean;
  capabilities: {
    total: number;
    valid: number;
    invalid: { id: string; errors: string[] }[];
  };
  actions: {
    total: number;
    valid: number;
    invalid: { id: string; errors: string[] }[];
  };
} {
  const results = {
    valid: true,
    capabilities: {
      total: actionsData.capabilities.length,
      valid: 0,
      invalid: [] as { id: string; errors: string[] }[],
    },
    actions: {
      total: actionsData.actions.length,
      valid: 0,
      invalid: [] as { id: string; errors: string[] }[],
    },
  };

  // Validate capabilities
  for (const capability of actionsData.capabilities) {
    const validation = validateCapability(capability);

    if (validation.valid) {
      results.capabilities.valid++;
    } else {
      results.valid = false;
      results.capabilities.invalid.push({
        id: capability.id,
        errors: validation.errors || ["Unknown error"],
      });
    }
  }

  // Validate actions
  for (const action of actionsData.actions) {
    const validation = validateAction(action);

    if (validation.valid) {
      results.actions.valid++;
    } else {
      results.valid = false;
      results.actions.invalid.push({
        id: action.id,
        errors: validation.errors || ["Unknown error"],
      });
    }
  }

  return results;
}

/**
 * Validate all configurations (repos and actions)
 */
export interface ValidationSummary {
  valid: boolean;
  repos: ReturnType<typeof validateAllRepos>;
  actions: ReturnType<typeof validateAllActions>;
}

export function validateAll(
  reposData: ReposYaml,
  actionsData: ActionsYaml
): ValidationSummary {
  const reposValidation = validateAllRepos(reposData);
  const actionsValidation = validateAllActions(actionsData);

  return {
    valid: reposValidation.valid && actionsValidation.valid,
    repos: reposValidation,
    actions: actionsValidation,
  };
}

import * as fs from "fs";
import * as path from "path";
import YAML from "yaml";
import {
  ReposYaml,
  ActionsYaml,
  Repo,
  Capability,
  Action,
} from "../types/index.js";

const ROOT_DIR = path.resolve(__dirname, "../..");
const CONFIG_DIR = path.join(ROOT_DIR, "config");
const SCHEMAS_DIR = path.join(ROOT_DIR, "schemas");

/**
 * Load and parse repos.yml configuration file
 */
export function loadRepos(): ReposYaml {
  const filePath = path.join(CONFIG_DIR, "repos.yml");

  if (!fs.existsSync(filePath)) {
    throw new Error(`repos.yml not found at ${filePath}`);
  }

  const content = fs.readFileSync(filePath, "utf8");
  const data = YAML.parse(content) as ReposYaml;

  if (!data || !Array.isArray(data.repos)) {
    throw new Error(
      "Invalid repos.yml structure: missing or invalid repositories array"
    );
  }

  return data;
}

/**
 * Load and parse actions.yml configuration file
 */
export function loadActions(): ActionsYaml {
  const filePath = path.join(CONFIG_DIR, "actions.yml");

  if (!fs.existsSync(filePath)) {
    throw new Error(`actions.yml not found at ${filePath}`);
  }

  const content = fs.readFileSync(filePath, "utf8");
  const data = YAML.parse(content) as ActionsYaml;

  if (
    !data ||
    !Array.isArray(data.capabilities) ||
    !Array.isArray(data.actions)
  ) {
    throw new Error(
      "Invalid actions.yml structure: missing capabilities or actions arrays"
    );
  }

  return data;
}

/**
 * Load a JSON schema file
 */
export function loadSchema(schemaPath: string): any {
  const fullPath = path.join(SCHEMAS_DIR, schemaPath);

  if (!fs.existsSync(fullPath)) {
    throw new Error(`Schema not found at ${fullPath}`);
  }

  const content = fs.readFileSync(fullPath, "utf8");
  return JSON.parse(content);
}

/**
 * Get a specific repository by name
 */
export function getRepo(name: string): Repo | undefined {
  const { repos } = loadRepos();
  return repos.find((repo) => repo.name === name || repo.id === name);
}

/**
 * Get a specific capability by ID
 */
export function getCapability(id: string): Capability | undefined {
  const { capabilities } = loadActions();
  return capabilities.find((cap) => cap.id === id);
}

/**
 * Get a specific action by ID
 */
export function getAction(id: string): Action | undefined {
  const { actions } = loadActions();
  return actions.find((action) => action.id === id);
}

/**
 * Get all actions for a specific capability
 */
export function getActionsForCapability(capabilityId: string): Action[] {
  const { actions } = loadActions();
  return actions.filter((action) => action.capability_id === capabilityId);
}

/**
 * Get all actions for a specific repo
 */
export function getActionsForRepo(repoName: string): Action[] {
  const { actions } = loadActions();
  return actions.filter((action) => action.repo === repoName);
}

/**
 * Filter repositories by criteria
 */
export function filterRepos(filters: {
  stage?: number;
  domain?: string;
  tier?: string;
  status?: string;
  tag?: string;
}): Repo[] {
  const { repos } = loadRepos();

  return repos.filter((repo) => {
    if (filters.stage !== undefined && repo.stage !== filters.stage)
      return false;
    if (filters.domain && repo.domain !== filters.domain) return false;
    if (filters.tier && repo.tier !== filters.tier) return false;
    if (filters.status && repo.status !== filters.status) return false;
    if (filters.tag && (!repo.tags || !repo.tags.includes(filters.tag)))
      return false;
    return true;
  });
}

/**
 * Filter capabilities by criteria
 */
export function filterCapabilities(filters: {
  domain?: string;
  tag?: string;
}): Capability[] {
  const { capabilities } = loadActions();

  return capabilities.filter((cap) => {
    if (filters.domain && cap.domain !== filters.domain) return false;
    if (filters.tag && (!cap.tags || !cap.tags.includes(filters.tag)))
      return false;
    return true;
  });
}

/**
 * Filter actions by criteria
 */
export function filterActions(filters: {
  repo?: string;
  capability?: string;
  domain?: string;
}): Action[] {
  const { actions, capabilities } = loadActions();

  return actions.filter((action) => {
    if (filters.repo && action.repo !== filters.repo) return false;
    if (filters.capability && action.capability_id !== filters.capability)
      return false;
    if (filters.domain) {
      const cap = capabilities.find((c) => c.id === action.capability_id);
      if (!cap || cap.domain !== filters.domain) return false;
    }
    return true;
  });
}
